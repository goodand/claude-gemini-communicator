#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("pipeline_router.py")


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=True,
    )


class PipelineRouterTests(unittest.TestCase):
    def test_md_target_routes_to_document_branch(self) -> None:
        result = run_cli("--target", "notes.md")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["branch"], "document_output")
        self.assertFalse(payload["tdd_required"])
        self.assertIsNone(payload["execution_evidence_handoff"])
        self.assertIsNone(payload["baseline_diff_handoff"])

    def test_script_target_routes_to_script_branch(self) -> None:
        result = run_cli("--target", "scripts/tool.py")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["branch"], "script_output")
        self.assertTrue(payload["tdd_required"])
        self.assertEqual(payload["execution_evidence_handoff"]["target_skill"], "evidence-trace-auditor")
        self.assertIn("build evidence ledger", payload["execution_evidence_handoff"]["sequence"][1])
        self.assertEqual(payload["baseline_diff_handoff"]["target_skill"], "baseline-diff-lab")
        self.assertIn("metricize", payload["baseline_diff_handoff"]["sequence"][0])
        self.assertIn("TDD 파일 생성", payload["next_actions"])
        self.assertIn("debug 메모 작성", payload["next_actions"])
        self.assertIn("evidence ledger/support audit 계산", payload["next_actions"])
        self.assertIn("raw smoke면 metricize 후 before/after diff 작성", payload["next_actions"])

    def test_non_md_target_routes_to_implementation_branch(self) -> None:
        result = run_cli("--target", "schema.json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["branch"], "implementation_output")
        self.assertTrue(payload["tdd_required"])
        self.assertEqual(payload["execution_evidence_handoff"]["planner_script"], "../skill-creation-process/scripts/execution_evidence_planner.py")
        self.assertEqual(payload["baseline_diff_handoff"]["target_skill"], "baseline-diff-lab")


if __name__ == "__main__":
    unittest.main()
