#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
ROOT_SCRIPT = ROOT_DIR / "scripts" / "promote_parser_sidecar_to_canonical_schema.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Policy-aware wrapper for parser sidecar promotion. "
            "Defaults to canonical project_domain manifest and smoke artifact surfaces."
        )
    )
    parser.add_argument("--raw-sidecar-json", required=True, help="Raw parser sidecar JSON artifact.")
    parser.add_argument(
        "--normalized-output-json",
        default="",
        help="Optional override for canonical normalized JSON output.",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional override for machine-readable promotion result output.",
    )
    parser.add_argument("--image-path", default="", help="Optional source image path override.")
    parser.add_argument("--table-id", default="t1")
    parser.add_argument("--parser-backend", default="paddleocr-mcp/pp_structurev3")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    argv = [
        sys.executable,
        str(ROOT_SCRIPT),
        "--raw-sidecar-json",
        args.raw_sidecar_json,
        "--table-id",
        args.table_id,
        "--parser-backend",
        args.parser_backend,
    ]
    if args.normalized_output_json:
        argv.extend(["--normalized-output-json", args.normalized_output_json])
    if args.output_json:
        argv.extend(["--output-json", args.output_json])
    if args.image_path:
        argv.extend(["--image-path", args.image_path])
    os.execv(sys.executable, argv)


if __name__ == "__main__":
    raise SystemExit(main())
