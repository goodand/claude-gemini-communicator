#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from uuid import uuid4

DEFAULT_EXCLUDES = frozenset({
    '.git',
    '.hg',
    '.svn',
    '.venv',
    'venv',
    'node_modules',
    '__pycache__',
    '.mypy_cache',
    '.pytest_cache',
})

# Canonical graph kinds allowed by spec
ALLOWED_GRAPH_KINDS = {"codebase_graph", "analysis_graph", "merged_graph"}

# Documentation-only file types excluded from canonical graph nodes
DOC_ONLY_SUFFIXES = {".md", ".txt", ".rst"}
DOC_ONLY_PREFIXES = {"README", "CHANGELOG", "LICENSE"}


def merge_excluded_dir_names(extra_names: Iterable[str] | None = None) -> set[str]:
    excluded = set(DEFAULT_EXCLUDES)
    if extra_names:
        excluded.update(name for name in extra_names if name)
    return excluded


def merge_name_filter(names: Iterable[str] | None = None) -> set[str]:
    if not names:
        return set()
    return {name for name in names if name}


def should_include_top_level(rel_path: Path, include_names: set[str], exclude_names: set[str]) -> bool:
    top_level = rel_path.parts[0] if rel_path.parts else '.'
    if include_names and top_level not in include_names:
        return False
    if top_level in exclude_names:
        return False
    return True


def iter_files(root: Path, excludes: set[str], include_top_level_names: set[str] | None = None, exclude_top_level_names: set[str] | None = None) -> Iterable[Path]:
    include_names = set(include_top_level_names or set())
    exclude_names = set(exclude_top_level_names or set())
    for path in root.rglob('*'):
        parts = set(path.parts)
        if parts & excludes:
            continue
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if not should_include_top_level(rel, include_names, exclude_names):
            continue
        yield path


