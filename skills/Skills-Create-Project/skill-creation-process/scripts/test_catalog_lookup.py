#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("catalog_lookup.py")


class CatalogLookupTest(unittest.TestCase):
    def test_help_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("show", result.stdout)
        self.assertIn("search", result.stdout)

    def test_list_tasks(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "list", "--type", "tasks"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["type"], "tasks")
        self.assertGreaterEqual(payload["count"], 12)

    def test_list_joins(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "list", "--type", "joins"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["type"], "joins")
        self.assertGreaterEqual(payload["count"], 12)

    def test_show_task_with_resolved_skills(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "show", "--key", "TASK-05"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        record = payload["record"]
        self.assertEqual(record["key"], "TASK-05")
        resolved_names = [item["name"] for item in record["resolved_primary_skills"]]
        self.assertIn("slice-experiment-lab", resolved_names)

    def test_show_issue_with_resolved_tasks(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "show", "--key", "ISSUE-07"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        record = payload["record"]
        task_keys = [item["key"] for item in record["resolved_tasks"]]
        self.assertIn("TASK-08", task_keys)

    def test_show_join_with_resolved_issue_tasks_and_skills(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "show", "--key", "JOIN-ISSUE-07"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        record = payload["record"]
        self.assertEqual(record["resolved_issue"]["key"], "ISSUE-07")
        task_keys = [item["key"] for item in record["resolved_tasks"]]
        skill_names = [item["name"] for item in record["resolved_skills"]]
        self.assertIn("TASK-05", task_keys)
        self.assertIn("TASK-08", task_keys)
        self.assertIn("slice-experiment-lab", skill_names)

    def test_show_unknown_key_fails(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "show", "--key", "TASK-99"],
            check=False,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(payload["status"], "not_found")

    def test_search_smoke_matches_tasks(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "search", "--query", "smoke", "--type", "tasks"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        self.assertGreaterEqual(payload["count"], 2)
        matched_keys = [match["item"]["key"] for match in payload["matches"]]
        self.assertIn("TASK-05", matched_keys)

    def test_search_slice_experiment_lab_matches_skill(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "search", "--query", "slice-experiment-lab", "--type", "skills"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        matched_keys = [match["item"]["key"] for match in payload["matches"]]
        self.assertIn("SKILL-slice-experiment-lab", matched_keys)

    def test_search_warning_matches_join(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "search", "--query", "warning", "--type", "joins"],
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(result.stdout)
        matched_keys = [match["item"]["key"] for match in payload["matches"]]
        self.assertIn("JOIN-ISSUE-07", matched_keys)


if __name__ == "__main__":
    unittest.main()
