# dependency-slice-planner final_slice_proposal_generator

- generated_at: `2026-03-19T17:50:10+09:00`
- status: `ok`
- algorithm_family: `final_slice_proposal_generator`
- parallel_slice_count: `1`
- do_not_split_count: `1`
- next_candidate: `None`

## Parallel Slices

### slice_01
- source_candidate_id: `seed_01`
- classification: `write_safe`
- root_dirs: `src/core`
- reason: refinement_recommendation=keep_seed; stop_decision=write_safe; triggered_stop_rules=none

## Do Not Split Regions

- `seed_02` -> `src/bootstrap.py` (single_large_hub_file)
