# dependency-slice-planner final_slice_proposal_generator

- generated_at: `2026-03-19T21:56:02+09:00`
- status: `ok`
- algorithm_family: `final_slice_proposal_generator`
- parallel_slice_count: `2`
- do_not_split_count: `0`
- next_candidate: `None`

## Parallel Slices

### slice_01
- source_candidate_id: `seed_01`
- classification: `write_safe`
- root_dirs: `src/core`
- total_bytes: `3448`
- language_buckets: `{'markdown': 1, 'python': 3}`
- reason: refinement_recommendation=keep_seed; stop_decision=write_safe; triggered_stop_rules=none

### slice_02
- source_candidate_id: `seed_02`
- classification: `analysis_only`
- root_dirs: `src/bootstrap.py`
- total_bytes: `512`
- language_buckets: `{'python': 1}`
- reason: refinement_recommendation=keep_seed; stop_decision=analysis_only; triggered_stop_rules=path_order_runtime_dependence

## Do Not Split Regions

- none
