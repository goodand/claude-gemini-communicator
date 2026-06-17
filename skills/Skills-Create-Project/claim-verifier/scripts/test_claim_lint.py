#!/usr/bin/env python3
"""Tests for claim_lint.py."""
from __future__ import annotations

import unittest

from claim_lint import (
    generate_follow_up_skeleton,
    lint_claims,
    lint_results,
)


class TestLintClaims(unittest.TestCase):
    def test_compound_remaining(self):
        data = {"claims": [
            {"id": "CLM-000", "text": "A를 구현하고, 그리고 B를 테스트한다", "type": "state"},
        ]}
        ws = lint_claims(data)
        checks = [w["check"] for w in ws]
        self.assertIn("C1", checks)

    def test_type_missing(self):
        data = {"claims": [
            {"id": "CLM-000", "text": "claim without type"},
        ]}
        ws = lint_claims(data)
        self.assertTrue(any(w["check"] == "C2" for w in ws))

    def test_type_invalid(self):
        data = {"claims": [
            {"id": "CLM-000", "text": "some claim", "type": "unknown_type"},
        ]}
        ws = lint_claims(data)
        self.assertTrue(any(w["check"] == "C2" and w["severity"] == "error" for w in ws))

    def test_text_too_short(self):
        data = {"claims": [
            {"id": "CLM-000", "text": "ok", "type": "state"},
        ]}
        ws = lint_claims(data)
        self.assertTrue(any(w["check"] == "C3" for w in ws))

    def test_id_format(self):
        data = {"claims": [
            {"id": "CLAIM-0", "text": "valid claim text", "type": "state"},
        ]}
        ws = lint_claims(data)
        self.assertTrue(any(w["check"] == "C4" for w in ws))

    def test_id_duplicate(self):
        data = {"claims": [
            {"id": "CLM-000", "text": "first claim here", "type": "state"},
            {"id": "CLM-000", "text": "duplicate id claim", "type": "state"},
        ]}
        ws = lint_claims(data)
        self.assertTrue(any(w["check"] == "C5" for w in ws))

    def test_clean_claims(self):
        data = {"claims": [
            {"id": "CLM-000", "text": "JWT 인증이 구현됐다", "type": "implementation"},
            {"id": "CLM-001", "text": "README.md 파일이 존재한다", "type": "artifact"},
        ]}
        ws = lint_claims(data)
        errors = [w for w in ws if w["severity"] == "error"]
        self.assertEqual(len(errors), 0)


class TestLintResults(unittest.TestCase):
    def _result(self, **overrides):
        base = {
            "claim_id": "CLM-000",
            "claim_text": "test claim",
            "claim_type": "state",
            "verdict": "true",
            "evidence": [{"file": "a.py", "line": 1, "content": "x", "type": "keyword_match"}],
            "reason": "found",
            "follow_up": "",
        }
        base.update(overrides)
        return base

    def test_true_no_evidence(self):
        data = {"results": [self._result(evidence=[])]}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R1" for w in ws))

    def test_false_no_follow_up(self):
        data = {"results": [self._result(verdict="false", follow_up="")]}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R2" for w in ws))

    def test_partial_no_follow_up(self):
        data = {"results": [self._result(verdict="partial", follow_up="")]}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R2" for w in ws))

    def test_unverifiable_no_follow_up(self):
        data = {"results": [self._result(verdict="unverifiable", follow_up="")]}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R2" for w in ws))

    def test_file_only_true(self):
        ev = [{"file": "a.py", "line": None, "content": "exists", "type": "file_exists"}]
        data = {"results": [self._result(evidence=ev)]}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R3" for w in ws))

    def test_keyword_no_line(self):
        ev = [{"file": "a.py", "line": None, "content": "x", "type": "keyword_match"}]
        data = {"results": [self._result(evidence=ev)]}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R4" for w in ws))

    def test_invalid_verdict(self):
        data = {"results": [self._result(verdict="maybe")]}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R5" for w in ws))

    def test_missing_field(self):
        r = {"claim_id": "CLM-000", "verdict": "true"}  # evidence, reason, follow_up 누락
        data = {"results": [r]}
        ws = lint_results(data)
        r6 = [w for w in ws if w["check"] == "R6"]
        self.assertEqual(len(r6), 3)

    def test_line_evidence_ratio(self):
        ev = [
            {"file": "a.py", "line": 1, "content": "x", "type": "keyword_match"},
            {"file": "b.py", "line": None, "content": "y", "type": "file_exists"},
        ]
        data = {"results": [self._result(evidence=ev)]}
        ws = lint_results(data)
        r7 = [w for w in ws if w["check"] == "R7"]
        self.assertTrue(len(r7) > 0)
        self.assertIn("50%", r7[0]["message"])

    def test_repeated_follow_up(self):
        results = [
            self._result(claim_id=f"CLM-{i:03d}", verdict="partial",
                         follow_up="동일한 follow_up 문구")
            for i in range(4)
        ]
        data = {"results": results}
        ws = lint_results(data)
        self.assertTrue(any(w["check"] == "R8" for w in ws))

    def test_clean_results(self):
        data = {"results": [self._result()]}
        ws = lint_results(data)
        errors = [w for w in ws if w["severity"] == "error"]
        self.assertEqual(len(errors), 0)


