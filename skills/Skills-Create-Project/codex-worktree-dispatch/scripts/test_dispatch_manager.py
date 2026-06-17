#!/usr/bin/env python3
"""dispatch_manager readiness gating tests (dependency-ready rule).

Negative fixture: a dependent dispatch must NOT become `ready` while its
upstream dispatch has not reached a passed state (complete/merged). This is
the machine-checkable form of the instruction acceptance:
"a dependent dispatch must not become ready when its upstream gate is not passed."

cmd_ready does only filesystem reads/writes against DISPATCH_DIR (no git),
so it is testable with a temp directory + a monkeypatched DISPATCH_DIR.
"""
from __future__ import annotations

import argparse
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import dispatch_manager


def _dispatch(dispatch_id, task_id, status, locked_paths, *, depends=None):
    data = {
        "dispatch_version": "0.1",
        "dispatch_id": dispatch_id,
        "task_id": task_id,
        "packet_path": f".codex/packets/{task_id}.json",
        "branch": f"feat/{task_id.lower()}",
        "worktree_path": f".worktrees/{task_id.lower()}",
        "assigned_agent": "codex",
        "status": status,
        "locked_paths": locked_paths,
        "history": [
            {"from": None, "to": status, "at": "2026-06-15T20:22:00+09:00",
             "by": "claude", "reason": "init"}
        ],
        "created_at": "2026-06-15T20:22:00+09:00",
        "created_by": "claude",
        "updated_at": "2026-06-15T20:22:00+09:00",
    }
    if depends:
        data["depends_on_dispatch_ids"] = depends
    return data


class ReadyGateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self._patch = mock.patch.object(dispatch_manager, "DISPATCH_DIR", str(self.dir))
        self._patch.start()

    def tearDown(self):
        self._patch.stop()
        self._tmp.cleanup()

    def _write(self, d):
        (self.dir / f"{d['dispatch_id']}.json").write_text(
            json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def test_dependent_not_ready_when_upstream_not_passed(self):
        """upstream이 complete/merged가 아니면 downstream은 ready로 못 가고 blocked가 된다."""
        self._write(_dispatch("DISPATCH-0002", "TASK-0002", "running", ["src/env/"]))
        self._write(_dispatch("DISPATCH-0003", "TASK-0003", "queued", ["src/app/"],
                              depends=["DISPATCH-0002"]))
        with self.assertRaises(SystemExit):
            dispatch_manager.cmd_ready(argparse.Namespace(dispatch_id="DISPATCH-0003"))
        after = json.loads((self.dir / "DISPATCH-0003.json").read_text(encoding="utf-8"))
        self.assertEqual(after["status"], "blocked")

    def test_dependent_ready_when_upstream_complete(self):
        """upstream이 complete면 downstream은 ready로 전이한다."""
        self._write(_dispatch("DISPATCH-0002", "TASK-0002", "complete", ["src/env/"]))
        self._write(_dispatch("DISPATCH-0003", "TASK-0003", "queued", ["src/app/"],
                              depends=["DISPATCH-0002"]))
        dispatch_manager.cmd_ready(argparse.Namespace(dispatch_id="DISPATCH-0003"))
        after = json.loads((self.dir / "DISPATCH-0003.json").read_text(encoding="utf-8"))
        self.assertEqual(after["status"], "ready")


if __name__ == "__main__":
    unittest.main()
