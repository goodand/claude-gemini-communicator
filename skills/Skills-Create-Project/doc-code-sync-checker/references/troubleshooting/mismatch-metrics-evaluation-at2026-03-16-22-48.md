# doc-code-sync-checker mismatch metrics evaluation

- measured_at: `2026-03-16T22:48:30+09:00`
- scope: `implemented slices + first typed mismatch slice`

## Metrics

- `implemented_slice_ratio = 1.0 (4/4)`
  - class: `strict`
  - formula: `implemented_rule_kind_count / planned_rule_kind_count`
  - note: `required_field`, `path_safety`, `transition_rule`, `enum_value` 기준. typed mismatch overlay는 제외.

- `typed_mismatch_capture_rate = 1.0 (1/1)`
  - class: `strict`
  - formula: `passed_seeded_typed_mismatch_tests / total_seeded_typed_mismatch_tests`
  - note: `enum_value_set_changed` synthetic negative fixture 기준.

- `evidence_completeness_ratio = 1.0 (1/1)`
  - class: `strict-on-artifact`
  - formula: `typed_mismatch_with_doc_and_code_evidence / total_typed_mismatch`
  - note: [typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json](./typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json) 기준.

- `bucket_separation_rate = 1.0 (7/7)`
  - class: `strict`
  - formula: `cases_with_correct_bucket_separation / total_compare_evaluation_cases`
  - note: compare 계열 테스트 7건 기준.

- `report_actionability_ratio = 1.0 (4/4)`
  - class: `strict-on-artifact`
  - formula: `findings_with_action / total_findings`
  - note: finding-bearing artifact 2개 기준.

- `zero_drift_pair_rate = 1.0 (4/4)`
  - class: `proxy`
  - formula: `real_pair_smokes_with_zero_drift / total_real_pair_smokes`
  - note: `required_field`, `path_safety`, `transition_rule`, `enum_value` real pair 기준.

- `review_confirmed_precision = 1.0 (1/1)`
  - class: `provisional`
  - formula: `human_confirmed_true_findings / human_reviewed_findings`
  - note: 현재는 `forbid_absolute_path` 문서 누락 1건만 human-reviewed evidence로 존재.

- `typed_mismatch_reduction_after_fix = 1.0`
  - class: `strict-on-experiment`
  - formula: `(typed_mismatch_before_fix - typed_mismatch_after_fix) / typed_mismatch_before_fix`
  - note: pre-fix `1`, post-fix `0`, absolute reduction `1`.

## Interpretation

- 구현된 rule kind 4종은 현재 checklist 기준으로 모두 닫혀 있다.
- 첫 typed mismatch slice는 synthetic negative fixture에서 재현되며, evidence 양쪽이 모두 붙는다.
- 보고서 actionability는 현재 artifact 기준으로 충분하다.
- 다만 `zero_drift_pair_rate`는 정합성 정렬 상태를 보는 proxy이고, `review_confirmed_precision`은 표본이 1건이라 아직 약하다.

## Evidence

- pre-fix typed mismatch:
  - [typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json](./typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json)
- post-fix typed mismatch:
  - [typed-mismatch-enum-value-post-fix-smoke-report-at2026-03-16-22-48.json](./typed-mismatch-enum-value-post-fix-smoke-report-at2026-03-16-22-48.json)
