#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = Path(__file__).with_name("verify_artifact_order.py")
SPEC = importlib.util.spec_from_file_location("verify_artifact_order", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class VerifyArtifactOrderTests(unittest.TestCase):
    def _write_markdown(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# test\n", encoding="utf-8")
        return path

    def _run_main(self, argv: list[str]) -> int:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with (
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(stdout),
            contextlib.redirect_stderr(stderr),
        ):
            return MODULE.main()

    def test_discover_default_chain_ignores_issue_kb(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp)
            self._write_markdown(
                skill_dir / "knowledge_bases" / "sample-issues-at2026-03-16-10-00.md"
            )
            target_kb = self._write_markdown(
                skill_dir / "knowledge_bases" / "sample-knowledge_base-at2026-03-16-10-01.md"
            )
            consistency = self._write_markdown(
                skill_dir
                / "checklist-forconsistency-evaluation"
                / "consistency-checklist-at2026-03-16-10-02.md"
            )
            implementation = self._write_markdown(
                skill_dir
                / "checklist-forimplementation"
                / "implementation-checklist-at2026-03-16-10-03.md"
            )

            chain = MODULE._discover_default_chain(skill_dir)

            self.assertEqual(
                chain,
                [
                    ("knowledge_base", target_kb),
                    ("consistency_checklist", consistency),
                    ("implementation_checklist", implementation),
                ],
            )

    def test_main_passes_for_ordered_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = self._write_markdown(root / "kb-at2026-03-16-10-00.md")
            consistency = self._write_markdown(root / "consistency-at2026-03-16-10-01.md")
            implementation = self._write_markdown(root / "implementation-at2026-03-16-10-02.md")

            result = self._run_main(
                ["verify_artifact_order.py", str(kb), str(consistency), str(implementation)]
            )

            self.assertEqual(result, 0)

    def test_main_fails_without_minute_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kb = self._write_markdown(root / "kb-at2026-03-16-10-00.md")
            consistency = self._write_markdown(root / "consistency.md")

            result = self._run_main(["verify_artifact_order.py", str(kb), str(consistency)])

            self.assertEqual(result, 1)

    def test_main_fails_for_reverse_order(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            older = self._write_markdown(root / "older-at2026-03-16-10-00.md")
            time.sleep(0.02)
            newer = self._write_markdown(root / "newer-at2026-03-16-10-01.md")

            result = self._run_main(["verify_artifact_order.py", str(newer), str(older)])

            self.assertEqual(result, 1)


if __name__ == "__main__":
    unittest.main()
