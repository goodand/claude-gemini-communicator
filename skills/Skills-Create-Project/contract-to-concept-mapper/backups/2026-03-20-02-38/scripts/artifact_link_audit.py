#!/usr/bin/env python3
"""Audit local artifact links and inline path references in skill markdown files."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`([^`]+)`")
PATH_PREFIXES = (
    "scripts/",
    "references/",
    "knowledge_bases/",
    "checklist-forconsistency-evaluation/",
    "checklist-forimplementation/",
    "evals/",
    "legacy/",
    "../",
    "./",
)


def _iter_markdown_files(skill_dir: Path) -> list[Path]:
    files = []
    for path in skill_dir.rglob("*.md"):
        if "legacy" in path.parts:
            continue
        files.append(path)
    return sorted(files)


def _normalize_candidate(raw: str) -> str | None:
    candidate = raw.strip()
    if not candidate:
        return None
    if candidate.startswith(("http://", "https://", "#", "mailto:")):
        return None
    if " " in candidate:
        return None
    if not candidate.startswith(PATH_PREFIXES):
        return None
    return candidate


def _resolves(path: Path, root: Path, candidate: str) -> bool:
    options = [
        (path.parent / candidate).resolve(),
        (root / candidate).resolve(),
    ]
    return any(option.exists() for option in options)


def _audit_markdown_links(path: Path, root: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")

    for target in MARKDOWN_LINK_RE.findall(text):
        normalized = _normalize_candidate(target)
        if normalized is None:
            continue
        if not _resolves(path, root, normalized):
            errors.append(f"{path}: broken markdown link -> {target}")

    for token in INLINE_CODE_RE.findall(text):
        normalized = _normalize_candidate(token)
        if normalized is None:
            continue
        if not _resolves(path, root, normalized):
            errors.append(f"{path}: broken inline path -> {token}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit local artifact links and inline path references."
    )
    parser.add_argument(
        "--skill-dir",
        default=".",
        help="Target skill directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    errors: list[str] = []
    files = _iter_markdown_files(skill_dir)

    print(f"[INFO] markdown_files={len(files)}")
    for path in files:
        _audit_markdown_links(path, skill_dir, errors)

    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        print("Artifact link audit failed")
        return 1

    print("Artifact link audit passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
