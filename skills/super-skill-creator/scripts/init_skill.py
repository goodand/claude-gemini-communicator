#!/usr/bin/env python3
"""Scaffold a new Claude Code skill directory."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


SKILL_TEMPLATE = """---
name: {skill_name}
description: >-
  TODO: Write a clear description explaining what this skill does and when it
  should be used.
---

# {title}

## Purpose

Describe the job this skill helps with.

## When to use

- use case
- use case

## Workflow

1. step
2. step
3. step

## Scripts

List any scripts in `scripts/` and when to use them.

## References

List any files in `references/` and when to read them.

## Notes

Add constraints, edge cases, or output conventions here.
"""

EVALS_TEMPLATE = {
    "skill_name": "TODO",
    "evals": [
        {
            "id": 0,
            "prompt": "TODO: realistic user prompt",
            "expected_output": "TODO: describe expected behavior",
            "files": [],
            "assertions": ["Output includes X", "Output includes Y"],
        }
    ],
}


def _find_skills_root():
    """Walk up from CWD to find skills/ or .claude/skills/ directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, check=True,
        )
        git_root = Path(result.stdout.strip())
        # 우선순위: skills/ > .claude/skills/
        for candidate in [git_root / "skills", git_root / ".claude" / "skills"]:
            if candidate.is_dir():
                return candidate
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    # Fallback: walk up from CWD
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        for name in ["skills", ".claude/skills"]:
            candidate = parent / name
            if candidate.is_dir():
                return candidate
    return None


def main():
    parser = argparse.ArgumentParser(description="Scaffold a new skill")
    parser.add_argument("skill_name", help="Name of the skill (e.g. my-skill)")
    parser.add_argument(
        "--target", "-t",
        help="Target directory (default: auto-detect .claude/skills/)",
        default=None,
    )
    args = parser.parse_args()

    skill_name = args.skill_name

    if args.target:
        root = Path(args.target) / skill_name
    else:
        skills_root = _find_skills_root()
        if skills_root:
            root = skills_root / skill_name
        else:
            root = Path(skill_name)
            print(f"Warning: .claude/skills/ not found, creating at {root}")

    if root.exists():
        print(f"Path already exists: {root}")
        sys.exit(1)

    subdirs = ["scripts", "references", "evals"]
    for d in subdirs:
        (root / d).mkdir(parents=True, exist_ok=True)
        (root / d / ".gitkeep").touch()

    title = skill_name.replace("-", " ").title()

    (root / "SKILL.md").write_text(
        SKILL_TEMPLATE.format(skill_name=skill_name, title=title),
        encoding="utf-8",
    )

    evals_data = dict(EVALS_TEMPLATE)
    evals_data["skill_name"] = skill_name
    (root / "evals" / "evals.json").write_text(
        json.dumps(evals_data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    # Remove .gitkeep from evals since it now has a file
    gitkeep = root / "evals" / ".gitkeep"
    if gitkeep.exists():
        gitkeep.unlink()

    print(f"Created skill scaffold at {root}")
    print(f"  SKILL.md        — edit name, description, workflow")
    print(f"  scripts/        — add deterministic logic")
    print(f"  references/     — add schemas, docs, examples")
    print(f"  evals/evals.json — add realistic test prompts")


if __name__ == "__main__":
    main()