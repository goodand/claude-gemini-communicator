#!/usr/bin/env python3
import sys
from pathlib import Path


TEMPLATE = """# Routing hints for {skill_name}

## Trigger this skill when

- the user wants to {action_1}
- the user wants to {action_2}
- the task strongly involves {topic}

## Do not trigger this skill when

- the task is only loosely related
- a more specific neighboring skill clearly fits better
- the user is asking for general discussion rather than task execution

## Nearby skills to disambiguate from

- [skill-name]: use that when ...
- [skill-name]: use that when ...

## Positive trigger examples

- "..."
- "..."
- "..."

## Negative trigger examples

- "..."
- "..."
- "..."
"""


def main():
    if len(sys.argv) != 2:
        print("Usage: make_routing_doc.py <skill_name>")
        sys.exit(1)

    skill_name = sys.argv[1]
    out = Path(f"{skill_name}-routing.md")
    out.write_text(
        TEMPLATE.format(
            skill_name=skill_name,
            action_1="perform the primary workflow",
            action_2="create or improve artifacts in this domain",
            topic="the skill's domain",
        ),
        encoding="utf-8",
    )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()