#!/usr/bin/env python3
"""slice-experiment-lab.

Usage:
    python3 slice_experiment_lab.py emit-experiment-bundle-contract
    python3 slice_experiment_lab.py evaluate-experiment-bundle --input-bundle <file>
    python3 slice_experiment_lab.py gate-strict-warning-policy --input-artifact <file>
    python3 slice_experiment_lab.py suggest-triad-names --slice <name>
    python3 slice_experiment_lab.py capture-quick-validate --skill-dir <dir>
    python3 slice_experiment_lab.py capture-smoke-command --expected-status <valid|invalid> --label <name> -- <command...>
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))
REQUIRED_FIELDS = [
    "skill_name",
    "current_slice",
    "contract_artifact",
    "valid_artifact",
    "invalid_artifact",
    "quick_validate_status",
]
QUICK_VALIDATE_ENUM = ["passed", "failed"]
SMOKE_EXPECTED_ENUM = ["valid", "invalid"]
TRIAD_CONTRACT_SUFFIX = "contract-smoke"
TRIAD_VALID_SUFFIX = "validation-smoke"
TRIAD_INVALID_SUFFIX = "invalid-validation-smoke"


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _relative_or_str(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON artifact must be dict: {path}")
    return payload


def _write_json(path_str: str | None, payload: dict[str, object]) -> None:
    if not path_str:
        return
    path = Path(path_str)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[INFO] JSON artifact written: {path}", file=sys.stderr)


def _write_md(path_str: str | None, content: str) -> None:
    if not path_str:
        return
    path = Path(path_str)
    path.write_text(content, encoding="utf-8")
    print(f"[INFO] Markdown summary written: {path}", file=sys.stderr)


def _parse_json_if_possible(raw_text: str) -> dict[str, object] | None:
    text = raw_text.strip()
    if not text:
        return None
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _safe_slug(value: str) -> str:
    lowered = value.strip().lower().replace(" ", "-")
    chars = []
    for char in lowered:
        if char.isalnum() or char in {"-", "_"}:
            chars.append(char)
        else:
            chars.append("-")
    slug = "".join(chars)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-") or "slice"


def emit_experiment_bundle_contract() -> dict[str, object]:
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "slice_experiment_bundle_contract",
        "version": "v0.2.0",
        "required_fields": REQUIRED_FIELDS,
        "quick_validate_enum": QUICK_VALIDATE_ENUM,
        "field_schema": {
            "skill_name": "str",
            "current_slice": "str",
            "contract_artifact": "path[str]",
            "valid_artifact": "path[str]",
            "invalid_artifact": "path[str]",
            "quick_validate_status": "enum(passed|failed)",
            "notes": "optional[str]",
        },
    }


def suggest_triad_names(slice_name: str, timestamp: str, references_dir: str = "references") -> dict[str, object]:
    slug = _safe_slug(slice_name)
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "artifact_triad_naming_suggestion",
        "slice_name": slice_name,
        "timestamp": timestamp,
        "references_dir": references_dir,
        "artifacts": {
            "contract_json": f"{references_dir}/{slug}-{TRIAD_CONTRACT_SUFFIX}-at{timestamp}.json",
            "contract_md": f"{references_dir}/{slug}-{TRIAD_CONTRACT_SUFFIX}-at{timestamp}.md",
            "valid_json": f"{references_dir}/{slug}-{TRIAD_VALID_SUFFIX}-at{timestamp}.json",
            "valid_md": f"{references_dir}/{slug}-{TRIAD_VALID_SUFFIX}-at{timestamp}.md",
            "invalid_json": f"{references_dir}/{slug}-{TRIAD_INVALID_SUFFIX}-at{timestamp}.json",
            "invalid_md": f"{references_dir}/{slug}-{TRIAD_INVALID_SUFFIX}-at{timestamp}.md",
        },
    }


def capture_quick_validate(skill_dir: str, strict: bool = False) -> dict[str, object]:
    command = [
        sys.executable,
        str(Path(__file__).resolve().parents[2] / "_shared" / "scripts" / "quick_validate.py"),
        skill_dir,
    ]
    if strict:
        command.append("--strict")
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    stdout_lines = [line for line in result.stdout.splitlines() if line.strip()]
    stderr_lines = [line for line in result.stderr.splitlines() if line.strip()]
    warnings = [line.removeprefix("[WARN] ").strip() for line in stderr_lines if line.startswith("[WARN] ")]
    errors = [line.removeprefix("[ERROR] ").strip() for line in stderr_lines if line.startswith("[ERROR] ")]
    final_stdout = stdout_lines[-1] if stdout_lines else ""
    normalized_status = "passed" if final_stdout == "Validation passed" and result.returncode == 0 else "failed"
    return {
        "status": normalized_status,
        "generated_at": _now_iso(),
        "contract_family": "quick_validate_capture",
        "skill_dir": skill_dir,
        "strict": strict,
        "command": command,
        "exit_code": result.returncode,
        "stdout_lines": stdout_lines,
        "stderr_lines": stderr_lines,
        "warnings": warnings,
        "errors": errors,
        "final_stdout": final_stdout,
    }


def capture_smoke_command(expected_status: str, label: str, command: list[str]) -> dict[str, object]:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    parsed_stdout = _parse_json_if_possible(result.stdout)
    parsed_status = parsed_stdout.get("status") if isinstance(parsed_stdout, dict) else None
    if (
        expected_status == "valid"
        and result.returncode == 0
        and (parsed_status is None or parsed_status == "valid")
    ):
        normalized_status = "valid"
    elif (
        expected_status == "invalid"
        and result.returncode != 0
        and (parsed_status is None or parsed_status == "invalid")
    ):
        normalized_status = "invalid"
    else:
        normalized_status = "capture_failed"
    return {
        "status": normalized_status,
        "generated_at": _now_iso(),
        "contract_family": "smoke_command_capture",
        "label": label,
        "expected_status": expected_status,
        "command": command,
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "parsed_stdout_status": parsed_status if isinstance(parsed_status, str) else None,
    }


def gate_strict_warning_policy(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []

    family = payload.get("contract_family")
    if family != "quick_validate_capture":
        errors.append("contract_family must be quick_validate_capture")

    artifact_status = payload.get("status")
    if not isinstance(artifact_status, str) or artifact_status not in QUICK_VALIDATE_ENUM:
        errors.append(f"status must be one of {QUICK_VALIDATE_ENUM}")

    warnings = payload.get("warnings")
    if not isinstance(warnings, list) or any(not isinstance(item, str) for item in warnings):
        errors.append("warnings must be list[str]")
        warnings = []

    quick_validate_errors = payload.get("errors")
    if not isinstance(quick_validate_errors, list) or any(not isinstance(item, str) for item in quick_validate_errors):
        errors.append("errors must be list[str]")
        quick_validate_errors = []

    reasons: list[str] = []
    if errors:
        decision = "invalid"
        reasons.append("artifact contract is invalid")
    else:
        warning_count = len(warnings)
        error_count = len(quick_validate_errors)
        if artifact_status == "failed":
            reasons.append("quick_validate capture status is failed")
        if error_count > 0:
            reasons.append("quick_validate capture errors present")
        if warning_count > 0:
            reasons.append("warnings present under strict policy")

        if artifact_status == "failed" or error_count > 0:
            decision = "invalid"
        elif warning_count > 0:
            decision = "hold"
        else:
            decision = "pass"

    return {
        "status": decision,
        "generated_at": _now_iso(),
        "contract_family": "strict_warning_policy_gate",
        "input_artifact": _relative_or_str(input_path),
        "decision": decision,
        "workflow_status": "ready_for_next_slice" if decision == "pass" else "hold_current_slice",
        "artifact_status": artifact_status if isinstance(artifact_status, str) else None,
        "warning_count": len(warnings),
        "error_count": len(quick_validate_errors),
        "warnings": warnings,
        "quick_validate_errors": quick_validate_errors,
        "reasons": reasons,
        "errors": errors,
    }


def _validate_non_empty_string(payload: dict[str, object], field_name: str, errors: list[str]) -> None:
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{field_name} must be non-empty str")


def evaluate_experiment_bundle(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    errors: list[str] = []
    gaps: list[str] = []

    for field in REQUIRED_FIELDS:
        if field not in payload:
            errors.append(f"missing field: {field}")
    for field in REQUIRED_FIELDS:
        if field in payload:
            _validate_non_empty_string(payload, field, errors)

    qv = payload.get("quick_validate_status")
    if isinstance(qv, str) and qv not in QUICK_VALIDATE_ENUM:
        errors.append(f"quick_validate_status must be one of {QUICK_VALIDATE_ENUM}")

    contract_family: str | None = None
    valid_status: str | None = None
    invalid_status: str | None = None

    for key in ["contract_artifact", "valid_artifact", "invalid_artifact"]:
        raw_path = payload.get(key)
        if not isinstance(raw_path, str) or not raw_path.strip():
            continue
        path = Path(raw_path)
        if not path.is_file():
            errors.append(f"{key} file does not exist: {raw_path}")
            continue
        try:
            artifact = _load_json(path)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{key} cannot be loaded as dict JSON: {exc}")
            continue

        if key == "contract_artifact":
            raw_family = artifact.get("contract_family")
            if not isinstance(raw_family, str) or "contract" not in raw_family:
                errors.append("contract_artifact.contract_family must contain 'contract'")
            else:
                contract_family = raw_family
        elif key == "valid_artifact":
            raw_status = artifact.get("status")
            if not isinstance(raw_status, str):
                errors.append("valid_artifact.status must be str")
            else:
                valid_status = raw_status
        elif key == "invalid_artifact":
            raw_status = artifact.get("status")
            if not isinstance(raw_status, str):
                errors.append("invalid_artifact.status must be str")
            else:
                invalid_status = raw_status

    if not errors:
        if valid_status != "valid":
            gaps.append("valid_artifact status is not valid")
        if invalid_status != "invalid":
            gaps.append("invalid_artifact status is not invalid")
        if qv != "passed":
            gaps.append("quick_validate_status is not passed")

    bundle_status = "valid" if not errors else "invalid"
    workflow_status = "ready_for_next_slice" if bundle_status == "valid" and not gaps else "hold_current_slice"

    return {
        "status": workflow_status,
        "generated_at": _now_iso(),
        "contract_family": "slice_experiment_bundle_evaluation",
        "input_bundle": _relative_or_str(input_path),
        "bundle_status": bundle_status,
        "workflow_status": workflow_status,
        "current_slice": payload.get("current_slice") if isinstance(payload.get("current_slice"), str) else None,
        "gaps": gaps,
        "errors": errors,
        "artifact_summary": {
            "contract_family": contract_family,
            "valid_status": valid_status,
            "invalid_status": invalid_status,
            "quick_validate_status": qv if isinstance(qv, str) else None,
        },
    }


def render_contract_markdown(payload: dict[str, object]) -> str:
    if payload["contract_family"] == "artifact_triad_naming_suggestion":
        artifacts = payload["artifacts"]
        return (
            "# slice-experiment-lab artifact triad naming suggestion\n\n"
            f"- generated_at: `{payload['generated_at']}`\n"
            f"- slice_name: `{payload['slice_name']}`\n"
            f"- timestamp: `{payload['timestamp']}`\n\n"
            "## Suggested Artifacts\n\n"
            f"- contract_json: `{artifacts['contract_json']}`\n"
            f"- contract_md: `{artifacts['contract_md']}`\n"
            f"- valid_json: `{artifacts['valid_json']}`\n"
            f"- valid_md: `{artifacts['valid_md']}`\n"
            f"- invalid_json: `{artifacts['invalid_json']}`\n"
            f"- invalid_md: `{artifacts['invalid_md']}`\n"
        )
    lines = [
        "# slice-experiment-lab experiment_bundle contract",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- contract_family: `{payload['contract_family']}`",
        f"- version: `{payload['version']}`",
        "",
        "## Required Fields",
        "",
    ]
    for field in payload["required_fields"]:
        lines.append(f"- `{field}`")
    return "\n".join(lines) + "\n"


def render_evaluation_markdown(payload: dict[str, object]) -> str:
    if payload["contract_family"] == "strict_warning_policy_gate":
        lines = [
            "# slice-experiment-lab strict warning policy gate",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- input_artifact: `{payload['input_artifact']}`",
            f"- decision: `{payload['decision']}`",
            f"- workflow_status: `{payload['workflow_status']}`",
            f"- artifact_status: `{payload['artifact_status']}`",
            f"- warning_count: `{payload['warning_count']}`",
            f"- error_count: `{payload['error_count']}`",
            "",
            "## Reasons",
            "",
        ]
        if payload["reasons"]:
            for reason in payload["reasons"]:
                lines.append(f"- {reason}")
        else:
            lines.append("- none")
        lines.extend(["", "## Errors", ""])
        if payload["errors"]:
            for error in payload["errors"]:
                lines.append(f"- {error}")
        else:
            lines.append("- none")
        return "\n".join(lines) + "\n"

    if payload["contract_family"] == "quick_validate_capture":
        lines = [
            "# slice-experiment-lab quick_validate capture",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- skill_dir: `{payload['skill_dir']}`",
            f"- strict: `{payload['strict']}`",
            f"- status: `{payload['status']}`",
            f"- exit_code: `{payload['exit_code']}`",
            "",
            "## Warnings",
            "",
        ]
        if payload["warnings"]:
            for warning in payload["warnings"]:
                lines.append(f"- {warning}")
        else:
            lines.append("- none")
        lines.extend(["", "## Errors", ""])
        if payload["errors"]:
            for error in payload["errors"]:
                lines.append(f"- {error}")
        else:
            lines.append("- none")
        return "\n".join(lines) + "\n"

    if payload["contract_family"] == "smoke_command_capture":
        lines = [
            "# slice-experiment-lab smoke command capture",
            "",
            f"- generated_at: `{payload['generated_at']}`",
            f"- label: `{payload['label']}`",
            f"- expected_status: `{payload['expected_status']}`",
            f"- status: `{payload['status']}`",
            f"- exit_code: `{payload['exit_code']}`",
            f"- parsed_stdout_status: `{payload['parsed_stdout_status']}`",
            "",
            "## Command",
            "",
            f"- `{' '.join(payload['command'])}`",
        ]
        return "\n".join(lines) + "\n"

    lines = [
        "# slice-experiment-lab experiment_bundle evaluation",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- input_bundle: `{payload['input_bundle']}`",
        f"- bundle_status: `{payload['bundle_status']}`",
        f"- workflow_status: `{payload['workflow_status']}`",
        "",
        "## Errors",
        "",
    ]
    if payload["errors"]:
        for error in payload["errors"]:
            lines.append(f"- {error}")
    else:
        lines.append("- none")
    lines.extend(["", "## Gaps", ""])
    if payload["gaps"]:
        for gap in payload["gaps"]:
            lines.append(f"- {gap}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def cmd_emit_experiment_bundle_contract(args: argparse.Namespace) -> int:
    payload = emit_experiment_bundle_contract()
    if args.output_json:
        _write_json(args.output_json, payload)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        _write_md(args.output_md, render_contract_markdown(payload))
    return 0


def cmd_evaluate_experiment_bundle(args: argparse.Namespace) -> int:
    input_path = Path(args.input_bundle)
    try:
        payload = _load_json(input_path)
        evaluation = evaluate_experiment_bundle(input_path, payload)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if args.output_json:
        _write_json(args.output_json, evaluation)
    else:
        print(json.dumps(evaluation, indent=2, ensure_ascii=False))
    if args.output_md:
        _write_md(args.output_md, render_evaluation_markdown(evaluation))
    return 0 if evaluation["bundle_status"] == "valid" else 1


def cmd_gate_strict_warning_policy(args: argparse.Namespace) -> int:
    input_path = Path(args.input_artifact)
    try:
        payload = _load_json(input_path)
        gate_payload = gate_strict_warning_policy(input_path, payload)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if args.output_json:
        _write_json(args.output_json, gate_payload)
    else:
        print(json.dumps(gate_payload, indent=2, ensure_ascii=False))
    if args.output_md:
        _write_md(args.output_md, render_evaluation_markdown(gate_payload))
    if gate_payload["decision"] == "pass":
        return 0
    if gate_payload["decision"] == "hold":
        return 2
    return 1


def cmd_suggest_triad_names(args: argparse.Namespace) -> int:
    payload = suggest_triad_names(args.slice, args.timestamp, args.references_dir)
    if args.output_json:
        _write_json(args.output_json, payload)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        _write_md(args.output_md, render_contract_markdown(payload))
    return 0


def cmd_capture_quick_validate(args: argparse.Namespace) -> int:
    payload = capture_quick_validate(args.skill_dir, strict=args.strict)
    if args.output_json:
        _write_json(args.output_json, payload)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        _write_md(args.output_md, render_evaluation_markdown(payload))
    return 0 if payload["status"] == "passed" else 1


def cmd_capture_smoke_command(args: argparse.Namespace) -> int:
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("[ERROR] smoke command is required after --", file=sys.stderr)
        return 1
    payload = capture_smoke_command(args.expected_status, args.label, command)
    if args.output_json:
        _write_json(args.output_json, payload)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    if args.output_md:
        _write_md(args.output_md, render_evaluation_markdown(payload))
    return 0 if payload["status"] != "capture_failed" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit and evaluate contract-slice experiment bundles.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    emit_parser = subparsers.add_parser(
        "emit-experiment-bundle-contract",
        help="Emit the canonical contract for a slice experiment bundle.",
    )
    emit_parser.add_argument("--output-json", help="Optional output path for contract JSON.")
    emit_parser.add_argument("--output-md", help="Optional output path for contract markdown summary.")
    emit_parser.set_defaults(func=cmd_emit_experiment_bundle_contract)

    eval_parser = subparsers.add_parser(
        "evaluate-experiment-bundle",
        help="Evaluate contract/valid/invalid triad plus quick_validate status.",
    )
    eval_parser.add_argument("--input-bundle", required=True, help="Path to experiment bundle JSON.")
    eval_parser.add_argument("--output-json", help="Optional output path for evaluation JSON.")
    eval_parser.add_argument("--output-md", help="Optional output path for evaluation markdown summary.")
    eval_parser.set_defaults(func=cmd_evaluate_experiment_bundle)

    warning_gate_parser = subparsers.add_parser(
        "gate-strict-warning-policy",
        help="Apply strict warning/error policy to a quick_validate capture artifact.",
    )
    warning_gate_parser.add_argument("--input-artifact", required=True, help="Path to quick_validate capture artifact JSON.")
    warning_gate_parser.add_argument("--output-json", help="Optional output path for gate report JSON.")
    warning_gate_parser.add_argument("--output-md", help="Optional output path for gate markdown summary.")
    warning_gate_parser.set_defaults(func=cmd_gate_strict_warning_policy)

    naming_parser = subparsers.add_parser(
        "suggest-triad-names",
        help="Suggest standard contract/valid/invalid artifact names for a slice.",
    )
    naming_parser.add_argument("--slice", required=True, help="Current contract slice name.")
    naming_parser.add_argument("--timestamp", required=True, help="Minute timestamp like YYYY-MM-DD-HH-MM.")
    naming_parser.add_argument("--references-dir", default="references", help="Relative references directory for artifacts.")
    naming_parser.add_argument("--output-json", help="Optional output path for naming JSON.")
    naming_parser.add_argument("--output-md", help="Optional output path for naming markdown summary.")
    naming_parser.set_defaults(func=cmd_suggest_triad_names)

    quick_validate_parser = subparsers.add_parser(
        "capture-quick-validate",
        help="Run quick_validate and normalize stdout/stderr/exit-code into a passed|failed artifact.",
    )
    quick_validate_parser.add_argument("--skill-dir", required=True, help="Skill directory to validate.")
    quick_validate_parser.add_argument("--strict", action="store_true", help="Pass --strict to quick_validate.")
    quick_validate_parser.add_argument("--output-json", help="Optional output path for capture JSON.")
    quick_validate_parser.add_argument("--output-md", help="Optional output path for capture markdown summary.")
    quick_validate_parser.set_defaults(func=cmd_capture_quick_validate)

    smoke_parser = subparsers.add_parser(
        "capture-smoke-command",
        help="Run a smoke command and normalize it into valid|invalid artifact input.",
    )
    smoke_parser.add_argument("--expected-status", required=True, choices=SMOKE_EXPECTED_ENUM, help="Expected normalized status.")
    smoke_parser.add_argument("--label", required=True, help="Short capture label.")
    smoke_parser.add_argument("--output-json", help="Optional output path for capture JSON.")
    smoke_parser.add_argument("--output-md", help="Optional output path for capture markdown summary.")
    smoke_parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    smoke_parser.set_defaults(func=cmd_capture_smoke_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
