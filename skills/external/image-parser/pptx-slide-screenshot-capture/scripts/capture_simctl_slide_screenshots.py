#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Capture one simulator-visible slide per image and emit a JSONL dataset.",
    )
    parser.add_argument("--udid", required=True, help="Simulator UDID for xcrun simctl.")
    parser.add_argument(
        "--job-manifest",
        type=Path,
        help="Cross-validation manifest path. Derives source_pptx and output directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for slide screenshots when not using --job-manifest.",
    )
    parser.add_argument(
        "--dataset-path",
        type=Path,
        help="Optional JSONL dataset output path. Defaults next to the output directory.",
    )
    parser.add_argument(
        "--source-pptx",
        type=Path,
        help="Source PPTX path when not using --job-manifest.",
    )
    parser.add_argument("--slide-count", type=int, required=True, help="Number of slides to capture.")
    parser.add_argument("--start-slide", type=int, default=1, help="Starting slide number.")
    parser.add_argument(
        "--prefix",
        default="slide",
        help="Filename prefix. Result is <prefix>-0001.png style.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.0,
        help="Wait between captures when the slide surface is advanced externally.",
    )
    parser.add_argument(
        "--manual-advance",
        action="store_true",
        help="Wait for Enter before each capture instead of sleeping.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing screenshots.",
    )
    return parser.parse_args()


def load_job_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def derive_paths(args: argparse.Namespace) -> tuple[Path, Path, str | None]:
    if args.job_manifest:
        manifest = load_job_manifest(args.job_manifest)
        output_dir = Path(
            manifest["cross_validation_methods"]["slide_screenshot_then_openai_api_via_simctl"][
                "planned_screenshot_dir"
            ]
        )
        dataset_path = args.dataset_path or output_dir.parent / "slide_screenshots_simctl_dataset.jsonl"
        source_pptx = manifest.get("source_pptx")
        return output_dir, dataset_path, source_pptx

    if not args.output_dir:
        raise SystemExit("Either --job-manifest or --output-dir is required.")

    output_dir = args.output_dir
    dataset_path = args.dataset_path or output_dir.parent / "slide_screenshots_simctl_dataset.jsonl"
    source_pptx = str(args.source_pptx) if args.source_pptx else None
    return output_dir, dataset_path, source_pptx


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def capture_one(udid: str, output_path: Path) -> None:
    subprocess.run(
        ["xcrun", "simctl", "io", udid, "screenshot", str(output_path)],
        check=True,
    )


def wait_for_next_slide(slide_no: int, manual_advance: bool, delay_seconds: float) -> None:
    if manual_advance:
        input(f"[slide {slide_no}] Display the correct slide, then press Enter to capture...")
        return
    if delay_seconds > 0:
        time.sleep(delay_seconds)


def image_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as fh:
        header = fh.read(24)
    png_signature = b"\x89PNG\r\n\x1a\n"
    if len(header) < 24 or not header.startswith(png_signature):
        raise SystemExit(f"Expected a PNG screenshot from simctl: {path}")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main() -> int:
    args = parse_args()
    output_dir, dataset_path, source_pptx = derive_paths(args)
    output_dir.mkdir(parents=True, exist_ok=True)
    dataset_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    current_slide = args.start_slide
    for index in range(args.slide_count):
        if index > 0:
            wait_for_next_slide(current_slide, args.manual_advance, args.delay_seconds)
        elif args.manual_advance:
            wait_for_next_slide(current_slide, True, 0.0)

        output_path = output_dir / f"{args.prefix}-{current_slide:04d}.png"
        if output_path.exists() and not args.overwrite:
            raise SystemExit(f"Refusing to overwrite existing file: {output_path}")

        capture_one(args.udid, output_path)
        width, height = image_dimensions(output_path)
        rows.append(
            {
                "slide_no": current_slide,
                "screenshot_path": str(output_path.resolve()),
                "source_pptx": source_pptx,
                "capture_method": "simctl_screenshot",
                "sha256": sha256_file(output_path),
                "image_width": width,
                "image_height": height,
            }
        )
        print(output_path.resolve())
        current_slide += 1

    with dataset_path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"DATASET_JSONL={dataset_path.resolve()}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\nCapture interrupted.", file=sys.stderr)
        raise SystemExit(130)
