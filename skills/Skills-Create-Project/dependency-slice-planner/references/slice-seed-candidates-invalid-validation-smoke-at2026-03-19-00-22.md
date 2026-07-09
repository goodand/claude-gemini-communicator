# dependency-slice-planner slice_seed_candidates validation

- generated_at: `2026-03-19T00:24:49+09:00`
- input_candidates: `dependency-slice-planner/references/slice-seed-candidates-invalid-sample-at2026-03-19-00-22.json`
- status: `invalid`
- error_count: `8`

## Errors

- candidates[1].candidate_id must be non-empty str
- candidates[1].root_dir must be non-empty str
- candidates[1].file_count must be non-negative int
- candidates[1].total_bytes must be non-negative int
- candidates[1].max_depth must be non-negative int
- candidates[1].seed_action must be one of ['keep', 'merge_candidate', 'split_candidate', 'stop_candidate']
- candidates[1].tags must contain non-empty strings
- candidates[1].reason must be non-empty str
