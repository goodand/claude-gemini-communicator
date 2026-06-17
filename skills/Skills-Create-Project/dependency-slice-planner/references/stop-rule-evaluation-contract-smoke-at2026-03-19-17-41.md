# dependency-slice-planner stop_rule_evaluation contract

- generated_at: `2026-03-19T17:41:24+09:00`
- contract_family: `stop_rule_evaluation_contract`
- version: `v0.1.0`

## Required Top-Level Fields

- `status`
- `generated_at`
- `algorithm_family`
- `version`
- `input_artifacts`
- `evaluation_count`
- `decision_summary`
- `evaluations`
- `next_candidate`

## Evaluation Required Fields

- `candidate_id`
- `root_dir`
- `refinement_recommendation`
- `stop_decision`
- `triggered_stop_rules`
- `scores`
- `signal_counts`
- `reason`

## Decision Enum

- `write_safe`
- `analysis_only`
- `do_not_split`

## Trigger Enum

- `single_large_hub_file`
- `wrapper_indirection_uncertainty`
- `high_cross_edge_density`
- `path_order_runtime_dependence`
- `coordination_cost_increase`
