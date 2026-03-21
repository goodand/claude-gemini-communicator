# Export Checklist

## Metadata
- scope: `codebase-analysis`
- checklist_type: `implementation_followup`
- basis_reference: `references/canonical-graph-artifact-contract-at2026-03-20-21-04.md`
- basis_schema: `references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md`
- created_at: `2026-03-20-21-51`

## Canonical Artifact Readiness

- [ ] `normalized_graph.json` contract is fixed
- [ ] `nodes.jsonl` contract is fixed
- [ ] `edges.jsonl` contract is fixed
- [ ] `graph_kind` values are defined
- [ ] node required fields are fixed
- [ ] edge required fields are fixed
- [ ] export code reads canonical artifacts rather than view-specific artifacts

## DOT Export

- [ ] DOT export reads canonical nodes and edges
- [ ] node labels are derived from canonical node fields
- [ ] edge labels are derived from canonical `rel`
- [ ] DOT export does not introduce new semantics unavailable in canonical artifacts
- [ ] a smoke DOT file is generated from sample canonical input

## CSV Export For Neo4j

- [ ] `nodes.csv` mapping is defined
- [ ] `rels.csv` mapping is defined
- [ ] node IDs remain stable across exports
- [ ] relation types remain stable across exports
- [ ] CSV export preserves required fields or maps them explicitly
- [ ] a smoke CSV export is generated from sample canonical input

## Cypher Export

- [ ] Cypher `MERGE` strategy is defined
- [ ] node label / node property mapping is defined
- [ ] relation type / relation property mapping is defined
- [ ] Cypher export avoids dropping canonical IDs
- [ ] a smoke Cypher export is generated from sample canonical input

## Round-Trip / Consistency Gates

- [ ] DOT, CSV, and Cypher exports are all derived from the same canonical input set
- [ ] no export path requires DOT as an upstream source of truth
- [ ] export outputs can be traced back to one canonical graph artifact set
- [ ] sample output differences are explainable by renderer/backend needs only

## Smoke Test Gates

- [ ] one minimal canonical graph fixture exists
- [ ] fixture exports to DOT successfully
- [ ] fixture exports to CSV successfully
- [ ] fixture exports to Cypher successfully
- [ ] smoke results are stored as artifacts, not only console output

## Follow-up Notes
- item
