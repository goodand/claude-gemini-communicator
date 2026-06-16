#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("artifact_lifecycle_guard.py")


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


class ArtifactLifecycleGuardTests(unittest.TestCase):
    def test_check_order_passes_for_timestamped_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            kb = root / "knowledge_bases" / "demo-knowledge_base-at2026-03-16-10-00.md"
            cc = root / "checklist-forconsistency-evaluation" / "consistency-checklist-at2026-03-16-10-01.md"
            impl = root / "checklist-forimplementation" / "implementation-checklist-at2026-03-16-10-02.md"
            _write(kb, "kb")
            time.sleep(0.02)
            _write(cc, "consistency")
            time.sleep(0.02)
            _write(impl, "implementation")

            result = run_cli("check-order", "--skill-dir", str(root))
            payload = json.loads(result.stdout)

        self.assertEqual(payload["status"], "passed")
        self.assertEqual(len(payload["artifacts"]), 3)

    def test_scan_duplicates_finds_same_content_active_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(root / "knowledge_bases" / "a-at2026-03-16-10-00.md", "same")
            _write(root / "checklist-forconsistency-evaluation" / "b-at2026-03-16-10-01.md", "same")

            result = run_cli("scan-duplicates", "--skill-dir", str(root), check=False)
            payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(len(payload["duplicate_groups"]), 1)

    def test_audit_fails_on_order_violation_and_missing_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            kb = root / "knowledge_bases" / "demo-knowledge_base.md"
            cc = root / "checklist-forconsistency-evaluation" / "consistency-checklist-at2026-03-16-10-01.md"
            impl = root / "checklist-forimplementation" / "implementation-checklist-at2026-03-16-10-00.md"
            _write(cc, "consistency")
            time.sleep(0.02)
            _write(kb, "kb")
            time.sleep(0.02)
            _write(impl, "implementation")

            result = run_cli("audit", "--skill-dir", str(root), check=False)
            payload = json.loads(result.stdout)

        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(payload["status"], "failed")
        self.assertIn("minute-level timestamp missing", " ".join(payload["order"]["errors"]))


