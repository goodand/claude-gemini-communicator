#!/usr/bin/env python3
"""evidence-trace-auditor v0.1.

Usage:
    python3 evidence_trace_auditor.py build-evidence-ledger --input-report <file>
    python3 evidence_trace_auditor.py build-test-result-ledger --input-junit-xml <file>
    python3 evidence_trace_auditor.py build-log-evidence-ledger --input-log-jsonl <file>
    python3 evidence_trace_auditor.py build-artifact-path-ledger --input-manifest <file>
    python3 evidence_trace_auditor.py build-attestation-ledger --input-attestation-manifest <file>
    python3 evidence_trace_auditor.py build-tool-call-ledger --input-tool-call-manifest <file>
    python3 evidence_trace_auditor.py audit-support --evidence-ledger <file> --contract-diff-basis <file>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET


KST = timezone(timedelta(hours=9))


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


def _relative_or_str(path: Path) -> str:
    try:
        return str(path.relative_to(Path.cwd()))
    except ValueError:
        return str(path)


def _load_json(path: Path) -> dict[str, object]:
    if not path.is_file():
        _err(f"파일이 없습니다: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        _err(f"JSON artifact가 dict가 아닙니다: {path}")
    return payload


def _normalize_evidence(raw: object) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(item) for item in raw if str(item).strip()]
    text = str(raw).strip()
    return [text] if text else []


def _map_observed_bucket(finding_family: str, item: dict[str, object]) -> str | None:
    if finding_family == "missing_in_code":
        return "missing_contract_unit"
    if finding_family == "missing_in_doc":
        return "extra_contract_unit"
    if finding_family == "mismatch":
        return "contract_value_changed"
    if finding_family != "typed_mismatch":
        return None

    typed_kind = str(item.get("kind", ""))
    typed_mapping = {
        "enum_value_set_changed": "contract_value_changed",
        "transition_rule_set_changed": "contract_value_changed",
        "path_rule_condition_changed": "contract_value_changed",
        "requiredness_changed": "requiredness_changed",
        "cli_argument_surface_changed": "cli_argument_surface_changed",
    }
    return typed_mapping.get(typed_kind)


def _entry_id(finding_family: str, item: dict[str, object], index: int) -> str:
    name = str(item.get("name") or f"entry-{index}")
    normalized = name.replace(" ", "-").replace("/", "-")
    return f"{finding_family}:{normalized}"


def build_evidence_ledger(input_path: Path, payload: dict[str, object]) -> dict[str, object]:
    supported_families = ["missing_in_code", "missing_in_doc", "mismatch", "typed_mismatch"]
    entries: list[dict[str, object]] = []

    for family in supported_families:
        raw_items = payload.get(family, [])
        if not isinstance(raw_items, list):
            _err(f"{family} 형식이 list가 아닙니다.")
        for index, raw_item in enumerate(raw_items, start=1):
            if not isinstance(raw_item, dict):
                _err(f"{family} entry가 dict가 아닙니다.")
            doc_evidence = _normalize_evidence(raw_item.get("doc_evidence"))
            code_evidence = _normalize_evidence(raw_item.get("code_evidence"))
            has_evidence = bool(doc_evidence or code_evidence)
            entries.append(
                {
                    "entry_id": _entry_id(family, raw_item, index),
                    "finding_family": family,
                    "kind": str(raw_item.get("kind", "")),
                    "name": str(raw_item.get("name", "")),
                    "observed_bucket": _map_observed_bucket(family, raw_item),
                    "evidence": {
                        "doc": doc_evidence,
                        "code": code_evidence,
                    },
                    "trace_status": "verified_evidence" if has_evidence else "missing_evidence",
                    "action": str(raw_item.get("action", "")),
                    "reason": str(raw_item.get("reason", "")),
                }
            )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "evidence_ledger",
        "source_report": _relative_or_str(input_path),
        "source_report_type": "raw_smoke_report",
        "scope": payload.get("scope"),
        "rule_kind": payload.get("rule_kind"),
        "pair": payload.get("pair"),
        "entry_count": len(entries),
        "entries": entries,
    }


def build_test_result_ledger(input_path: Path) -> dict[str, object]:
    try:
        root = ET.fromstring(input_path.read_text(encoding="utf-8"))
    except ET.ParseError as exc:
        _err(f"JUnit XML parse 실패: {exc}")

    testcase_elements: list[ET.Element] = []
    if root.tag == "testsuite":
        testcase_elements.extend(root.findall(".//testcase"))
    elif root.tag == "testsuites":
        testcase_elements.extend(root.findall(".//testcase"))
    else:
        _err("지원하지 않는 JUnit XML root 입니다. testsuite 또는 testsuites 가 필요합니다.")

    entries: list[dict[str, object]] = []
    for index, testcase in enumerate(testcase_elements, start=1):
        name = testcase.get("name", f"testcase-{index}")
        classname = testcase.get("classname", "")
        full_name = f"{classname}::{name}" if classname else name

        failure = testcase.find("failure")
        error = testcase.find("error")
        skipped = testcase.find("skipped")
        if failure is None and error is None and skipped is None:
            continue

        status = "failed"
        observed_bucket = "contract_value_changed"
        detail_node = failure
        if error is not None:
            status = "error"
            observed_bucket = "contract_value_changed"
            detail_node = error
        elif skipped is not None:
            status = "skipped"
            observed_bucket = None
            detail_node = skipped

        detail_text = ""
        if detail_node is not None:
            message = detail_node.get("message", "").strip()
            body = (detail_node.text or "").strip()
            detail_text = message or body or status

        entries.append(
            {
                "entry_id": f"test_result:{full_name.replace(' ', '-').replace('/', '-')}",
                "finding_family": "test_result",
                "kind": "test_case_result",
                "name": full_name,
                "observed_bucket": observed_bucket,
                "evidence": {
                    "doc": [],
                    "code": [f"{status}: {detail_text}".strip(": ")],
                },
                "trace_status": "verified_evidence",
                "action": "failing/skipped test의 원인과 contract alignment 검토",
                "reason": status,
            }
        )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "evidence_ledger",
        "source_report": _relative_or_str(input_path),
        "source_report_type": "junit_xml",
        "scope": "test_result_evidence",
        "rule_kind": "test_result",
        "pair": {"doc": None, "script": None},
        "entry_count": len(entries),
        "entries": entries,
    }


def build_log_evidence_ledger(input_path: Path) -> dict[str, object]:
    entries: list[dict[str, object]] = []
    lines = input_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            _err(f"log JSONL parse 실패 line {index}: {exc}")
        if not isinstance(record, dict):
            _err(f"log JSONL line {index} 형식이 dict가 아닙니다.")

        attributes = record.get("attributes", {})
        if not isinstance(attributes, dict):
            _err(f"log JSONL line {index} attributes 형식이 dict가 아닙니다.")

        name = str(attributes.get("name") or f"log-event-{index}")
        body = str(record.get("body", "")).strip()
        timestamp = str(record.get("timestamp", "")).strip()
        severity = str(record.get("severity_text", "")).strip()
        evidence_parts = [part for part in [timestamp, severity, body] if part]
        evidence_text = " | ".join(evidence_parts)
        observed_bucket = attributes.get("observed_bucket")
        if observed_bucket is not None:
            observed_bucket = str(observed_bucket)

        entries.append(
            {
                "entry_id": f"log_event:{name.replace(' ', '-').replace('/', '-')}",
                "finding_family": "log_event",
                "kind": str(attributes.get("kind", "log_record")),
                "name": name,
                "observed_bucket": observed_bucket,
                "evidence": {
                    "doc": [],
                    "code": [evidence_text] if evidence_text else [],
                },
                "trace_status": "verified_evidence" if evidence_text else "missing_evidence",
                "action": str(attributes.get("action", "")),
                "reason": str(attributes.get("reason", body)),
            }
        )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "evidence_ledger",
        "source_report": _relative_or_str(input_path),
        "source_report_type": "jsonl_log",
        "scope": "log_evidence",
        "rule_kind": "log_event",
        "pair": {"doc": None, "script": None},
        "entry_count": len(entries),
        "entries": entries,
    }


def build_artifact_path_ledger(input_path: Path, manifest: dict[str, object]) -> dict[str, object]:
    raw_entries = manifest.get("entries", [])
    if not isinstance(raw_entries, list):
        _err("artifact path manifest의 entries 형식이 list가 아닙니다.")

    entries: list[dict[str, object]] = []
    for index, raw_entry in enumerate(raw_entries, start=1):
        if not isinstance(raw_entry, dict):
            _err("artifact path manifest entry가 dict가 아닙니다.")
        path_text = str(raw_entry.get("path", "")).strip()
        if not path_text:
            _err("artifact path manifest entry에 path가 없습니다.")
        target_path = Path(path_text)
        exists = target_path.exists()
        name = str(raw_entry.get("name") or target_path.name or f"artifact-{index}")
        observed_bucket = raw_entry.get("observed_bucket")
        if observed_bucket is not None:
            observed_bucket = str(observed_bucket)
        entries.append(
            {
                "entry_id": f"artifact_path:{name.replace(' ', '-').replace('/', '-')}",
                "finding_family": "artifact_path",
                "kind": str(raw_entry.get("kind", "artifact_path")),
                "name": name,
                "observed_bucket": observed_bucket,
                "evidence": {
                    "doc": [],
                    "code": [path_text] if exists else [],
                },
                "trace_status": "verified_evidence" if exists else "missing_evidence",
                "action": str(raw_entry.get("action", "artifact path existence 검토")),
                "reason": str(raw_entry.get("reason", "artifact path exists" if exists else "artifact path missing")),
                "required": bool(raw_entry.get("required", False)),
            }
        )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "evidence_ledger",
        "source_report": _relative_or_str(input_path),
        "source_report_type": "artifact_path_manifest",
        "scope": "artifact_path_evidence",
        "rule_kind": "artifact_path",
        "pair": {"doc": None, "script": None},
        "entry_count": len(entries),
        "entries": entries,
    }


def build_attestation_ledger(input_path: Path, manifest: dict[str, object]) -> dict[str, object]:
    raw_entries = manifest.get("entries", [])
    if not isinstance(raw_entries, list):
        _err("attestation manifest의 entries 형식이 list가 아닙니다.")

    entries: list[dict[str, object]] = []
    for index, raw_entry in enumerate(raw_entries, start=1):
        if not isinstance(raw_entry, dict):
            _err("attestation manifest entry가 dict가 아닙니다.")

        name = str(raw_entry.get("name") or f"attestation-{index}")
        tool_name = str(raw_entry.get("tool_name", "")).strip()
        command = str(raw_entry.get("command", "")).strip()
        cwd = str(raw_entry.get("cwd", "")).strip()
        actor = str(raw_entry.get("actor", "")).strip()
        started_at = str(raw_entry.get("started_at", "")).strip()
        finished_at = str(raw_entry.get("finished_at", "")).strip()
        exit_code = raw_entry.get("exit_code")
        input_paths = [str(item).strip() for item in raw_entry.get("input_paths", []) if str(item).strip()]
        output_paths = [str(item).strip() for item in raw_entry.get("output_paths", []) if str(item).strip()]

        if not command:
            trace_status = "missing_evidence"
            reason = "attested command missing"
        else:
            existing_outputs = [path for path in output_paths if Path(path).exists()]
            missing_outputs = [path for path in output_paths if not Path(path).exists()]
            if missing_outputs:
                trace_status = "missing_evidence"
                reason = f"required output missing: {', '.join(missing_outputs)}"
            elif exit_code == 0 and existing_outputs:
                trace_status = "verified_evidence"
                reason = str(raw_entry.get("reason", "attested step produced required outputs"))
            else:
                trace_status = "residual_uncertainty"
                if exit_code != 0:
                    reason = str(raw_entry.get("reason", f"non-zero exit_code: {exit_code}"))
                else:
                    reason = str(raw_entry.get("reason", "no output path to verify attestation"))

        observed_bucket = raw_entry.get("observed_bucket")
        if observed_bucket is not None:
            observed_bucket = str(observed_bucket)

        evidence_parts = [part for part in [tool_name, command, cwd] if part]
        if exit_code is not None:
            evidence_parts.append(f"exit_code={exit_code}")
        if actor:
            evidence_parts.append(f"actor={actor}")
        if started_at:
            evidence_parts.append(f"started_at={started_at}")
        if finished_at:
            evidence_parts.append(f"finished_at={finished_at}")
        if input_paths:
            evidence_parts.append(f"inputs={','.join(input_paths)}")
        if output_paths:
            evidence_parts.append(f"outputs={','.join(output_paths)}")

        entries.append(
            {
                "entry_id": f"attestation:{name.replace(' ', '-').replace('/', '-')}",
                "finding_family": "attestation",
                "kind": str(raw_entry.get("kind", "step_attestation")),
                "name": name,
                "observed_bucket": observed_bucket,
                "evidence": {
                    "doc": [],
                    "code": [" | ".join(evidence_parts)] if evidence_parts else [],
                },
                "trace_status": trace_status,
                "action": str(raw_entry.get("action", "attested step provenance 검토")),
                "reason": reason,
                "attestation": {
                    "tool_name": tool_name,
                    "command": command,
                    "cwd": cwd,
                    "actor": actor,
                    "started_at": started_at,
                    "finished_at": finished_at,
                    "exit_code": exit_code,
                    "input_paths": input_paths,
                    "output_paths": output_paths,
                },
            }
        )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "evidence_ledger",
        "source_report": _relative_or_str(input_path),
        "source_report_type": "attestation_manifest",
        "scope": "attestation_evidence",
        "rule_kind": "attestation",
        "pair": {"doc": None, "script": None},
        "entry_count": len(entries),
        "entries": entries,
    }


def build_tool_call_ledger(input_path: Path, manifest: dict[str, object]) -> dict[str, object]:
    raw_entries = manifest.get("entries", [])
    if not isinstance(raw_entries, list):
        _err("tool call manifest의 entries 형식이 list가 아닙니다.")

    entries: list[dict[str, object]] = []
    for index, raw_entry in enumerate(raw_entries, start=1):
        if not isinstance(raw_entry, dict):
            _err("tool call manifest entry가 dict가 아닙니다.")

        name = str(raw_entry.get("name") or f"tool-call-{index}")
        tool_name = str(raw_entry.get("tool_name", "")).strip()
        command = str(raw_entry.get("command", "")).strip()
        args = [str(item).strip() for item in raw_entry.get("args", []) if str(item).strip()]
        cwd = str(raw_entry.get("cwd", "")).strip()
        exit_code = raw_entry.get("exit_code")
        stdout_excerpt = str(raw_entry.get("stdout_excerpt", "")).strip()
        stderr_excerpt = str(raw_entry.get("stderr_excerpt", "")).strip()
        output_paths = [str(item).strip() for item in raw_entry.get("output_paths", []) if str(item).strip()]

        if not tool_name or not command:
            trace_status = "missing_evidence"
            reason = "tool call identity missing"
        else:
            missing_outputs = [path for path in output_paths if not Path(path).exists()]
            existing_outputs = [path for path in output_paths if Path(path).exists()]
            has_result_signal = bool(stdout_excerpt or stderr_excerpt or existing_outputs)
            if missing_outputs:
                trace_status = "missing_evidence"
                reason = f"required tool output missing: {', '.join(missing_outputs)}"
            elif exit_code != 0:
                trace_status = "residual_uncertainty"
                reason = str(raw_entry.get("reason", f"tool call exited non-zero: {exit_code}"))
            elif has_result_signal:
                trace_status = "verified_evidence"
                reason = str(raw_entry.get("reason", "tool call produced verifiable result signal"))
            else:
                trace_status = "residual_uncertainty"
                reason = str(raw_entry.get("reason", "tool call lacks stdout/stderr/output evidence"))

        observed_bucket = raw_entry.get("observed_bucket")
        if observed_bucket is not None:
            observed_bucket = str(observed_bucket)

        evidence_parts = [part for part in [tool_name, command, cwd] if part]
        if args:
            evidence_parts.append(f"args={','.join(args)}")
        if exit_code is not None:
            evidence_parts.append(f"exit_code={exit_code}")
        if stdout_excerpt:
            evidence_parts.append(f"stdout={stdout_excerpt}")
        if stderr_excerpt:
            evidence_parts.append(f"stderr={stderr_excerpt}")
        if output_paths:
            evidence_parts.append(f"outputs={','.join(output_paths)}")

        entries.append(
            {
                "entry_id": f"tool_call:{name.replace(' ', '-').replace('/', '-')}",
                "finding_family": "tool_call",
                "kind": str(raw_entry.get("kind", "tool_call_result")),
                "name": name,
                "observed_bucket": observed_bucket,
                "evidence": {
                    "doc": [],
                    "code": [" | ".join(evidence_parts)] if evidence_parts else [],
                },
                "trace_status": trace_status,
                "action": str(raw_entry.get("action", "tool call result 검토")),
                "reason": reason,
                "tool_call": {
                    "tool_name": tool_name,
                    "command": command,
                    "args": args,
                    "cwd": cwd,
                    "exit_code": exit_code,
                    "stdout_excerpt": stdout_excerpt,
                    "stderr_excerpt": stderr_excerpt,
                    "output_paths": output_paths,
                },
            }
        )

    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "evidence_ledger",
        "source_report": _relative_or_str(input_path),
        "source_report_type": "tool_call_manifest",
        "scope": "tool_call_evidence",
        "rule_kind": "tool_call",
        "pair": {"doc": None, "script": None},
        "entry_count": len(entries),
        "entries": entries,
    }


def render_evidence_ledger_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# evidence-trace-auditor evidence_ledger summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- source_report: `{payload['source_report']}`",
        f"- source_report_type: `{payload['source_report_type']}`",
        f"- entry_count: `{payload['entry_count']}`",
        "",
        "## Entries",
        "",
    ]
    for entry in payload["entries"]:
        lines.append(f"- `{entry['entry_id']}`")
        lines.append(f"  - finding_family: `{entry['finding_family']}`")
        lines.append(f"  - name: `{entry['name']}`")
        lines.append(f"  - observed_bucket: `{entry['observed_bucket']}`")
        lines.append(f"  - trace_status: `{entry['trace_status']}`")
        lines.append(f"  - doc_evidence_count: `{len(entry['evidence']['doc'])}`")
        lines.append(f"  - code_evidence_count: `{len(entry['evidence']['code'])}`")
    return "\n".join(lines) + "\n"


def _summarize_entry(entry: dict[str, object]) -> dict[str, object]:
    return {
        "entry_id": entry["entry_id"],
        "finding_family": entry["finding_family"],
        "kind": entry["kind"],
        "name": entry["name"],
        "observed_bucket": entry["observed_bucket"],
        "trace_status": entry["trace_status"],
        "action": entry["action"],
    }


def audit_support(
    ledger_path: Path,
    ledger: dict[str, object],
    diff_basis_path: Path,
    diff_basis: dict[str, object],
) -> dict[str, object]:
    if ledger.get("contract_family") != "evidence_ledger":
        _err("입력 artifact의 contract_family가 evidence_ledger가 아닙니다.")
    if diff_basis.get("contract_family") != "contract_diff_basis":
        _err("입력 artifact의 contract_family가 contract_diff_basis가 아닙니다.")

    recommended = set(diff_basis.get("recommended_diff_buckets", []))
    entries = ledger.get("entries", [])
    if not isinstance(entries, list):
        _err("evidence ledger entries 형식이 list가 아닙니다.")

    supported: list[dict[str, object]] = []
    missing_evidence: list[dict[str, object]] = []
    residual: list[dict[str, object]] = []

    for raw_entry in entries:
        if not isinstance(raw_entry, dict):
            _err("evidence ledger entry가 dict가 아닙니다.")
        entry = dict(raw_entry)
        has_evidence = bool(entry["evidence"]["doc"] or entry["evidence"]["code"])
        bucket = entry.get("observed_bucket")
        trace_status = entry.get("trace_status")
        if trace_status == "missing_evidence" or not has_evidence:
            missing_evidence.append(_summarize_entry(entry))
        elif trace_status == "residual_uncertainty":
            residual.append(_summarize_entry(entry))
        elif bucket is None or bucket not in recommended:
            residual.append(_summarize_entry(entry))
        else:
            supported.append(_summarize_entry(entry))

    entry_count = len(entries)
    return {
        "status": "ok",
        "generated_at": _now_iso(),
        "contract_family": "evidence_trace_audit",
        "input_evidence_ledger": _relative_or_str(ledger_path),
        "input_contract_diff_basis": _relative_or_str(diff_basis_path),
        "entry_count": entry_count,
        "recommended_diff_buckets": list(diff_basis.get("recommended_diff_buckets", [])),
        "supported_count": len(supported),
        "missing_evidence_count": len(missing_evidence),
        "residual_uncertainty_count": len(residual),
        "support_ratio": (len(supported) / entry_count) if entry_count else 0.0,
        "supported_entries": supported,
        "missing_evidence_entries": missing_evidence,
        "residual_uncertainty_entries": residual,
    }


def render_support_audit_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# evidence-trace-auditor support audit summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- input_evidence_ledger: `{payload['input_evidence_ledger']}`",
        f"- input_contract_diff_basis: `{payload['input_contract_diff_basis']}`",
        f"- entry_count: `{payload['entry_count']}`",
        f"- supported_count: `{payload['supported_count']}`",
        f"- missing_evidence_count: `{payload['missing_evidence_count']}`",
        f"- residual_uncertainty_count: `{payload['residual_uncertainty_count']}`",
        f"- support_ratio: `{payload['support_ratio']}`",
        "",
        "## Recommended Diff Buckets",
        "",
    ]
    for bucket in payload["recommended_diff_buckets"]:
        lines.append(f"- `{bucket}`")

    lines.extend(["", "## Supported Entries", ""])
    for entry in payload["supported_entries"]:
        lines.append(f"- `{entry['entry_id']}` -> `{entry['observed_bucket']}`")

    lines.extend(["", "## Missing Evidence Entries", ""])
    for entry in payload["missing_evidence_entries"]:
        lines.append(f"- `{entry['entry_id']}`")

    lines.extend(["", "## Residual Uncertainty Entries", ""])
    for entry in payload["residual_uncertainty_entries"]:
        lines.append(f"- `{entry['entry_id']}` -> `{entry['observed_bucket']}`")

    return "\n".join(lines) + "\n"


def cmd_build_evidence_ledger(args: argparse.Namespace) -> int:
    input_path = Path(args.input_report)
    payload = _load_json(input_path)
    ledger = build_evidence_ledger(input_path, payload)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_evidence_ledger_markdown(ledger), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_build_test_result_ledger(args: argparse.Namespace) -> int:
    input_path = Path(args.input_junit_xml)
    if not input_path.is_file():
        _err(f"JUnit XML 파일이 없습니다: {input_path}")
    ledger = build_test_result_ledger(input_path)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_evidence_ledger_markdown(ledger), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_build_log_evidence_ledger(args: argparse.Namespace) -> int:
    input_path = Path(args.input_log_jsonl)
    if not input_path.is_file():
        _err(f"log JSONL 파일이 없습니다: {input_path}")
    ledger = build_log_evidence_ledger(input_path)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_evidence_ledger_markdown(ledger), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_build_artifact_path_ledger(args: argparse.Namespace) -> int:
    input_path = Path(args.input_manifest)
    manifest = _load_json(input_path)
    ledger = build_artifact_path_ledger(input_path, manifest)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_evidence_ledger_markdown(ledger), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_build_attestation_ledger(args: argparse.Namespace) -> int:
    input_path = Path(args.input_attestation_manifest)
    manifest = _load_json(input_path)
    ledger = build_attestation_ledger(input_path, manifest)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_evidence_ledger_markdown(ledger), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_build_tool_call_ledger(args: argparse.Namespace) -> int:
    input_path = Path(args.input_tool_call_manifest)
    manifest = _load_json(input_path)
    ledger = build_tool_call_ledger(input_path, manifest)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(ledger, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_evidence_ledger_markdown(ledger), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def cmd_audit_support(args: argparse.Namespace) -> int:
    ledger_path = Path(args.evidence_ledger)
    diff_basis_path = Path(args.contract_diff_basis)
    ledger = _load_json(ledger_path)
    diff_basis = _load_json(diff_basis_path)
    audit = audit_support(ledger_path, ledger, diff_basis_path, diff_basis)

    if args.output_json:
        output_json = Path(args.output_json)
        output_json.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON artifact written: {output_json}", file=sys.stderr)
    else:
        print(json.dumps(audit, indent=2, ensure_ascii=False))

    if args.output_md:
        output_md = Path(args.output_md)
        output_md.write_text(render_support_audit_markdown(audit), encoding="utf-8")
        print(f"[INFO] Markdown summary written: {output_md}", file=sys.stderr)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Normalize runtime evidence and audit it against contract-aware diff buckets."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ledger_parser = subparsers.add_parser(
        "build-evidence-ledger",
        help="Convert a raw smoke report into a machine-readable evidence ledger.",
    )
    ledger_parser.add_argument("--input-report", required=True, help="Path to raw smoke report JSON artifact.")
    ledger_parser.add_argument("--output-json", help="Optional output path for evidence ledger JSON.")
    ledger_parser.add_argument("--output-md", help="Optional output path for evidence ledger markdown summary.")
    ledger_parser.set_defaults(func=cmd_build_evidence_ledger)

    test_parser = subparsers.add_parser(
        "build-test-result-ledger",
        help="Convert a JUnit XML test result into a machine-readable evidence ledger.",
    )
    test_parser.add_argument("--input-junit-xml", required=True, help="Path to JUnit XML report.")
    test_parser.add_argument("--output-json", help="Optional output path for evidence ledger JSON.")
    test_parser.add_argument("--output-md", help="Optional output path for evidence ledger markdown summary.")
    test_parser.set_defaults(func=cmd_build_test_result_ledger)

    log_parser = subparsers.add_parser(
        "build-log-evidence-ledger",
        help="Convert JSONL log records into a machine-readable evidence ledger.",
    )
    log_parser.add_argument("--input-log-jsonl", required=True, help="Path to JSONL log file.")
    log_parser.add_argument("--output-json", help="Optional output path for evidence ledger JSON.")
    log_parser.add_argument("--output-md", help="Optional output path for evidence ledger markdown summary.")
    log_parser.set_defaults(func=cmd_build_log_evidence_ledger)

    artifact_parser = subparsers.add_parser(
        "build-artifact-path-ledger",
        help="Convert an artifact path manifest into a machine-readable evidence ledger.",
    )
    artifact_parser.add_argument("--input-manifest", required=True, help="Path to artifact path manifest JSON.")
    artifact_parser.add_argument("--output-json", help="Optional output path for evidence ledger JSON.")
    artifact_parser.add_argument("--output-md", help="Optional output path for evidence ledger markdown summary.")
    artifact_parser.set_defaults(func=cmd_build_artifact_path_ledger)

    attestation_parser = subparsers.add_parser(
        "build-attestation-ledger",
        help="Convert an attestation manifest into a machine-readable evidence ledger.",
    )
    attestation_parser.add_argument(
        "--input-attestation-manifest",
        required=True,
        help="Path to attestation manifest JSON.",
    )
    attestation_parser.add_argument("--output-json", help="Optional output path for evidence ledger JSON.")
    attestation_parser.add_argument("--output-md", help="Optional output path for evidence ledger markdown summary.")
    attestation_parser.set_defaults(func=cmd_build_attestation_ledger)

    tool_call_parser = subparsers.add_parser(
        "build-tool-call-ledger",
        help="Convert a tool call manifest into a machine-readable evidence ledger.",
    )
    tool_call_parser.add_argument(
        "--input-tool-call-manifest",
        required=True,
        help="Path to tool call manifest JSON.",
    )
    tool_call_parser.add_argument("--output-json", help="Optional output path for evidence ledger JSON.")
    tool_call_parser.add_argument("--output-md", help="Optional output path for evidence ledger markdown summary.")
    tool_call_parser.set_defaults(func=cmd_build_tool_call_ledger)

    audit_parser = subparsers.add_parser(
        "audit-support",
        help="Audit evidence ledger entries against a contract_diff_basis artifact.",
    )
    audit_parser.add_argument("--evidence-ledger", required=True, help="Path to evidence ledger JSON artifact.")
    audit_parser.add_argument("--contract-diff-basis", required=True, help="Path to contract_diff_basis JSON artifact.")
    audit_parser.add_argument("--output-json", help="Optional output path for support audit JSON.")
    audit_parser.add_argument("--output-md", help="Optional output path for support audit markdown summary.")
    audit_parser.set_defaults(func=cmd_audit_support)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
