#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("execution_evidence_planner.py")


class ExecutionEvidencePlannerTests(unittest.TestCase):
    def _write_file(self, path: Path, text: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_help_lists_required_flags(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--implementation-checklist", result.stdout)
        self.assertIn("--contract-diff-basis", result.stdout)
        self.assertIn("--target", result.stdout)

    def test_pre_execution_plan_points_to_smoke_then_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checklist = self._write_file(root / "implementation-checklist-at2026-03-17-04-03.md", "# impl\n")
            diff_basis = self._write_file(root / "contract-diff-basis-at2026-03-17-04-03.json", "{\"contract_family\":\"contract_diff_basis\"}\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--skill",
                    "execution-contract-mapper",
                    "--implementation-checklist",
                    str(checklist),
                    "--contract-diff-basis",
                    str(diff_basis),
                    "--target",
                    "dispatch path safety",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["stage"], "pre_execution")
            self.assertEqual(payload["experiment"], "dispatch-path-safety")
            self.assertEqual(payload["handoffs"][0]["target_skill"], "evidence-trace-auditor")
            self.assertEqual(payload["handoffs"][0]["when"], "after smoke")

    def test_post_smoke_plan_points_to_audit_now(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checklist = self._write_file(root / "implementation-checklist-at2026-03-17-04-03.md", "# impl\n")
            diff_basis = self._write_file(root / "contract-diff-basis-at2026-03-17-04-03.json", "{\"contract_family\":\"contract_diff_basis\"}\n")
            smoke = self._write_file(root / "dispatch-smoke-report-at2026-03-17-04-03.json", "{\"status\":\"ok\"}\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--skill",
                    "doc-code-sync-checker",
                    "--implementation-checklist",
                    str(checklist),
                    "--contract-diff-basis",
                    str(diff_basis),
                    "--target",
                    "dispatch smoke",
                    "--smoke",
                    str(smoke),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["stage"], "post_smoke")
            self.assertEqual(payload["handoffs"][0]["when"], "now")
            self.assertIn("support_audit_json", payload["suggested_outputs"])

    def test_ready_for_diff_adds_baseline_diff_handoff_and_metricize_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checklist = self._write_file(root / "implementation-checklist-at2026-03-17-04-03.md", "# impl\n")
            diff_basis = self._write_file(root / "contract-diff-basis-at2026-03-17-04-03.json", "{\"contract_family\":\"contract_diff_basis\"}\n")
            pre = self._write_file(root / "dispatch-pre-fix-smoke-report-at2026-03-17-04-03.json", "{\"status\":\"ok\"}\n")
            post = self._write_file(root / "dispatch-post-fix-smoke-report-at2026-03-17-04-03.json", "{\"status\":\"ok\"}\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--skill",
                    "doc-code-sync-checker",
                    "--implementation-checklist",
                    str(checklist),
                    "--contract-diff-basis",
                    str(diff_basis),
                    "--target",
                    "dispatch",
                    "--pre-fix",
                    str(pre),
                    "--post-fix",
                    str(post),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["stage"], "ready_for_diff")
            self.assertEqual(payload["handoffs"][1]["target_skill"], "baseline-diff-lab")
            self.assertIn("adapter", payload["handoffs"][1])
            self.assertIn("diff_json", payload["suggested_outputs"])
            self.assertTrue(any("metricize_smoke_report.py" in note for note in payload["notes"]))


if __name__ == "__main__":
    unittest.main()
