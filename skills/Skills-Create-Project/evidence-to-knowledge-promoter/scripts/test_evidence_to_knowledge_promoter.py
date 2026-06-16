#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("evidence_to_knowledge_promoter.py")


SUPPORT_AUDIT_FIXTURE = {
    "status": "ok",
    "support_ratio": 1.0,
    "supported_entries": [
        {
            "entry_id": "typed_mismatch:status",
            "finding_family": "typed_mismatch",
            "kind": "enum_value_set_changed",
            "name": "status",
            "observed_bucket": "contract_value_changed",
            "trace_status": "verified_evidence",
            "action": "status enum 정렬 검토",
        }
    ],
    "missing_evidence_entries": [],
    "residual_uncertainty_entries": [],
}


BASELINE_DIFF_FIXTURE = {
    "status": "computed",
    "metrics": {
        "typed_mismatch_count": {
            "before": 1,
            "after": 0,
            "delta": -1,
            "relative_change": -1.0,
            "reduction_after_fix": 1.0,
        },
        "zero_drift_pair_rate": {
            "before": 0.0,
            "after": 1.0,
            "delta": 1.0,
            "relative_change": None,
            "reduction_after_fix": None,
        },
    },
}


PROMOTION_SUMMARY_WITH_LESSON = {
    "status": "ok",
    "contract_family": "promotion_candidate_summary",
    "summary_counts": {
        "finding": 1,
        "delta": 1,
        "lesson_candidate": 1,
        "residual_uncertainty": 0,
    },
    "entries": [
        {
            "kind": "lesson_candidate",
            "name": "verified-evidence-backed-fix-pattern",
            "source": "diff.json",
            "value": {
                "delta_count": 2,
                "finding_count": 1,
                "support_ratio": 1.0,
                "repetition_count": 2,
            },
            "evidence": "typed_mismatch_count",
            "promotion_decision": "candidate",
            "reason": "candidate lesson",
        }
    ],
}

PROMOTION_TRIGGER_EVAL_PROMOTE = {
    "status": "ok",
    "contract_family": "promotion_trigger_evaluation",
    "summary_counts": {
        "finding": 1,
        "delta": 1,
        "lesson_candidate": 1,
        "residual_uncertainty": 0,
    },
    "decisions": {
        "hybrid_kb": {
            "decision": "promote",
            "reason": "promote",
        },
        "canonical_design_kb": {
            "decision": "hold",
            "reason": "hold",
        },
    },
}

PROMOTION_TRIGGER_EVAL_HOLD = {
    "status": "ok",
    "contract_family": "promotion_trigger_evaluation",
    "summary_counts": {
        "finding": 2,
        "delta": 3,
        "lesson_candidate": 0,
        "residual_uncertainty": 1,
    },
    "decisions": {
        "hybrid_kb": {
            "decision": "hold",
            "reason": "hold",
        },
        "canonical_design_kb": {
            "decision": "hold",
            "reason": "hold",
        },
    },
}

PROMOTION_TRIGGER_EVAL_CANDIDATE = {
    "status": "ok",
    "contract_family": "promotion_trigger_evaluation",
    "summary_counts": {
        "finding": 1,
        "delta": 1,
        "lesson_candidate": 1,
        "residual_uncertainty": 0,
    },
    "decisions": {
        "hybrid_kb": {
            "decision": "promote",
            "reason": "promote",
        },
        "canonical_design_kb": {
            "decision": "candidate",
            "reason": "candidate",
        },
    },
}


