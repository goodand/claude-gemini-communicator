#!/usr/bin/env python3
"""Check whether implementation checklist preserves consistency checklist anchors.

정합성 평가용 checklist를 source of truth로 보고, 구현용 checklist가
필수 anchor를 유지하는지 검사한다. 구현용 checklist는 변경 가능하므로
세부 항목 1:1 매핑보다는 핵심 의미 보존 여부를 본다.
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    severity: str
    anchor: str
    ok: bool
    detail: str


@dataclass
class Profile:
    name: str
    results: list[CheckResult]
    required_markers: tuple[str, ...]


def _pick_latest_file(directory: Path, keyword: str) -> Path | None:
    if not directory.is_dir():
        return None

    candidates = [
        path for path in directory.iterdir()
        if path.is_file() and path.suffix == ".md" and keyword in path.name
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime)


def _contains_all(text: str, tokens: tuple[str, ...]) -> bool:
    return all(token in text for token in tokens)


def _contains_any(text: str, tokens: tuple[str, ...]) -> bool:
    return any(token in text for token in tokens)


def _build_default_profile(implementation_text: str, consistency_path: Path) -> Profile:
    return Profile(
        name="default_contract_to_concept",
        required_markers=("정합성 평가용 checklist", "구현용 checklist"),
        results=[
            CheckResult(
                severity="ERROR",
                anchor="precondition_reference",
                ok=consistency_path.name in implementation_text,
                detail="implementation checklist should reference the current consistency checklist filename",
            ),
            CheckResult(
                severity="ERROR",
                anchor="input_contract",
                ok=_contains_all(implementation_text, ("checklist",)) and _contains_any(
                    implementation_text,
                    ("schema", "task", "CLI contract", "signature"),
                ),
                detail="implementation checklist should preserve checklist-first input coverage",
            ),
            CheckResult(
                severity="ERROR",
                anchor="output_triplet",
                ok=_contains_all(
                    implementation_text,
                    ("concept summary", "boundary description", "semantic relation map"),
                ),
                detail="implementation checklist should preserve the canonical output triplet",
            ),
            CheckResult(
                severity="ERROR",
                anchor="traceability",
                ok=_contains_any(
                    implementation_text,
                    ("derived_from", "역참조", "trace"),
                ),
                detail="implementation checklist should preserve traceability anchors",
            ),
            CheckResult(
                severity="ERROR",
                anchor="scope_guardrail",
                ok=_contains_all(
                    implementation_text,
                    ("code 수정", "로그 수집", "외부 검색"),
                ),
                detail="implementation checklist should preserve exclusion guardrails",
            ),
            CheckResult(
                severity="WARN",
                anchor="uncertainty",
                ok=_contains_any(
                    implementation_text,
                    ("uncertainty", "불충분한 근거", "weak support"),
                ),
                detail="implementation checklist should ideally preserve uncertainty handling",
            ),
            CheckResult(
                severity="WARN",
                anchor="project_context",
                ok=_contains_any(
                    implementation_text,
                    ("project-level context", "project context"),
                ),
                detail="implementation checklist should ideally preserve project-level context handling",
            ),
            CheckResult(
                severity="WARN",
                anchor="scaffold_visibility",
                ok=_contains_any(
                    implementation_text,
                    ("scaffold", "미구현", "구현 전"),
                ),
                detail="implementation checklist should keep scaffold-stage visibility",
            ),
        ],
    )


def _build_kb_to_consistency_profile(implementation_text: str, consistency_path: Path) -> Profile:
    return Profile(
        name="kb_to_consistency",
        required_markers=("knowledge_base <-> 정합성 평가용 checklist", "구현용 checklist"),
        results=[
            CheckResult(
                severity="ERROR",
                anchor="precondition_reference",
                ok=consistency_path.name in implementation_text,
                detail="implementation checklist should reference the current kb-to-consistency consistency checklist filename",
            ),
            CheckResult(
                severity="ERROR",
                anchor="comparison_direction",
                ok=_contains_all(implementation_text, ("forward", "backward")),
                detail="implementation checklist should preserve forward/backward comparison directions",
            ),
            CheckResult(
                severity="ERROR",
                anchor="verdict_taxonomy",
                ok=_contains_all(
                    implementation_text,
                    (
                        "covered",
                        "missing_from_checklist",
                        "unsupported_in_checklist",
                        "scope_inflation",
                        "boundary_loss",
                    ),
                ),
                detail="implementation checklist should preserve the verdict taxonomy",
            ),
            CheckResult(
                severity="ERROR",
                anchor="metrics",
                ok=_contains_all(
                    implementation_text,
                    (
                        "coverage_ratio",
                        "unsupported_item_ratio",
                        "traceability_ratio",
                        "boundary_preservation_ratio",
                    ),
                ),
                detail="implementation checklist should preserve the core metrics",
            ),
            CheckResult(
                severity="ERROR",
                anchor="output_contract",
                ok=_contains_any(implementation_text, ("JSON", "coverage.json")) and _contains_any(
                    implementation_text,
                    ("markdown", "coverage_report.md"),
                ) and _contains_any(
                    implementation_text,
                    ("human review", "human_review_queue"),
                ),
                detail="implementation checklist should preserve JSON/report/human-review outputs",
            ),
            CheckResult(
                severity="ERROR",
                anchor="traceability",
                ok=_contains_any(
                    implementation_text,
                    ("traceability", "traceability matrix", "mapping"),
                ),
                detail="implementation checklist should preserve traceability or mapping anchors",
            ),
            CheckResult(
                severity="WARN",
                anchor="heuristic_guardrail",
                ok=_contains_any(
                    implementation_text,
                    ("heuristic", "anchor/keyword", "section-level comparison"),
                ),
                detail="implementation checklist should keep the v0.1 heuristic guardrail visible",
            ),
            CheckResult(
                severity="WARN",
                anchor="not_final_truth",
                ok=_contains_any(
                    implementation_text,
                    ("candidate", "최종 truth", "human review"),
                ),
                detail="implementation checklist should avoid framing heuristic output as final truth",
            ),
        ],
    )


def _select_profile(consistency_path: Path, implementation_text: str) -> Profile:
    if "kb-to-consistency" in consistency_path.name:
        return _build_kb_to_consistency_profile(implementation_text, consistency_path)
    return _build_default_profile(implementation_text, consistency_path)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether implementation checklist preserves consistency checklist anchors."
    )
    parser.add_argument(
        "--skill-dir",
        default=".",
        help="Target skill directory. Defaults to current directory.",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    consistency_path = _pick_latest_file(
        skill_dir / "checklist-forconsistency-evaluation",
        "consistency",
    )
    implementation_path = _pick_latest_file(
        skill_dir / "checklist-forimplementation",
        "implementation",
    )

    if consistency_path is None or implementation_path is None:
        print(
            "[ERROR] Missing consistency or implementation checklist artifact.",
            file=sys.stderr,
        )
        return 1

    consistency_text = consistency_path.read_text(encoding="utf-8")
    implementation_text = implementation_path.read_text(encoding="utf-8")
    profile = _select_profile(consistency_path, implementation_text)

    print(f"[INFO] consistency={consistency_path}")
    print(f"[INFO] implementation={implementation_path}")
    print(f"[INFO] profile={profile.name}")

    # Defensive check: the current consistency checklist should still mention
    # both checklist layers. If not, the anchor model itself is stale.
    if any(marker not in consistency_text for marker in profile.required_markers):
        print(
            "[ERROR] consistency checklist no longer contains the expected layer relationship markers.",
            file=sys.stderr,
        )
        return 1

    errors = 0
    for result in profile.results:
        status = "PASS" if result.ok else result.severity
        line = f"[{status}] {result.anchor}: {result.detail}"
        if result.ok:
            print(line)
            continue
        if result.severity == "ERROR":
            errors += 1
            print(line, file=sys.stderr)
        else:
            print(line, file=sys.stderr)

    if errors:
        print("Consistency-to-implementation validation failed")
        return 1

    print("Consistency-to-implementation validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
