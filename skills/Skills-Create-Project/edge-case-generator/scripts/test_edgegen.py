#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("edgegen.py")


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=True,
    )


SAMPLE_VALIDATE_SCRIPT = """\
REQUIRED_FIELDS = {"task_id", "goal"}
VALID_STATUS = {"queued", "running"}

def validate_sample(data):
    errors = []
    warnings = []
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        errors.append("missing")
    if data.get("status") not in VALID_STATUS:
        errors.append("bad status")
    if len(str(data.get("goal", "")).strip()) < 3:
        errors.append("goal short")
    if "locked_paths" in data:
        for p in data["locked_paths"]:
            ps = str(p)
            if ".." in ps:
                errors.append("traversal")
            if ps.startswith("/"):
                errors.append("absolute")
    return errors, warnings
"""


class EdgegenCliTests(unittest.TestCase):
    def test_analyze_extracts_expected_rule_types(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "sample_validate.py"
            target.write_text(SAMPLE_VALIDATE_SCRIPT, encoding="utf-8")

            result = run_cli("analyze", "--script", str(target))
            payload = json.loads(result.stdout)

        rule_types = {rule["type"] for rule in payload["rules"]}
        self.assertIn("required_field", rule_types)
        self.assertIn("enum_value", rule_types)
        self.assertIn("string_length", rule_types)
        self.assertIn("path_safety", rule_types)

    def test_generate_writes_cases_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            target = root / "sample_validate.py"
            output_dir = root / "edge_cases"
            target.write_text(SAMPLE_VALIDATE_SCRIPT, encoding="utf-8")

            result = run_cli("generate", "--script", str(target), "--output", str(output_dir))
            summary = json.loads((output_dir / "cases_summary.json").read_text(encoding="utf-8"))

        self.assertIn("[OK]", result.stdout)
        self.assertGreater(summary["rules_count"], 0)
        self.assertGreater(summary["cases_count"], 0)
        self.assertIn("baseline_input", summary)

    def test_report_prints_unexpected_case_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            results = root / "run_results.json"
            results.write_text(
                json.dumps(
                    {
                        "script": "sample_validate.py",
                        "validate_func": "validate_sample",
                        "run_at": "2026-03-17T00:00:00+09:00",
                        "total": 2,
                        "ok": 1,
                        "results": [
                            {
                                "name": "case_ok",
                                "expected": "pass",
                                "actual": "pass",
                                "status": "OK",
                            },
                            {
                                "name": "case_bad",
                                "expected": "fail",
                                "actual": "pass",
                                "status": "UNEXPECTED",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = run_cli("report", "--results", str(results))

        self.assertIn("EDGE CASE REPORT", result.stdout)
        self.assertIn("case_bad", result.stdout)
        self.assertIn("실패해야 하는데 통과", result.stdout)


if __name__ == "__main__":
    unittest.main()
