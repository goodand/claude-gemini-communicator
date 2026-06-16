#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("baseline_diff_compute.py")


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


class BaselineDiffComputeTests(unittest.TestCase):
    def test_computes_delta_from_metric_objects(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pre = root / "pre.json"
            post = root / "post.json"
            pre.write_text(json.dumps({"metrics": {"coverage_ratio": {"value": 0.4}}}), encoding="utf-8")
            post.write_text(json.dumps({"metrics": {"coverage_ratio": {"value": 0.9}}}), encoding="utf-8")

            result = run_cli(
                "--pre",
                str(pre),
                "--post",
                str(post),
                "--metric",
                "coverage_ratio",
                "--experiment",
                "coverage-up",
            )
            payload = json.loads(result.stdout)

        entry = payload["metrics"]["coverage_ratio"]
        self.assertEqual(payload["status"], "computed")
        self.assertEqual(payload["experiment"], "coverage-up")
        self.assertEqual(entry["before"], 0.4)
        self.assertEqual(entry["after"], 0.9)
        self.assertEqual(entry["delta"], 0.5)

    def test_plan_input_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pre = root / "pre.json"
            post = root / "post.json"
            plan = root / "plan.json"
            diff_json = root / "references" / "exp-fix-diff.json"
            diff_md = root / "references" / "exp-fix-diff.md"
            pre.write_text(json.dumps({"metrics": {"typed_mismatch_reduction_after_fix": 1.0}}), encoding="utf-8")
            post.write_text(json.dumps({"metrics": {"typed_mismatch_reduction_after_fix": 0.0}}), encoding="utf-8")
            plan.write_text(
                json.dumps(
                    {
                        "experiment": "exp",
                        "inputs": {
                            "pre_fix": str(pre),
                            "post_fix": str(post),
                            "debug_evidence": [],
                            "metrics": ["typed_mismatch_reduction_after_fix"],
                        },
                        "suggested_outputs": {
                            "diff_json": str(diff_json),
                            "diff_md": str(diff_md),
                        },
                    }
                ),
                encoding="utf-8",
            )

            result = run_cli("--plan", str(plan))
            payload = json.loads(result.stdout)

            self.assertEqual(payload["status"], "computed")
            self.assertTrue(diff_json.is_file())
            self.assertTrue(diff_md.is_file())

    def test_missing_metric_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pre = root / "pre.json"
            post = root / "post.json"
            pre.write_text(json.dumps({"metrics": {"coverage_ratio": 1.0}}), encoding="utf-8")
            post.write_text(json.dumps({"metrics": {"coverage_ratio": 0.5}}), encoding="utf-8")

            result = run_cli(
                "--pre",
                str(pre),
                "--post",
                str(post),
                "--metric",
                "missing_metric",
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("metric 없음", result.stderr)


if __name__ == "__main__":
    unittest.main()
