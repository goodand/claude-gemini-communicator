#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("diagnostic_audit.py")


GOOD_TEXT = """from __future__ import annotations

from pathlib import Path

VALUE = Path("x")
print(VALUE)
"""


UNUSED_TEXT = """import os
import sys

thing = 1
print("ok")
"""


LOADER_TEXT = """import importlib.util

spec = importlib.util.spec_from_file_location("m", "mod.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
"""


class DiagnosticAuditTest(unittest.TestCase):
    def test_help_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("audit", result.stdout)

    def test_audit_reports_clean_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "good.py"
            target.write_text(GOOD_TEXT, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "audit", "--target", str(target)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "ok")
            self.assertTrue(payload["runtime_gate"]["ok"])
            self.assertEqual(payload["finding_count"], 0)

    def test_audit_reports_unused_import_and_variable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "unused.py"
            target.write_text(UNUSED_TEXT, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "audit", "--target", str(target)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("unused_import", categories)
            self.assertIn("unused_variable", categories)

    def test_audit_reports_missing_loader_guard(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "loader.py"
            target.write_text(LOADER_TEXT, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "audit", "--target", str(target)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            categories = {finding["category"] for finding in payload["findings"]}
            self.assertIn("optional_loader_guard_missing", categories)

    def test_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            target = Path(tmpdir) / "unused.py"
            output_json = Path(tmpdir) / "audit.json"
            output_md = Path(tmpdir) / "audit.md"
            target.write_text(UNUSED_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "audit",
                    "--target",
                    str(target),
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
            self.assertEqual(payload["finding_count"], 3)
            self.assertIn("python-static-diagnostic-fixer audit summary", summary)


if __name__ == "__main__":
    unittest.main()
