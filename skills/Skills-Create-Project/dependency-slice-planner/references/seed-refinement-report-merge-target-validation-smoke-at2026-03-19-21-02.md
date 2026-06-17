# dependency-slice-planner seed_to_refinement_report

- generated_at: `2026-03-19T21:06:17+09:00`
- status: `ok`
- algorithm_family: `seed_to_refinement_report`
- runtime_overlay_used: `False`
- recommendation_count: `3`
- next_candidate: `stop_rule_evaluator`

## Recommendation Summary

- `keep_seed`: `0`
- `merge_with_neighbor`: `3`
- `re_cut_with_dependency_overlay`: `0`
- `mark_analysis_only`: `0`
- `stop_split`: `0`

## Recommendations

### seed_01
- root_dir: `src/api`
- seed_action: `merge_candidate`
- recommendation: `merge_with_neighbor`
- scores: `size=1.0`, `cohesion=0.75`, `cross_edge_ratio=0.5`
- risk_signals: `cross_edge_ratio, ownership_conflict_penalty`
- reason: seed_action=merge_candidate; size_score=1.0; cross_edge_ratio=0.5; target_candidate_ids=seed_02; risk_signals=cross_edge_ratio,ownership_conflict_penalty

### seed_02
- root_dir: `src/core`
- seed_action: `keep`
- recommendation: `merge_with_neighbor`
- scores: `size=0.75`, `cohesion=0.75`, `cross_edge_ratio=0.5`
- risk_signals: `cross_edge_ratio, ownership_conflict_penalty`
- reason: seed_action=keep; size_score=0.75; cross_edge_ratio=0.5; target_candidate_ids=seed_01; risk_signals=cross_edge_ratio,ownership_conflict_penalty

### seed_03
- root_dir: `src/jobs`
- seed_action: `keep`
- recommendation: `merge_with_neighbor`
- scores: `size=1.0`, `cohesion=0.75`, `cross_edge_ratio=0.5`
- risk_signals: `cross_edge_ratio, ownership_conflict_penalty`
- reason: seed_action=keep; size_score=1.0; cross_edge_ratio=0.5; target_candidate_ids=seed_01; risk_signals=cross_edge_ratio,ownership_conflict_penalty

