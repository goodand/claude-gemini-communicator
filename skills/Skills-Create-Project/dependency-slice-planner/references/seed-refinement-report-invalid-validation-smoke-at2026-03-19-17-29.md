# dependency-slice-planner seed_to_refinement_report

- generated_at: `2026-03-19T17:29:38+09:00`
- status: `invalid_inputs`
- algorithm_family: `seed_to_refinement_report`
- runtime_overlay_used: `False`
- recommendation_count: `None`
- next_candidate: `None`

## Errors

- candidates[1].candidate_id must be non-empty str
- candidates[1].root_dir must be non-empty str
- candidates[1].file_count must be non-negative int
- candidates[1].total_bytes must be non-negative int
- candidates[1].max_depth must be non-negative int
- candidates[1].seed_action must be one of ['keep', 'merge_candidate', 'split_candidate', 'stop_candidate']
- candidates[1].tags must contain non-empty strings
- candidates[1].reason must be non-empty str
