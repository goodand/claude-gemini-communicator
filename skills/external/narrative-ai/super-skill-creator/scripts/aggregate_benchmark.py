#!/usr/bin/env python3
import json
import statistics
import sys
from pathlib import Path


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def safe_mean(values):
    return statistics.mean(values) if values else 0


def collect_variant_runs(iteration_dir: Path):
    """
    Expected structure:
      iteration-N/
        eval-0/
          with_skill/
            timing.json
            grading.json
          baseline/
            timing.json
            grading.json
    """
    variant_data = {}

    for eval_dir in sorted(iteration_dir.iterdir()):
        if not eval_dir.is_dir():
            continue
        for variant_dir in sorted(eval_dir.iterdir()):
            if not variant_dir.is_dir():
                continue
            variant_name = variant_dir.name
            timing_path = variant_dir / "timing.json"
            grading_path = variant_dir / "grading.json"

            if not timing_path.exists() or not grading_path.exists():
                continue

            timing = load_json(timing_path)
            grading = load_json(grading_path)

            expectations = grading.get("expectations", [])
            if expectations:
                pass_rate = sum(1 for x in expectations if x.get("passed")) / len(expectations)
            else:
                pass_rate = 0.0

            variant_data.setdefault(variant_name, []).append(
                {
                    "pass_rate": pass_rate,
                    "duration_ms": timing.get("duration_ms", 0),
                    "tokens": timing.get("total_tokens", 0),
                }
            )

    return variant_data


def aggregate(skill_name: str, iteration_dir: Path):
    raw = collect_variant_runs(iteration_dir)
    variants = []

    for variant_name, runs in raw.items():
        variants.append(
            {
                "name": variant_name,
                "mean_pass_rate": safe_mean([r["pass_rate"] for r in runs]),
                "mean_duration_ms": safe_mean([r["duration_ms"] for r in runs]),
                "mean_tokens": safe_mean([r["tokens"] for r in runs]),
                "num_runs": len(runs),
            }
        )

    return {
        "skill_name": skill_name,
        "iteration": iteration_dir.name,
        "variants": variants,
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: aggregate_benchmark.py <skill_name> <iteration_dir>")
        sys.exit(1)

    skill_name = sys.argv[1]
    iteration_dir = Path(sys.argv[2])

    if not iteration_dir.exists():
        print(f"Iteration dir not found: {iteration_dir}")
        sys.exit(1)

    benchmark = aggregate(skill_name, iteration_dir)
    out_path = iteration_dir / "benchmark.json"

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(benchmark, f, indent=2, ensure_ascii=False)

    print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()