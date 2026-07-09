#!/usr/bin/env python3
import shutil
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        print("Usage: package_skill.py <skill_dir>")
        sys.exit(1)

    skill_dir = Path(sys.argv[1]).resolve()
    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"Skill dir not found: {skill_dir}")
        sys.exit(1)

    base_name = skill_dir.name
    parent = skill_dir.parent

    zip_path = shutil.make_archive(str(parent / base_name), "zip", root_dir=parent, base_dir=base_name)
    print(f"Wrote {zip_path}")


if __name__ == "__main__":
    main()