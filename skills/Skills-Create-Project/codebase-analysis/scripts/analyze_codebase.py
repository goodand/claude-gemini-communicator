#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

DEFAULT_EXCLUDES = {'.git', '.hg', '.svn', '.venv', 'venv', 'node_modules', '__pycache__', '.mypy_cache', '.pytest_cache'}


def iter_files(root: Path, excludes: set[str]) -> Iterable[Path]:
    for path in root.rglob('*'):
        parts = set(path.parts)
        if parts & excludes:
            continue
        if path.is_file():
            yield path


def top_level_bucket(root: Path, path: Path) -> str:
    rel = path.relative_to(root)
    return rel.parts[0] if rel.parts else '.'


def import_count(py_file: Path) -> int:
    try:
        tree = ast.parse(py_file.read_text(encoding='utf-8'))
    except Exception:
        return 0
    count = 0
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            count += 1
    return count


def build_summary(root: Path, top_n_ext: int) -> dict:
    total_files = 0
    python_files = 0
    total_import_statements = 0
    top_level_counts: dict[str, int] = defaultdict(int)
    ext_counts: Counter[str] = Counter()

    for path in iter_files(root, DEFAULT_EXCLUDES):
        total_files += 1
        top_level_counts[top_level_bucket(root, path)] += 1
        ext = path.suffix or '<no_ext>'
        ext_counts[ext] += 1
        if path.suffix == '.py':
            python_files += 1
            total_import_statements += import_count(path)

    return {
        'repo_root': str(root),
        'total_files': total_files,
        'python_files': python_files,
        'total_import_statements': total_import_statements,
        'top_level_file_counts': dict(sorted(top_level_counts.items())),
        'top_extensions': dict(ext_counts.most_common(top_n_ext)),
        'excluded_dir_names': sorted(DEFAULT_EXCLUDES),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Run a coarse codebase analysis summary for a repository root.')
    parser.add_argument('repo_root', help='Path to the repository root to analyze')
    parser.add_argument('--top-n-ext', type=int, default=10, help='How many file extensions to keep in the summary')
    parser.add_argument('--output', help='Optional path to write the JSON summary')
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f'repo_root must be an existing directory: {root}')

    summary = build_summary(root, args.top_n_ext)
    text = json.dumps(summary, ensure_ascii=False, indent=2) + '\n'

    if args.output:
        out = Path(args.output)
        out.write_text(text, encoding='utf-8')
    else:
        print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
