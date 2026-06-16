#!/usr/bin/env python3
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import fix_jsonl
import resume_precheck
import sanitize_utils


class ClaudeSessionPoisonRecoveryTests(unittest.TestCase):
    def test_sanitize_for_api_removes_surrogate_and_nul_recursively(self) -> None:
        payload = {
            "message": "ok\ud800bad\x00end",
            "items": ["a\udfff", {"nested": "x\x00y"}],
        }
        sanitized = sanitize_utils.sanitize_for_api(payload)
        self.assertEqual(sanitized["message"], "okbadend")
        self.assertEqual(sanitized["items"][0], "a")
        self.assertEqual(sanitized["items"][1]["nested"], "xy")

    def test_safe_json_write_writes_clean_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            out = Path(tmpdir) / "payload.json"
            sanitize_utils.safe_json_write(out, {"text": "a\ud800b\x00c"}, ensure_ascii=False, indent=2)
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["text"], "abc")

    def test_fix_line_recovers_parsable_clean_json(self) -> None:
        raw = "{\"text\":\"a\ud800b\\u0000c\"}\n"
        fixed, modified, error = fix_jsonl.fix_line(raw)
        self.assertIsNone(error)
        self.assertTrue(modified)
        self.assertIsNotNone(fixed)
        self.assertEqual(json.loads(fixed)["text"], "abc")

    def test_collect_surrogates_finds_nested_hit(self) -> None:
        hits = resume_precheck.collect_surrogates({"a": ["x", {"b": "q\ud800w"}]})
        self.assertEqual(len(hits), 1)
        self.assertEqual(hits[0]["path"], "$.a[1].b")


if __name__ == "__main__":
    unittest.main()
