#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("audit_cross_skill_dependencies.py")


def run_cli(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        check=check,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_skill(root: Path, name: str) -> Path:
    skill_dir = root / name
    _write(skill_dir / "SKILL.md", f"# {name}\n")
    return skill_dir


class CrossSkillDependencyAuditTests(unittest.TestCase):
    def test_missing_declaration_for_target_skill(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _make_skill(root, "consumer-skill")

            result = run_cli(
                "--skills-root", str(root),
                "--skill", "consumer-skill",
                "--format", "json",
                check=False,
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload[0]["status"], "missing_declaration")

    def test_missing_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            consumer = _make_skill(root, "consumer-skill")
            _write(
                consumer / "references" / "cross_skill_dependencies.yaml",
                'cross_skill_dependencies:\n'
                '  - provider: "missing-provider"\n'
                '    contract: "references/contracts/demo.json"\n'
                '    consumed_facts: ["x"]\n'
                '    last_synced_at: "2026-03-27T14:30:00+09:00"\n',
            )

            result = run_cli("--skills-root", str(root), "--format", "json", check=False)
            payload = json.loads(result.stdout)

        self.assertEqual(payload[0]["status"], "missing_provider")

    def test_missing_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            provider = _make_skill(root, "provider-skill")
            consumer = _make_skill(root, "consumer-skill")
            _write(
                consumer / "references" / "cross_skill_dependencies.yaml",
                'cross_skill_dependencies:\n'
                '  - provider: "provider-skill"\n'
                '    contract: "references/contracts/demo.json"\n'
                '    consumed_facts: ["x"]\n'
                '    last_synced_at: "2026-03-27T14:30:00+09:00"\n',
            )
            self.assertFalse((provider / "references" / "contracts" / "demo.json").exists())

            result = run_cli("--skills-root", str(root), "--format", "json", check=False)
            payload = json.loads(result.stdout)

        self.assertEqual(payload[0]["status"], "missing_contract")

    def test_invalid_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            provider = _make_skill(root, "provider-skill")
            consumer = _make_skill(root, "consumer-skill")
            _write(provider / "references" / "contracts" / "demo.json", '{"v":"1"}')
            _write(
                consumer / "references" / "cross_skill_dependencies.yaml",
                'cross_skill_dependencies:\n'
                '  - provider: "provider-skill"\n'
                '    contract: "references/contracts/demo.json"\n'
                '    consumed_facts: ["x"]\n'
                '    last_synced_at: "not-a-timestamp"\n',
            )

            result = run_cli("--skills-root", str(root), "--format", "json", check=False)
            payload = json.loads(result.stdout)

        self.assertEqual(payload[0]["status"], "invalid_timestamp")

    def test_stale_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            provider = _make_skill(root, "provider-skill")
            consumer = _make_skill(root, "consumer-skill")
            _write(provider / "references" / "contracts" / "demo.json", '{"v":"1"}')
            time.sleep(0.05)
            _write(
                consumer / "references" / "cross_skill_dependencies.yaml",
                'cross_skill_dependencies:\n'
                '  - provider: "provider-skill"\n'
                '    contract: "references/contracts/demo.json"\n'
                '    consumed_facts: ["x"]\n'
                '    last_synced_at: "2026-03-01T10:00:00+09:00"\n',
            )

            result = run_cli("--skills-root", str(root), "--format", "json", check=False)
            payload = json.loads(result.stdout)

        self.assertEqual(payload[0]["status"], "stale_dependency")

    def test_ok_dependency(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            provider = _make_skill(root, "provider-skill")
            consumer = _make_skill(root, "consumer-skill")
            _write(provider / "references" / "contracts" / "demo.json", '{"v":"1"}')
            now = "2099-03-27T14:30:00+09:00"
            _write(
                consumer / "references" / "cross_skill_dependencies.yaml",
                'cross_skill_dependencies:\n'
                '  - provider: "provider-skill"\n'
                '    contract: "references/contracts/demo.json"\n'
                '    consumed_facts: ["x"]\n'
                f'    last_synced_at: "{now}"\n',
            )

            result = run_cli("--skills-root", str(root), "--format", "json", check=False)
            payload = json.loads(result.stdout)

        self.assertEqual(payload[0]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
