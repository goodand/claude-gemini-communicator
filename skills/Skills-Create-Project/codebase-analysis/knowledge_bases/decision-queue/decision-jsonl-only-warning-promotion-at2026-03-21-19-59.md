# Decision — jsonl_only warning promotion

- created_at: `2026-03-21-19-59`
- scope: `codebase-analysis`
- status: `pending`
- promotion_target: `troubleshooting.md or validator rule`

## Context

- related artifacts:
  - `scripts/export_canonical_graph.py`
  - `references/smoke/SMOKE_export_canonical_graph_2026-03-21-12-49.md`
  - `logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/`
- triggering smoke / experiment:
  - `run_export_canonical_graph_smoke.sh 2026-03-21-19-13`
- current boundary:
  - `jsonl_only` is a split-only path with explicit fallback metadata and warning discipline

## Decision Needed

- should the current `jsonl_only` warning pattern be promoted into a reusable troubleshooting rule or validator-level rule?

## Options

### Option A
- promote the warning pattern into troubleshooting guidance only

### Option B
- promote the warning pattern into a validator or code rule

## Advantages

- option A:
  - keeps flexibility while the split-form policy is still evolving
  - low coupling to current exporter implementation
- option B:
  - prevents silent misuse of split-only metadata paths
  - enforces canonical/split-only boundary mechanically

## Side Effects

- option A:
  - discipline remains documentation-driven
  - repeated warning interpretation may continue
- option B:
  - may harden too early while experimentation is still active
  - could over-apply to tools that intentionally use structure-only split exports

## Current Recommendation

- defer validator promotion for now
- keep the rule documented and revisit after more exporter/smoke cases accumulate

## Exit Condition

- promote when the same warning pattern repeats across multiple tools or exporters
