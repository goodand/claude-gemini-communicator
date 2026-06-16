# dependency-slice-planner extension - seed_to_refinement_report merge target selection

- created_at: `2026-03-19-21-02`
- extended_slice: `seed_to_refinement_report`

## Goal

`merge_with_neighbor` recommendation이 나왔을 때 실제 `target_candidate_ids`를 deterministic하게 채운다.

## Rule

- static overlay edge text에서 현재 candidate root와 다른 candidate root가 같이 등장한 횟수를 센다.
- touch count가 가장 높은 candidate를 merge target으로 선택한다.
- 동률이면 `candidate_id` lexical order로 tie-break 한다.
- merge recommendation이 아니면 `target_candidate_ids = []`.

## Evidence

- updated contract:
  - `seed-refinement-report-contract-smoke-at2026-03-19-21-02.json`
  - `seed-refinement-report-contract-smoke-at2026-03-19-21-02.md`
- merge-target valid sample:
  - `seed-refinement-report-merge-target-validation-smoke-at2026-03-19-21-02.json`
  - `seed-refinement-report-merge-target-validation-smoke-at2026-03-19-21-02.md`

## Current Result

- `seed_01`
  - `recommendation = merge_with_neighbor`
  - `target_candidate_ids = ["seed_02"]`

## Note

- v0.1 core planner는 유지하고, merge recommendation을 실제 handoff planning에 더 가까운 shape로 보강한 확장이다.
