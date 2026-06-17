# dependency-slice-planner seed_refinement_report contract

- generated_at: `2026-03-19T21:06:17+09:00`
- contract_family: `seed_refinement_report_contract`
- version: `v0.1.0`

## Required Top-Level Fields

- `status`
- `generated_at`
- `algorithm_family`
- `version`
- `input_artifacts`
- `runtime_overlay_used`
- `recommendation_count`
- `recommendations`
- `next_candidate`

## Recommendation Required Fields

- `candidate_id`
- `root_dir`
- `seed_action`
- `recommendation`
- `target_candidate_ids`
- `scores`
- `signal_counts`
- `risk_signals`
- `reason`

## Recommendation Enum

- `keep_seed`
- `merge_with_neighbor`
- `re_cut_with_dependency_overlay`
- `mark_analysis_only`
- `stop_split`
