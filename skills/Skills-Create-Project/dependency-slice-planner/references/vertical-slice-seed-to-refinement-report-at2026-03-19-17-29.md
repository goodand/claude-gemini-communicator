# dependency-slice-planner vertical slice - seed_to_refinement_report

- created_at: `2026-03-19-17-29`
- source_of_truth: `knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md`
- implementation_target: `seed_to_refinement_report`

## Goal

contract phase 다음 첫 algorithm slice로, `inventory_snapshot`, `slice_seed_candidates`, `static_dependency_overlay`, optional `runtime_overlay`를 읽고 각 seed에 대해 `keep_seed`, `merge_with_neighbor`, `re_cut_with_dependency_overlay`, `mark_analysis_only`, `stop_split` recommendation을 생성한다.

## Inputs

- `inventory_snapshot.json`
- `slice_seed_candidates.json`
- `static_dependency_overlay.json`
- `runtime_overlay.json` (optional)

## Output

- machine-readable refinement artifact
- top-level `next_candidate = stop_rule_evaluator`
- per-candidate scoring:
  - `size_score`
  - `internal_cohesion_score`
  - `cross_edge_ratio`
  - `shared_hub_penalty`
  - `runtime_condition_penalty`
  - `ownership_conflict_penalty`

## Smoke Artifacts

- contract:
  - `seed-refinement-report-contract-smoke-at2026-03-19-17-29.json`
  - `seed-refinement-report-contract-smoke-at2026-03-19-17-29.md`
- valid:
  - `seed-refinement-report-validation-smoke-at2026-03-19-17-29.json`
  - `seed-refinement-report-validation-smoke-at2026-03-19-17-29.md`
- invalid:
  - `seed-refinement-report-invalid-validation-smoke-at2026-03-19-17-29.json`
  - `seed-refinement-report-invalid-validation-smoke-at2026-03-19-17-29.md`

## Current Result

- valid sample:
  - `recommendation_count = 2`
  - `keep_seed = 1`
  - `stop_split = 1`
  - `next_candidate = stop_rule_evaluator`
- invalid sample:
  - `status = invalid_inputs`
  - invalid family: `slice_seed_candidates`

## Notes

- v0.1은 graph partitioning full solver가 아니라 deterministic heuristic report다.
- longest-prefix graph matching 대신 root overlap 기반 signal 집계를 먼저 쓴다.
- 다음 조각은 `stop_rule_evaluator`로 이어서 `analysis_only / write_safe / do_not_split` gate를 명시한다.
