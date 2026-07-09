#!/usr/bin/env python3
"""TDD tests for kb_to_consistency_check.py."""
from __future__ import annotations

import json
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "scripts" / "kb_to_consistency_check.py"


def _write(path: Path, content: str) -> None:
    path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")


class KBToConsistencyCheckTDD(unittest.TestCase):
    maxDiff = None

    def _run_tool(self, kb_text: str, checklist_text: str) -> dict:
        if not TARGET.exists():
            self.fail(f"Missing target script: {TARGET}")

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            kb_path = root / "kb.md"
            checklist_path = root / "checklist.md"
            json_path = root / "coverage.json"
            report_path = root / "coverage_report.md"

            _write(kb_path, kb_text)
            _write(checklist_path, checklist_text)

            result = subprocess.run(
                [
                    "python3",
                    str(TARGET),
                    "--kb",
                    str(kb_path),
                    "--checklist",
                    str(checklist_path),
                    "--output-json",
                    str(json_path),
                    "--output-md",
                    str(report_path),
                ],
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                result.returncode,
                0,
                msg=f"stdout:\n{result.stdout}\n\nstderr:\n{result.stderr}",
            )
            self.assertTrue(json_path.exists(), "coverage.json should be created")
            self.assertTrue(report_path.exists(), "coverage_report.md should be created")
            payload = json.loads(json_path.read_text(encoding="utf-8"))
            payload["_report_text"] = report_path.read_text(encoding="utf-8")
            self.assertIn("metrics", payload)
            self.assertIn("metric_specs", payload)
            self.assertIn("human_review_queue", payload)
            self.assertIn("verdicts", payload)
            return payload

    def test_reports_missing_from_checklist_for_uncovered_kb_unit(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - `forward`: KB unit이 checklist에 반영되었는가
            - `boundary_loss`: guardrail 누락을 따로 본다
            """,
            checklist_text="""
            - [ ] `forward` 비교를 구현한다
            """,
        )
        self.assertIn("missing_from_checklist", payload["verdicts"])
        self.assertTrue(
            any("boundary_loss" in item.get("kb_unit", "") for item in payload["verdicts"]["missing_from_checklist"])
        )

    def test_reports_unsupported_in_checklist_for_unjustified_item(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - `covered`
            - `missing_from_checklist`
            """,
            checklist_text="""
            - [ ] `covered`를 판정한다
            - [ ] `unsupported_in_checklist`를 판정한다
            - [ ] `vector_db_export`를 필수 출력으로 둔다
            """,
        )
        self.assertIn("unsupported_in_checklist", payload["verdicts"])
        self.assertTrue(
            any("vector_db_export" in item.get("checklist_item", "") for item in payload["verdicts"]["unsupported_in_checklist"])
        )

    def test_reports_boundary_loss_when_guardrail_is_missing(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Current Implementation Target
            - 완전 자동 semantic judge가 아니라 candidate detector로 시작한다
            - heuristic mapping 결과를 최종 truth로 단정하지 않는다
            """,
            checklist_text="""
            - [ ] 자동 semantic judge처럼 coverage를 판정한다
            """,
        )
        self.assertIn("boundary_loss", payload["verdicts"])
        self.assertGreaterEqual(len(payload["human_review_queue"]), 1)

    def test_reports_scope_inflation_when_checklist_adds_stronger_requirement(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - v0.1은 section-level comparison으로 시작한다
            """,
            checklist_text="""
            - [ ] AST parser와 full semantic graph를 필수 구현한다
            """,
        )
        self.assertIn("scope_inflation", payload["verdicts"])
        self.assertTrue(
            any("AST parser" in item.get("checklist_item", "") for item in payload["verdicts"]["scope_inflation"])
        )

    def test_outputs_core_metrics(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - `coverage_ratio`
            - `unsupported_item_ratio`
            - `traceability_ratio`
            - `boundary_preservation_ratio`
            """,
            checklist_text="""
            - [ ] `coverage_ratio`를 계산한다
            - [ ] `unsupported_item_ratio`를 계산한다
            - [ ] `traceability_ratio`를 계산한다
            - [ ] `boundary_preservation_ratio`를 계산한다
            """,
        )
        for key in (
            "coverage_ratio",
            "unsupported_item_ratio",
            "traceability_ratio",
            "boundary_preservation_ratio",
        ):
            self.assertIn(key, payload["metrics"])
            self.assertIn(key, payload["metric_specs"])

    def test_metric_specs_include_formula_and_class(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - `coverage_ratio`
            - `unsupported_item_ratio`
            - `traceability_ratio`
            - `boundary_preservation_ratio`
            """,
            checklist_text="""
            - [ ] `coverage_ratio`를 계산한다
            - [ ] `unsupported_item_ratio`를 계산한다
            - [ ] `traceability_ratio`를 계산한다
            - [ ] `boundary_preservation_ratio`를 계산한다
            """,
        )
        for key, spec in payload["metric_specs"].items():
            self.assertIn("class", spec, key)
            self.assertIn("formula", spec, key)
            self.assertIn("semantic", spec, key)
            self.assertIn("current_execution_note", spec, key)
            self.assertIn("interpretation", spec, key)

    def test_markdown_report_includes_metric_metadata(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - `coverage_ratio`
            - `traceability_ratio`
            """,
            checklist_text="""
            - [ ] `coverage_ratio`를 계산한다
            - [ ] `traceability_ratio`를 계산한다
            """,
        )
        report_text = payload["_report_text"]
        self.assertIn("class: `proxy-profile`", report_text)
        self.assertIn("formula: `matched_canonical_kb_units / total_canonical_kb_units`", report_text)
        self.assertIn("interpretation:", report_text)

    def test_ignores_kb_metadata_toc_and_reference_inventory(self) -> None:
        payload = self._run_tool(
            kb_text="""
            # research URL Knowledge Base
            - ver: `v0.1.0`
            - generated_at: `2026-03-16`

            ## Table of Contents
            - [Canonical Design Takeaways](#canonical-design-takeaways)

            ## Canonical Design Takeaways
            - `forward`: KB unit이 checklist에 반영되었는가

            ## Paper-like URLs
            - [StrictDoc](https://github.com/strictdoc-project/strictdoc)
            """,
            checklist_text="""
            - [ ] `forward` 비교가 정의돼 있다
            """,
        )
        self.assertEqual(payload["metrics"]["coverage_ratio"], 1.0)
        missing_units = [item["kb_unit"] for item in payload["verdicts"]["missing_from_checklist"]]
        self.assertFalse(any("ver:" in item for item in missing_units))
        self.assertFalse(any("generated_at:" in item for item in missing_units))
        self.assertFalse(any("StrictDoc" in item for item in missing_units))
        self.assertEqual(payload["ignored_counts"]["metadata"], 2)
        self.assertEqual(payload["ignored_counts"]["toc"], 1)
        self.assertEqual(payload["ignored_counts"]["reference_inventory"], 1)

    def test_extracts_nested_kb_bullets_and_normalizes_checklist_labels(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - 최소 비교 방향은 아래 두 개다.
              - `forward`: KB unit이 checklist에 반영되었는가
              - `backward`: checklist item이 KB 근거를 갖는가
            - 출력은 단일 score보다 아래 두 층이 더 적합하다.
              - machine-readable JSON
              - human-readable markdown report
            """,
            checklist_text="""
            - [ ] **B-01**: `forward` 비교가 정의돼 있다
            - [ ] **B-02**: `backward` 비교가 정의돼 있다
            - [ ] **G-01**: machine-readable JSON 출력이 있다
            - [ ] **G-02**: human-readable markdown report 출력이 있다
            """,
        )
        unsupported = [item["checklist_item"] for item in payload["verdicts"]["unsupported_in_checklist"]]
        self.assertFalse(any("forward" in item for item in unsupported))
        self.assertFalse(any("backward" in item for item in unsupported))
        self.assertFalse(any("machine-readable json" in item.lower() for item in unsupported))
        self.assertFalse(any("human-readable markdown report" in item.lower() for item in unsupported))
        covered = [item["checklist_item"] for item in payload["verdicts"]["covered"]]
        self.assertTrue(any("`forward`" in item for item in covered))
        self.assertTrue(any("`backward`" in item for item in covered))

    def test_uses_support_units_from_reference_inventory_for_mapping(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - `covered`

            ## Paper-like URLs
            - [Example](https://example.com)
              - taxonomy: `artifact_vs_object`
              - execution_conditions: `coverage_ratio`와 `unsupported_item_ratio`를 함께 계산해야 함
              - key_idea: ambiguity가 높은 항목은 human review queue로 보낸다
            """,
            checklist_text="""
            - [ ] artifact-level과 object-level을 구분한다
            - [ ] `coverage_ratio`를 계산하거나 동등 지표가 있다
            - [ ] `unsupported_item_ratio`를 계산하거나 동등 지표가 있다
            - [ ] ambiguity가 높은 항목은 human review queue로 보낸다
            """,
        )
        unsupported = [item["checklist_item"] for item in payload["verdicts"]["unsupported_in_checklist"]]
        self.assertFalse(any("artifact-level" in item for item in unsupported))
        self.assertFalse(any("coverage_ratio" in item for item in unsupported))
        self.assertFalse(any("unsupported_item_ratio" in item for item in unsupported))
        self.assertFalse(any("ambiguity" in item for item in unsupported))
        self.assertEqual(payload["support_counts"]["support"], 3)

    def test_treats_summary_and_current_target_bullets_as_support_not_missing(self) -> None:
        payload = self._run_tool(
            kb_text="""
            ## Canonical Design Takeaways
            - 최소 비교 방향은 아래 두 개다.
              - `forward`: KB unit이 checklist에 반영되었는가
              - `backward`: checklist item이 KB 근거를 갖는가

            ## Current Implementation Target
            - 따라서 v0.1의 핵심은 아래다.
              - KB canonical unit 추출
              - checklist item 추출
            """,
            checklist_text="""
            - [ ] `forward` 비교가 정의돼 있다
            - [ ] `backward` 비교가 정의돼 있다
            """,
        )
        missing = [item["kb_unit"] for item in payload["verdicts"]["missing_from_checklist"]]
        self.assertFalse(any("최소 비교 방향은 아래 두 개다." == item for item in missing))
        self.assertFalse(any("따라서 v0.1의 핵심은 아래다." == item for item in missing))
        self.assertFalse(any("KB canonical unit 추출" == item for item in missing))
        self.assertFalse(any("checklist item 추출" == item for item in missing))
        self.assertGreaterEqual(payload["support_counts"]["support"], 4)

    def test_marks_research_index_kb_profile_when_no_canonical_units_exist(self) -> None:
        payload = self._run_tool(
            kb_text="""
            # research URL Knowledge Base
            - canonical_role: `research index`

            ## Paper-like URLs
            - [Example](https://example.com)
              - key_idea: explainability가 중요하다
              - execution_conditions: trace link가 필요하다
            """,
            checklist_text="""
            - [ ] traceability가 필요하다
            """,
        )
        self.assertEqual(payload["kb_profile"], "research_index_kb")
        self.assertIsNone(payload["metrics"]["coverage_ratio"])
        self.assertTrue(any("canonical unit이 없습니다" in warning for warning in payload["warnings"]))

    def test_marks_canonical_design_kb_when_canonical_sections_exist_without_reference_inventory(self) -> None:
        payload = self._run_tool(
            kb_text="""
            # canonical design Knowledge Base
            - canonical_role: `source of truth`
            - canonical_slice: `이 문서 전체`
            - source_research_kb: `research-index.md`

            ## Canonical Design Takeaways
            - `forward`: KB unit이 checklist에 반영되었는가

            ## Current Implementation Target
            - `compare`는 normalization 이후의 rule set 비교라는 의미를 유지한다
            """,
            checklist_text="""
            - [ ] `forward` 비교가 정의돼 있다
            - [ ] `compare`는 normalization 이후의 rule set 비교라는 의미를 유지한다
            """,
        )
        self.assertEqual(payload["kb_profile"], "canonical_design_kb")
        self.assertIsNotNone(payload["metrics"]["coverage_ratio"])

    def test_marks_hybrid_kb_when_canonical_sections_and_reference_inventory_coexist(self) -> None:
        payload = self._run_tool(
            kb_text="""
            # research URL Knowledge Base
            - canonical_role: `research/hybrid`
            - canonical_slice: `Canonical Design Takeaways`

            ## Canonical Design Takeaways
            - `forward`: KB unit이 checklist에 반영되었는가

            ## Paper-like URLs
            - [Example](https://example.com)
              - key_idea: traceability가 필요하다
            """,
            checklist_text="""
            - [ ] `forward` 비교가 정의돼 있다
            """,
        )
        self.assertEqual(payload["kb_profile"], "hybrid_kb")


if __name__ == "__main__":
    unittest.main()
