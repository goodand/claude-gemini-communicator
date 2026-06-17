#!/usr/bin/env python3
"""Validate execution-evidence planner payloads against handoff contracts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VALID_STAGES = {"pre_execution", "post_smoke", "ready_for_diff"}
REQUIRED_TOP_KEYS = {
    "status",
    "skill",
    "stage",
    "target",
    "experiment",
    "inputs",
    "suggested_outputs",
    "handoffs",
    "next_actions",
    "notes",
    "pattern_doc",
}
REQUIRED_INPUT_KEYS = {
    "implementation_checklist",
    "contract_diff_basis",
    "smoke_artifacts",
    "pre_fix",
    "post_fix",
    "metrics",
}


def _load_json(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"[ERROR] planner payload 없음: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[ERROR] planner payload JSON 파싱 실패: {path}") from exc
    if not isinstance(payload, dict):
        raise SystemExit(f"[ERROR] planner payload는 JSON object여야 합니다: {path}")
    return payload


def _has_metrics_dict(workspace_root: Path, path_text: object) -> bool:
    if not isinstance(path_text, str) or not path_text:
        return False
    path = workspace_root / path_text
    if not path.is_file() or path.suffix != ".json":
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return isinstance(payload, dict) and isinstance(payload.get("metrics"), dict)


def _find_handoff(payload: dict[str, object], target_skill: str) -> dict[str, object] | None:
    handoffs = payload.get("handoffs")
    if not isinstance(handoffs, list):
        return None
    for item in handoffs:
        if isinstance(item, dict) and item.get("target_skill") == target_skill:
            return item
    return None


def _require_file(
    workspace_root: Path,
    path_text: object,
    label: str,
    errors: list[str],
    *,
    allow_empty: bool = False,
) -> None:
    if path_text is None and allow_empty:
        return
    if not isinstance(path_text, str) or not path_text:
        errors.append(f"{label}가 비어 있다")
        return
    path = workspace_root / path_text
    if not path.is_file():
        errors.append(f"{label} 파일이 없다: {path_text}")


def _validate_general(payload: dict[str, object], workspace_root: Path, errors: list[str]) -> None:
    missing = sorted(REQUIRED_TOP_KEYS - payload.keys())
    if missing:
        errors.append(f"top-level required key 누락: {', '.join(missing)}")

    stage = payload.get("stage")
    if stage not in VALID_STAGES:
        errors.append(f"유효하지 않은 stage: {stage}")

    inputs = payload.get("inputs")
    if not isinstance(inputs, dict):
        errors.append("inputs가 object가 아니다")
        return
    input_missing = sorted(REQUIRED_INPUT_KEYS - inputs.keys())
    if input_missing:
        errors.append(f"inputs required key 누락: {', '.join(input_missing)}")

    if payload.get("status") != "planned":
        errors.append("status는 planned여야 한다")

    _require_file(workspace_root, payload.get("pattern_doc"), "pattern_doc", errors)
    _require_file(workspace_root, inputs.get("implementation_checklist"), "implementation_checklist", errors)
    _require_file(workspace_root, inputs.get("contract_diff_basis"), "contract_diff_basis", errors)


def _validate_pre_execution(payload: dict[str, object], workspace_root: Path, errors: list[str]) -> None:
    del workspace_root
    inputs = payload["inputs"]
    smoke_artifacts = inputs.get("smoke_artifacts")
    if smoke_artifacts not in ([], None):
        errors.append("pre_execution에서는 smoke_artifacts가 비어 있어야 한다")
    if inputs.get("pre_fix") is not None or inputs.get("post_fix") is not None:
        errors.append("pre_execution에서는 pre_fix/post_fix가 없어야 한다")

    evidence_handoff = _find_handoff(payload, "evidence-trace-auditor")
    if evidence_handoff is None:
        errors.append("pre_execution에서도 evidence-trace-auditor handoff가 있어야 한다")
    elif evidence_handoff.get("when") != "after smoke":
        errors.append("pre_execution evidence handoff는 after smoke여야 한다")


def _validate_post_smoke(payload: dict[str, object], workspace_root: Path, errors: list[str]) -> None:
    inputs = payload["inputs"]
    smoke_artifacts = inputs.get("smoke_artifacts")
    if not isinstance(smoke_artifacts, list) or not smoke_artifacts:
        errors.append("post_smoke에서는 smoke_artifacts가 1개 이상이어야 한다")
    else:
        for index, item in enumerate(smoke_artifacts):
            _require_file(workspace_root, item, f"smoke_artifacts[{index}]", errors)

    if inputs.get("pre_fix") is not None or inputs.get("post_fix") is not None:
        errors.append("post_smoke에서는 pre_fix/post_fix가 없어야 한다")

    evidence_handoff = _find_handoff(payload, "evidence-trace-auditor")
    if evidence_handoff is None:
        errors.append("post_smoke에는 evidence-trace-auditor handoff가 있어야 한다")
    elif evidence_handoff.get("when") != "now":
        errors.append("post_smoke evidence handoff는 now여야 한다")

    suggested = payload.get("suggested_outputs")
    if isinstance(suggested, dict):
        for key in (
            "evidence_ledger_json",
            "evidence_ledger_md",
            "support_audit_json",
            "support_audit_md",
        ):
            if key not in suggested:
                errors.append(f"post_smoke suggested_outputs에 {key}가 없다")


def _validate_ready_for_diff(payload: dict[str, object], workspace_root: Path, errors: list[str]) -> None:
    inputs = payload["inputs"]
    _require_file(workspace_root, inputs.get("pre_fix"), "pre_fix", errors)
    _require_file(workspace_root, inputs.get("post_fix"), "post_fix", errors)

    evidence_handoff = _find_handoff(payload, "evidence-trace-auditor")
    if evidence_handoff is None:
        errors.append("ready_for_diff에는 evidence-trace-auditor handoff가 있어야 한다")
    elif evidence_handoff.get("when") != "now":
        errors.append("ready_for_diff evidence handoff는 now여야 한다")

    diff_handoff = _find_handoff(payload, "baseline-diff-lab")
    if diff_handoff is None:
        errors.append("ready_for_diff에는 baseline-diff-lab handoff가 있어야 한다")
    elif diff_handoff.get("when") != "now":
        errors.append("ready_for_diff baseline-diff-lab handoff는 now여야 한다")

    suggested = payload.get("suggested_outputs")
    if isinstance(suggested, dict):
        for key in ("diff_json", "diff_md"):
            if key not in suggested:
                errors.append(f"ready_for_diff suggested_outputs에 {key}가 없다")

    needs_metricize = not (
        _has_metrics_dict(workspace_root, inputs.get("pre_fix"))
        and _has_metrics_dict(workspace_root, inputs.get("post_fix"))
    )
    has_adapter = isinstance(diff_handoff, dict) and isinstance(diff_handoff.get("adapter"), str)
    if needs_metricize and not has_adapter:
        errors.append("metrics dict가 없는 ready_for_diff payload에는 adapter가 있어야 한다")
    if not needs_metricize and has_adapter:
        errors.append("metrics dict가 이미 있으면 ready_for_diff payload에 adapter가 없어야 한다")


def _build_report(payload: dict[str, object], workspace_root: Path) -> dict[str, object]:
    errors: list[str] = []
    warnings: list[str] = []
    _validate_general(payload, workspace_root, errors)

    if not errors and isinstance(payload.get("inputs"), dict):
        stage = payload.get("stage")
        if stage == "pre_execution":
            _validate_pre_execution(payload, workspace_root, errors)
        elif stage == "post_smoke":
            _validate_post_smoke(payload, workspace_root, errors)
        elif stage == "ready_for_diff":
            _validate_ready_for_diff(payload, workspace_root, errors)

    report = {
        "status": "valid" if not errors else "invalid",
        "skill": payload.get("skill"),
        "stage": payload.get("stage"),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "errors": errors,
        "warnings": warnings,
        "validated_handoffs": [
            handoff.get("target_skill")
            for handoff in payload.get("handoffs", [])
            if isinstance(handoff, dict) and isinstance(handoff.get("target_skill"), str)
        ],
    }
    return report


def _write_markdown(path: Path, report: dict[str, object]) -> None:
    lines = [
        "# Execution Handoff Validation Report",
        "",
        f"- status: `{report['status']}`",
        f"- skill: `{report.get('skill')}`",
        f"- stage: `{report.get('stage')}`",
        f"- error_count: `{report['error_count']}`",
        f"- warning_count: `{report['warning_count']}`",
        "",
        "## Validated Handoffs",
        "",
    ]
    for handoff in report["validated_handoffs"]:
        lines.append(f"- `{handoff}`")
    lines.extend(["", "## Errors", ""])
    if report["errors"]:
        for error in report["errors"]:
            lines.append(f"- {error}")
    else:
        lines.append("- 없음")
    lines.extend(["", "## Warnings", ""])
    if report["warnings"]:
        for warning in report["warnings"]:
            lines.append(f"- {warning}")
    else:
        lines.append("- 없음")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate execution_evidence_planner payloads against downstream handoff contracts."
    )
    parser.add_argument("--planner-payload", required=True, help="Planner payload JSON path.")
    parser.add_argument(
        "--workspace-root",
        default=".",
        help="Workspace root used to resolve relative artifact paths.",
    )
    parser.add_argument("--output-json", help="Optional validation report JSON output path.")
    parser.add_argument("--output-md", help="Optional validation report Markdown output path.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    workspace_root = Path(args.workspace_root).resolve()
    payload_path = Path(args.planner_payload)
    payload = _load_json(payload_path)
    report = _build_report(payload, workspace_root)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.output_md:
        output_md = Path(args.output_md)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        _write_markdown(output_md, report)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    if report["status"] != "valid":
        sys.exit(1)


if __name__ == "__main__":
    main()
