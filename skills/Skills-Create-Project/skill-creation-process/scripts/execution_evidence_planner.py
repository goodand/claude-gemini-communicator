#!/usr/bin/env python3
"""Plan execution-contract -> smoke -> evidence -> diff handoffs."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))
TIMESTAMP_RE = re.compile(r"-at\d{4}-\d{2}-\d{2}-\d{2}-\d{2}$")
NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def _now_stamp() -> str:
    return datetime.now(KST).strftime("%Y-%m-%d-%H-%M")


def _normalize_stem(name: str) -> str:
    lowered = TIMESTAMP_RE.sub("", name.lower())
    for suffix in (
        "-post-fix-smoke-report",
        "-pre-fix-smoke-report",
        "-smoke-report",
        "-support-audit-smoke",
        "-evidence-ledger-smoke",
        "-fix-diff",
        "-baseline-measure",
    ):
        if lowered.endswith(suffix):
            lowered = lowered[: -len(suffix)]
            break
    normalized = NON_ALNUM_RE.sub("-", lowered).strip("-")
    return normalized or "execution-evidence"


def _derive_experiment_name(
    explicit: str | None,
    target: str,
    smoke_paths: list[Path],
    pre_path: Path | None,
) -> str:
    if explicit:
        return _normalize_stem(explicit)
    if pre_path is not None:
        return _normalize_stem(pre_path.stem)
    if smoke_paths:
        return _normalize_stem(smoke_paths[0].stem)
    return _normalize_stem(target)


def _load_json_if_possible(path: Path) -> dict[str, object] | None:
    if path.suffix != ".json" or not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _has_metrics_dict(path: Path | None) -> bool:
    if path is None:
        return False
    payload = _load_json_if_possible(path)
    return isinstance(payload.get("metrics"), dict) if payload else False


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan the execution-contract to evidence loop for a skill implementation."
    )
    parser.add_argument("--skill", required=True, help="Upstream skill name.")
    parser.add_argument("--implementation-checklist", required=True, help="Implementation checklist path.")
    parser.add_argument("--contract-diff-basis", required=True, help="contract_diff_basis artifact path.")
    parser.add_argument("--target", required=True, help="Pair, fixture, or execution target name.")
    parser.add_argument("--smoke", action="append", default=[], help="Existing smoke artifact path. Repeatable.")
    parser.add_argument("--pre-fix", help="Pre-fix artifact path for diff planning.")
    parser.add_argument("--post-fix", help="Post-fix artifact path for diff planning.")
    parser.add_argument("--metric", action="append", default=[], help="Metric names to carry into diff planning.")
    parser.add_argument("--experiment", help="Optional explicit experiment name.")
    return parser.parse_args()


def _plan_stage(smoke_paths: list[Path], pre_fix: Path | None, post_fix: Path | None) -> str:
    if pre_fix is not None or post_fix is not None:
        if pre_fix is None or post_fix is None:
            _err("--pre-fix와 --post-fix는 함께 줘야 합니다.")
        return "ready_for_diff"
    if smoke_paths:
        return "post_smoke"
    return "pre_execution"


def _build_handoffs(stage: str, needs_metricize: bool) -> list[dict[str, object]]:
    handoffs: list[dict[str, object]] = []
    evidence_when = "now" if stage in {"post_smoke", "ready_for_diff"} else "after smoke"
    handoffs.append(
        {
            "target_skill": "evidence-trace-auditor",
            "when": evidence_when,
            "purpose": "raw smoke를 evidence ledger와 support audit로 정규화",
            "entrypoint": "evidence-trace-auditor/scripts/evidence_trace_auditor.py",
        }
    )
    if stage == "post_smoke":
        handoffs.append(
            {
                "target_skill": "baseline-diff-lab",
                "when": "when pre/post pair exists",
                "purpose": "fix effect를 주장해야 할 때 before/after diff 계산",
                "entrypoint": "baseline-diff-lab/scripts/baseline_diff_planner.py",
            }
        )
    if stage == "ready_for_diff":
        handoff: dict[str, object] = {
            "target_skill": "baseline-diff-lab",
            "when": "now",
            "purpose": "before/after diff와 reduction metric 계산",
            "entrypoint": "baseline-diff-lab/scripts/baseline_diff_planner.py",
        }
        if needs_metricize:
            handoff["adapter"] = "baseline-diff-lab/scripts/metricize_smoke_report.py"
        handoffs.append(handoff)
    return handoffs


def main() -> None:
    args = _parse_args()

    implementation_checklist = Path(args.implementation_checklist)
    contract_diff_basis = Path(args.contract_diff_basis)
    smoke_paths = [Path(item) for item in args.smoke]
    pre_fix = Path(args.pre_fix) if args.pre_fix else None
    post_fix = Path(args.post_fix) if args.post_fix else None

    if not implementation_checklist.is_file():
        _err(f"implementation checklist 없음: {implementation_checklist}")
    if not contract_diff_basis.is_file():
        _err(f"contract_diff_basis 없음: {contract_diff_basis}")
    for smoke_path in smoke_paths:
        if not smoke_path.is_file():
            _err(f"smoke artifact 없음: {smoke_path}")
    if pre_fix is not None and not pre_fix.is_file():
        _err(f"pre-fix artifact 없음: {pre_fix}")
    if post_fix is not None and not post_fix.is_file():
        _err(f"post-fix artifact 없음: {post_fix}")

    stage = _plan_stage(smoke_paths, pre_fix, post_fix)
    experiment = _derive_experiment_name(args.experiment, args.target, smoke_paths, pre_fix)
    stamp = _now_stamp()
    needs_metricize = stage == "ready_for_diff" and not (_has_metrics_dict(pre_fix) and _has_metrics_dict(post_fix))

    suggested_outputs: dict[str, str] = {
        "smoke_json": f"references/{experiment}-smoke-report-at{stamp}.json",
        "smoke_md": f"references/{experiment}-smoke-report-at{stamp}.md",
        "evidence_ledger_json": f"references/{experiment}-evidence-ledger-at{stamp}.json",
        "evidence_ledger_md": f"references/{experiment}-evidence-ledger-at{stamp}.md",
        "support_audit_json": f"references/{experiment}-support-audit-at{stamp}.json",
        "support_audit_md": f"references/{experiment}-support-audit-at{stamp}.md",
    }
    if stage == "ready_for_diff":
        suggested_outputs["diff_json"] = f"references/{experiment}-fix-diff-at{stamp}.json"
        suggested_outputs["diff_md"] = f"references/{experiment}-fix-diff-at{stamp}.md"

    if stage == "pre_execution":
        next_actions = [
            "implementation checklist 기준으로 TDD를 먼저 고정한다",
            "contract-aware implementation을 진행한다",
            "raw smoke artifact를 JSON/MD로 저장한다",
            "smoke artifact와 contract_diff_basis를 evidence-trace-auditor로 넘긴다",
        ]
    elif stage == "post_smoke":
        next_actions = [
            "raw smoke artifact를 evidence ledger로 정규화한다",
            "contract_diff_basis 기준 support audit를 계산한다",
            "troubleshooting과 residual uncertainty를 정리한다",
            "fix effect를 주장해야 하면 pre/post artifact를 모아 baseline-diff-lab으로 넘긴다",
        ]
    else:
        next_actions = [
            "pre/post artifact가 같은 execution target을 가리키는지 확인한다",
            "필요하면 raw smoke artifact를 metric artifact로 정규화한다",
            "baseline-diff-lab planner로 diff artifact 이름을 고정한다",
            "baseline-diff-lab compute로 before/after diff를 계산한다",
        ]

    notes = [
        "execution contract artifact 없이 smoke/evidence 단계로 넘어가지 않는다",
        "evidence ledger와 support audit 없이 lesson을 KB로 바로 승격하지 않는다",
        "pre-fix와 post-fix는 같은 target과 같은 metric family를 기준으로 비교한다",
    ]
    if needs_metricize:
        notes.append("pre/post artifact에 metrics dict가 없으면 metricize_smoke_report.py를 먼저 사용한다")

    payload = {
        "status": "planned",
        "skill": args.skill,
        "stage": stage,
        "target": args.target,
        "experiment": experiment,
        "inputs": {
            "implementation_checklist": str(implementation_checklist),
            "contract_diff_basis": str(contract_diff_basis),
            "smoke_artifacts": [str(path) for path in smoke_paths],
            "pre_fix": str(pre_fix) if pre_fix else None,
            "post_fix": str(post_fix) if post_fix else None,
            "metrics": args.metric,
        },
        "suggested_outputs": suggested_outputs,
        "handoffs": _build_handoffs(stage, needs_metricize),
        "next_actions": next_actions,
        "notes": notes,
        "pattern_doc": "skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md",
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
