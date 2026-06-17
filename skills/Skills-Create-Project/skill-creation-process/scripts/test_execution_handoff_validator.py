#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("execution_handoff_validator.py")


class ExecutionHandoffValidatorTests(unittest.TestCase):
    def _write_file(self, path: Path, text: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def _base_workspace(self, root: Path) -> None:
        self._write_file(
            root / "skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md",
            "# pattern\n",
        )
        self._write_file(root / "impl.md", "# impl\n")
        self._write_file(root / "basis.json", "{\"contract_family\":\"contract_diff_basis\"}\n")

    def _run_validator(self, workspace: Path, payload_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT_PATH),
                "--planner-payload",
                str(payload_path),
                "--workspace-root",
                str(workspace),
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_help_lists_planner_payload_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--planner-payload", result.stdout)
        self.assertIn("--workspace-root", result.stdout)

    def test_pre_execution_payload_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._base_workspace(root)
            payload = {
                "status": "planned",
                "skill": "execution-contract-mapper",
                "stage": "pre_execution",
                "target": "dispatch path safety",
                "experiment": "dispatch-path-safety",
                "inputs": {
                    "implementation_checklist": "impl.md",
                    "contract_diff_basis": "basis.json",
                    "smoke_artifacts": [],
                    "pre_fix": None,
                    "post_fix": None,
                    "metrics": [],
                },
                "suggested_outputs": {},
                "handoffs": [
                    {
                        "target_skill": "evidence-trace-auditor",
                        "when": "after smoke",
                        "entrypoint": "evidence-trace-auditor/scripts/evidence_trace_auditor.py",
                    }
                ],
                "next_actions": [],
                "notes": [],
                "pattern_doc": "skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md",
            }
            payload_path = self._write_file(root / "payload.json", json.dumps(payload))
            result = self._run_validator(root, payload_path)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "valid")

    def test_post_smoke_payload_requires_existing_smoke_and_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._base_workspace(root)
            self._write_file(root / "smoke.json", "{\"status\":\"ok\"}\n")
            payload = {
                "status": "planned",
                "skill": "doc-code-sync-checker",
                "stage": "post_smoke",
                "target": "doc-code-sync path rule",
                "experiment": "typed-mismatch-path-rule",
                "inputs": {
                    "implementation_checklist": "impl.md",
                    "contract_diff_basis": "basis.json",
                    "smoke_artifacts": ["smoke.json"],
                    "pre_fix": None,
                    "post_fix": None,
                    "metrics": [],
                },
                "suggested_outputs": {
                    "evidence_ledger_json": "references/x.json",
                    "evidence_ledger_md": "references/x.md",
                    "support_audit_json": "references/y.json",
                    "support_audit_md": "references/y.md",
                },
                "handoffs": [
                    {
                        "target_skill": "evidence-trace-auditor",
                        "when": "now",
                        "entrypoint": "evidence-trace-auditor/scripts/evidence_trace_auditor.py",
                    }
                ],
                "next_actions": [],
                "notes": [],
                "pattern_doc": "skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md",
            }
            payload_path = self._write_file(root / "payload.json", json.dumps(payload))
            result = self._run_validator(root, payload_path)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "valid")

    def test_ready_for_diff_raw_smoke_requires_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._base_workspace(root)
            self._write_file(root / "pre.json", "{\"status\":\"ok\"}\n")
            self._write_file(root / "post.json", "{\"status\":\"ok\"}\n")
            payload = {
                "status": "planned",
                "skill": "doc-code-sync-checker",
                "stage": "ready_for_diff",
                "target": "doc-code-sync path rule",
                "experiment": "typed-mismatch-path-rule",
                "inputs": {
                    "implementation_checklist": "impl.md",
                    "contract_diff_basis": "basis.json",
                    "smoke_artifacts": [],
                    "pre_fix": "pre.json",
                    "post_fix": "post.json",
                    "metrics": [],
                },
                "suggested_outputs": {
                    "diff_json": "references/diff.json",
                    "diff_md": "references/diff.md",
                },
                "handoffs": [
                    {"target_skill": "evidence-trace-auditor", "when": "now"},
                    {
                        "target_skill": "baseline-diff-lab",
                        "when": "now",
                        "entrypoint": "baseline-diff-lab/scripts/baseline_diff_planner.py",
                    },
                ],
                "next_actions": [],
                "notes": [],
                "pattern_doc": "skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md",
            }
            payload_path = self._write_file(root / "payload.json", json.dumps(payload))
            result = self._run_validator(root, payload_path)
            self.assertNotEqual(result.returncode, 0)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "invalid")
            self.assertTrue(any("adapter" in error for error in report["errors"]))

    def test_ready_for_diff_metric_artifacts_do_not_require_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._base_workspace(root)
            self._write_file(root / "pre.json", "{\"metrics\":{\"typed_mismatch_count\":1}}\n")
            self._write_file(root / "post.json", "{\"metrics\":{\"typed_mismatch_count\":0}}\n")
            payload = {
                "status": "planned",
                "skill": "doc-code-sync-checker",
                "stage": "ready_for_diff",
                "target": "doc-code-sync path rule",
                "experiment": "typed-mismatch-path-rule",
                "inputs": {
                    "implementation_checklist": "impl.md",
                    "contract_diff_basis": "basis.json",
                    "smoke_artifacts": [],
                    "pre_fix": "pre.json",
                    "post_fix": "post.json",
                    "metrics": [],
                },
                "suggested_outputs": {
                    "diff_json": "references/diff.json",
                    "diff_md": "references/diff.md",
                },
                "handoffs": [
                    {"target_skill": "evidence-trace-auditor", "when": "now"},
                    {
                        "target_skill": "baseline-diff-lab",
                        "when": "now",
                        "entrypoint": "baseline-diff-lab/scripts/baseline_diff_planner.py",
                    },
                ],
                "next_actions": [],
                "notes": [],
                "pattern_doc": "skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md",
            }
            payload_path = self._write_file(root / "payload.json", json.dumps(payload))
            result = self._run_validator(root, payload_path)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "valid")


if __name__ == "__main__":
    unittest.main()
