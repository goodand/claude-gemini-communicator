#!/usr/bin/env python3
"""Tests for claim-verifier."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from claim_verifier import (
    CLAIM_TYPES,
    VERDICTS,
    _classify_claim,
    _extract_keywords,
    _extract_paths,
    _split_compound,
    extract_claims,
    format_report,
    verify_batch,
    verify_claim,
    verify_text,
)


class TestClassifyClaim(unittest.TestCase):
    def test_implementation(self):
        self.assertEqual(_classify_claim("JWT 인증이 구현됐다"), "implementation")

    def test_state(self):
        self.assertEqual(_classify_claim("모든 테스트가 통과한다"), "state")

    def test_artifact(self):
        self.assertEqual(_classify_claim("report.md 파일이 존재한다"), "artifact")

    def test_boundary(self):
        self.assertEqual(_classify_claim("runtime 필드를 포함하지 않는다"), "boundary")

    def test_consistency(self):
        self.assertEqual(_classify_claim("문서와 코드가 일치한다"), "consistency")

    def test_fallback_state(self):
        self.assertEqual(_classify_claim("unknown pattern here"), "state")


class TestSplitCompound(unittest.TestCase):
    def test_simple(self):
        self.assertEqual(_split_compound("단일 claim"), ["단일 claim"])

    def test_comma_split(self):
        parts = _split_compound("A를 구현하고, B를 테스트한다")
        self.assertEqual(len(parts), 2)

    def test_semicolon_split(self):
        parts = _split_compound("파일이 존재한다; 테스트가 통과한다")
        self.assertEqual(len(parts), 2)


class TestExtractPaths(unittest.TestCase):
    def test_file_path(self):
        paths = _extract_paths("src/auth/jwt_middleware.py가 존재한다")
        self.assertIn("src/auth/jwt_middleware.py", paths)

    def test_dir_path(self):
        paths = _extract_paths("src/auth/ 디렉토리 아래")
        self.assertTrue(any("src/auth/" in p for p in paths))

    def test_no_path(self):
        paths = _extract_paths("단순한 텍스트")
        self.assertEqual(paths, [])


class TestExtractKeywords(unittest.TestCase):
    def test_quoted(self):
        kw = _extract_keywords("'validate_packet' 함수가 존재한다")
        self.assertIn("validate_packet", kw)

    def test_identifier(self):
        kw = _extract_keywords("packet_builder 모듈")
        self.assertIn("packet_builder", kw)


class TestExtractClaims(unittest.TestCase):
    def test_markdown_list(self):
        text = "# Header\n\n- claim one is here\n- claim two is here\n"
        claims = extract_claims(text)
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0]["id"], "CLM-000")
        self.assertEqual(claims[1]["id"], "CLM-001")

    def test_skip_header(self):
        text = "# This is a header\n\n- actual claim text here\n"
        claims = extract_claims(text)
        self.assertEqual(len(claims), 1)
        self.assertNotIn("header", claims[0]["text"].lower())

    def test_skip_code_block(self):
        text = "- before code\n```\ncode line\n```\n- after code\n"
        claims = extract_claims(text)
        texts = [c["text"] for c in claims]
        self.assertFalse(any("code line" in t for t in texts))

    def test_skip_short(self):
        text = "- ok\n- this is a real claim\n"
        claims = extract_claims(text)
        self.assertEqual(len(claims), 1)

    def test_source_line(self):
        text = "# header\n- claim on line 2\n"
        claims = extract_claims(text)
        self.assertEqual(claims[0]["source_line"], 2)

    def test_checklist_item(self):
        text = "- [x] 구현 완료된 항목\n- [ ] 미완료 항목\n"
        claims = extract_claims(text)
        self.assertEqual(len(claims), 2)
        self.assertNotIn("[x]", claims[0]["text"])

    def test_has_type(self):
        text = "- src/auth.py 파일이 존재한다\n"
        claims = extract_claims(text)
        self.assertEqual(claims[0]["type"], "artifact")


class TestVerifyClaim(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # 테스트용 파일 생성
        Path(self.tmpdir, "src").mkdir()
        Path(self.tmpdir, "src", "auth.py").write_text("def login():\n    pass\n")
        Path(self.tmpdir, "README.md").write_text("# Project\n\nThis is a project.\n")

    def test_artifact_true(self):
        claim = {"id": "CLM-000", "text": "src/auth.py 파일이 존재한다", "type": "artifact"}
        result = verify_claim(claim, self.tmpdir)
        self.assertEqual(result["verdict"], "true")

    def test_artifact_false(self):
        claim = {"id": "CLM-001", "text": "src/nonexistent_xyz.py 파일이 존재한다", "type": "artifact"}
        result = verify_claim(claim, self.tmpdir)
        self.assertIn(result["verdict"], ("false", "unverifiable"))

    def test_unverifiable_no_evidence(self):
        claim = {"id": "CLM-002", "text": "완전히 무관한 내용", "type": "state"}
        result = verify_claim(claim, self.tmpdir)
        self.assertEqual(result["verdict"], "unverifiable")
        self.assertTrue(result["follow_up"])

    def test_result_structure(self):
        claim = {"id": "CLM-003", "text": "README.md가 존재한다", "type": "artifact"}
        result = verify_claim(claim, self.tmpdir)
        self.assertIn("claim_id", result)
        self.assertIn("verdict", result)
        self.assertIn("evidence", result)
        self.assertIn("reason", result)
        self.assertIn("follow_up", result)
        self.assertIn(result["verdict"], VERDICTS)

    def test_keyword_evidence_has_line(self):
        claim = {"id": "CLM-004", "text": "'login' 함수가 구현됐다", "type": "implementation"}
        result = verify_claim(claim, self.tmpdir)
        kw_evidence = [e for e in result["evidence"] if e.get("type") == "keyword_match"]
        if kw_evidence:
            self.assertIsNotNone(kw_evidence[0]["line"])


class TestVerifyText(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Path(self.tmpdir, "README.md").write_text("# Hello\n")

    def test_end_to_end(self):
        text = "- README.md 파일이 존재한다\n- missing.py 파일이 존재한다\n"
        result = verify_text(text, self.tmpdir)
        self.assertEqual(result["total"], 2)
        self.assertIn("summary", result)
        self.assertIn("claims", result)
        self.assertIn("results", result)


class TestFormatReport(unittest.TestCase):
    def test_report_structure(self):
        data = {
            "verified_at": "2026-03-25T00:00:00+09:00",
            "repo": ".",
            "total": 1,
            "summary": {"true": 1, "false": 0, "partial": 0, "unverifiable": 0},
            "results": [
                {
                    "claim_id": "CLM-000",
                    "claim_text": "파일 존재",
                    "claim_type": "artifact",
                    "verdict": "true",
                    "evidence": [{"file": "README.md", "line": 1, "content": "# Hello", "type": "file_exists"}],
                    "reason": "파일 존재 확인",
                    "follow_up": "",
                }
            ],
        }
        report = format_report(data)
        self.assertIn("Claim Verification Report", report)
        self.assertIn("CLM-000", report)
        self.assertIn("true", report)
        self.assertIn("README.md", report)


class TestVerifyBatch(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        Path(self.tmpdir, "README.md").write_text("# Hello\n")

    def test_mixed_input(self):
        items = [
            "- README.md 파일이 존재한다\n",
            {"text": "missing.py 파일이 존재한다", "type": "artifact"},
        ]
        result = verify_batch(items, self.tmpdir)
        self.assertEqual(result["total"], 2)
        self.assertIn("summary", result)
        self.assertIn("claims", result)
        self.assertIn("results", result)

    def test_ids_sequential(self):
        items = [
            "- claim one here\n- claim two here\n",
            {"text": "claim three here"},
        ]
        result = verify_batch(items, self.tmpdir)
        ids = [c["id"] for c in result["claims"]]
        self.assertEqual(ids, ["CLM-000", "CLM-001", "CLM-002"])

    def test_auto_type_for_dict(self):
        items = [{"text": "src/auth.py 파일이 존재한다"}]
        result = verify_batch(items, self.tmpdir)
        self.assertEqual(result["claims"][0]["type"], "artifact")

    def test_empty_input(self):
        result = verify_batch([], self.tmpdir)
        self.assertEqual(result["total"], 0)


class TestConsistencyDelegation(unittest.TestCase):
    """consistency claim은 partial/unverifiable + doc-code-sync-checker 위임."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        doc = Path(self.tmpdir, "fields.md")
        doc.write_text(
            "## 필수 필드\n\n"
            "| 필드 | 타입 | 설명 |\n"
            "|---|---|---|\n"
            "| `name` | str | 이름 |\n"
            "| `age` | int | 나이 |\n"
        )
        code = Path(self.tmpdir, "validator.py")
        code.write_text('REQUIRED_FIELDS = {"name", "age"}\n')

    def test_consistency_partial_with_evidence(self):
        """파일+키워드 증거 있어도 consistency는 partial (pairwise는 doc-code-sync-checker 담당)."""
        claim = {"id": "CLM-000", "text": "fields.md와 validator.py가 일치한다", "type": "consistency"}
        result = verify_claim(claim, self.tmpdir)
        self.assertIn(result["verdict"], ("partial", "unverifiable"))

    def test_consistency_follow_up_delegates(self):
        """follow_up이 doc-code-sync-checker를 가리킨다."""
        claim = {"id": "CLM-001", "text": "fields.md와 validator.py가 일치한다", "type": "consistency"}
        result = verify_claim(claim, self.tmpdir)
        self.assertIn("doc-code-sync-checker", result["follow_up"])

    def test_consistency_no_evidence_unverifiable(self):
        """증거 없는 consistency claim은 unverifiable (일반 분기)."""
        claim = {"id": "CLM-002", "text": "문서와 코드가 일치한다", "type": "consistency"}
        result = verify_claim(claim, self.tmpdir)
        self.assertEqual(result["verdict"], "unverifiable")
        self.assertTrue(result["follow_up"])

    def test_consistency_no_pairwise_evidence_type(self):
        """claim-verifier는 pairwise_drift/pairwise_sync evidence를 생성하지 않는다."""
        claim = {"id": "CLM-003", "text": "fields.md와 validator.py가 일치한다", "type": "consistency"}
        result = verify_claim(claim, self.tmpdir)
        pairwise = [e for e in result["evidence"] if "pairwise" in e.get("type", "")]
        self.assertEqual(len(pairwise), 0)


if __name__ == "__main__":
    unittest.main()
