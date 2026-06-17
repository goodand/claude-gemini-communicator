#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("metricize_smoke_report.py")


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


class MetricizeSmokeReportTests(unittest.TestCase):
    def test_metricizes_raw_smoke_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw = root / "raw.json"
            raw.write_text(
                json.dumps(
                    {
                        "scope": "pairwise_smoke_test",
                        "rule_kind": "enum_value",
                        "pair": {"doc": "doc", "script": "code"},
                        "missing_in_code": [{"name": "a"}],
                        "missing_in_doc": [{"name": "b"}],
                        "mismatch": [],
                        "typed_mismatch": [{"kind": "enum_value_set_changed"}],
                    }
                ),
                encoding="utf-8",
            )

            result = run_cli("--input", str(raw))
            payload = json.loads(result.stdout)

        self.assertEqual(payload["status"], "metricized")
        self.assertEqual(payload["metrics"]["missing_in_code_count"], 1)
        self.assertEqual(payload["metrics"]["missing_in_doc_count"], 1)
        self.assertEqual(payload["metrics"]["typed_mismatch_count"], 1)
        self.assertEqual(payload["metrics"]["total_finding_count"], 3)
        self.assertEqual(payload["metrics"]["zero_drift_pair_rate"], 0.0)

    def test_zero_drift_pair_rate_is_one_when_no_findings(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw = root / "raw.json"
            raw.write_text(
                json.dumps(
                    {
                        "missing_in_code": [],
                        "missing_in_doc": [],
                        "mismatch": [],
                        "typed_mismatch": [],
                    }
                ),
                encoding="utf-8",
            )

            result = run_cli("--input", str(raw))
            payload = json.loads(result.stdout)

        self.assertEqual(payload["metrics"]["total_finding_count"], 0)
        self.assertEqual(payload["metrics"]["zero_drift_pair_rate"], 1.0)

    def test_writes_output_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw = root / "raw.json"
            out = root / "metricized.json"
            raw.write_text(
                json.dumps(
                    {
                        "missing_in_code": [],
                        "missing_in_doc": [{"name": "x"}],
                        "mismatch": [],
                        "typed_mismatch": [],
                    }
                ),
                encoding="utf-8",
            )

            run_cli("--input", str(raw), "--output-json", str(out))
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertTrue(out.is_file())
            self.assertEqual(payload["metrics"]["missing_in_doc_count"], 1)


if __name__ == "__main__":
    unittest.main()
