# Graph Sample Fixture

Minimal canonical graph fixture for export smoke.

## Fixture Bundle Form

This fixture bundle contains:
- `normalized_graph.json`
- `nodes.jsonl`
- `edges.jsonl`
- optional `graph_meta.json`

## Rule

- `normalized_graph.json` remains the canonical full snapshot in this fixture.
- `nodes.jsonl` and `edges.jsonl` are split-form exports of the same graph.
- `graph_meta.json` is an optional sidecar used when split-form fixture consumption needs preserved top-level metadata without consulting `normalized_graph.json`.
