# dependency-slice-planner vertical slice - stop_rule_evaluator

- created_at: `2026-03-19-17-41`
- source_of_truth: `knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md`
- implementation_target: `stop_rule_evaluator`

## Goal

`seed_to_refinement_report` 결과를 읽고 각 candidate를 `write_safe`, `analysis_only`, `do_not_split` gate로 분류한다. 이 단계의 목적은 refinement recommendation을 final proposal 직전의 stop-rule decision으로 바꾸는 것이다.

## Input

- `seed_refinement_report.json`

## Output

- machine-readable stop rule evaluation artifact
- per-candidate fields:
  - `refinement_recommendation`
  - `stop_decision`
  - `triggered_stop_rules`
  - `scores`
  - `signal_counts`
- top-level `next_candidate = final_slice_proposal_generator`

## Decision Rules

- `stop_split` 또는 `stop_candidate`면 `do_not_split`
- runtime/path-order uncertainty, high cross-edge density, re-cut recommendation은 `analysis_only`
- triggered stop rule이 없으면 `write_safe`

## Smoke Artifacts

- contract:
  - `stop-rule-evaluation-contract-smoke-at2026-03-19-17-41.json`
  - `stop-rule-evaluation-contract-smoke-at2026-03-19-17-41.md`
- valid:
  - `stop-rule-evaluation-validation-smoke-at2026-03-19-17-41.json`
  - `stop-rule-evaluation-validation-smoke-at2026-03-19-17-41.md`
- invalid:
  - `stop-rule-evaluation-invalid-validation-smoke-at2026-03-19-17-41.json`
  - `stop-rule-evaluation-invalid-validation-smoke-at2026-03-19-17-41.md`

## Current Result

- valid sample:
  - `write_safe = 1`
  - `do_not_split = 1`
  - `analysis_only = 0`
  - `next_candidate = final_slice_proposal_generator`
- invalid sample:
  - `status = invalid_inputs`
  - invalid family: `seed_refinement_report`

## Notes

- v0.1은 stop rule 전체를 별도 launch policy로 확장하지 않고, final slice proposal 직전의 gate artifact로 둔다.
- `analysis_only`와 `do_not_split`을 분리해서 이후 `parallel_slices.json`과 `do_not_split_regions.json` 생성에 바로 쓰게 한다.
