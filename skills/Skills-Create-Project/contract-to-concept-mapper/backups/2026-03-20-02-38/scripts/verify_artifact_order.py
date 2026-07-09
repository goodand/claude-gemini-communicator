#!/usr/bin/env python3
"""Verify KB/checklist artifact order for contract-to-concept-mapper.

하드 규칙:
- knowledge_base는 정합성 평가용 checklist보다 먼저 있어야 한다.
- 정합성 평가용 checklist는 분 단위 타임스탬프 파일명을 가져야 한다.

소프트 규칙:
- 구현용 checklist는 상황에 따라 갱신 가능하므로, 수정 시각 기준으로 후행 여부를 본다.
- 구현용 checklist 관련 위반은 기본적으로 warning으로 처리한다.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re


MINUTE_TS_RE = re.compile(r"-at\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")


@dataclass
class StageSpec:
    label: str
    directory: str
    keyword: str
    strict: bool
    mutable: bool = False
    excluded_keywords: tuple[str, ...] = ()


@dataclass
class ArtifactInfo:
    spec: StageSpec
    path: Path
    created_epoch: float | None
    modified_epoch: float
    has_minute_timestamp: bool
    text: str

    @property
    def order_epoch(self) -> float:
        if self.spec.mutable:
            return max(self.created_epoch or self.modified_epoch, self.modified_epoch)
        return self.created_epoch if self.created_epoch is not None else self.modified_epoch

    @property
    def order_label(self) -> str:
        return "modified" if self.spec.mutable else "created"


def _format_epoch(epoch: float | None) -> str:
    if epoch is None:
        return "N/A"
    return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d %H:%M:%S")


def _pick_latest_file(directory: Path, keyword: str, excluded_keywords: tuple[str, ...]) -> Path | None:
    if not directory.is_dir():
        return None

    candidates = []
    for path in directory.iterdir():
        if not path.is_file() or path.suffix != ".md":
            continue
        if any(excluded in path.name for excluded in excluded_keywords):
            continue
        candidates.append(path)

    preferred = [path for path in candidates if keyword in path.name]
    pool = preferred or candidates
    if not pool:
        return None
    return max(pool, key=lambda path: path.stat().st_mtime)


def _load_artifact(skill_dir: Path, spec: StageSpec) -> ArtifactInfo | None:
    path = _pick_latest_file(skill_dir / spec.directory, spec.keyword, spec.excluded_keywords)
    if path is None:
        return None

    stats = path.stat()
    return ArtifactInfo(
        spec=spec,
        path=path,
        created_epoch=getattr(stats, "st_birthtime", None),
        modified_epoch=stats.st_mtime,
        has_minute_timestamp=bool(MINUTE_TS_RE.search(path.stem)),
        text=path.read_text(encoding="utf-8"),
    )


def _add_issue(target: list[str], severity: str, message: str) -> None:
    target.append(f"[{severity}] {message}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify artifact order for contract-to-concept-mapper."
    )
    parser.add_argument(
        "--skill-dir",
        default=".",
        help="Target skill directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    stages = [
        StageSpec(
            label="knowledge_base",
            directory="knowledge_bases",
            keyword="knowledge_base",
            strict=True,
            excluded_keywords=("issues",),
        ),
        StageSpec(
            label="consistency_checklist",
            directory="checklist-forconsistency-evaluation",
            keyword="consistency",
            strict=True,
        ),
        StageSpec(
            label="implementation_checklist",
            directory="checklist-forimplementation",
            keyword="implementation",
            strict=False,
            mutable=True,
        ),
    ]

    infos = {spec.label: _load_artifact(skill_dir, spec) for spec in stages}
    errors: list[str] = []
    warnings: list[str] = []

    for spec in stages:
        info = infos[spec.label]
        issues = errors if spec.strict else warnings
        severity = "ERROR" if spec.strict else "WARN"
        if info is None:
            _add_issue(
                issues,
                severity,
                f"{spec.label}: missing artifact in {spec.directory}/",
            )
            continue

        print(
            f"[INFO] {spec.label}: {info.path} | "
            f"created={_format_epoch(info.created_epoch)} | "
            f"modified={_format_epoch(info.modified_epoch)} | "
            f"order_source={info.order_label} | "
            f"minute_ts={'OK' if info.has_minute_timestamp else 'FAIL'}"
        )

        if not info.has_minute_timestamp:
            _add_issue(
                issues,
                severity,
                f"{spec.label}: minute-level timestamp missing — '{info.path.name}'",
            )

    kb = infos["knowledge_base"]
    consistency = infos["consistency_checklist"]
    implementation = infos["implementation_checklist"]

    if kb and consistency and kb.order_epoch > consistency.order_epoch:
        _add_issue(
            errors,
            "ERROR",
            "knowledge_base must be earlier than consistency_checklist",
        )

    if consistency:
        if "정합성 평가 체크리스트" not in consistency.text:
            _add_issue(
                errors,
                "ERROR",
                "consistency_checklist: expected checklist marker not found",
            )
        if "정합성 평가용 checklist" not in consistency.text or "구현용 checklist" not in consistency.text:
            _add_issue(
                errors,
                "ERROR",
                "consistency_checklist: priority/relationship markers missing",
            )

    if implementation:
        if "선행조건:" not in implementation.text:
            _add_issue(
                warnings,
                "WARN",
                "implementation_checklist: precondition marker missing",
            )
        elif consistency and consistency.path.name not in implementation.text:
            _add_issue(
                warnings,
                "WARN",
                "implementation_checklist: precondition does not reference current consistency checklist filename",
            )

    if consistency and implementation and implementation.order_epoch < consistency.order_epoch:
        _add_issue(
            warnings,
            "WARN",
            "implementation_checklist appears older than consistency_checklist by effective order time",
        )

    for line in warnings:
        print(line, file=sys.stderr)
    for line in errors:
        print(line, file=sys.stderr)

    if errors:
        print("Artifact order validation failed")
        return 1

    print("Artifact order validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
