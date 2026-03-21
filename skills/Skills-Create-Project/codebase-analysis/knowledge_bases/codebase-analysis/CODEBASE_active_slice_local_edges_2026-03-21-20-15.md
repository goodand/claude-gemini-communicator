# Active Slice Local Edge Pass

Date: 2026-03-21 20:15 KST
Scope: `src/rag`, `scripts`, `tests/rag`
Raw artifact: `tmp/active_slice_local_edges_2026-03-21-20-16.json`

## Summary

- extracted local edges: `12`
- unresolved local candidates: `14`
- relation kinds found in this pass:
  - `IMPORTS_LOCAL`

This pass was intentionally narrow:

- no graph synthesis
- no promotion
- no `runpy` / `sys.path` edge extraction yet
- only local import-like edges from the active slice

## Confirmed Local Edge Signals

Observed local edge producers:

- `src/rag/bootstrap.py`
- `tests/rag/test_candidate_bundle.py`
- `tests/rag/test_hyde_variant.py`
- `scripts/eval_chunks_grid.py`
- `scripts/eval_semscore_top4.py`
- `scripts/eval_summary_parent_child.py`
- `scripts/eval_topic3_parent_child.py`
- `scripts/eval_topic_parent_child.py`
- `scripts/eval_topic_soft_variants.py`

Immediate interpretation:

- `scripts/eval_*` cluster already has a shared local utility dependency surface
- `src/rag/*` and `tests/rag/*` are directly coupled
- active local edge extraction is feasible before entering the larger `plans/codex` archive slice

## Unresolved Local Candidates

Unresolved local-candidate imports are currently concentrated in:

- `src.rag`
- `mode_registry`
- `retrieval_strategies`
- `raglab.two_phase.*`
- `raglab.mode_registry`

Immediate interpretation:

- these are not random misses
- they represent the next boundary-expansion targets
- especially `raglab.*`, `mode_registry`, and `retrieval_strategies` indicate that active tests depend on code not yet included in the first slice

## Loop Issue Encountered And Fixed

### Issue

The first post-processing command failed with `FileNotFoundError` even though the raw JSON artifact had already been created.

### Cause

The follow-up summary command was executed without the correct `workdir`, so the relative path to `tmp/active_slice_local_edges_2026-03-21-20-16.json` was resolved incorrectly.

### Fix

- rerun the summary step with the correct workspace root
- keep raw artifact creation and summary extraction as separate steps, but always pin `workdir` explicitly

### Why It Matters

This is not a design decision.
It is a repeatable execution hygiene issue in fast smoke / extraction loops.

## Repeated Task Candidate

The loop pattern is already repeating:

1. run a narrow extractor
2. save raw artifact
3. summarize counts
4. note execution issue if any
5. continue to next extractor

This should eventually become a reusable smoke/extraction mini-template, but no promotion is needed yet.

## Next Non-Decision Step

Continue with one of these, without waiting for a design decision:

1. expand local edge coverage to resolve `src.rag`, `mode_registry`, `retrieval_strategies`, and `raglab.*`
2. run a separate extractor for `RUNS_WITH_RUNPY`, `MUTATES_SYS_PATH`, and `LOADS_WITH_IMPORTLIB`

The second option is better for keeping relation kinds separated.
