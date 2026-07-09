#!/usr/bin/env python3
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 4:
        print("Usage: init_iteration.py <workspace_dir> <iteration_name> <evals.json>")
        sys.exit(1)

    workspace_dir = Path(sys.argv[1])
    iteration_name = sys.argv[2]
    evals_path = Path(sys.argv[3])

    if not evals_path.exists():
        print(f"Missing evals file: {evals_path}")
        sys.exit(1)

    data = json.loads(evals_path.read_text(encoding="utf-8"))
    evals = data.get("evals", [])

    iteration_dir = workspace_dir / iteration_name
    iteration_dir.mkdir(parents=True, exist_ok=True)

    for item in evals:
        eval_id = item.get("id")
        eval_name = f"eval-{eval_id}"
        eval_dir = iteration_dir / eval_name
        (eval_dir / "with_skill").mkdir(parents=True, exist_ok=True)
        (eval_dir / "baseline").mkdir(parents=True, exist_ok=True)

        metadata = {
            "eval_id": eval_id,
            "eval_name": eval_name,
            "prompt": item.get("prompt", ""),
            "assertions": item.get("assertions", []),
        }
        (eval_dir / "eval_metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    print(f"Initialized {iteration_dir}")


if __name__ == "__main__":
    main()