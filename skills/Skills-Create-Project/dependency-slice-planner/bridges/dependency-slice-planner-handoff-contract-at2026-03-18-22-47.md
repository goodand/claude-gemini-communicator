# Handoff Contract — Dependency Slice Planner

## Input contract

- `tree_snapshot`
- `graph_summary`
- `risk_boundaries`
- `size_thresholds`
- `entrypoint_hints`
- `artifact_destination`

## Output contract

- `proposed_slices`
- `why_safe`
- `do_not_split_regions`
- `parallel_safe_summary`
- `follow_up_probes`

## Rule

- Only pass the minimum file links and packet fields required for slice planning.
- If static graph evidence is incomplete, return a probe request rather than guessing runtime behavior.
