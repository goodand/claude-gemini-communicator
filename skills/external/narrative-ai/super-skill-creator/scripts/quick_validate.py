#!/usr/bin/env python3
import re
import sys
from pathlib import Path


def validate_frontmatter(text: str):
    if not text.startswith("---\n"):
        return False, "Missing YAML frontmatter start"

    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, "Invalid YAML frontmatter"

    frontmatter = parts[1]
    if not re.search(r"(?m)^name:\s*", frontmatter):
        return False, "Missing 'name' field"
    if not re.search(r"(?m)^description:\s*", frontmatter):
        return False, "Missing 'description' field"

    return True, "OK"


def main():
    if len(sys.argv) != 2:
        print("Usage: quick_validate.py <skill_dir>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    skill_md = skill_dir / "SKILL.md"

    if not skill_md.exists():
        print("Missing SKILL.md")
        sys.exit(1)

    text = skill_md.read_text(encoding="utf-8")
    ok, msg = validate_frontmatter(text)
    if not ok:
        print(f"Validation failed: {msg}")
        sys.exit(1)

    print("Validation passed")


if __name__ == "__main__":
    main()