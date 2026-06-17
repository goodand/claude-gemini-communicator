#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("baseline_diff_planner.py")


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


class BaselineDiffPlannerTests(unittest.TestCase):
    def test_plans_diff_outputs_in_references_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pre = root / "typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json"
            post = root / "typed-mismatch-enum-value-post-fix-smoke-report-at2026-03-16-22-48.json"
            pre.write_text("{}", encoding="utf-8")
            post.write_text("{}", encoding="utf-8")

            result = run_cli(
                "--skill",
                "doc-code-sync-checker",
                "--pre",
                str(pre),
                "--post",
                str(post),
                "--metric",
                "typed_mismatch_reduction_after_fix",
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["experiment"], "typed-mismatch-enum-value")
        self.assertTrue(payload["suggested_outputs"]["diff_json"].startswith("references/"))
        self.assertIn("compute delta and reduction metrics", payload["next_actions"])

    def test_accepts_debug_evidence_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pre = root / "pre.json"
            post = root / "post.json"
            debug = root / "debug.md"
            pre.write_text("{}", encoding="utf-8")
            post.write_text("{}", encoding="utf-8")
            debug.write_text("# debug", encoding="utf-8")

            result = run_cli(
                "--skill",
                "doc-code-sync-checker",
                "--pre",
                str(pre),
                "--post",
                str(post),
                "--debug",
                str(debug),
                "--metric",
                "coverage_ratio",
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["inputs"]["debug_evidence"], [str(debug)])
        self.assertEqual(payload["inputs"]["metrics"], ["coverage_ratio"])

    def test_missing_pre_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            post = root / "post.json"
            post.write_text("{}", encoding="utf-8")

            result = run_cli(
                "--skill",
                "doc-code-sync-checker",
                "--pre",
                str(root / "missing.json"),
                "--post",
                str(post),
                "--metric",
                "coverage_ratio",
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("pre-fix artifact 없음", result.stderr)


if __name__ == "__main__":
    unittest.main()
