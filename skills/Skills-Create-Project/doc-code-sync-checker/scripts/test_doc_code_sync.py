#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("doc_code_sync.py")
ROOT = Path(__file__).resolve().parents[2]
REAL_DOC = ROOT / "agent-task-packet" / "references" / "packet-fields.md"
REAL_CODE = ROOT / "agent-task-packet" / "scripts" / "packet_builder.py"
REAL_PATH_DOC = ROOT / "codex-worktree-dispatch" / "references" / "dispatch-fields.md"
REAL_PATH_CODE = ROOT / "codex-worktree-dispatch" / "scripts" / "dispatch_manager.py"


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=True,
    )


class DocCodeSyncCliTests(unittest.TestCase):
    maxDiff = None

    def test_help_lists_subcommands(self) -> None:
        result = run_cli("--help")
        self.assertIn("extract-doc", result.stdout)
        self.assertIn("extract-code", result.stdout)
        self.assertIn("compare", result.stdout)
        self.assertIn("report", result.stdout)

    def test_extract_doc_reads_required_fields_from_real_reference(self) -> None:
        result = run_cli("extract-doc", "--doc", str(REAL_DOC))
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["command"], "extract-doc")
        self.assertEqual(payload["rule_kind"], "required_field")
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("task_id", names)
        self.assertIn("goal", names)
        self.assertIn("done_definition", names)

    def test_extract_code_reads_required_fields_from_real_script(self) -> None:
        result = run_cli("extract-code", "--script", str(REAL_CODE))
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["command"], "extract-code")
        self.assertTrue(payload["validate_missing_check"])
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("task_id", names)
        self.assertIn("goal", names)
        self.assertIn("deliverables", names)

    def test_compare_real_pair_has_no_required_field_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules_path.write_text(run_cli("extract-doc", "--doc", str(REAL_DOC)).stdout, encoding="utf-8")
            code_rules_path.write_text(run_cli("extract-code", "--script", str(REAL_CODE)).stdout, encoding="utf-8")

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["status"], "implemented")
        self.assertTrue(payload["normalization"]["implemented"])
        self.assertEqual(payload["missing_in_code"], [])
        self.assertEqual(payload["missing_in_doc"], [])
        self.assertEqual(payload["mismatch"], [])

    def test_extract_doc_reads_path_safety_rules_from_dispatch_reference(self) -> None:
        result = run_cli("extract-doc", "--doc", str(REAL_PATH_DOC), "--rule-kind", "path_safety")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["rule_kind"], "path_safety")
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("locked_paths_subset_allowed_paths", names)
        self.assertIn("normalize_trailing_slash", names)
        self.assertIn("forbid_path_traversal", names)
        self.assertIn("forbid_absolute_path", names)
        self.assertIn("forbid_symlink", names)

    def test_extract_code_reads_path_safety_rules_from_dispatch_script(self) -> None:
        result = run_cli("extract-code", "--script", str(REAL_PATH_CODE), "--rule-kind", "path_safety")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["rule_kind"], "path_safety")
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("locked_paths_subset_allowed_paths", names)
        self.assertIn("normalize_trailing_slash", names)
        self.assertIn("forbid_path_traversal", names)
        self.assertIn("forbid_absolute_path", names)
        self.assertIn("forbid_symlink", names)

    def test_compare_real_path_safety_pair_has_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules_path.write_text(
                run_cli("extract-doc", "--doc", str(REAL_PATH_DOC), "--rule-kind", "path_safety").stdout,
                encoding="utf-8",
            )
            code_rules_path.write_text(
                run_cli("extract-code", "--script", str(REAL_PATH_CODE), "--rule-kind", "path_safety").stdout,
                encoding="utf-8",
            )

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["rule_kind"], "path_safety")
        self.assertEqual(payload["missing_in_code"], [])
        self.assertEqual(payload["missing_in_doc"], [])
        self.assertEqual(payload["mismatch"], [])
        self.assertEqual(payload["typed_mismatch"], [])

    def test_compare_reports_typed_mismatch_for_path_rule_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules = {
                "status": "implemented",
                "command": "extract-doc",
                "rule_kind": "path_safety",
                "rules": [
                    {
                        "kind": "path_safety",
                        "name": "locked_paths_subset_allowed_paths",
                        "source": "doc",
                        "value": True,
                        "evidence": "doc subset",
                    },
                    {
                        "kind": "path_safety",
                        "name": "forbid_path_traversal",
                        "source": "doc",
                        "value": True,
                        "evidence": "doc traversal",
                    },
                    {
                        "kind": "path_safety",
                        "name": "forbid_symlink",
                        "source": "doc",
                        "value": True,
                        "evidence": "doc symlink",
                    },
                ],
            }
            code_rules = {
                "status": "implemented",
                "command": "extract-code",
                "rule_kind": "path_safety",
                "rules": [
                    {
                        "kind": "path_safety",
                        "name": "locked_paths_subset_allowed_paths",
                        "source": "code",
                        "value": True,
                        "evidence": "code subset",
                    },
                    {
                        "kind": "path_safety",
                        "name": "forbid_absolute_path",
                        "source": "code",
                        "value": True,
                        "evidence": "code absolute",
                    },
                    {
                        "kind": "path_safety",
                        "name": "forbid_symlink",
                        "source": "code",
                        "value": True,
                        "evidence": "code symlink",
                    },
                ],
            }
            doc_rules_path.write_text(json.dumps(doc_rules, ensure_ascii=False), encoding="utf-8")
            code_rules_path.write_text(json.dumps(code_rules, ensure_ascii=False), encoding="utf-8")

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual([item["name"] for item in payload["missing_in_code"]], ["forbid_path_traversal"])
        self.assertEqual([item["name"] for item in payload["missing_in_doc"]], ["forbid_absolute_path"])
        self.assertEqual(payload["mismatch"], [])
        self.assertEqual(len(payload["typed_mismatch"]), 1)
        typed = payload["typed_mismatch"][0]
        self.assertEqual(typed["kind"], "path_rule_condition_changed")
        self.assertEqual(typed["name"], "locked_paths_conditions")
        self.assertEqual(typed["doc_only"], ["forbid_path_traversal"])
        self.assertEqual(typed["code_only"], ["forbid_absolute_path"])

    def test_extract_doc_reads_transition_rules_from_dispatch_reference(self) -> None:
        result = run_cli("extract-doc", "--doc", str(REAL_PATH_DOC), "--rule-kind", "transition_rule")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["rule_kind"], "transition_rule")
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("queued->blocked", names)
        self.assertIn("ready->running", names)
        self.assertIn("complete->merged", names)

    def test_extract_code_reads_transition_rules_from_dispatch_script(self) -> None:
        result = run_cli("extract-code", "--script", str(REAL_PATH_CODE), "--rule-kind", "transition_rule")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["rule_kind"], "transition_rule")
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("queued->blocked", names)
        self.assertIn("ready->running", names)
        self.assertIn("complete->merged", names)

    def test_compare_real_transition_pair_has_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules_path.write_text(
                run_cli("extract-doc", "--doc", str(REAL_PATH_DOC), "--rule-kind", "transition_rule").stdout,
                encoding="utf-8",
            )
            code_rules_path.write_text(
                run_cli("extract-code", "--script", str(REAL_PATH_CODE), "--rule-kind", "transition_rule").stdout,
                encoding="utf-8",
            )

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["rule_kind"], "transition_rule")
        self.assertEqual(payload["missing_in_code"], [])
        self.assertEqual(payload["missing_in_doc"], [])
        self.assertEqual(payload["mismatch"], [])
        self.assertEqual(payload["typed_mismatch"], [])

    def test_compare_reports_typed_mismatch_for_transition_set_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules = {
                "status": "implemented",
                "command": "extract-doc",
                "rule_kind": "transition_rule",
                "rules": [
                    {
                        "kind": "transition_rule",
                        "name": "queued->blocked",
                        "source": "doc",
                        "value": True,
                        "evidence": "doc queued->blocked",
                    },
                    {
                        "kind": "transition_rule",
                        "name": "ready->running",
                        "source": "doc",
                        "value": True,
                        "evidence": "doc ready->running",
                    },
                ],
            }
            code_rules = {
                "status": "implemented",
                "command": "extract-code",
                "rule_kind": "transition_rule",
                "rules": [
                    {
                        "kind": "transition_rule",
                        "name": "queued->ready",
                        "source": "code",
                        "value": True,
                        "evidence": "code queued->ready",
                    },
                    {
                        "kind": "transition_rule",
                        "name": "ready->running",
                        "source": "code",
                        "value": True,
                        "evidence": "code ready->running",
                    },
                ],
            }
            doc_rules_path.write_text(json.dumps(doc_rules, ensure_ascii=False), encoding="utf-8")
            code_rules_path.write_text(json.dumps(code_rules, ensure_ascii=False), encoding="utf-8")

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual([item["name"] for item in payload["missing_in_code"]], ["queued->blocked"])
        self.assertEqual([item["name"] for item in payload["missing_in_doc"]], ["queued->ready"])
        self.assertEqual(payload["mismatch"], [])
        self.assertEqual(len(payload["typed_mismatch"]), 1)
        typed = payload["typed_mismatch"][0]
        self.assertEqual(typed["kind"], "transition_rule_set_changed")
        self.assertEqual(typed["name"], "status_transitions")
        self.assertEqual(typed["doc_only"], ["queued->blocked"])
        self.assertEqual(typed["code_only"], ["queued->ready"])

    def test_extract_doc_reads_status_enum_from_dispatch_reference(self) -> None:
        result = run_cli("extract-doc", "--doc", str(REAL_PATH_DOC), "--rule-kind", "enum_value")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["rule_kind"], "enum_value")
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("status:queued", names)
        self.assertIn("status:ready", names)
        self.assertIn("status:blocked", names)
        self.assertIn("status:merged", names)

    def test_extract_code_reads_status_enum_from_dispatch_script(self) -> None:
        result = run_cli("extract-code", "--script", str(REAL_PATH_CODE), "--rule-kind", "enum_value")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "implemented")
        self.assertEqual(payload["rule_kind"], "enum_value")
        names = {rule["name"] for rule in payload["rules"]}
        self.assertIn("status:queued", names)
        self.assertIn("status:ready", names)
        self.assertIn("status:blocked", names)
        self.assertIn("status:merged", names)

    def test_compare_real_enum_pair_has_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules_path.write_text(
                run_cli("extract-doc", "--doc", str(REAL_PATH_DOC), "--rule-kind", "enum_value").stdout,
                encoding="utf-8",
            )
            code_rules_path.write_text(
                run_cli("extract-code", "--script", str(REAL_PATH_CODE), "--rule-kind", "enum_value").stdout,
                encoding="utf-8",
            )

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["rule_kind"], "enum_value")
        self.assertEqual(payload["missing_in_code"], [])
        self.assertEqual(payload["missing_in_doc"], [])
        self.assertEqual(payload["mismatch"], [])
        self.assertEqual(payload["typed_mismatch"], [])

    def test_compare_reports_typed_mismatch_for_enum_set_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules = {
                "status": "implemented",
                "command": "extract-doc",
                "rule_kind": "enum_value",
                "rules": [
                    {
                        "kind": "enum_value",
                        "name": "status:queued",
                        "source": "doc",
                        "value": True,
                        "evidence": "doc queued",
                    },
                    {
                        "kind": "enum_value",
                        "name": "status:ready",
                        "source": "doc",
                        "value": True,
                        "evidence": "doc ready",
                    },
                ],
            }
            code_rules = {
                "status": "implemented",
                "command": "extract-code",
                "rule_kind": "enum_value",
                "rules": [
                    {
                        "kind": "enum_value",
                        "name": "status:queued",
                        "source": "code",
                        "value": True,
                        "evidence": "code queued",
                    },
                    {
                        "kind": "enum_value",
                        "name": "status:running",
                        "source": "code",
                        "value": True,
                        "evidence": "code running",
                    },
                ],
            }
            doc_rules_path.write_text(json.dumps(doc_rules, ensure_ascii=False), encoding="utf-8")
            code_rules_path.write_text(json.dumps(code_rules, ensure_ascii=False), encoding="utf-8")

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual([item["name"] for item in payload["missing_in_code"]], ["status:ready"])
        self.assertEqual([item["name"] for item in payload["missing_in_doc"]], ["status:running"])
        self.assertEqual(payload["mismatch"], [])
        self.assertEqual(len(payload["typed_mismatch"]), 1)
        typed = payload["typed_mismatch"][0]
        self.assertEqual(typed["kind"], "enum_value_set_changed")
        self.assertEqual(typed["name"], "status")
        self.assertEqual(typed["doc_only"], ["ready"])
        self.assertEqual(typed["code_only"], ["running"])

    def test_compare_reports_missing_in_code_for_negative_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules = {
                "status": "implemented",
                "command": "extract-doc",
                "rules": [
                    {
                        "kind": "required_field",
                        "name": "task_id",
                        "source": "doc",
                        "value": True,
                        "evidence": "task_id row",
                    },
                    {
                        "kind": "required_field",
                        "name": "goal",
                        "source": "doc",
                        "value": True,
                        "evidence": "goal row",
                    },
                ],
            }
            code_rules = {
                "status": "implemented",
                "command": "extract-code",
                "rules": [
                    {
                        "kind": "required_field",
                        "name": "task_id",
                        "source": "code",
                        "value": True,
                        "evidence": "REQUIRED_FIELDS",
                    }
                ],
            }
            doc_rules_path.write_text(json.dumps(doc_rules, ensure_ascii=False), encoding="utf-8")
            code_rules_path.write_text(json.dumps(code_rules, ensure_ascii=False), encoding="utf-8")

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual([item["name"] for item in payload["missing_in_code"]], ["goal"])
        self.assertEqual(payload["missing_in_doc"], [])
        self.assertEqual(payload["mismatch"], [])

    def test_compare_reports_missing_in_doc_for_negative_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            doc_rules_path = root / "doc_rules.json"
            code_rules_path = root / "code_rules.json"

            doc_rules = {
                "status": "implemented",
                "command": "extract-doc",
                "rules": [
                    {
                        "kind": "required_field",
                        "name": "task_id",
                        "source": "doc",
                        "value": True,
                        "evidence": "task_id row",
                    }
                ],
            }
            code_rules = {
                "status": "implemented",
                "command": "extract-code",
                "rules": [
                    {
                        "kind": "required_field",
                        "name": "task_id",
                        "source": "code",
                        "value": True,
                        "evidence": "REQUIRED_FIELDS",
                    },
                    {
                        "kind": "required_field",
                        "name": "goal",
                        "source": "code",
                        "value": True,
                        "evidence": "REQUIRED_FIELDS",
                    },
                ],
            }
            doc_rules_path.write_text(json.dumps(doc_rules, ensure_ascii=False), encoding="utf-8")
            code_rules_path.write_text(json.dumps(code_rules, ensure_ascii=False), encoding="utf-8")

            result = run_cli(
                "compare",
                "--doc-rules",
                str(doc_rules_path),
                "--code-rules",
                str(code_rules_path),
            )
            payload = json.loads(result.stdout)

        self.assertEqual([item["name"] for item in payload["missing_in_doc"]], ["goal"])
        self.assertEqual(payload["missing_in_code"], [])
        self.assertEqual(payload["mismatch"], [])

    def test_report_outputs_human_readable_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            results_path = root / "results.json"
            results = {
                "rule_kind": "required_field",
                "pair": {"doc": "packet-fields.md", "script": "packet_builder.py"},
                "compared_at": "2026-03-16T20:10:00+09:00",
                "missing_in_code": [{"name": "goal", "action": "REQUIRED_FIELDS 또는 validate evidence에 'goal' 추가 검토"}],
                "missing_in_doc": [],
                "mismatch": [],
                "typed_mismatch": [],
            }
            results_path.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")

            result = run_cli("report", "--results", str(results_path))

        self.assertIn("# Doc-Code Drift Report", result.stdout)
        self.assertIn("pair: packet-fields.md <-> packet_builder.py", result.stdout)
        self.assertIn("missing_in_code: 1", result.stdout)
        self.assertIn("goal ->", result.stdout)
        self.assertIn("missing_in_doc: 0", result.stdout)
        self.assertIn("typed_mismatch: 0", result.stdout)
        self.assertIn("없음", result.stdout)

    def test_report_outputs_typed_mismatch_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            results_path = root / "results.json"
            results = {
                "rule_kind": "enum_value",
                "pair": {"doc": "dispatch-fields.md", "script": "dispatch_manager.py"},
                "compared_at": "2026-03-16T22:40:00+09:00",
                "missing_in_code": [{"name": "status:ready", "action": "VALID_STATUSES에 'status:ready' 허용값 추가 검토"}],
                "missing_in_doc": [{"name": "status:running", "action": "status enum 문서에 'status:running' 허용값 문서화 검토"}],
                "mismatch": [],
                "typed_mismatch": [
                    {
                        "kind": "enum_value_set_changed",
                        "name": "status",
                        "doc_only": ["ready"],
                        "code_only": ["running"],
                        "action": "status enum의 doc/code 허용값 집합 정렬 검토",
                    }
                ],
            }
            results_path.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")

            result = run_cli("report", "--results", str(results_path))

        self.assertIn("typed_mismatch: 1", result.stdout)
        self.assertIn("[enum_value_set_changed] status", result.stdout)
        self.assertIn("doc_only=ready", result.stdout)
        self.assertIn("code_only=running", result.stdout)

    def test_report_outputs_path_typed_mismatch_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            results_path = root / "results.json"
            results = {
                "rule_kind": "path_safety",
                "pair": {"doc": "dispatch-fields.md", "script": "dispatch_manager.py"},
                "compared_at": "2026-03-17T00:06:00+09:00",
                "missing_in_code": [{"name": "forbid_path_traversal", "action": "validate_dispatch 경로 검증에 'forbid_path_traversal' 규칙 구현 검토"}],
                "missing_in_doc": [{"name": "forbid_absolute_path", "action": "## locked_paths 규칙에 'forbid_absolute_path' 규칙 문서화 검토"}],
                "mismatch": [],
                "typed_mismatch": [
                    {
                        "kind": "path_rule_condition_changed",
                        "name": "locked_paths_conditions",
                        "doc_only": ["forbid_path_traversal"],
                        "code_only": ["forbid_absolute_path"],
                        "action": "locked_paths 경로 규칙의 doc/code 조건 집합 정렬 검토",
                    }
                ],
            }
            results_path.write_text(json.dumps(results, ensure_ascii=False), encoding="utf-8")

            result = run_cli("report", "--results", str(results_path))

        self.assertIn("typed_mismatch: 1", result.stdout)
        self.assertIn("[path_rule_condition_changed] locked_paths_conditions", result.stdout)
        self.assertIn("doc_only=forbid_path_traversal", result.stdout)
        self.assertIn("code_only=forbid_absolute_path", result.stdout)


if __name__ == "__main__":
    unittest.main()