def top_level_bucket(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    return rel.parts[0] if rel.parts else '.'


def analyze_python_file(py_file: Path) -> tuple[int, bool]:
    try:
        tree = ast.parse(py_file.read_text(encoding='utf-8'))
    except Exception:
        return 0, True
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            count += 1
    return count, False


def build_summary(
    root: Path,
    top_n_ext: int,
    excluded_dir_names: set[str] | None = None,
    include_top_level_names: set[str] | None = None,
    exclude_top_level_names: set[str] | None = None,
) -> dict:
    excludes = set(excluded_dir_names or DEFAULT_EXCLUDES)
    include_names = set(include_top_level_names or set())
    exclude_names = set(exclude_top_level_names or set())
    total_files = 0
    python_files = 0
    total_import_statements = 0
    python_parse_failure_files: list[str] = []
    top_level_counts: dict[str, int] = defaultdict(int)
    ext_counts: Counter[str] = Counter()

    for path in iter_files(root, excludes, include_names, exclude_names):
        total_files += 1
        rel_path = path.relative_to(root)
        top_level_counts[top_level_bucket(root, path)] += 1
        ext = path.suffix or '<no_ext>'
        ext_counts[ext] += 1
        if path.suffix == '.py':
            python_files += 1
            import_count, parse_failed = analyze_python_file(path)
            total_import_statements += import_count
            if parse_failed:
                python_parse_failure_files.append(rel_path.as_posix())

    return {
        'repo_root': str(root),
        'total_files': total_files,
        'python_files': python_files,
        'total_import_statements': total_import_statements,
        'python_parse_failure_count': len(python_parse_failure_files),
        'python_parse_failure_files': sorted(python_parse_failure_files),
        'top_level_file_counts': dict(sorted(top_level_counts.items())),
        'top_extensions': dict(ext_counts.most_common(top_n_ext)),
        'excluded_dir_names': sorted(excludes),
        'included_top_level_names': sorted(include_names),
        'excluded_top_level_names': sorted(exclude_names),
    }


def _resolve_module_to_file(module_name: str, py_file: Path, root: Path, level: int) -> Path | None:
    """Resolve a module name to a file path within the repo.

    Returns the resolved Path if found, else None.
    level > 0 means relative import (from . import x, from .. import y).
    """
    if level > 0:
        # Relative import: base is py_file's directory, going up (level-1) times
        base = py_file.parent
        for _ in range(level - 1):
            base = base.parent
        # module_name may be empty for bare "from . import x"
        if module_name:
            rel_parts = module_name.replace(".", "/")
            candidates = [
                base / (rel_parts + ".py"),
                base / rel_parts / "__init__.py",
            ]
        else:
            # "from . import x" — base package __init__.py
            candidates = [base / "__init__.py"]
    else:
        rel_parts = module_name.replace(".", "/")
        candidates = [
            root / (rel_parts + ".py"),
            root / rel_parts / "__init__.py",
        ]

    for candidate in candidates:
        try:
            if candidate.exists() and candidate.is_file():
                # Ensure it's inside the repo
                candidate.relative_to(root)
                return candidate
        except ValueError:
            continue
    return None


def extract_imports(py_file: Path, root: Path) -> tuple[list[dict], list[dict]]:
    """Extract import edges and sidecar evidence from a Python file.

    Returns:
        edges: list of edge dicts with src, dst, rel fields
        sidecar: list of sidecar evidence dicts
    """
    edges: list[dict] = []
    sidecar: list[dict] = []

    src_rel = py_file.relative_to(root).as_posix()
    src_anchor = f"file:{src_rel}"

    try:
        source = py_file.read_text(encoding='utf-8')
        tree = ast.parse(source)
    except Exception as exc:
        sidecar.append({
            "evidence_kind": "warning",
            "subject_anchor": src_anchor,
            "summary": f"Failed to parse {src_rel}",
            "source_path": src_rel,
            "evidence_path": src_rel,
            "reason": f"parse failure: {exc}",
            "confidence": 0.0,
        })
        return edges, sidecar

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_name = alias.name
                resolved = _resolve_module_to_file(module_name, py_file, root, level=0)
                if resolved is not None:
                    dst_rel = resolved.relative_to(root).as_posix()
                    edges.append({
                        "src": src_anchor,
                        "dst": f"file:{dst_rel}",
                        "rel": "IMPORTS",
                        "source_tool": "ast_import_extractor",
                        "confidence": 1.0,
                    })
                else:
                    sidecar.append({
                        "evidence_kind": "unresolved",
                        "subject_anchor": src_anchor,
                        "summary": f"Unresolved import: {module_name}",
                        "source_path": src_rel,
                        "evidence_path": src_rel,
                        "reason": f"module '{module_name}' not found in repo",
                        "confidence": 0.0,
                    })
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            level = node.level
            # For each imported name, first try resolving module_name.alias_name
            # (e.g. "from src import core" → try "src.core" → src/core.py).
            # Fall back to resolving module_name alone if that fails.
            resolved_any = False
            for alias in node.names:
                resolved = None
                if module_name and not level:
                    # Try the more-specific sub-module path first
                    combined = f"{module_name}.{alias.name}"
                    resolved = _resolve_module_to_file(combined, py_file, root, level=0)
                if resolved is None:
                    resolved = _resolve_module_to_file(module_name, py_file, root, level=level)
                if resolved is not None:
                    dst_rel = resolved.relative_to(root).as_posix()
                    edges.append({
                        "src": src_anchor,
                        "dst": f"file:{dst_rel}",
                        "rel": "IMPORTS",
                        "source_tool": "ast_import_extractor",
                        "confidence": 1.0,
                    })
                    resolved_any = True
            if not resolved_any:
                full_module = ("." * level) + module_name if module_name else "." * level
                sidecar.append({
                    "evidence_kind": "unresolved",
                    "subject_anchor": src_anchor,
                    "summary": f"Unresolved import: {full_module}",
                    "source_path": src_rel,
                    "evidence_path": src_rel,
                    "reason": f"module '{full_module}' not found in repo",
                    "confidence": 0.0,
                })

    return edges, sidecar


def _is_doc_only_file(path: Path) -> bool:
    """Return True if file should be excluded from canonical graph nodes."""
    if path.suffix.lower() in DOC_ONLY_SUFFIXES:
        return True
    for prefix in DOC_ONLY_PREFIXES:
        if path.name.startswith(prefix):
            return True
    return False


def collect_nodes(
    root: Path,
    excludes: set[str],
    include_top_level_names: set[str] | None = None,
    exclude_top_level_names: set[str] | None = None,
) -> list[dict]:
    """Collect File and Folder nodes for the canonical graph.

    Documentation-only files (.md, .txt, .rst, README*, CHANGELOG*, LICENSE*)
    are excluded. Empty directories (no included files) produce no Folder node.
    """
    nodes: list[dict] = []
    seen_folders: set[str] = set()

    for path in iter_files(root, excludes, include_top_level_names, exclude_top_level_names):
        if _is_doc_only_file(path):
            continue

        rel = path.relative_to(root)
        rel_posix = rel.as_posix()
        file_id = f"file:{rel_posix}"

        # Determine region (top-level directory or ".")
        region = rel.parts[0] if len(rel.parts) > 1 else "."

        # Parent folder
        parent_rel = rel.parent
        if parent_rel == Path("."):
            parent_id = "folder:."
        else:
            parent_id = f"folder:{parent_rel.as_posix()}"

        nodes.append({
            "id": file_id,
            "kind": "File",
            "name": path.name,
            "path": rel_posix,
            "parent_id": parent_id,
            "region": region,
            "source_tool": "tree_survey",
            "confidence": 1.0,
        })

        # Ensure Folder node for parent (and ancestors up to root)
        current = rel.parent
        while True:
            if current == Path("."):
                folder_id = "folder:."
                folder_name = root.name
                folder_parent_id = None
            else:
                folder_id = f"folder:{current.as_posix()}"
                folder_name = current.name
                parent_of_current = current.parent
                if parent_of_current == Path("."):
                    folder_parent_id = "folder:."
                else:
                    folder_parent_id = f"folder:{parent_of_current.as_posix()}"

            if folder_id not in seen_folders:
                seen_folders.add(folder_id)
                folder_node: dict = {
                    "id": folder_id,
                    "kind": "Folder",
                    "name": folder_name,
                    "path": current.as_posix(),
                    "source_tool": "tree_survey",
                    "confidence": 1.0,
                }
                if folder_parent_id is not None:
                    folder_node["parent_id"] = folder_parent_id
                nodes.append(folder_node)

            if current == Path("."):
                break
            current = current.parent

    return nodes


def build_canonical_graph(
    root: Path,
    graph_kind: str = "codebase_graph",
    excludes: set[str] | None = None,
    include_top_level_names: set[str] | None = None,
    exclude_top_level_names: set[str] | None = None,
) -> tuple[dict, list[dict]]:
    """Build the canonical graph dict and sidecar evidence list.

    Returns:
        graph_dict: normalized_graph.json-shaped dict
        sidecar_evidence: list of sidecar evidence records
    """
    if graph_kind not in ALLOWED_GRAPH_KINDS:
        raise ValueError(
            f"graph_kind must be one of {ALLOWED_GRAPH_KINDS!r}, got {graph_kind!r}"
        )

    effective_excludes = set(excludes if excludes is not None else DEFAULT_EXCLUDES)

    # Step 2a: collect nodes
    nodes = collect_nodes(
        root,
        effective_excludes,
        include_top_level_names,
        exclude_top_level_names,
    )

    # Step 2b: collect edges and sidecar from Python files
    edges: list[dict] = []
    sidecar_evidence: list[dict] = []

    for node in nodes:
        if node["kind"] == "File" and node["name"].endswith(".py"):
            file_path = root / node["path"]
            file_edges, file_sidecar = extract_imports(file_path, root)
            edges.extend(file_edges)
            sidecar_evidence.extend(file_sidecar)

    # Step 2c: assemble graph dict
    timestamp = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    graph_id = f"{graph_kind}_{root.name}_{timestamp}"

    graph_dict = {
        "graph_id": graph_id,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "source_scope": str(root),
        "graph_kind": graph_kind,
        "schema_version": "1",
        "nodes": nodes,
        "edges": edges,
    }

    return graph_dict, sidecar_evidence


def write_canonical_artifacts(
    graph_dict: dict,
    sidecar_evidence: list[dict],
    output_dir: Path,
) -> dict:
    """Write canonical artifact files to output_dir.

    Outputs:
        normalized_graph.json
        nodes.jsonl
        edges.jsonl
        graph_meta.json
        sidecar_evidence.jsonl  (only if sidecar_evidence is non-empty)

    Returns:
        graph_meta dict
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # normalized_graph.json
    normalized_path = output_dir / "normalized_graph.json"
    normalized_path.write_text(
        json.dumps(graph_dict, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # nodes.jsonl
    nodes_path = output_dir / "nodes.jsonl"
    nodes_lines = "\n".join(json.dumps(n, ensure_ascii=False) for n in graph_dict["nodes"])
    nodes_path.write_text(nodes_lines + "\n" if nodes_lines else "", encoding="utf-8")

    # edges.jsonl
    edges_path = output_dir / "edges.jsonl"
    edges_lines = "\n".join(json.dumps(e, ensure_ascii=False) for e in graph_dict["edges"])
    edges_path.write_text(edges_lines + "\n" if edges_lines else "", encoding="utf-8")

    # graph_meta.json
    graph_meta = {
        "graph_id": graph_dict["graph_id"],
        "schema_version": graph_dict["schema_version"],
        "generated_at": graph_dict["generated_at"],
        "source_scope": graph_dict["source_scope"],
        "graph_kind": graph_dict["graph_kind"],
        "artifact_paths": {
            "normalized_graph": "normalized_graph.json",
            "nodes": "nodes.jsonl",
            "edges": "edges.jsonl",
        },
        "trace_id": str(uuid4()),
        "artifact_location": str(output_dir),
    }
    meta_path = output_dir / "graph_meta.json"
    meta_path.write_text(json.dumps(graph_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    # Sidecar routing path — write only if non-empty, but the branch always exists
    if sidecar_evidence:
        sidecar_path = output_dir / "sidecar_evidence.jsonl"
        sidecar_lines = "\n".join(json.dumps(s, ensure_ascii=False) for s in sidecar_evidence)
        sidecar_path.write_text(sidecar_lines + "\n", encoding="utf-8")

    return graph_meta


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a coarse codebase analysis summary for a repository root.')
    parser.add_argument('repo_root', help='Path to the repository root to analyze')
    parser.add_argument('--top-n-ext', type=int, default=10, help='How many file extensions to keep in the summary')
    parser.add_argument(
        '--exclude-dir-name',
        action='append',
        default=[],
        help='Additional directory name to exclude anywhere in the tree. Repeatable.',
    )
    parser.add_argument(
        '--include-top-level',
        action='append',
        default=[],
        help='Restrict analysis to these top-level names. Repeatable.',
    )
    parser.add_argument(
        '--exclude-top-level',
        action='append',
        default=[],
        help='Exclude these top-level names after include filtering. Repeatable.',
    )
    parser.add_argument('--output', help='Optional path to write the JSON summary')
    parser.add_argument(
        '--canonical-output',
        help='Optional directory to write canonical graph artifacts (normalized_graph.json, nodes.jsonl, edges.jsonl, graph_meta.json)',
    )
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f'repo_root must be an existing directory: {root}')

    summary = build_summary(
        root,
        args.top_n_ext,
        excluded_dir_names=merge_excluded_dir_names(args.exclude_dir_name),
        include_top_level_names=merge_name_filter(args.include_top_level),
        exclude_top_level_names=merge_name_filter(args.exclude_top_level),
    )
    text = json.dumps(summary, ensure_ascii=False, indent=2) + '\n'

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding='utf-8')
    else:
        print(text, end='')

    if args.canonical_output:
        canonical_dir = Path(args.canonical_output)
        graph_dict, sidecar_evidence = build_canonical_graph(
            root,
            excludes=merge_excluded_dir_names(args.exclude_dir_name),
            include_top_level_names=merge_name_filter(args.include_top_level),
            exclude_top_level_names=merge_name_filter(args.exclude_top_level),
        )
        write_canonical_artifacts(graph_dict, sidecar_evidence, canonical_dir)

    return 0


if __name__ == '__main__':
    raise SystemExit(main())
