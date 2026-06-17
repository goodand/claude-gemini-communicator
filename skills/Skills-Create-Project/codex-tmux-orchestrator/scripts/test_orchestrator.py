#!/usr/bin/env python3
"""TDD smoke tests for orchestrator.py."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest import mock


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "orchestrator.py"


def _load_target() -> ModuleType:
    spec = importlib.util.spec_from_file_location("orchestrator_under_test", TARGET)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Failed to load target: {TARGET}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class OrchestratorSmokeTests(unittest.TestCase):
    target: ModuleType

    @classmethod
    def setUpClass(cls) -> None:
        cls.target = _load_target()

    def test_session_name_uses_dispatch_id_deterministically(self) -> None:
        self.assertEqual(self.target._session_name("DSP-123"), "codex-DSP-123")

    def test_check_runtime_health_keeps_completed_status(self) -> None:
        rt = {"runtime_status": "completed", "dispatch_id": "DSP-1"}
        status, reason = self.target._check_runtime_health(rt)
        self.assertEqual(status, "completed")
        self.assertEqual(reason, "")

    def test_check_runtime_health_marks_failed_when_session_missing(self) -> None:
        rt = {
            "runtime_status": "running",
            "dispatch_id": "DSP-2",
            "session_name": "missing-session",
            "log_path": "",
        }
        with mock.patch.object(self.target, "_session_exists", return_value=False):
            status, reason = self.target._check_runtime_health(rt)
        self.assertEqual(status, "failed")
        self.assertIn("tmux session 없음", reason)

    def test_check_runtime_health_marks_completed_when_done_marker_found(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / "runtime.log"
            log_path.write_text(
                f"prefix\n{self.target.MARKER_DONE}:DSP-3:1:0:2026-03-16T19:00:00+09:00\n",
                encoding="utf-8",
            )
            rt = {
                "runtime_status": "running",
                "dispatch_id": "DSP-3",
                "session_name": "missing-session",
                "log_path": str(log_path),
            }
            with mock.patch.object(self.target, "_session_exists", return_value=False):
                status, reason = self.target._check_runtime_health(rt)
        self.assertEqual(status, "completed")
        self.assertIn("종료 marker 발견", reason)

    def test_preflight_reports_missing_packet_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_path = Path(tmpdir) / "missing-packet.json"
            dispatch_path = Path(tmpdir) / "dispatch.json"
            dispatch_path.write_text("{}", encoding="utf-8")
            errors, packet, dispatch = self.target.preflight(str(packet_path), str(dispatch_path))

        self.assertEqual(packet, None)
        self.assertEqual(dispatch, None)
        self.assertTrue(any("packet 파일 없음" in msg for msg in errors))

    def test_preflight_reports_missing_dispatch_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_path = Path(tmpdir) / "packet.json"
            packet_path.write_text("{}", encoding="utf-8")
            dispatch_path = Path(tmpdir) / "missing-dispatch.json"
            errors, packet, dispatch = self.target.preflight(str(packet_path), str(dispatch_path))

        self.assertEqual(packet, None)
        self.assertEqual(dispatch, None)
        self.assertTrue(any("dispatch 파일 없음" in msg for msg in errors))

    def test_preflight_surfaces_status_and_missing_cli_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            packet_path = Path(tmpdir) / "packet.json"
            dispatch_path = Path(tmpdir) / "dispatch.json"
            packet_path.write_text(json.dumps({"goal": "test"}, ensure_ascii=False), encoding="utf-8")
            dispatch_path.write_text(
                json.dumps(
                    {
                        "dispatch_id": "DSP-4",
                        "status": "queued",
                        "worktree_path": str(Path(tmpdir) / "missing-worktree"),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            fake_which = mock.Mock(returncode=1, stdout="", stderr="")
            with mock.patch.object(self.target.subprocess, "run", return_value=fake_which):
                errors, packet, dispatch = self.target.preflight(str(packet_path), str(dispatch_path))

        self.assertIsNotNone(packet)
        self.assertIsNotNone(dispatch)
        self.assertTrue(any("dispatch status가 'ready'가 아님" in msg for msg in errors))
        self.assertTrue(any("worktree 디렉토리 없음" in msg for msg in errors))
        self.assertTrue(any("codex CLI를 찾을 수 없음" in msg for msg in errors))


if __name__ == "__main__":
    unittest.main()
