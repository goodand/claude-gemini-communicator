#!/usr/bin/env python3
"""Verify artifact naming and metadata order for skill documentation.

사용법:
    python3 verify_artifact_order.py --skill-dir <skill_dir>
    python3 verify_artifact_order.py <artifact1> <artifact2> <artifact3>
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable


MINUTE_TIMESTAMP_RE = re.compile(r"-at\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")


@dataclass
class ArtifactInfo:
    label: str
    path: Path
    created_epoch: float | None
    modified_epoch: float
    has_minute_timestamp: bool
    time_source: str

    @property
    def order_epoch(self) -> float:
        return self.created_epoch if self.created_epoch is not None else self.modified_epoch

    @property
    def order_key(self) -> tuple[float, float]:
        return (self.order_epoch, self.modified_epoch)


def _format_epoch(epoch: float | None) -> str:
    if epoch is None:
        return "N/A"
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def _collect_markdown_files(directory: Path) -> list[Path]:
    if not directory.is_dir():
        return []
    return sorted(
        [path for path in directory.iterdir() if path.is_file() and path.suffix == ".md"],
        key=lambda path: path.stat().st_mtime,
    )


def _pick_stage_file(directory: Path, preferred_keyword: str | None, excluded_keywords: Iterable[str] = ()) -> Path | None:
    files = _collect_markdown_files(directory)
    if not files:
        return None

    filtered = [path for path in files if not any(keyword in path.name for keyword in excluded_keywords)]
    if preferred_keyword:
        preferred = [path for path in filtered if preferred_keyword in path.name]
        if preferred:
            return preferred[-1]
    if filtered:
        return filtered[-1]
    return files[-1]


def _discover_default_chain(skill_dir: Path) -> list[tuple[str, Path]]:
    chain = []

    knowledge_base = _pick_stage_file(
        skill_dir / "knowledge_bases",
        preferred_keyword="knowledge_base",
        excluded_keywords=("issues",),
    )
    consistency = _pick_stage_file(
        skill_dir / "checklist-forconsistency-evaluation",
        preferred_keyword="consistency",
    )
    implementation = _pick_stage_file(
        skill_dir / "checklist-forimplementation",
        preferred_keyword="implementation",
    )

    if knowledge_base is not None:
        chain.append(("knowledge_base", knowledge_base))
    if consistency is not None:
        chain.append(("consistency_checklist", consistency))
    if implementation is not None:
        chain.append(("implementation_checklist", implementation))
    return chain


def _build_info(label: str, path: Path) -> ArtifactInfo:
    stats = path.stat()
    created_epoch = getattr(stats, "st_birthtime", None)
    modified_epoch = stats.st_mtime
    time_source = "created" if created_epoch is not None else "modified"
    has_minute_timestamp = bool(MINUTE_TIMESTAMP_RE.search(path.stem))
    return ArtifactInfo(
        label=label,
        path=path,
        created_epoch=created_epoch,
        modified_epoch=modified_epoch,
        has_minute_timestamp=has_minute_timestamp,
        time_source=time_source,
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify minute-level artifact naming and metadata order."
    )
    parser.add_argument(
        "artifacts",
        nargs="*",
        help="Artifacts in expected creation order. Use instead of --skill-dir for explicit validation.",
    )
    parser.add_argument(
        "--skill-dir",
        help="Skill directory. Auto-discovers knowledge_base -> consistency -> implementation chain.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    if bool(args.skill_dir) == bool(args.artifacts):
        print(
            "Usage: verify_artifact_order.py --skill-dir <skill_dir>\n"
            "   or: verify_artifact_order.py <artifact1> <artifact2> [<artifact3> ...]",
            file=sys.stderr,
        )
        return 1

    discovered: list[tuple[str, Path]]
    if args.skill_dir:
        skill_dir = Path(args.skill_dir)
        discovered = _discover_default_chain(skill_dir)
        if len(discovered) < 2:
            print(
                "[ERROR] Auto-discovery failed. Need at least knowledge_base and one checklist artifact.",
                file=sys.stderr,
            )
            return 1
    else:
        discovered = [(f"artifact_{i + 1}", Path(raw_path)) for i, raw_path in enumerate(args.artifacts)]

    errors: list[str] = []
    infos: list[ArtifactInfo] = []

    for label, raw_path in discovered:
        path = raw_path if raw_path.is_absolute() else Path(os.getcwd()) / raw_path
        if not path.exists():
            errors.append(f"{label}: missing file — {raw_path}")
            continue
        info = _build_info(label, path)
        infos.append(info)
        if not info.has_minute_timestamp:
            errors.append(
                f"{label}: minute-level timestamp missing — '{info.path.name}' "
                "(expected '*-atYYYY-MM-DD-HH-MM.md')"
            )

    for info in infos:
        print(
            f"[INFO] {info.label}: {info.path} | "
            f"created={_format_epoch(info.created_epoch)} | "
            f"modified={_format_epoch(info.modified_epoch)} | "
            f"time_source={info.time_source} | "
            f"minute_ts={'OK' if info.has_minute_timestamp else 'FAIL'}"
        )

    for previous, current in zip(infos, infos[1:]):
        if previous.order_key > current.order_key:
            errors.append(
                "metadata order violated: "
                f"{previous.label} ({_format_epoch(previous.order_epoch)} / modified={_format_epoch(previous.modified_epoch)}) "
                f"must be earlier than {current.label} "
                f"({_format_epoch(current.order_epoch)} / modified={_format_epoch(current.modified_epoch)})"
            )

    if errors:
        for error in errors:
            print(f"[ERROR] {error}", file=sys.stderr)
        print("Artifact order validation failed")
        return 1

    print("Artifact order validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