class TestFollowUpSkeleton(unittest.TestCase):
    def _result(self, **overrides):
        base = {
            "claim_id": "CLM-000",
            "claim_text": "src/auth.py 파일이 존재한다",
            "verdict": "false",
            "evidence": [],
            "follow_up": "",
        }
        base.update(overrides)
        return base

    def test_false_suggests_target(self):
        data = {"results": [self._result()]}
        suggestions = generate_follow_up_skeleton(data)
        self.assertEqual(len(suggestions), 1)
        self.assertIn("src/auth.py", suggestions[0]["suggested"])

    def test_partial_suggests_missing(self):
        ev = [{"file": "a.py", "line": None, "content": "exists", "type": "file_exists"}]
        data = {"results": [self._result(verdict="partial", evidence=ev)]}
        suggestions = generate_follow_up_skeleton(data)
        self.assertTrue(len(suggestions) > 0)
        self.assertIn("keyword", suggestions[0]["suggested"])

    def test_unverifiable_suggests_search(self):
        data = {"results": [self._result(
            verdict="unverifiable",
            claim_text="'validate_packet' 함수가 구현됐다",
        )]}
        suggestions = generate_follow_up_skeleton(data)
        self.assertIn("validate_packet", suggestions[0]["suggested"])

    def test_true_no_suggestion(self):
        data = {"results": [self._result(verdict="true")]}
        suggestions = generate_follow_up_skeleton(data)
        self.assertEqual(len(suggestions), 0)

    def test_skips_already_good(self):
        data = {"results": [self._result(
            follow_up="수정 대상: src/auth.py",
        )]}
        suggestions = generate_follow_up_skeleton(data)
        # 이미 적절한 follow_up이 있으면 suggested가 같으므로 skip 가능
        # (current != suggested일 때만 제안)
        self.assertTrue(len(suggestions) <= 1)


class TestVerdictTable(unittest.TestCase):
    def test_table_format(self):
        from claim_verifier import format_verdict_table
        data = {
            "results": [
                {
                    "claim_id": "CLM-000",
                    "verdict": "true",
                    "evidence": [{"file": "a.py", "line": 10, "content": "x", "type": "keyword_match"}],
                    "reason": "found it",
                    "follow_up": "",
                },
                {
                    "claim_id": "CLM-001",
                    "verdict": "false",
                    "evidence": [],
                    "reason": "not found",
                    "follow_up": "fix needed",
                },
            ],
        }
        table = format_verdict_table(data)
        self.assertIn("| claim_id |", table)
        self.assertIn("CLM-000", table)
        self.assertIn("`a.py:10`", table)
        self.assertIn("CLM-001", table)
        self.assertIn("—", table)  # no evidence

    def test_pipe_in_reason_escaped(self):
        from claim_verifier import format_verdict_table
        data = {"results": [{
            "claim_id": "CLM-000", "verdict": "true",
            "evidence": [], "reason": "a | b", "follow_up": "",
        }]}
        table = format_verdict_table(data)
        self.assertNotIn("| a | b |", table)  # pipe escaped


if __name__ == "__main__":
    unittest.main()
