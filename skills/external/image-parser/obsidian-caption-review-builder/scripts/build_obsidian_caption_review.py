#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT_SCRIPT = (
    Path(__file__).resolve().parents[3] / "scripts" / "build_obsidian_caption_review.py"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Skill wrapper for building an Obsidian-friendly caption review. "
            "Defaults to the canonical copied-asset mode."
        )
    )
    parser.add_argument(
        "--ledger-glob",
        required=True,
        help="Glob for worker ledger JSON files.",
    )
    parser.add_argument(
        "--exclude-glob",
        action="append",
        default=["*smoke*"],
        help="Glob patterns to exclude from ledger matches.",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Target markdown path.",
    )
    parser.add_argument(
        "--review-title",
        default="Caption Review",
        help="Heading text shown at the top of the generated markdown review.",
    )
    parser.add_argument(
        "--mode",
        choices=["canonical-copy", "direct", "prefixed"],
        default="canonical-copy",
        help="Embed strategy. Defaults to the canonical copied-asset mode.",
    )
    parser.add_argument(
        "--asset-dir",
        help=(
            "Directory for copied review assets. "
            "If omitted in canonical-copy mode, defaults to <output-dir>/review_assets/<output-stem>."
        ),
    )
    parser.add_argument(
        "--source-root",
        help="Common source root for image files when --mode prefixed is used.",
    )
    parser.add_argument(
        "--embed-prefix",
        help="Embed path prefix for --mode prefixed, for example 'img/pptx_jobs'.",
    )
    return parser.parse_args()


def default_asset_dir(output_path: Path) -> Path:
    return output_path.parent / "review_assets" / output_path.stem


def build_root_command(args: argparse.Namespace) -> list[str]:
    if not ROOT_SCRIPT.is_file():
        raise SystemExit(f"Root review-builder script not found: {ROOT_SCRIPT}")

    output_path = Path(args.output).resolve()
    command = [
        sys.executable,
        str(ROOT_SCRIPT),
        "--ledger-glob",
        args.ledger_glob,
        "--output",
        str(output_path),
        "--review-title",
        args.review_title,
    ]

    for pattern in args.exclude_glob:
        command.extend(["--exclude-glob", pattern])

    if args.mode == "canonical-copy":
        asset_dir = Path(args.asset_dir).resolve() if args.asset_dir else default_asset_dir(output_path)
        command.extend(
            [
                "--copy-assets",
                "--asset-dir",
                str(asset_dir),
            ]
        )
        return command

    if args.mode == "direct":
        if args.asset_dir or args.source_root or args.embed_prefix:
            raise SystemExit(
                "--mode direct does not accept --asset-dir, --source-root, or --embed-prefix."
            )
        return command

    if not args.source_root or not args.embed_prefix:
        raise SystemExit("--mode prefixed requires both --source-root and --embed-prefix.")
    if args.asset_dir:
        raise SystemExit("--mode prefixed does not accept --asset-dir.")
    command.extend(
        [
            "--source-root",
            str(Path(args.source_root).resolve()),
            "--embed-prefix",
            args.embed_prefix,
        ]
    )
    return command


def main() -> int:
    args = parse_args()
    command = build_root_command(args)
    completed = subprocess.run(command, check=False)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
