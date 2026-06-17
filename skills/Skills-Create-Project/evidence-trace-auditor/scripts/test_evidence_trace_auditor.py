#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("evidence_trace_auditor.py")


RAW_SMOKE_TEXT = json.dumps(
    {
        "status": "implemented",
        "scope": "pairwise_smoke_test",
        "command": "compare",
        "rule_kind": "enum_value",
        "pair": {"doc": "synthetic-doc", "script": "synthetic-script"},
        "missing_in_code": [
            {
                "kind": "enum_value",
                "name": "status:ready",
                "doc_evidence": "doc ready",
                "action": "code align",
            }
        ],
        "missing_in_doc": [
            {
                "kind": "enum_value",
                "name": "status:running",
                "code_evidence": "code running",
                "action": "doc align",
            }
        ],
        "mismatch": [],
        "typed_mismatch": [
            {
                "kind": "enum_value_set_changed",
                "name": "status",
                "doc_evidence": ["doc queued", "doc ready"],
                "code_evidence": ["code queued", "code running"],
                "reason": "set changed",
                "action": "align set",
            }
        ],
    },
    ensure_ascii=False,
)


CONTRACT_DIFF_BASIS_TEXT = json.dumps(
    {
        "status": "ok",
        "contract_family": "contract_diff_basis",
        "recommended_diff_buckets": [
            "missing_contract_unit",
            "extra_contract_unit",
            "contract_value_changed",
            "requiredness_changed",
            "cli_argument_surface_changed",
        ],
    },
    ensure_ascii=False,
)

JUNIT_XML_TEXT = """<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="example" tests="3" failures="1" skipped="1">
  <testcase classname="sync" name="test_ok" time="0.01" />
  <testcase classname="sync" name="test_failed" time="0.02">
    <failure message="expected drift to close">Traceback...</failure>
  </testcase>
  <testcase classname="sync" name="test_skipped" time="0.00">
    <skipped message="fixture not ready" />
  </testcase>
</testsuite>
"""

LOG_JSONL_TEXT = """{"timestamp":"2026-03-17T02:08:00+09:00","severity_text":"ERROR","body":"missing contract unit detected","attributes":{"name":"status:ready","kind":"log_record","observed_bucket":"missing_contract_unit","action":"log/code alignment 검토","reason":"missing enum value in code"}}
{"timestamp":"2026-03-17T02:08:01+09:00","severity_text":"WARN","body":"contract value changed detected","attributes":{"name":"status","kind":"log_record","observed_bucket":"contract_value_changed","action":"value set alignment 검토","reason":"enum set changed"}}"""

ATTESTATION_MANIFEST = {
    "entries": [
        {
            "name": "verified-step",
            "tool_name": "python3",
            "command": "python3 scripts/run.py --ok",
            "cwd": "/tmp/example",
            "actor": "codex",
            "exit_code": 0,
            "output_paths": [],
            "observed_bucket": "contract_value_changed",
            "reason": "no outputs yet",
            "action": "attestation 검토",
        }
    ]
}