class StaleCandidateTests(unittest.TestCase):
    """scan-stale-candidates 서브커맨드 테스트."""

    def test_target_newer_is_candidate_stale(self) -> None:
        """문서보다 target이 최신이면 candidate_stale."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(root / "scripts" / "foo.py", "print('hello')")
            time.sleep(0.05)
            _write(
                root / "references" / "doc-at2026-03-25-10-00.md",
                "참조: `scripts/foo.py`\n",
            )
            time.sleep(0.05)
            # target을 doc보다 나중에 수정
            (root / "scripts" / "foo.py").write_text("print('updated')")

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            payload = json.loads(result.stdout)

        stale = [e for e in payload["entries"] if e["status"] == "candidate_stale"]
        self.assertTrue(len(stale) > 0)

    def test_doc_newer_is_fresh(self) -> None:
        """문서가 target보다 최신이면 fresh."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(root / "scripts" / "bar.py", "x = 1")
            time.sleep(0.05)
            _write(
                root / "references" / "ref-at2026-03-25-10-00.md",
                "참조: `scripts/bar.py`\n",
            )

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            payload = json.loads(result.stdout)

        fresh = [e for e in payload["entries"] if e["status"] == "fresh"]
        self.assertTrue(len(fresh) > 0)

    def test_no_targets_is_needs_mapping(self) -> None:
        """target을 하나도 못 찾으면 needs_mapping."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root / "references" / "orphan-at2026-03-25-10-00.md",
                "이 문서에는 경로 참조가 없습니다.\n",
            )

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            payload = json.loads(result.stdout)

        mapping = [e for e in payload["entries"] if e["status"] == "needs_mapping"]
        self.assertTrue(len(mapping) > 0)

    def test_broken_path_is_missing_target(self) -> None:
        """target path가 존재하지 않으면 missing_target."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root / "references" / "broken-at2026-03-25-10-00.md",
                "참조: `scripts/nonexistent_xyz.py`\n",
            )

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            payload = json.loads(result.stdout)

        missing = [e for e in payload["entries"] if e["status"] == "missing_target"]
        self.assertTrue(len(missing) > 0)

    def test_legacy_excluded_by_default(self) -> None:
        """legacy/ 디렉토리는 기본 제외."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root / "references" / "legacy" / "old-at2026-03-20-10-00.md",
                "legacy doc `scripts/old.py`\n",
            )

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["total"], 0)

    def test_fail_on_candidate_exit_code(self) -> None:
        """--fail-on-candidate일 때 candidate_stale → exit 1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(root / "scripts" / "target.py", "v1")
            time.sleep(0.05)
            _write(
                root / "references" / "doc-at2026-03-25-10-00.md",
                "참조: `scripts/target.py`\n",
            )
            time.sleep(0.05)
            (root / "scripts" / "target.py").write_text("v2")

            # --fail-on-candidate 없으면 exit 0
            r1 = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            self.assertEqual(r1.returncode, 0)

            # --fail-on-candidate 있으면 exit 1
            r2 = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root),
                "--fail-on-candidate", check=False,
            )
            self.assertEqual(r2.returncode, 1)

    def test_semantic_owner_classification(self) -> None:
        """checklist-for* → rule_bearing, references/ 일반문서 → claim_heavy, index → informational."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root / "checklist-forconsistency-evaluation" / "check-at2026-03-25-10-00.md",
                "checklist `scripts/a.py`\n",
            )
            _write(
                root / "references" / "general-at2026-03-25-10-00.md",
                "general ref `scripts/b.py`\n",
            )
            _write(
                root / "references" / "fields-spec-at2026-03-25-10-00.md",
                "fields `scripts/c.py`\n",
            )
            _write(
                root / "references" / "index-at2026-03-25-10-00.md",
                "index `scripts/d.py`\n",
            )
            _write(root / "scripts" / "a.py", "a")
            _write(root / "scripts" / "b.py", "b")
            _write(root / "scripts" / "c.py", "c")
            _write(root / "scripts" / "d.py", "d")

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            payload = json.loads(result.stdout)

        by_path = {e["doc_path"]: e for e in payload["entries"]}

        # checklist → rule_bearing
        checklist_entry = [v for k, v in by_path.items() if "checklist" in k][0]
        self.assertEqual(checklist_entry["doc_kind"], "rule_bearing")
        self.assertEqual(checklist_entry["semantic_owner"], "rule_bearing")
        self.assertEqual(checklist_entry["recheck_owner"], "doc-code-sync-checker")

        # general references → claim_heavy
        general_entry = [v for k, v in by_path.items() if "general" in k][0]
        self.assertEqual(general_entry["doc_kind"], "claim_heavy")
        self.assertEqual(general_entry["semantic_owner"], "claim_heavy")
        self.assertEqual(general_entry["recheck_owner"], "claim-verifier")

        # fields-spec → rule_bearing (path keyword match)
        fields_entry = [v for k, v in by_path.items() if "fields" in k][0]
        self.assertEqual(fields_entry["doc_kind"], "rule_bearing")

        # index → informational
        index_entry = [v for k, v in by_path.items() if "index" in k][0]
        self.assertEqual(index_entry["doc_kind"], "informational")
        self.assertEqual(index_entry["recheck_owner"], "manual-review")

    def test_review_record_detection(self) -> None:
        """references는 frontmatter, KB는 sidecar review record를 감지한다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root / "references" / "doc-at2026-03-25-10-00.md",
                "---\nfreshness_review:\n  reviewed_at: 2026-03-27T14:30:00+09:00\n---\n`scripts/a.py`\n",
            )
            _write(
                root / "knowledge_bases" / "kb-at2026-03-25-10-00.md",
                "`scripts/b.py`\n",
            )
            _write(
                root / "knowledge_bases" / ".freshness_audit.yaml",
                'entries:\n  - file: "kb-at2026-03-25-10-00.md"\n    freshness_review:\n      reviewed_at: "2026-03-27T14:30:00+09:00"\n',
            )
            _write(root / "scripts" / "a.py", "a")
            _write(root / "scripts" / "b.py", "b")

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root), check=False,
            )
            payload = json.loads(result.stdout)

        by_path = {e["doc_path"]: e for e in payload["entries"]}
        ref_entry = [v for k, v in by_path.items() if "references/" in k][0]
        kb_entry = [v for k, v in by_path.items() if "knowledge_bases/" in k][0]

        self.assertEqual(ref_entry["review_record_expected"], "frontmatter")
        self.assertTrue(ref_entry["review_record_present"])
        self.assertEqual(kb_entry["review_record_expected"], "sidecar")
        self.assertTrue(kb_entry["review_record_present"])

    def test_audit_include_stale(self) -> None:
        """audit --include-stale가 stale_candidates 섹션을 포함한다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            kb = root / "knowledge_bases" / "kb-at2026-03-16-10-00.md"
            cc = root / "checklist-forconsistency-evaluation" / "cc-at2026-03-16-10-01.md"
            _write(kb, "kb ref `scripts/x.py`")
            time.sleep(0.02)
            _write(cc, "cc ref `scripts/x.py`")

            result = run_cli(
                "audit", "--skill-dir", str(root), "--include-stale", check=False,
            )
            payload = json.loads(result.stdout)

        self.assertIn("stale_candidates", payload)
        self.assertIn("total", payload["stale_candidates"])

    def test_scope_filter(self) -> None:
        """--scope references는 references만 스캔한다."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write(
                root / "references" / "ref-at2026-03-25-10-00.md",
                "ref only\n",
            )
            _write(
                root / "knowledge_bases" / "kb-at2026-03-25-10-00.md",
                "kb only\n",
            )

            result = run_cli(
                "scan-stale-candidates", "--skill-dir", str(root),
                "--scope", "references", check=False,
            )
            payload = json.loads(result.stdout)

        self.assertEqual(payload["total"], 1)
        self.assertIn("references", payload["entries"][0]["doc_path"])


if __name__ == "__main__":
    unittest.main()
