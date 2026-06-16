# dependency-slice-planner seed_to_refinement_report

- generated_at: `2026-03-19T17:29:38+09:00`
- status: `ok`
- algorithm_family: `seed_to_refinement_report`
- runtime_overlay_used: `True`
- recommendation_count: `2`
- next_candidate: `stop_rule_evaluator`

## Recommendation Summary

- `keep_seed`: `1`
- `merge_with_neighbor`: `0`
- `re_cut_with_dependency_overlay`: `0`
- `mark_analysis_only`: `0`
- `stop_split`: `1`

## Recommendations

### seed_01
- root_dir: `src/core`
- seed_action: `keep`
- recommendation: `keep_seed`
- scores: `size=0.75`, `cohesion=0.6042`, `cross_edge_ratio=0.25`
- risk_signals: `shared_hub_penalty, ownership_conflict_penalty`
- reason: seed_action=keep; size_score=0.75; cross_edge_ratio=0.25; risk_signals=shared_hub_penalty,ownership_conflict_penalty

### seed_02
- root_dir: `src/bootstrap.py`
- seed_action: `stop_candidate`
- recommendation: `stop_split`
- scores: `size=0.5`, `cohesion=0.6667`, `cross_edge_ratio=0.0`
- risk_signals: `large_single_file`
- reason: seed_action=stop_candidate; size_score=0.5; cross_edge_ratio=0.0; risk_signals=large_single_file

