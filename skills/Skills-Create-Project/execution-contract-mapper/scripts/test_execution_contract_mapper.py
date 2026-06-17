#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("execution_contract_mapper.py")


CHECKLIST_TEXT = """# Example Consistency Checklist

> 목적: test
> source of truth: `knowledge_bases/example.md`

## A. Identity

- [ ] 이 skill의 핵심 목적이 고정돼 있다
- [ ] 중간층 역할이 정의돼 있다

## B. Boundary

- [ ] 후행 책임이 분리돼 있다
"""


class ExecutionContractMapperTest(unittest.TestCase):
    def test_map_rule_schema_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checklist = Path(tmpdir) / "consistency.md"
            checklist.write_text(CHECKLIST_TEXT, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "map-rule-schema", "--checklist", str(checklist)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "rule_schema")
            self.assertEqual(payload["rule_count"], 3)
            self.assertEqual(payload["source_of_truth"], "`knowledge_bases/example.md`")
            self.assertEqual(payload["rules"][0]["kind"], "rule_schema")
            self.assertIn("identity__", payload["rules"][0]["name"])

    def test_map_rule_schema_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checklist = Path(tmpdir) / "consistency.md"
            output_json = Path(tmpdir) / "rules.json"
            output_md = Path(tmpdir) / "rules.md"
            checklist.write_text(CHECKLIST_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "map-rule-schema",
                    "--checklist",
                    str(checklist),
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
            self.assertEqual(payload["rule_count"], 3)
            self.assertIn("execution-contract-mapper rule_schema summary", summary)
            self.assertIn("중간층 역할이 정의돼 있다", summary)

    def test_help_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("map-rule-schema", result.stdout)
        self.assertIn("emit-schema-contract", result.stdout)
        self.assertIn("emit-cli-contract", result.stdout)
        self.assertIn("emit-contract-diff-basis", result.stdout)

    def test_missing_rule_items_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checklist = Path(tmpdir) / "empty.md"
            checklist.write_text("# Empty\n\n## A. Identity\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "map-rule-schema", "--checklist", str(checklist)],
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("rule_schema item", result.stderr)

    def test_emit_schema_contract_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checklist = Path(tmpdir) / "consistency.md"
            rule_json = Path(tmpdir) / "rules.json"
            checklist.write_text(CHECKLIST_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "map-rule-schema",
                    "--checklist",
                    str(checklist),
                    "--output-json",
                    str(rule_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), "emit-schema-contract", "--rule-schema", str(rule_json)],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "schema_contract")
            self.assertEqual(payload["source_contract_family"], "rule_schema")
            self.assertEqual(payload["schema"]["properties"]["contract_family"]["const"], "rule_schema")
            self.assertIn("rules", payload["schema"]["required"])

    def test_emit_schema_contract_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checklist = Path(tmpdir) / "consistency.md"
            rule_json = Path(tmpdir) / "rules.json"
            schema_json = Path(tmpdir) / "schema.json"
            schema_md = Path(tmpdir) / "schema.md"
            checklist.write_text(CHECKLIST_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "map-rule-schema",
                    "--checklist",
                    str(checklist),
                    "--output-json",
                    str(rule_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-schema-contract",
                    "--rule-schema",
                    str(rule_json),
                    "--output-json",
                    str(schema_json),
                    "--output-md",
                    str(schema_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(schema_json.read_text(encoding="utf-8"))
            summary = schema_md.read_text(encoding="utf-8")
            self.assertEqual(payload["schema_name"], "ExecutionContractMapperRuleSchemaArtifact")
            self.assertIn("Required Fields", summary)
            self.assertIn("contract_family", summary)

    def test_emit_cli_contract_stdout_json(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "emit-cli-contract"],
            check=True,
            capture_output=True,
            text=True,
        )

        payload = json.loads(result.stdout)
        self.assertEqual(payload["contract_family"], "cli_contract")
        self.assertGreaterEqual(payload["subcommand_count"], 3)
        names = {item["name"] for item in payload["subcommands"]}
        self.assertIn("map-rule-schema", names)
        self.assertIn("emit-schema-contract", names)
        self.assertIn("emit-cli-contract", names)

    def test_emit_cli_contract_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_json = Path(tmpdir) / "cli.json"
            output_md = Path(tmpdir) / "cli.md"

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-cli-contract",
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
            self.assertEqual(payload["contract_family"], "cli_contract")
            self.assertIn("Subcommands", summary)
            self.assertIn("emit-cli-contract", summary)

    def test_emit_contract_diff_basis_stdout_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checklist = Path(tmpdir) / "consistency.md"
            rule_json = Path(tmpdir) / "rules.json"
            schema_json = Path(tmpdir) / "schema.json"
            cli_json = Path(tmpdir) / "cli.json"
            checklist.write_text(CHECKLIST_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "map-rule-schema",
                    "--checklist",
                    str(checklist),
                    "--output-json",
                    str(rule_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-schema-contract",
                    "--rule-schema",
                    str(rule_json),
                    "--output-json",
                    str(schema_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-cli-contract",
                    "--output-json",
                    str(cli_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-contract-diff-basis",
                    "--rule-schema",
                    str(rule_json),
                    "--schema-contract",
                    str(schema_json),
                    "--cli-contract",
                    str(cli_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(result.stdout)
            self.assertEqual(payload["contract_family"], "contract_diff_basis")
            self.assertEqual(payload["basis_count"], 3)
            self.assertEqual(payload["compare_order"], ["rule_schema", "schema_contract", "cli_contract"])
            families = {item["contract_family"] for item in payload["diff_bases"]}
            self.assertEqual(families, {"rule_schema", "schema_contract", "cli_contract"})
            self.assertIn("requiredness_changed", payload["recommended_diff_buckets"])

    def test_emit_contract_diff_basis_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            checklist = Path(tmpdir) / "consistency.md"
            rule_json = Path(tmpdir) / "rules.json"
            schema_json = Path(tmpdir) / "schema.json"
            cli_json = Path(tmpdir) / "cli.json"
            diff_json = Path(tmpdir) / "diff-basis.json"
            diff_md = Path(tmpdir) / "diff-basis.md"
            checklist.write_text(CHECKLIST_TEXT, encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "map-rule-schema",
                    "--checklist",
                    str(checklist),
                    "--output-json",
                    str(rule_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-schema-contract",
                    "--rule-schema",
                    str(rule_json),
                    "--output-json",
                    str(schema_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-cli-contract",
                    "--output-json",
                    str(cli_json),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "emit-contract-diff-basis",
                    "--rule-schema",
                    str(rule_json),
                    "--schema-contract",
                    str(schema_json),
                    "--cli-contract",
                    str(cli_json),
                    "--output-json",
                    str(diff_json),
                    "--output-md",
                    str(diff_md),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            payload = json.loads(diff_json.read_text(encoding="utf-8"))
            summary = diff_md.read_text(encoding="utf-8")
            self.assertEqual(payload["contract_family"], "contract_diff_basis")
            self.assertIn("Recommended Diff Buckets", summary)
            self.assertIn("cli_argument_surface_changed", summary)


if __name__ == "__main__":
    unittest.main()
