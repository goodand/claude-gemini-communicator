#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
ROOT_SCRIPT = ROOT_DIR / "scripts" / "build_component_split_ocr_report.py"
DEFAULT_OUTPUT_ROOT = ROOT_DIR / "control" / "project_domain" / "runs" / "component_split_ocr"

sys.path.insert(0, str(ROOT_DIR / "scripts"))

from alpha_component_lib import (  # noqa: E402
    DEFAULT_ALPHA_THRESHOLD,
    DEFAULT_MIN_COMPONENTS_FOR_SUCCESS,
    DEFAULT_MIN_PIXELS,
    DEFAULT_PADDING,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Policy-aware wrapper for the shared component split OCR report builder. "
            "Defaults to the canonical project_domain run surface."
        )
    )
    parser.add_argument("--image-path", required=True, help="Absolute or repo-relative image path.")
    parser.add_argument(
        "--output-root",
        default=str(DEFAULT_OUTPUT_ROOT),
        help="Canonical output root for component split OCR review artifacts.",
    )
    parser.add_argument("--alpha-threshold", type=int, default=DEFAULT_ALPHA_THRESHOLD)
    parser.add_argument("--min-pixels", type=int, default=DEFAULT_MIN_PIXELS)
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING)
    parser.add_argument("--min-components-for-success", type=int, default=DEFAULT_MIN_COMPONENTS_FOR_SUCCESS)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    argv = [
        sys.executable,
        str(ROOT_SCRIPT),
        "--image-path",
        args.image_path,
        "--output-root",
        args.output_root,
        "--alpha-threshold",
        str(args.alpha_threshold),
        "--min-pixels",
        str(args.min_pixels),
        "--padding",
        str(args.padding),
        "--min-components-for-success",
        str(args.min_components_for_success),
    ]
    os.execv(sys.executable, argv)


if __name__ == "__main__":
    raise SystemExit(main())
