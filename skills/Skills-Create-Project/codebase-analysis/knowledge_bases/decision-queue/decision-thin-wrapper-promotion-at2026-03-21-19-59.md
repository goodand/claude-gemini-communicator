# Decision — thin smoke wrapper promotion

- created_at: `2026-03-21-19-59`
- scope: `codebase-analysis`
- status: `pending`
- promotion_target: `workspace-artifact-production-process or codebase-analysis rule`

## Context

- related artifacts:
  - `scripts/run_export_canonical_graph_smoke.sh`
  - `references/smoke/SMOKE_export_canonical_graph_2026-03-21-12-49.md`
  - `logs/smoke/export_canonical_graph/2026-03-21-19-13/`
- triggering smoke / experiment:
  - wrapper-based smoke archive generation for three cases
- current boundary:
  - wrapper is intentionally thin: timestamp/bootstrap/case execution only

## Decision Needed

- should the thin wrapper pattern be promoted as a general smoke helper rule, or remain exporter-local for now?

## Options

### Option A
- keep the wrapper local to this exporter until more cases exist

### Option B
- promote a general thin-wrapper pattern into shared rules

## Advantages

- option A:
  - avoids premature abstraction
  - keeps responsibility tight and tool-specific
- option B:
  - standardizes archive bootstrap across smoke commands
  - reduces repeated shell setup work in future smoke runners

## Side Effects

- option A:
  - similar wrappers may be rebuilt manually in nearby tools
- option B:
  - generic wrapper rules may harden before enough variation is observed
  - scope creep risk if wrappers start to parse or reinterpret summaries

## Current Recommendation

- keep local for now
- revisit promotion after at least one more smoke runner uses the same archive/bootstrap pattern

## Exit Condition

- promote when another command adopts the same thin-wrapper structure without needing command-specific exceptions