class EvidenceTraceAuditorTest(unittest.TestCase):
    def test_help_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("build-evidence-ledger", result.stdout)
        self.assertIn("build-test-result-ledger", result.stdout)
        self.assertIn("build-log-evidence-ledger", result.stdout)
        self.assertIn("build-artifact-path-ledger", result.stdout)
        self.assertIn("build-attestation-ledger", result.stdout)
        self.assertIn("build-tool-call-ledger", result.stdout)
        self.assertIn("audit-support", result.stdout)

    def test_build_evidence_ledger_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            smoke_path = Path(tmpdir) / "raw.json"
            smoke_path.write_text(RAW_SMOKE_TEXT, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "build-evidence-ledger", "--input-report", str(smoke_path)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "evidence_ledger")
            self.assertEqual(payload["entry_count"], 3)
            self.assertEqual(payload["entries"][0]["trace_status"], "verified_evidence")
            buckets = {entry["observed_bucket"] for entry in payload["entries"]}
            self.assertIn("missing_contract_unit", buckets)
            self.assertIn("extra_contract_unit", buckets)
            self.assertIn("contract_value_changed", buckets)

    def test_build_evidence_ledger_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            smoke_path = Path(tmpdir) / "raw.json"
            output_json = Path(tmpdir) / "ledger.json"
            output_md = Path(tmpdir) / "ledger.md"
            smoke_path.write_text(RAW_SMOKE_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-evidence-ledger",
                    "--input-report",
                    str(smoke_path),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            summary = output_md.read_text(encoding="utf-8")
            self.assertEqual(payload["entry_count"], 3)
            self.assertIn("evidence_ledger summary", summary)
            self.assertIn("missing_contract_unit", summary)

    def test_audit_support_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            smoke_path = Path(tmpdir) / "raw.json"
            ledger_json = Path(tmpdir) / "ledger.json"
            basis_json = Path(tmpdir) / "basis.json"
            smoke_path.write_text(RAW_SMOKE_TEXT, encoding="utf-8")
            basis_json.write_text(CONTRACT_DIFF_BASIS_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-evidence-ledger",
                    "--input-report",
                    str(smoke_path),
                    "--output-json",
                    str(ledger_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "audit-support",
                    "--evidence-ledger",
                    str(ledger_json),
                    "--contract-diff-basis",
                    str(basis_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "evidence_trace_audit")
            self.assertEqual(payload["supported_count"], 3)
            self.assertEqual(payload["missing_evidence_count"], 0)
            self.assertEqual(payload["residual_uncertainty_count"], 0)
            self.assertEqual(payload["support_ratio"], 1.0)

    def test_audit_support_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            smoke_path = Path(tmpdir) / "raw.json"
            ledger_json = Path(tmpdir) / "ledger.json"
            basis_json = Path(tmpdir) / "basis.json"
            audit_json = Path(tmpdir) / "audit.json"
            audit_md = Path(tmpdir) / "audit.md"
            smoke_path.write_text(RAW_SMOKE_TEXT, encoding="utf-8")
            basis_json.write_text(CONTRACT_DIFF_BASIS_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-evidence-ledger",
                    "--input-report",
                    str(smoke_path),
                    "--output-json",
                    str(ledger_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "audit-support",
                    "--evidence-ledger",
                    str(ledger_json),
                    "--contract-diff-basis",
                    str(basis_json),
                    "--output-json",
                    str(audit_json),
                    "--output-md",
                    str(audit_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(audit_json.read_text(encoding="utf-8"))
            summary = audit_md.read_text(encoding="utf-8")
            self.assertEqual(payload["supported_count"], 3)
            self.assertIn("support audit summary", summary)
            self.assertIn("supported_count", summary)

    def test_build_test_result_ledger_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "junit.xml"
            xml_path.write_text(JUNIT_XML_TEXT, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "build-test-result-ledger", "--input-junit-xml", str(xml_path)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "evidence_ledger")
            self.assertEqual(payload["source_report_type"], "junit_xml")
            self.assertEqual(payload["entry_count"], 2)
            names = {entry["name"] for entry in payload["entries"]}
            self.assertIn("sync::test_failed", names)
            self.assertIn("sync::test_skipped", names)

    def test_build_test_result_ledger_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "junit.xml"
            output_json = Path(tmpdir) / "ledger.json"
            output_md = Path(tmpdir) / "ledger.md"
            xml_path.write_text(JUNIT_XML_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-test-result-ledger",
                    "--input-junit-xml",
                    str(xml_path),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            summary = output_md.read_text(encoding="utf-8")
            self.assertEqual(payload["entry_count"], 2)
            self.assertIn("junit_xml", payload["source_report_type"])
            self.assertIn("sync::test_failed", summary)

    def test_build_log_evidence_ledger_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "events.jsonl"
            log_path.write_text(LOG_JSONL_TEXT, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "build-log-evidence-ledger", "--input-log-jsonl", str(log_path)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "evidence_ledger")
            self.assertEqual(payload["source_report_type"], "jsonl_log")
            self.assertEqual(payload["entry_count"], 2)
            buckets = {entry["observed_bucket"] for entry in payload["entries"]}
            self.assertEqual(buckets, {"missing_contract_unit", "contract_value_changed"})

    def test_build_log_evidence_ledger_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "events.jsonl"
            output_json = Path(tmpdir) / "ledger.json"
            output_md = Path(tmpdir) / "ledger.md"
            log_path.write_text(LOG_JSONL_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-log-evidence-ledger",
                    "--input-log-jsonl",
                    str(log_path),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            summary = output_md.read_text(encoding="utf-8")
            self.assertEqual(payload["entry_count"], 2)
            self.assertIn("jsonl_log", payload["source_report_type"])
            self.assertIn("status:ready", summary)

    def test_build_artifact_path_ledger_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir) / "exists.json"
            existing.write_text("{}", encoding="utf-8")
            missing = Path(tmpdir) / "missing.json"
            manifest = Path(tmpdir) / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "name": "existing-artifact",
                                "path": str(existing),
                                "kind": "artifact_path",
                                "observed_bucket": "contract_value_changed",
                                "required": True,
                                "action": "existing artifact 확인",
                            },
                            {
                                "name": "missing-artifact",
                                "path": str(missing),
                                "kind": "artifact_path",
                                "observed_bucket": "missing_contract_unit",
                                "required": True,
                                "action": "missing artifact 생성 검토",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "build-artifact-path-ledger", "--input-manifest", str(manifest)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "evidence_ledger")
            self.assertEqual(payload["source_report_type"], "artifact_path_manifest")
            self.assertEqual(payload["entry_count"], 2)
            statuses = {entry["trace_status"] for entry in payload["entries"]}
            self.assertEqual(statuses, {"verified_evidence", "missing_evidence"})

    def test_build_artifact_path_ledger_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            existing = Path(tmpdir) / "exists.md"
            existing.write_text("ok", encoding="utf-8")
            manifest = Path(tmpdir) / "manifest.json"
            output_json = Path(tmpdir) / "ledger.json"
            output_md = Path(tmpdir) / "ledger.md"
            manifest.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "name": "existing-md",
                                "path": str(existing),
                                "kind": "artifact_path",
                                "observed_bucket": "extra_contract_unit",
                                "required": False,
                                "action": "markdown artifact 확인",
                            }
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-artifact-path-ledger",
                    "--input-manifest",
                    str(manifest),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            summary = output_md.read_text(encoding="utf-8")
            self.assertEqual(payload["entry_count"], 1)
            self.assertIn("artifact_path_manifest", payload["source_report_type"])
            self.assertIn("existing-md", summary)

    def test_build_attestation_ledger_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            verified = Path(tmpdir) / "verified.json"
            verified.write_text("{}", encoding="utf-8")
            missing = Path(tmpdir) / "missing.json"
            manifest = Path(tmpdir) / "attestation.json"
            manifest.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "name": "verified-step",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --ok",
                                "cwd": str(Path(tmpdir)),
                                "actor": "codex",
                                "exit_code": 0,
                                "output_paths": [str(verified)],
                                "observed_bucket": "contract_value_changed",
                                "action": "verified attestation 검토",
                            },
                            {
                                "name": "missing-output-step",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --missing",
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 0,
                                "output_paths": [str(missing)],
                                "observed_bucket": "missing_contract_unit",
                                "action": "missing output attestation 검토",
                            },
                            {
                                "name": "residual-step",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --uncertain",
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 1,
                                "output_paths": [],
                                "observed_bucket": "contract_value_changed",
                                "action": "residual attestation 검토",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "build-attestation-ledger", "--input-attestation-manifest", str(manifest)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "evidence_ledger")
            self.assertEqual(payload["source_report_type"], "attestation_manifest")
            self.assertEqual(payload["entry_count"], 3)
            statuses = {entry["trace_status"] for entry in payload["entries"]}
            self.assertEqual(statuses, {"verified_evidence", "missing_evidence", "residual_uncertainty"})

    def test_build_attestation_ledger_writes_json_and_markdown_and_audits(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            verified = Path(tmpdir) / "verified.json"
            verified.write_text("{}", encoding="utf-8")
            manifest = Path(tmpdir) / "attestation.json"
            ledger_json = Path(tmpdir) / "ledger.json"
            ledger_md = Path(tmpdir) / "ledger.md"
            basis_json = Path(tmpdir) / "basis.json"
            audit_json = Path(tmpdir) / "audit.json"
            audit_md = Path(tmpdir) / "audit.md"
            basis_json.write_text(CONTRACT_DIFF_BASIS_TEXT, encoding="utf-8")
            manifest.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "name": "verified-step",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --ok",
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 0,
                                "output_paths": [str(verified)],
                                "observed_bucket": "contract_value_changed",
                                "action": "verified attestation 검토",
                            },
                            {
                                "name": "residual-step",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --uncertain",
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 1,
                                "output_paths": [],
                                "observed_bucket": "contract_value_changed",
                                "action": "residual attestation 검토",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-attestation-ledger",
                    "--input-attestation-manifest",
                    str(manifest),
                    "--output-json",
                    str(ledger_json),
                    "--output-md",
                    str(ledger_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "audit-support",
                    "--evidence-ledger",
                    str(ledger_json),
                    "--contract-diff-basis",
                    str(basis_json),
                    "--output-json",
                    str(audit_json),
                    "--output-md",
                    str(audit_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(ledger_json.read_text(encoding="utf-8"))
            audit = json.loads(audit_json.read_text(encoding="utf-8"))
            summary = ledger_md.read_text(encoding="utf-8")
            self.assertEqual(payload["entry_count"], 2)
            self.assertIn("attestation_manifest", payload["source_report_type"])
            self.assertIn("verified-step", summary)
            self.assertEqual(audit["supported_count"], 1)
            self.assertEqual(audit["residual_uncertainty_count"], 1)

    def test_build_tool_call_ledger_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "validate.json"
            output_path.write_text("{}", encoding="utf-8")
            missing_output = Path(tmpdir) / "missing.json"
            manifest = Path(tmpdir) / "tool-call.json"
            manifest.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "name": "validated-rule-schema",
                                "tool_name": "python3",
                                "command": "python3 scripts/execution_contract_mapper.py emit-schema-contract",
                                "args": ["emit-schema-contract", "--rule-schema", "rule.json"],
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 0,
                                "stdout_excerpt": "schema contract emitted",
                                "output_paths": [str(output_path)],
                                "observed_bucket": "contract_value_changed",
                                "action": "tool call result 검토",
                            },
                            {
                                "name": "missing-output-call",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --missing",
                                "args": ["--missing"],
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 0,
                                "stdout_excerpt": "planned output missing",
                                "output_paths": [str(missing_output)],
                                "observed_bucket": "missing_contract_unit",
                                "action": "missing output call 검토",
                            },
                            {
                                "name": "failing-call",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --fail",
                                "args": ["--fail"],
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 1,
                                "stderr_excerpt": "traceback",
                                "observed_bucket": "contract_value_changed",
                                "action": "failing call 검토",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "build-tool-call-ledger", "--input-tool-call-manifest", str(manifest)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "evidence_ledger")
            self.assertEqual(payload["source_report_type"], "tool_call_manifest")
            self.assertEqual(payload["entry_count"], 3)
            statuses = {entry["trace_status"] for entry in payload["entries"]}
            self.assertEqual(statuses, {"verified_evidence", "missing_evidence", "residual_uncertainty"})

    def test_build_tool_call_ledger_writes_json_and_markdown_and_audits(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "validate.json"
            output_path.write_text("{}", encoding="utf-8")
            manifest = Path(tmpdir) / "tool-call.json"
            ledger_json = Path(tmpdir) / "ledger.json"
            ledger_md = Path(tmpdir) / "ledger.md"
            basis_json = Path(tmpdir) / "basis.json"
            audit_json = Path(tmpdir) / "audit.json"
            audit_md = Path(tmpdir) / "audit.md"
            basis_json.write_text(CONTRACT_DIFF_BASIS_TEXT, encoding="utf-8")
            manifest.write_text(
                json.dumps(
                    {
                        "entries": [
                            {
                                "name": "validated-rule-schema",
                                "tool_name": "python3",
                                "command": "python3 scripts/execution_contract_mapper.py emit-schema-contract",
                                "args": ["emit-schema-contract", "--rule-schema", "rule.json"],
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 0,
                                "stdout_excerpt": "schema contract emitted",
                                "output_paths": [str(output_path)],
                                "observed_bucket": "contract_value_changed",
                                "action": "validated tool call 검토",
                            },
                            {
                                "name": "failing-call",
                                "tool_name": "python3",
                                "command": "python3 scripts/run.py --fail",
                                "args": ["--fail"],
                                "cwd": str(Path(tmpdir)),
                                "exit_code": 1,
                                "stderr_excerpt": "traceback",
                                "observed_bucket": "contract_value_changed",
                                "action": "failing tool call 검토",
                            },
                        ]
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "build-tool-call-ledger",
                    "--input-tool-call-manifest",
                    str(manifest),
                    "--output-json",
                    str(ledger_json),
                    "--output-md",
                    str(ledger_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "audit-support",
                    "--evidence-ledger",
                    str(ledger_json),
                    "--contract-diff-basis",
                    str(basis_json),
                    "--output-json",
                    str(audit_json),
                    "--output-md",
                    str(audit_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(ledger_json.read_text(encoding="utf-8"))
            audit = json.loads(audit_json.read_text(encoding="utf-8"))
            summary = ledger_md.read_text(encoding="utf-8")
            self.assertEqual(payload["entry_count"], 2)
            self.assertIn("tool_call_manifest", payload["source_report_type"])
            self.assertIn("validated-rule-schema", summary)
            self.assertEqual(audit["supported_count"], 1)
            self.assertEqual(audit["residual_uncertainty_count"], 1)


    def test_noop_smoke_report_not_verified(self) -> None:
        """no-op 입력(모든 finding family 비어있음)은 verified로 분류되지 않는다.

        empty/no-op validator result must not be classified as verified_evidence.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            smoke_path = Path(tmpdir) / "noop.json"
            ledger_json = Path(tmpdir) / "ledger.json"
            basis_json = Path(tmpdir) / "basis.json"
            smoke_path.write_text(
                json.dumps(
                    {"missing_in_code": [], "missing_in_doc": [], "mismatch": [], "typed_mismatch": []},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            basis_json.write_text(CONTRACT_DIFF_BASIS_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable, str(SCRIPT_PATH), "build-evidence-ledger",
                    "--input-report", str(smoke_path), "--output-json", str(ledger_json),
                ],
                check=True, capture_output=True, text=True,
            )
            ledger = json.loads(ledger_json.read_text(encoding="utf-8"))
            self.assertEqual(ledger["entry_count"], 0)

            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT_PATH), "audit-support",
                    "--evidence-ledger", str(ledger_json), "--contract-diff-basis", str(basis_json),
                ],
                check=True, capture_output=True, text=True,
            )
            audit = json.loads(result.stdout)
            self.assertEqual(audit["supported_count"], 0)
            self.assertEqual(audit["support_ratio"], 0.0)

    def test_passing_only_junit_not_verified(self) -> None:
        """통과만 있는(no-op) 테스트 결과는 verified_evidence entry를 만들지 않는다."""
        passing_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<testsuite name="release" tests="2" failures="0" skipped="0">\n'
            '  <testcase classname="release" name="test_a" time="0.01" />\n'
            '  <testcase classname="release" name="test_b" time="0.01" />\n'
            '</testsuite>\n'
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            xml_path = Path(tmpdir) / "passing.xml"
            xml_path.write_text(passing_xml, encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable, str(SCRIPT_PATH), "build-test-result-ledger",
                    "--input-junit-xml", str(xml_path),
                ],
                check=True, capture_output=True, text=True,
            )
            payload = json.loads(result.stdout)
            self.assertEqual(payload["entry_count"], 0)
            statuses = {entry["trace_status"] for entry in payload["entries"]}
            self.assertNotIn("verified_evidence", statuses)


if __name__ == "__main__":
    unittest.main()
