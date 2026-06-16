# dependency-slice-planner stop_rule_evaluator

- generated_at: `2026-03-19T17:41:24+09:00`
- status: `ok`
- algorithm_family: `stop_rule_evaluator`
- evaluation_count: `2`
- next_candidate: `final_slice_proposal_generator`

## Decision Summary

- `write_safe`: `1`
- `analysis_only`: `0`
- `do_not_split`: `1`

## Evaluations

### seed_01
- root_dir: `src/core`
- refinement_recommendation: `keep_seed`
- stop_decision: `write_safe`
- triggered_stop_rules: `none`
- reason: refinement_recommendation=keep_seed; stop_decision=write_safe; triggered_stop_rules=none

### seed_02
- root_dir: `src/bootstrap.py`
- refinement_recommendation: `stop_split`
- stop_decision: `do_not_split`
- triggered_stop_rules: `single_large_hub_file`
- reason: refinement_recommendation=stop_split; stop_decision=do_not_split; triggered_stop_rules=single_large_hub_file