class EvidenceToKnowledgePromoterTest(unittest.TestCase):
    def _write_json(self, directory: Path, name: str, payload: dict[str, object]) -> Path:
        path = directory / name
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path

    def test_help(self) -> None:
        result = subprocess.run(
            ["python3", str(SCRIPT), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("build-promotion-summary", result.stdout)
        self.assertIn("evaluate-promotion-trigger", result.stdout)
        self.assertIn("build-hybrid-kb-patch-plan", result.stdout)
        self.assertIn("build-canonical-kb-patch-plan", result.stdout)

    def test_build_promotion_summary_outputs_categories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            support_path = self._write_json(base, "support.json", SUPPORT_AUDIT_FIXTURE)
            diff_path = self._write_json(base, "diff.json", BASELINE_DIFF_FIXTURE)

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-promotion-summary",
                    "--support-audit",
                    str(support_path),
                    "--baseline-diff",
                    str(diff_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["summary_counts"]["finding"], 1)
            self.assertEqual(payload["summary_counts"]["delta"], 2)
            self.assertEqual(payload["summary_counts"]["lesson_candidate"], 1)
            self.assertEqual(payload["summary_counts"]["residual_uncertainty"], 0)

    def test_hold_when_missing_evidence_exists(self) -> None:
        support = dict(SUPPORT_AUDIT_FIXTURE)
        support["missing_evidence_entries"] = [
            {
                "entry_id": "artifact_path:missing",
                "finding_family": "artifact_path",
                "kind": "artifact_path",
                "name": "missing-artifact",
                "observed_bucket": "missing_contract_unit",
                "trace_status": "missing_evidence",
                "action": "누락 artifact 생성 검토",
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            support_path = self._write_json(base, "support.json", support)
            diff_path = self._write_json(base, "diff.json", BASELINE_DIFF_FIXTURE)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-promotion-summary",
                    "--support-audit",
                    str(support_path),
                    "--baseline-diff",
                    str(diff_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["summary_counts"]["lesson_candidate"], 0)
            self.assertEqual(payload["summary_counts"]["residual_uncertainty"], 1)

    def test_writes_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            support_path = self._write_json(base, "support.json", SUPPORT_AUDIT_FIXTURE)
            diff_path = self._write_json(base, "diff.json", BASELINE_DIFF_FIXTURE)
            out_json = base / "summary.json"
            out_md = base / "summary.md"

            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-promotion-summary",
                    "--support-audit",
                    str(support_path),
                    "--baseline-diff",
                    str(diff_path),
                    "--output-json",
                    str(out_json),
                    "--output-md",
                    str(out_md),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(out_json.exists())
            self.assertTrue(out_md.exists())
            self.assertIn("promotion summary", out_md.read_text(encoding="utf-8"))

    def test_evaluate_promotion_trigger_holds_when_residual_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            support_path = self._write_json(base, "support.json", SUPPORT_AUDIT_FIXTURE | {
                "missing_evidence_entries": [
                    {
                        "entry_id": "artifact_path:missing",
                        "finding_family": "artifact_path",
                        "kind": "artifact_path",
                        "name": "missing-artifact",
                        "observed_bucket": "missing_contract_unit",
                        "trace_status": "missing_evidence",
                        "action": "누락 artifact 생성 검토",
                    }
                ]
            })
            diff_path = self._write_json(base, "diff.json", BASELINE_DIFF_FIXTURE)
            summary_path = base / "summary.json"
            subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-promotion-summary",
                    "--support-audit",
                    str(support_path),
                    "--baseline-diff",
                    str(diff_path),
                    "--output-json",
                    str(summary_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "evaluate-promotion-trigger",
                    "--summary",
                    str(summary_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decisions"]["hybrid_kb"]["decision"], "hold")
            self.assertEqual(payload["decisions"]["canonical_design_kb"]["decision"], "hold")

    def test_evaluate_promotion_trigger_can_promote(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            summary_path = self._write_json(base, "summary.json", PROMOTION_SUMMARY_WITH_LESSON)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "evaluate-promotion-trigger",
                    "--summary",
                    str(summary_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["decisions"]["hybrid_kb"]["decision"], "promote")
            self.assertEqual(payload["decisions"]["canonical_design_kb"]["decision"], "candidate")

    def test_build_patch_plan_hold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            summary_path = self._write_json(base, "summary.json", {
                "status": "ok",
                "contract_family": "promotion_candidate_summary",
                "summary_counts": PROMOTION_TRIGGER_EVAL_HOLD["summary_counts"],
                "entries": [],
            })
            eval_path = self._write_json(base, "eval.json", PROMOTION_TRIGGER_EVAL_HOLD)
            target_kb = self._write_json(base, "kb.json", {"name": "dummy"})
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-hybrid-kb-patch-plan",
                    "--summary",
                    str(summary_path),
                    "--evaluation",
                    str(eval_path),
                    "--target-kb",
                    str(target_kb),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["patch_decision"], "hold")
            self.assertEqual(payload["planned_operations"][0]["op"], "hold")

    def test_build_patch_plan_promote(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            summary_path = self._write_json(base, "summary.json", PROMOTION_SUMMARY_WITH_LESSON)
            eval_path = self._write_json(base, "eval.json", PROMOTION_TRIGGER_EVAL_PROMOTE)
            target_kb = self._write_json(base, "kb.json", {"name": "dummy"})
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-hybrid-kb-patch-plan",
                    "--summary",
                    str(summary_path),
                    "--evaluation",
                    str(eval_path),
                    "--target-kb",
                    str(target_kb),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["patch_decision"], "promote")
            ops = payload["planned_operations"]
            self.assertTrue(any(op["entry_kind"] == "lesson_candidate" for op in ops))

    def test_evaluate_canonical_candidate_hold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            summary_path = self._write_json(base, "summary.json", {
                "status": "ok",
                "contract_family": "promotion_candidate_summary",
                "summary_counts": {
                    "finding": 2,
                    "delta": 1,
                    "lesson_candidate": 0,
                    "residual_uncertainty": 1,
                },
                "entries": [],
            })
            eval_path = self._write_json(base, "eval.json", PROMOTION_TRIGGER_EVAL_HOLD)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "evaluate-canonical-candidate",
                    "--summary",
                    str(summary_path),
                    "--evaluation",
                    str(eval_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["canonical_decision"]["decision"], "hold")
            self.assertIn("lesson_candidate_present", payload["missing_requirements"])

    def test_evaluate_canonical_candidate_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            summary_path = self._write_json(base, "summary.json", {
                "status": "ok",
                "contract_family": "promotion_candidate_summary",
                "summary_counts": {
                    "finding": 1,
                    "delta": 1,
                    "lesson_candidate": 1,
                    "residual_uncertainty": 0,
                },
                "entries": [
                    {
                        "kind": "lesson_candidate",
                        "name": "verified-evidence-backed-fix-pattern",
                        "source": "diff.json",
                        "value": {
                            "repetition_count": 2,
                        },
                        "evidence": "typed_mismatch_count",
                        "promotion_decision": "candidate",
                        "reason": "candidate lesson",
                    }
                ],
            })
            eval_path = self._write_json(base, "eval.json", PROMOTION_TRIGGER_EVAL_CANDIDATE)
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "evaluate-canonical-candidate",
                    "--summary",
                    str(summary_path),
                    "--evaluation",
                    str(eval_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["canonical_decision"]["decision"], "candidate")
            self.assertEqual(payload["missing_requirements"], [])

    def test_build_canonical_patch_plan_hold(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            summary_path = self._write_json(base, "summary.json", {
                "status": "ok",
                "contract_family": "promotion_candidate_summary",
                "summary_counts": PROMOTION_TRIGGER_EVAL_HOLD["summary_counts"],
                "entries": [],
            })
            eval_path = self._write_json(base, "eval.json", {
                "status": "ok",
                "contract_family": "canonical_candidate_evaluation",
                "canonical_decision": {
                    "decision": "hold",
                    "reason": "hold",
                },
                "missing_requirements": ["lesson_candidate_present"],
                "candidate_lessons": [],
            })
            target_kb = base / "canonical.md"
            target_kb.write_text("# Canonical\n\n## Canonical Design Takeaways\n\n- existing\n", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-canonical-kb-patch-plan",
                    "--summary",
                    str(summary_path),
                    "--evaluation",
                    str(eval_path),
                    "--target-kb",
                    str(target_kb),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["patch_decision"], "hold")
            self.assertEqual(payload["planned_operations"][0]["op"], "hold")

    def test_build_canonical_patch_plan_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            summary_path = self._write_json(base, "summary.json", {
                "status": "ok",
                "contract_family": "promotion_candidate_summary",
                "summary_counts": {
                    "finding": 1,
                    "delta": 1,
                    "lesson_candidate": 1,
                    "residual_uncertainty": 0,
                },
                "entries": [
                    {
                        "kind": "lesson_candidate",
                        "name": "verified-evidence-backed-fix-pattern",
                        "source": "diff.json",
                        "value": {
                            "repetition_count": 2,
                        },
                        "evidence": "typed_mismatch_count",
                        "promotion_decision": "candidate",
                        "reason": "candidate lesson",
                    },
                    {
                        "kind": "delta",
                        "name": "typed_mismatch_count",
                        "source": "diff.json",
                        "value": {
                            "before": 1,
                            "after": 0,
                            "reduction_after_fix": 1.0,
                        },
                        "evidence": "typed_mismatch_count",
                        "promotion_decision": "candidate",
                        "reason": "delta",
                    },
                ],
            })
            eval_path = self._write_json(base, "eval.json", {
                "status": "ok",
                "contract_family": "canonical_candidate_evaluation",
                "canonical_decision": {
                    "decision": "candidate",
                    "reason": "candidate",
                },
                "missing_requirements": [],
                "candidate_lessons": [
                    {
                        "name": "verified-evidence-backed-fix-pattern",
                        "evidence": "typed_mismatch_count",
                        "repetition_count": 2,
                    }
                ],
            })
            target_kb = base / "canonical.md"
            target_kb.write_text("# Canonical\n\n## Canonical Design Takeaways\n\n- existing\n", encoding="utf-8")
            result = subprocess.run(
                [
                    "python3",
                    str(SCRIPT),
                    "build-canonical-kb-patch-plan",
                    "--summary",
                    str(summary_path),
                    "--evaluation",
                    str(eval_path),
                    "--target-kb",
                    str(target_kb),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["patch_decision"], "candidate")
            ops = payload["planned_operations"]
            self.assertEqual(len(ops), 1)
            self.assertEqual(ops[0]["entry_kind"], "lesson_candidate")
            self.assertEqual(ops[0]["target_section"], "Canonical Design Takeaways")

if __name__ == "__main__":
    unittest.main()
