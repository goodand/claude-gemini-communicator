#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Iterable


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_RELATIVE_RE = re.compile(r"`((?:\.\.?/)[^`]+)`")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Audit portable hierarchy for skill docs by classifying internal, bridge, "
            "and external sibling references."
        )
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=Path.cwd(),
        help="Workspace root that contains the audited skill directories.",
    )
    parser.add_argument(
        "--skill-dir",
        action="append",
        dest="skill_dirs",
        type=Path,
        required=True,
        help="Skill directory to audit. Repeat for multiple skills.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Optional path to write machine-readable audit output.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        help="Optional path to write markdown audit summary.",
    )
    parser.add_argument(
        "--include-legacy",
        action="store_true",
        help="Include markdown files under legacy/ directories. Default excludes them.",
    )
    parser.add_argument(
        "--exclude-glob",
        action="append",
        default=[],
        help="Glob pattern, relative to the skill dir, to exclude from audit. Repeatable.",
    )
    return parser.parse_args()


def _iter_markdown_files(skill_dir: Path, include_legacy: bool, exclude_globs: list[str]) -> Iterable[Path]:
    for path in sorted(skill_dir.rglob("*.md")):
        if path.is_file():
            if not include_legacy and "legacy" in path.parts:
                continue
            relative_path = path.relative_to(skill_dir)
            if any(relative_path.match(pattern) for pattern in exclude_globs):
                continue
            yield path


def _normalize_raw_reference(raw: str) -> str | None:
    value = raw.strip()
    if not value:
        return None
    if value == "URL":
        return None
    if value.startswith(("http://", "https://", "mailto:", "#")):
        return None
    if value.startswith("<") and value.endswith(">"):
        value = value[1:-1]
    if " " in value and not value.startswith("/"):
        value = value.split(" ", 1)[0]
    return value


def _extract_references(text: str) -> list[str]:
    found: set[str] = set()
    for raw in MARKDOWN_LINK_RE.findall(text):
        normalized = _normalize_raw_reference(raw)
        if normalized is not None:
            found.add(normalized)
    for raw in INLINE_RELATIVE_RE.findall(text):
        normalized = _normalize_raw_reference(raw)
        if normalized is not None:
            found.add(normalized)
    return sorted(found)


def _render_markdown(payload: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append("# Skill Portability Audit")
    lines.append("")
    lines.append(f"- workspace_root: `{payload['workspace_root']}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    totals = payload["summary"]["classification_totals"]
    for key in [
        "internal",
        "bridge",
        "external_dependency",
        "outside_workspace",
        "absolute_path",
        "missing",
    ]:
        lines.append(f"- `{key}`: `{totals.get(key, 0)}`")
    lines.append("")
    lines.append("## Skills")
    lines.append("")
    for skill_result in payload["skills"]:
        lines.append(f"### {skill_result['skill']}")
        lines.append("")
        counts = skill_result["counts"]
        for key in [
            "internal",
            "bridge",
            "external_dependency",
            "outside_workspace",
            "absolute_path",
            "missing",
        ]:
            lines.append(f"- `{key}`: `{counts.get(key, 0)}`")
        findings = skill_result["findings"]
        if findings:
            lines.append("- notable findings:")
            for finding in findings[:8]:
                target = finding.get("target_skill") or finding["classification"]
                lines.append(
                    f"  - `{finding['classification']}`: `{finding['source']}` -> "
                    f"`{finding['raw_reference']}` ({target})"
                )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _classify_reference(
    raw_reference: str,
    source_path: Path,
    current_skill_root: Path,
    workspace_root: Path,
    audited_skill_roots: dict[str, Path],
) -> dict[str, object]:
    if raw_reference.startswith("/"):
        resolved = Path(raw_reference)
        return {
            "source": str(source_path.relative_to(current_skill_root)),
            "raw_reference": raw_reference,
            "resolved_path": str(resolved),
            "classification": "absolute_path",
        }

    resolved = (source_path.parent / raw_reference).resolve()
    if not resolved.exists():
        return {
            "source": str(source_path.relative_to(current_skill_root)),
            "raw_reference": raw_reference,
            "resolved_path": str(resolved),
            "classification": "missing",
        }

    if resolved.is_relative_to(current_skill_root.resolve()):
        classification = "internal"
        target_skill = current_skill_root.name
    else:
        classification = "outside_workspace"
        target_skill = None
        for skill_name, skill_root in audited_skill_roots.items():
            if skill_root == current_skill_root:
                continue
            if resolved.is_relative_to(skill_root.resolve()):
                classification = "bridge"
                target_skill = skill_name
                break
        if classification != "bridge" and resolved.is_relative_to(workspace_root.resolve()):
            classification = "external_dependency"

    finding: dict[str, object] = {
        "source": str(source_path.relative_to(current_skill_root)),
        "raw_reference": raw_reference,
        "resolved_path": str(resolved),
        "classification": classification,
    }
    if target_skill is not None:
        finding["target_skill"] = target_skill
    return finding


def _audit_skill(
    skill_root: Path,
    workspace_root: Path,
    audited_skill_roots: dict[str, Path],
    include_legacy: bool,
    exclude_globs: list[str],
) -> dict[str, object]:
    findings: list[dict[str, object]] = []
    counts = {
        "internal": 0,
        "bridge": 0,
        "external_dependency": 0,
        "outside_workspace": 0,
        "absolute_path": 0,
        "missing": 0,
    }
    for markdown_path in _iter_markdown_files(
        skill_root,
        include_legacy=include_legacy,
        exclude_globs=exclude_globs,
    ):
        text = markdown_path.read_text(encoding="utf-8")
        for raw_reference in _extract_references(text):
            finding = _classify_reference(
                raw_reference=raw_reference,
                source_path=markdown_path,
                current_skill_root=skill_root,
                workspace_root=workspace_root,
                audited_skill_roots=audited_skill_roots,
            )
            counts[finding["classification"]] += 1
            findings.append(finding)
    return {
        "skill": skill_root.name,
        "counts": counts,
        "findings": findings,
    }


def main() -> int:
    args = _parse_args()
    workspace_root = args.workspace_root.resolve()
    skill_roots = [path.resolve() for path in args.skill_dirs]
    audited_skill_roots = {path.name: path for path in skill_roots}

    skill_results = [
        _audit_skill(
            skill_root=skill_root,
            workspace_root=workspace_root,
            audited_skill_roots=audited_skill_roots,
            include_legacy=args.include_legacy,
            exclude_globs=args.exclude_glob,
        )
        for skill_root in skill_roots
    ]

    totals = {
        "internal": 0,
        "bridge": 0,
        "external_dependency": 0,
        "outside_workspace": 0,
        "absolute_path": 0,
        "missing": 0,
    }
    for skill_result in skill_results:
        for key, value in skill_result["counts"].items():
            totals[key] += value

    payload = {
        "workspace_root": str(workspace_root),
        "summary": {
            "skill_count": len(skill_results),
            "classification_totals": totals,
        },
        "skills": skill_results,
    }

    rendered_json = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(rendered_json, encoding="utf-8")
    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        args.output_md.write_text(_render_markdown(payload), encoding="utf-8")
    sys.stdout.write(rendered_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
