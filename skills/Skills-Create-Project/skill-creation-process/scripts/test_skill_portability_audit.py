#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).with_name("skill_portability_audit.py")


class SkillPortabilityAuditTests(unittest.TestCase):
    def _write_file(self, path: Path, text: str) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_help_lists_skill_dir_flag(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_PATH), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("--skill-dir", result.stdout)
        self.assertIn("--workspace-root", result.stdout)

    def test_audit_classifies_internal_bridge_external_and_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_a = root / "skill-a"
            skill_b = root / "skill-b"
            fixture = root / "fixture-pack"

            self._write_file(skill_a / "SKILL.md", "# A\n")
            self._write_file(skill_a / "references" / "internal.md", "# internal\n")
            self._write_file(skill_b / "SKILL.md", "# B\n")
            self._write_file(fixture / "references" / "sample.md", "# sample\n")

            self._write_file(
                skill_a / "references" / "links.md",
                "\n".join(
                    [
                        "[internal](./internal.md)",
                        "[bridge](../../skill-b/SKILL.md)",
                        "[external](../../fixture-pack/references/sample.md)",
                        "[missing](../../skill-b/references/missing.md)",
                        "[absolute](/tmp/portable-test.md)",
                    ]
                )
                + "\n",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--workspace-root",
                    str(root),
                    "--skill-dir",
                    str(skill_a),
                    "--skill-dir",
                    str(skill_b),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            skill_a_result = next(item for item in payload["skills"] if item["skill"] == "skill-a")
            self.assertEqual(skill_a_result["counts"]["internal"], 1)
            self.assertEqual(skill_a_result["counts"]["bridge"], 1)
            self.assertEqual(skill_a_result["counts"]["external_dependency"], 1)
            self.assertEqual(skill_a_result["counts"]["missing"], 1)
            self.assertEqual(skill_a_result["counts"]["absolute_path"], 1)

    def test_writes_json_and_markdown_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_a = root / "skill-a"
            self._write_file(skill_a / "SKILL.md", "[self](./SKILL.md)\n")
            output_json = root / "audit.json"
            output_md = root / "audit.md"

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--workspace-root",
                    str(root),
                    "--skill-dir",
                    str(skill_a),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(output_json.exists())
            self.assertTrue(output_md.exists())
            self.assertIn("Skill Portability Audit", output_md.read_text(encoding="utf-8"))

    def test_ignores_legacy_and_url_placeholder_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_a = root / "skill-a"
            self._write_file(skill_a / "SKILL.md", "# A\n")
            self._write_file(skill_a / "knowledge_bases" / "current.md", "[skip](URL)\n")
            self._write_file(skill_a / "legacy" / "old.md", "[old](../SKILL.md)\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--workspace-root",
                    str(root),
                    "--skill-dir",
                    str(skill_a),
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            skill_a_result = payload["skills"][0]
            self.assertEqual(skill_a_result["counts"]["missing"], 0)
            self.assertEqual(skill_a_result["counts"]["internal"], 0)

    def test_exclude_glob_skips_matching_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_a = root / "skill-a"
            self._write_file(skill_a / "SKILL.md", "# A\n")
            self._write_file(skill_a / "references" / "audit-report.md", "[self](../SKILL.md)\n")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_PATH),
                    "--workspace-root",
                    str(root),
                    "--skill-dir",
                    str(skill_a),
                    "--exclude-glob",
                    "references/*audit*.md",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            skill_a_result = payload["skills"][0]
            self.assertEqual(skill_a_result["counts"]["internal"], 0)


if __name__ == "__main__":
    unittest.main()
