---
name: codebase-graph-representation-kb
kb_profile: canonical_design_kb
role: codebase graph representation strategy
ver: 1
created_at: 2026-03-20-21-04
updated_at: 2026-03-20-21-04
---

# Codebase Graph Representation KB

## Purpose

Capture a practical representation strategy for codebase graph analysis so that graph storage, graph querying, and graph visualization do not collapse into one tool choice too early.

## Core Decision

The source of truth should not be a visualization format.

Canonical graph artifacts should be:
- `normalized_graph.json`
- `nodes.jsonl`
- `edges.jsonl`

These artifacts should be produced first, then exported into visualization or database-specific formats.

## Tool Role Split

### Graphviz

Use for:
- static diagrams
- presentation artifacts
- compact topology snapshots
- procedural or architectural explanations

Do not treat as:
- canonical graph storage
- long-term query backend

### Neo4j

Use for:
- persistent graph storage
- multi-hop graph query
- dependency tracing
- repeated codebase analysis
- expansion into ownership, issue, test, and history relations

### Cytoscape / Cytoscape.js

Use for:
- interactive graph visualization
- browser-based or UI-based graph inspection
- graph exploration over exported graph data

### Gephi

Use for:
- macro exploration of large graphs
- layout experimentation
- hub, cluster, and network pattern inspection

Do not treat as:
- canonical persistent graph backend

## Canonical Representation Principle

The graph should be modeled in a tool-neutral representation first.

Recommended build sequence:
1. extract graph facts
2. normalize into canonical node and edge schema
3. write `normalized_graph.json`
4. write `nodes.jsonl`
5. write `edges.jsonl`
6. export into Graphviz, Neo4j CSV/Cypher, Cytoscape JSON, or other view layers

## Why This Matters

If DOT becomes the source of truth:
- layout concerns leak into data modeling
- graph semantics become harder to normalize
- later export to Neo4j or Cytoscape becomes more fragile

If a canonical graph schema exists first:
- Graphviz stays a view layer
- Neo4j stays a storage/query layer
- Cytoscape and Gephi stay exploration layers
- orchestration and code graphs can share one export discipline without sharing one visual format

## Recommended Canonical Artifacts

### `normalized_graph.json`

Purpose:
- one snapshot artifact for end-to-end transport or debugging

Recommended top-level shape:
- metadata
- node schema version
- edge schema version
- nodes
- edges
- optional overlays

Suggested fields:
- graph_id
- generated_at
- source_scope
- graph_kind
- nodes[]
- edges[]
- overlays[]

### `nodes.jsonl`

Purpose:
- streaming-friendly node store
- easy to diff, grep, filter, and transform

Suggested node fields:
- `id`
- `kind`
- `name`
- `path`
- `parent_id`
- `region`
- `source_tool`
- `confidence`
- `attrs`

### `edges.jsonl`

Purpose:
- streaming-friendly relation store
- easy export into CSV, Cypher, or graph databases

Suggested edge fields:
- `src`
- `dst`
- `rel`
- `kind`
- `source_tool`
- `confidence`
- `evidence_path`
- `attrs`

## Layer Separation Rule

Keep these graphs logically separate even if they are stored in one backend.

### Codebase Graph

Typical nodes:
- `Project`
- `Package`
- `Folder`
- `File`
- `Module`
- `Type`
- `Function`
- `Entrypoint`
- `Wrapper`
- `Manifest`

Typical relations:
- `CONTAINS`
- `DECLARES`
- `IMPORTS`
- `CALLS`
- `DEPENDS_ON`
- `WRAPS`
- `MUTATES_PATH`
- `RUNS`
- `READS_MANIFEST`

### Analysis / Orchestration Graph

Typical nodes:
- `Slice`
- `Agent`
- `Artifact`
- `Claim`
- `Gap`
- `Contradiction`

Typical relations:
- `ASSIGNED_TO`
- `EMITS`
- `CONSUMES`
- `SUPPORTS`
- `CONTRADICTS`
- `BLOCKED_BY`
- `LEAVES_GAP`

## DOT To Neo4j Note

DOT to Neo4j conversion is acceptable, but it should be treated as a migration or export path rather than the primary modeling path.

Recommended practical route:
1. read DOT
2. parse nodes and edges
3. convert into `nodes.csv` and `rels.csv`, or Cypher `MERGE` statements
4. import via `LOAD CSV` or APOC

This is useful for preserving existing Graphviz assets, but the long-term preferred direction is:
- canonical graph artifacts first
- DOT and Neo4j exports second

## Operational Recommendation

For codebase analysis work:
- keep Neo4j as the long-term storage and query option
- keep Graphviz as the static explanation layer
- keep Cytoscape or Gephi as exploration layers
- keep canonical graph artifacts as the source of truth

## Canonical Design Takeaways

- storage/query and visualization should not share the same source artifact
- Graphviz is a rendering target, not the canonical graph model
- Neo4j is the best center when graph querying and repeated analysis matter
- `normalized_graph.json + nodes.jsonl + edges.jsonl` is the safest expansion-friendly baseline
