# Canonical Graph Artifact Contract

## Canonical Output Set

Canonical artifacts:
- `normalized_graph.json`
- `nodes.jsonl`
- `edges.jsonl`

Optional metadata sidecar:
- `graph_meta.json`

Optional exports:
- `graph.dot`
- `nodes.csv`
- `rels.csv`
- `neo4j_import.cypher`
- `cytoscape.json`

## Bundle Rules

### Canonical Full Snapshot

Files:
- `normalized_graph.json`

Rule:
- `normalized_graph.json` is the canonical self-describing snapshot artifact.
- top-level metadata should be preserved here first.

### Canonical Bundle With Derived Split Exports

Files:
- `normalized_graph.json`
- `nodes.jsonl`
- `edges.jsonl`
- optional `graph_meta.json`

Rule:
- `nodes.jsonl` and `edges.jsonl` are derived split exports from the same canonical graph model.
- `graph_meta.json` may be added as an optional metadata sidecar when split exports need top-level metadata preserved without consulting `normalized_graph.json`.

### Split-Only Fixture Or Export

Files:
- `nodes.jsonl`
- `edges.jsonl`
- optional `graph_meta.json`

Rule:
- this form is allowed for local fixture use, exporter smoke, and transport-oriented workflows.
- `graph_meta.json` is the preferred sidecar when split-only flows need preserved metadata such as `graph_id` or `graph_kind`.
- split-only form should not be treated as replacing `normalized_graph.json` as the canonical full snapshot.

## Minimum Metadata

Required canonical metadata:
- `graph_id`
- `generated_at`
- `source_scope`
- `graph_kind`
- `schema_version`

Recommended sidecar metadata:
- `node_schema_version`
- `edge_schema_version`

## `graph_kind`

Allowed examples:
- `codebase_graph`
- `analysis_graph`
- `merged_graph`

## Node Contract

Required fields:
- `id`
- `kind`
- `name`

Recommended fields:
- `path`
- `parent_id`
- `region`
- `source_tool`
- `confidence`
- `attrs`

## Edge Contract

Required fields:
- `src`
- `dst`
- `rel`

Recommended fields:
- `kind`
- `source_tool`
- `confidence`
- `evidence_path`
- `attrs`

## Export Rule

Renderers and databases consume exports derived from canonical artifacts. They do not replace canonical artifacts.
