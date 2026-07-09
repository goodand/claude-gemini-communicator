#!/usr/bin/env python3
"""evidence-to-knowledge-promoter v0.1 vertical slice.

Usage:
    python3 evidence_to_knowledge_promoter.py build-promotion-summary \
        --support-audit <file> \
        --baseline-diff <file>
    python3 evidence_to_knowledge_promoter.py evaluate-promotion-trigger \
        --summary <file>
    python3 evidence_to_knowledge_promoter.py build-hybrid-kb-patch-plan \
        --summary <file> \
        --evaluation <file> \
        --target-kb <file>
    python3 evidence_to_knowledge_promoter.py apply-hybrid-kb-patch \
        --patch-plan <file> \
        --target-kb <file> \
        --output-kb <file>
    python3 evidence_to_knowledge_promoter.py evaluate-canonical-candidate \
        --summary <file> \
        --evaluation <file>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def _load_json(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        _err(f"파일을 찾지 못했습니다: {path}")
    except json.JSONDecodeError as exc:
        _err(f"JSON 파싱 실패: {path} ({exc})")


def _relative_or_str(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _finding_entries(support_audit: dict[str, object], source: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for item in support_audit.get("supported_entries", []):
        entries.append(
            {
                "kind": "finding",
                "name": item["name"],
                "source": source,
                "value": {
                    "finding_family": item["finding_family"],
                    "observed_bucket": item["observed_bucket"],
                    "trace_status": item["trace_status"],
                },
                "evidence": item["entry_id"],
                "promotion_decision": "observe",
                "reason": "verified evidence가 있어 reusable finding으로 남길 수 있다.",
            }
        )
    return entries


def _residual_entries(support_audit: dict[str, object], source: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for group_name in ("missing_evidence_entries", "residual_uncertainty_entries"):
        for item in support_audit.get(group_name, []):
            entries.append(
                {
                    "kind": "residual_uncertainty",
                    "name": item["name"],
                    "source": source,
                    "value": {
                        "finding_family": item["finding_family"],
                        "observed_bucket": item["observed_bucket"],
                        "trace_status": item["trace_status"],
                    },
                    "evidence": item["entry_id"],
                    "promotion_decision": "hold",
                    "reason": "evidence가 부족하거나 bucket 해석이 아직 닫히지 않았다.",
                }
            )
    return entries


def _is_delta_candidate(metric_name: str, metric_payload: dict[str, object]) -> bool:
    before = metric_payload.get("before")
    after = metric_payload.get("after")
    if before is None or after is None:
        return False
    if before != after:
        return True
    return False


def _delta_entries(baseline_diff: dict[str, object], source: str) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for metric_name, metric_payload in baseline_diff.get("metrics", {}).items():
        if not _is_delta_candidate(metric_name, metric_payload):
            continue
        reduction = metric_payload.get("reduction_after_fix")
        decision = "candidate" if reduction not in (None, 0, 0.0) else "observe"
        reason = (
            "before/after diff가 수치로 닫혀 reusable delta 후보가 된다."
            if decision == "candidate"
            else "수치 변화는 있지만 바로 lesson 규칙으로 승격하기엔 추가 반복 검증이 필요하다."
        )
        entries.append(
            {
                "kind": "delta",
                "name": metric_name,
                "source": source,
                "value": {
                    "before": metric_payload.get("before"),
                    "after": metric_payload.get("after"),
                    "delta": metric_payload.get("delta"),
                    "relative_change": metric_payload.get("relative_change"),
                    "reduction_after_fix": reduction,
                },
                "evidence": metric_name,
                "promotion_decision": decision,
                "reason": reason,
            }
        )
    return entries


def _lesson_candidates(
    findings: list[dict[str, object]],
    deltas: list[dict[str, object]],
    residuals: list[dict[str, object]],
    support_audit: dict[str, object],
    diff_source: str,
) -> list[dict[str, object]]:
    if residuals:
        return []
    if float(support_audit.get("support_ratio", 0.0)) < 1.0:
        return []
    improving = [entry for entry in deltas if entry["promotion_decision"] == "candidate"]
    if not improving:
        return []
    return [
        {
            "kind": "lesson_candidate",
            "name": "verified-evidence-backed-fix-pattern",
            "source": diff_source,
            "value": {
                "delta_count": len(improving),
                "finding_count": len(findings),
                "support_ratio": support_audit.get("support_ratio"),
            },
            "evidence": improving[0]["name"],
            "promotion_decision": "candidate",
            "reason": "verified evidence와 positive delta가 함께 있어 lesson candidate로 승격할 수 있다.",
        }
    ]


def build_promotion_summary(support_audit_path: Path, baseline_diff_path: Path) -> dict[str, object]:
    support_audit = _load_json(support_audit_path)
    baseline_diff = _load_json(baseline_diff_path)

    support_source = _relative_or_str(support_audit_path)
    diff_source = _relative_or_str(baseline_diff_path)

    findings = _finding_entries(support_audit, support_source)
    residuals = _residual_entries(support_audit, support_source)
    deltas = _delta_entries(baseline_diff, diff_source)
    lesson_candidates = _lesson_candidates(findings, deltas, residuals, support_audit, diff_source)

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "promotion_candidate_summary",
        "input_support_audit": support_source,
        "input_baseline_diff": diff_source,
        "summary_counts": {
            "finding": len(findings),
            "delta": len(deltas),
            "lesson_candidate": len(lesson_candidates),
            "residual_uncertainty": len(residuals),
        },
        "entries": findings + deltas + lesson_candidates + residuals,
    }


def render_markdown(payload: dict[str, object]) -> str:
    if payload.get("contract_family") == "canonical_kb_patch_apply_result":
        lines = [
            "# evidence-to-knowledge-promoter canonical KB patch apply result",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- input_patch_plan: `{payload['input_patch_plan']}`",
            f"- target_kb: `{payload['target_kb']}`",
            f"- output_kb: `{payload['output_kb']}`",
            f"- patch_decision: `{payload['patch_decision']}`",
            f"- applied_count: `{payload['applied_count']}`",
            f"- skipped_count: `{payload['skipped_count']}`",
            "",
            "## Operations",
            "",
        ]
        for item in payload["operations"]:
            lines.extend(
                [
                    f"- `{item['status']}` / `{item['entry_name']}`",
                    f"  - target_section: `{item['target_section']}`",
                    f"  - line: {item['line']}",
                    f"  - note: {item['note']}",
                ]
            )
        return "\n".join(lines) + "\n"

    if payload.get("contract_family") == "canonical_kb_patch_plan":
        lines = [
            "# evidence-to-knowledge-promoter canonical KB patch plan",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- input_summary: `{payload['input_summary']}`",
            f"- input_evaluation: `{payload['input_evaluation']}`",
            f"- target_kb: `{payload['target_kb']}`",
            f"- patch_decision: `{payload['patch_decision']}`",
            "",
            "## Planned Operations",
            "",
        ]
        for item in payload["planned_operations"]:
            lines.extend(
                [
                    f"- `{item['op']}` -> `{item['target_section']}`",
                    f"  - entry_kind: `{item['entry_kind']}`",
                    f"  - entry_name: `{item['entry_name']}`",
                    f"  - evidence: `{item['evidence']}`",
                    f"  - reason: {item['reason']}",
                ]
            )
        return "\n".join(lines) + "\n"

    if payload.get("contract_family") == "canonical_candidate_evaluation":
        decision = payload["canonical_decision"]
        lines = [
            "# evidence-to-knowledge-promoter canonical candidate evaluation",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- input_summary: `{payload['input_summary']}`",
            f"- input_evaluation: `{payload['input_evaluation']}`",
            f"- decision: `{decision['decision']}`",
            f"- reason: {decision['reason']}",
            "",
            "## Missing Requirements",
            "",
        ]
        if payload["missing_requirements"]:
            for item in payload["missing_requirements"]:
                lines.append(f"- `{item}`")
        else:
            lines.append("- none")
        lines.extend(["", "## Candidate Lessons", ""])
        if payload["candidate_lessons"]:
            for lesson in payload["candidate_lessons"]:
                lines.append(f"- `{lesson['name']}`")
        else:
            lines.append("- none")
        return "\n".join(lines) + "\n"

    if payload.get("contract_family") == "hybrid_kb_patch_apply_result":
        lines = [
            "# evidence-to-knowledge-promoter hybrid KB patch apply result",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- input_patch_plan: `{payload['input_patch_plan']}`",
            f"- target_kb: `{payload['target_kb']}`",
            f"- output_kb: `{payload['output_kb']}`",
            f"- patch_decision: `{payload['patch_decision']}`",
            f"- applied_count: `{payload['applied_count']}`",
            f"- skipped_count: `{payload['skipped_count']}`",
            "",
            "## Operations",
            "",
        ]
        for item in payload["operations"]:
            lines.extend(
                [
                    f"- `{item['status']}` / `{item['entry_name']}`",
                    f"  - target_section: `{item['target_section']}`",
                    f"  - line: {item['line']}",
                    f"  - note: {item['note']}",
                ]
            )
        return "\n".join(lines) + "\n"

    if payload.get("contract_family") == "hybrid_kb_patch_plan":
        decisions = payload["decisions"]
        lines = [
            "# evidence-to-knowledge-promoter hybrid KB patch plan",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- input_summary: `{payload['input_summary']}`",
            f"- input_evaluation: `{payload['input_evaluation']}`",
            f"- target_kb: `{payload['target_kb']}`",
            f"- patch_decision: `{payload['patch_decision']}`",
            "",
            "## Rationale",
            "",
            f"- hybrid_kb decision: `{decisions['hybrid_kb']['decision']}`",
            f"- reason: {decisions['hybrid_kb']['reason']}",
            "",
            "## Planned Operations",
            "",
        ]
        for item in payload["planned_operations"]:
            lines.extend(
                [
                    f"- `{item['op']}` -> `{item['target_section']}`",
                    f"  - entry_kind: `{item['entry_kind']}`",
                    f"  - entry_name: `{item['entry_name']}`",
                    f"  - reason: {item['reason']}",
                ]
            )
        return "\n".join(lines) + "\n"

    if payload.get("contract_family") == "promotion_trigger_evaluation":
        decisions = payload["decisions"]
        summary_counts = payload["summary_counts"]
        lines = [
            "# evidence-to-knowledge-promoter promotion trigger evaluation",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- input_summary: `{payload['input_summary']}`",
            "",
            "## Summary Counts",
            "",
            f"- finding: `{summary_counts['finding']}`",
            f"- delta: `{summary_counts['delta']}`",
            f"- lesson_candidate: `{summary_counts['lesson_candidate']}`",
            f"- residual_uncertainty: `{summary_counts['residual_uncertainty']}`",
            "",
            "## Decisions",
            "",
            f"- hybrid_kb: `{decisions['hybrid_kb']['decision']}`",
            f"  - reason: {decisions['hybrid_kb']['reason']}",
            f"- canonical_design_kb: `{decisions['canonical_design_kb']['decision']}`",
            f"  - reason: {decisions['canonical_design_kb']['reason']}",
        ]
        return "\n".join(lines) + "\n"

    counts = payload["summary_counts"]
    lines = [
        "# evidence-to-knowledge-promoter promotion summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- input_support_audit: `{payload['input_support_audit']}`",
        f"- input_baseline_diff: `{payload['input_baseline_diff']}`",
        "",
        "## Counts",
        "",
        f"- finding: `{counts['finding']}`",
        f"- delta: `{counts['delta']}`",
        f"- lesson_candidate: `{counts['lesson_candidate']}`",
        f"- residual_uncertainty: `{counts['residual_uncertainty']}`",
        "",
        "## Entries",
        "",
    ]
    for entry in payload["entries"]:
        lines.extend(
            [
                f"- `{entry['kind']}` / `{entry['name']}`",
                f"  - source: `{entry['source']}`",
                f"  - promotion_decision: `{entry['promotion_decision']}`",
                f"  - evidence: `{entry['evidence']}`",
                f"  - reason: {entry['reason']}",
            ]
        )
    return "\n".join(lines) + "\n"


def _write_outputs(payload: dict[str, object], output_json: Path | None, output_md: Path | None) -> None:
    if output_json is not None:
        output_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if output_md is not None:
        output_md.write_text(render_markdown(payload), encoding="utf-8")


def evaluate_promotion_trigger(summary_path: Path) -> dict[str, object]:
    summary = _load_json(summary_path)
    if summary.get("contract_family") != "promotion_candidate_summary":
        _err(f"promotion_candidate_summary가 아닙니다: {summary_path}")

    summary_counts = summary.get("summary_counts", {})
    entries = summary.get("entries", [])
    lesson_candidates = [
        entry
        for entry in entries
        if entry.get("kind") == "lesson_candidate" and entry.get("promotion_decision") == "candidate"
    ]
    residual_count = int(summary_counts.get("residual_uncertainty", 0))

    hybrid_decision = "hold"
    hybrid_reason = "lesson_candidate가 부족하거나 residual uncertainty가 남아 있다."
    if lesson_candidates and residual_count == 0:
        hybrid_decision = "promote"
        hybrid_reason = "lesson_candidate가 있고 residual uncertainty가 없어 hybrid_kb source of truth slice로 승격 가능하다."

    canonical_decision = "hold"
    canonical_reason = "v0.1에서는 반복 검증 신호가 명시될 때만 canonical_design_kb 후보로 본다."
    repeated_signal = any(
        int(entry.get("value", {}).get("repetition_count", 0)) >= 2 for entry in lesson_candidates
    )
    if hybrid_decision == "promote" and repeated_signal:
        canonical_decision = "candidate"
        canonical_reason = "반복 검증 신호가 있어 canonical_design_kb 후보로 검토할 수 있다."

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "promotion_trigger_evaluation",
        "input_summary": _relative_or_str(summary_path),
        "summary_counts": summary_counts,
        "decisions": {
            "hybrid_kb": {
                "decision": hybrid_decision,
                "reason": hybrid_reason,
            },
            "canonical_design_kb": {
                "decision": canonical_decision,
                "reason": canonical_reason,
            },
        },
    }


def build_hybrid_kb_patch_plan(
    summary_path: Path,
    evaluation_path: Path,
    target_kb_path: Path,
) -> dict[str, object]:
    summary = _load_json(summary_path)
    evaluation = _load_json(evaluation_path)

    if summary.get("contract_family") != "promotion_candidate_summary":
        _err(f"promotion_candidate_summary가 아닙니다: {summary_path}")
    if evaluation.get("contract_family") != "promotion_trigger_evaluation":
        _err(f"promotion_trigger_evaluation이 아닙니다: {evaluation_path}")

    hybrid_decision = evaluation["decisions"]["hybrid_kb"]["decision"]
    planned_operations: list[dict[str, object]] = []

    if hybrid_decision == "promote":
        for entry in summary.get("entries", []):
            entry_kind = entry.get("kind")
            if entry_kind == "lesson_candidate":
                planned_operations.append(
                    {
                        "op": "append",
                        "target_section": "Canonical Design Takeaways",
                        "entry_kind": entry_kind,
                        "entry_name": entry["name"],
                        "reason": "재사용 가능한 lesson candidate를 canonical takeaway로 올린다.",
                    }
                )
            elif entry_kind == "delta" and entry.get("promotion_decision") == "candidate":
                planned_operations.append(
                    {
                        "op": "append",
                        "target_section": "Current Implementation Target",
                        "entry_kind": entry_kind,
                        "entry_name": entry["name"],
                        "reason": "수치 변화가 닫힌 delta를 implementation target evidence로 기록한다.",
                    }
                )
            elif entry_kind == "finding":
                planned_operations.append(
                    {
                        "op": "append",
                        "target_section": "Research Focus",
                        "entry_kind": entry_kind,
                        "entry_name": entry["name"],
                        "reason": "반복 해석 전 단계의 verified finding을 supporting note로 남긴다.",
                    }
                )
    else:
        planned_operations.append(
            {
                "op": "hold",
                "target_section": "troubleshooting",
                "entry_kind": "residual_uncertainty",
                "entry_name": "promotion-hold",
                "reason": "residual uncertainty 또는 lesson candidate 부족으로 KB patch를 보류한다.",
            }
        )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "hybrid_kb_patch_plan",
        "input_summary": _relative_or_str(summary_path),
        "input_evaluation": _relative_or_str(evaluation_path),
        "target_kb": _relative_or_str(target_kb_path),
        "patch_decision": hybrid_decision,
        "decisions": evaluation["decisions"],
        "planned_operations": planned_operations,
    }


def build_canonical_kb_patch_plan(
    summary_path: Path,
    evaluation_path: Path,
    target_kb_path: Path,
) -> dict[str, object]:
    summary = _load_json(summary_path)
    evaluation = _load_json(evaluation_path)

    if summary.get("contract_family") != "promotion_candidate_summary":
        _err(f"promotion_candidate_summary가 아닙니다: {summary_path}")
    if evaluation.get("contract_family") != "canonical_candidate_evaluation":
        _err(f"canonical_candidate_evaluation이 아닙니다: {evaluation_path}")

    decision = evaluation["canonical_decision"]["decision"]
    candidate_names = {item["name"] for item in evaluation.get("candidate_lessons", [])}
    planned_operations: list[dict[str, object]] = []

    if decision == "candidate":
        for entry in summary.get("entries", []):
            if entry.get("kind") != "lesson_candidate":
                continue
            if entry.get("promotion_decision") != "candidate":
                continue
            if entry.get("name") not in candidate_names:
                continue
            planned_operations.append(
                {
                    "op": "append",
                    "target_section": "Canonical Design Takeaways",
                    "entry_kind": "lesson_candidate",
                    "entry_name": entry["name"],
                    "reason": "반복 검증된 lesson candidate만 canonical_design_kb takeaway로 승격한다.",
                    "evidence": entry.get("evidence"),
                }
            )
    else:
        planned_operations.append(
            {
                "op": "hold",
                "target_section": "canonical-gate",
                "entry_kind": "canonical_candidate",
                "entry_name": "canonical-promotion-hold",
                "reason": evaluation["canonical_decision"]["reason"],
                "evidence": ",".join(evaluation.get("missing_requirements", [])),
            }
        )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "canonical_kb_patch_plan",
        "input_summary": _relative_or_str(summary_path),
        "input_evaluation": _relative_or_str(evaluation_path),
        "target_kb": _relative_or_str(target_kb_path),
        "patch_decision": decision,
        "canonical_decision": evaluation["canonical_decision"],
        "planned_operations": planned_operations,
    }


def evaluate_canonical_candidate(summary_path: Path, evaluation_path: Path) -> dict[str, object]:
    summary = _load_json(summary_path)
    evaluation = _load_json(evaluation_path)

    if summary.get("contract_family") != "promotion_candidate_summary":
        _err(f"promotion_candidate_summary가 아닙니다: {summary_path}")
    if evaluation.get("contract_family") != "promotion_trigger_evaluation":
        _err(f"promotion_trigger_evaluation이 아닙니다: {evaluation_path}")

    summary_counts = summary.get("summary_counts", {})
    entries = summary.get("entries", [])
    candidate_lessons = [
        entry
        for entry in entries
        if entry.get("kind") == "lesson_candidate" and entry.get("promotion_decision") == "candidate"
    ]

    missing_requirements: list[str] = []
    if evaluation["decisions"]["hybrid_kb"]["decision"] != "promote":
        missing_requirements.append("hybrid_kb_promote_gate")
    if int(summary_counts.get("residual_uncertainty", 0)) > 0:
        missing_requirements.append("no_residual_uncertainty")
    if not candidate_lessons:
        missing_requirements.append("lesson_candidate_present")

    repeated_signal = False
    for lesson in candidate_lessons:
        if int(lesson.get("value", {}).get("repetition_count", 0)) >= 2:
            repeated_signal = True
            break
    if not repeated_signal:
        missing_requirements.append("repetition_count>=2")

    if missing_requirements:
        decision = {
            "decision": "hold",
            "reason": "canonical_design_kb로 올리기엔 반복 검증 또는 안정성 조건이 아직 부족하다.",
        }
    else:
        decision = {
            "decision": "candidate",
            "reason": "반복 검증된 lesson candidate가 있어 canonical_design_kb 후보로 검토할 수 있다.",
        }

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "canonical_candidate_evaluation",
        "input_summary": _relative_or_str(summary_path),
        "input_evaluation": _relative_or_str(evaluation_path),
        "canonical_decision": decision,
        "missing_requirements": missing_requirements,
        "candidate_lessons": [
            {
                "name": lesson["name"],
                "evidence": lesson["evidence"],
                "repetition_count": lesson.get("value", {}).get("repetition_count", 0),
            }
            for lesson in candidate_lessons
        ],
    }


def _append_under_section(lines: list[str], section_name: str, bullet: str) -> tuple[list[str], int]:
    header = f"## {section_name}"
    try:
        section_index = lines.index(header)
    except ValueError:
        _err(f"대상 섹션을 찾지 못했습니다: {section_name}")

    insert_at = len(lines)
    for index in range(section_index + 1, len(lines)):
        if lines[index].startswith("## "):
            insert_at = index
            break

    new_lines = list(lines)
    if insert_at > 0 and new_lines[insert_at - 1].strip() != "":
        new_lines.insert(insert_at, "")
        insert_at += 1
    new_lines.insert(insert_at, bullet)
    return new_lines, insert_at + 1


def _bullet_for_operation(operation: dict[str, object]) -> str:
    kind = operation["entry_kind"]
    name = operation["entry_name"]
    reason = operation["reason"]
    if kind == "lesson_candidate":
        return f"- promoted lesson: `{name}` — {reason}"
    if kind == "delta":
        return f"- promoted delta: `{name}` — {reason}"
    if kind == "finding":
        return f"- promoted finding: `{name}` — {reason}"
    return f"- promoted note: `{name}` — {reason}"


def _apply_kb_patch(
    patch_plan_path: Path,
    target_kb_path: Path,
    output_kb_path: Path,
    expected_contract_family: str,
    result_contract_family: str,
) -> dict[str, object]:
    patch_plan = _load_json(patch_plan_path)
    if patch_plan.get("contract_family") != expected_contract_family:
        _err(f"{expected_contract_family}이 아닙니다: {patch_plan_path}")

    original_text = target_kb_path.read_text(encoding="utf-8")
    lines = original_text.splitlines()
    operations_out: list[dict[str, object]] = []
    applied_count = 0
    skipped_count = 0

    for operation in patch_plan.get("planned_operations", []):
        if operation["op"] != "append":
            operations_out.append(
                {
                    "status": "skipped",
                    "entry_name": operation["entry_name"],
                    "target_section": operation["target_section"],
                    "line": None,
                    "note": operation["reason"],
                }
            )
            skipped_count += 1
            continue

        bullet = _bullet_for_operation(operation)
        if bullet in lines:
            operations_out.append(
                {
                    "status": "skipped",
                    "entry_name": operation["entry_name"],
                    "target_section": operation["target_section"],
                    "line": None,
                    "note": "동일 bullet이 이미 있어 중복 적용하지 않았다.",
                }
            )
            skipped_count += 1
            continue

        lines, inserted_line = _append_under_section(lines, operation["target_section"], bullet)
        operations_out.append(
            {
                "status": "applied",
                "entry_name": operation["entry_name"],
                "target_section": operation["target_section"],
                "line": inserted_line,
                "note": operation["reason"],
            }
        )
        applied_count += 1

    output_kb_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": result_contract_family,
        "input_patch_plan": _relative_or_str(patch_plan_path),
        "target_kb": _relative_or_str(target_kb_path),
        "output_kb": _relative_or_str(output_kb_path),
        "patch_decision": patch_plan["patch_decision"],
        "applied_count": applied_count,
        "skipped_count": skipped_count,
        "operations": operations_out,
    }


def apply_hybrid_kb_patch(patch_plan_path: Path, target_kb_path: Path, output_kb_path: Path) -> dict[str, object]:
    return _apply_kb_patch(
        patch_plan_path,
        target_kb_path,
        output_kb_path,
        expected_contract_family="hybrid_kb_patch_plan",
        result_contract_family="hybrid_kb_patch_apply_result",
    )


def apply_canonical_kb_patch(patch_plan_path: Path, target_kb_path: Path, output_kb_path: Path) -> dict[str, object]:
    return _apply_kb_patch(
        patch_plan_path,
        target_kb_path,
        output_kb_path,
        expected_contract_family="canonical_kb_patch_plan",
        result_contract_family="canonical_kb_patch_apply_result",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Promote evidence artifacts into KB insight candidates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    summary_parser = subparsers.add_parser(
        "build-promotion-summary",
        help="support_audit와 baseline diff를 promotion candidate summary로 정리한다.",
    )
    summary_parser.add_argument("--support-audit", required=True, help="support audit JSON path")
    summary_parser.add_argument("--baseline-diff", required=True, help="baseline diff JSON path")
    summary_parser.add_argument("--output-json", help="write summary JSON to path")
    summary_parser.add_argument("--output-md", help="write summary Markdown to path")

    evaluator_parser = subparsers.add_parser(
        "evaluate-promotion-trigger",
        help="promotion candidate summary를 읽고 hybrid/canonical 승격 가능 여부를 판단한다.",
    )
    evaluator_parser.add_argument("--summary", required=True, help="promotion candidate summary JSON path")
    evaluator_parser.add_argument("--output-json", help="write evaluation JSON to path")
    evaluator_parser.add_argument("--output-md", help="write evaluation Markdown to path")

    patch_parser = subparsers.add_parser(
        "build-hybrid-kb-patch-plan",
        help="promotion trigger evaluation을 읽고 hybrid KB patch plan을 만든다.",
    )
    patch_parser.add_argument("--summary", required=True, help="promotion candidate summary JSON path")
    patch_parser.add_argument("--evaluation", required=True, help="promotion trigger evaluation JSON path")
    patch_parser.add_argument("--target-kb", required=True, help="target hybrid KB path")
    patch_parser.add_argument("--output-json", help="write patch plan JSON to path")
    patch_parser.add_argument("--output-md", help="write patch plan Markdown to path")

    apply_parser = subparsers.add_parser(
        "apply-hybrid-kb-patch",
        help="hybrid KB patch plan을 target KB copy에 적용한다.",
    )
    apply_parser.add_argument("--patch-plan", required=True, help="hybrid KB patch plan JSON path")
    apply_parser.add_argument("--target-kb", required=True, help="target hybrid KB path")
    apply_parser.add_argument("--output-kb", required=True, help="patched KB copy path")
    apply_parser.add_argument("--output-json", help="write apply result JSON to path")
    apply_parser.add_argument("--output-md", help="write apply result Markdown to path")

    canonical_parser = subparsers.add_parser(
        "evaluate-canonical-candidate",
        help="canonical_design_kb 후보 여부와 부족한 조건을 평가한다.",
    )
    canonical_parser.add_argument("--summary", required=True, help="promotion candidate summary JSON path")
    canonical_parser.add_argument("--evaluation", required=True, help="promotion trigger evaluation JSON path")
    canonical_parser.add_argument("--output-json", help="write evaluation JSON to path")
    canonical_parser.add_argument("--output-md", help="write evaluation Markdown to path")

    canonical_patch_parser = subparsers.add_parser(
        "build-canonical-kb-patch-plan",
        help="canonical candidate evaluation을 읽고 canonical KB patch plan을 만든다.",
    )
    canonical_patch_parser.add_argument("--summary", required=True, help="promotion candidate summary JSON path")
    canonical_patch_parser.add_argument("--evaluation", required=True, help="canonical candidate evaluation JSON path")
    canonical_patch_parser.add_argument("--target-kb", required=True, help="target canonical KB path")
    canonical_patch_parser.add_argument("--output-json", help="write patch plan JSON to path")
    canonical_patch_parser.add_argument("--output-md", help="write patch plan Markdown to path")

    canonical_apply_parser = subparsers.add_parser(
        "apply-canonical-kb-patch",
        help="canonical KB patch plan을 target KB copy에 적용한다.",
    )
    canonical_apply_parser.add_argument("--patch-plan", required=True, help="canonical KB patch plan JSON path")
    canonical_apply_parser.add_argument("--target-kb", required=True, help="target canonical KB path")
    canonical_apply_parser.add_argument("--output-kb", required=True, help="patched KB copy path")
    canonical_apply_parser.add_argument("--output-json", help="write apply result JSON to path")
    canonical_apply_parser.add_argument("--output-md", help="write apply result Markdown to path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "build-promotion-summary":
        payload = build_promotion_summary(Path(args.support_audit), Path(args.baseline_diff))
        _write_outputs(
            payload,
            Path(args.output_json) if args.output_json else None,
            Path(args.output_md) if args.output_md else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "evaluate-promotion-trigger":
        payload = evaluate_promotion_trigger(Path(args.summary))
        _write_outputs(
            payload,
            Path(args.output_json) if args.output_json else None,
            Path(args.output_md) if args.output_md else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "build-hybrid-kb-patch-plan":
        payload = build_hybrid_kb_patch_plan(
            Path(args.summary),
            Path(args.evaluation),
            Path(args.target_kb),
        )
        _write_outputs(
            payload,
            Path(args.output_json) if args.output_json else None,
            Path(args.output_md) if args.output_md else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "apply-hybrid-kb-patch":
        payload = apply_hybrid_kb_patch(
            Path(args.patch_plan),
            Path(args.target_kb),
            Path(args.output_kb),
        )
        _write_outputs(
            payload,
            Path(args.output_json) if args.output_json else None,
            Path(args.output_md) if args.output_md else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "evaluate-canonical-candidate":
        payload = evaluate_canonical_candidate(
            Path(args.summary),
            Path(args.evaluation),
        )
        _write_outputs(
            payload,
            Path(args.output_json) if args.output_json else None,
            Path(args.output_md) if args.output_md else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "build-canonical-kb-patch-plan":
        payload = build_canonical_kb_patch_plan(
            Path(args.summary),
            Path(args.evaluation),
            Path(args.target_kb),
        )
        _write_outputs(
            payload,
            Path(args.output_json) if args.output_json else None,
            Path(args.output_md) if args.output_md else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    if args.command == "apply-canonical-kb-patch":
        payload = apply_canonical_kb_patch(
            Path(args.patch_plan),
            Path(args.target_kb),
            Path(args.output_kb),
        )
        _write_outputs(
            payload,
            Path(args.output_json) if args.output_json else None,
            Path(args.output_md) if args.output_md else None,
        )
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    _err(f"알 수 없는 command: {args.command}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
