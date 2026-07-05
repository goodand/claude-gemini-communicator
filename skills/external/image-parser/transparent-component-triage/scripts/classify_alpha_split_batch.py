#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
ROOT_SCRIPT = ROOT_DIR / "skills" / "object-isolation-correction" / "scripts" / "classify_alpha_split_batch.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Policy-aware wrapper for conservative transparent-component triage. "
            "Builds a review-gated alpha-only candidate subset from bounded PPT-extracted media."
        )
    )
    parser.add_argument("--input-root", default=None)
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--manifest-jsonl", default=None)
    parser.add_argument("--summary-json", default=None)
    parser.add_argument("--report-md", default=None)
    parser.add_argument("--worker-python", default=None)
    parser.add_argument("--worker-script", default=None)
    parser.add_argument("--alpha-threshold", type=int, default=None)
    parser.add_argument("--min-pixels", type=int, default=None)
    parser.add_argument("--padding", type=int, default=None)
    parser.add_argument("--min-components-for-success", type=int, default=None)
    parser.add_argument("--limit", type=int, default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    argv = [sys.executable, str(ROOT_SCRIPT)]
    optional_pairs = [
        ("--input-root", args.input_root),
        ("--output-root", args.output_root),
        ("--manifest-jsonl", args.manifest_jsonl),
        ("--summary-json", args.summary_json),
        ("--report-md", args.report_md),
        ("--worker-python", args.worker_python),
        ("--worker-script", args.worker_script),
        ("--alpha-threshold", args.alpha_threshold),
        ("--min-pixels", args.min_pixels),
        ("--padding", args.padding),
        ("--min-components-for-success", args.min_components_for_success),
        ("--limit", args.limit),
    ]
    for flag, value in optional_pairs:
        if value is None:
            continue
        argv.extend([flag, str(value)])
    os.execv(sys.executable, argv)


if __name__ == "__main__":
    raise SystemExit(main())
