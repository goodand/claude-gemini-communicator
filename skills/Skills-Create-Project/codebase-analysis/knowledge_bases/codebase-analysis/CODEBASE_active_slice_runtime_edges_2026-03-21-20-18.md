# Active Slice Runtime Edge Pass

Date: 2026-03-21 20:18 KST
Scope: `src/rag`, `scripts`, `tests/rag`
Raw artifact: `tmp/active_slice_runtime_edges_2026-03-21-20-18.json`

## Summary

- extracted runtime rows: `13`
- relation kinds:
  - `LOADS_WITH_IMPORT`: `1`
  - `RUNS_WITH_RUNPY`: `1`
  - `MUTATES_SYS_PATH`: `9`
  - `LOADS_WITH_IMPORTLIB`: `2`

## Key Observation

These runtime-oriented edges are not spread evenly across the active slice.
They are concentrated in a narrow cluster:

- `scripts/eval_rerank5_3mode_only_2026-03-10-14-05.py`
- `scripts/test_pinecone_rerank_integration_2026-03-10-17-30.py`
- `tests/rag/test_hete_parent_cluster.py`
- `tests/rag/test_hete_window_inject.py`
- `tests/rag/test_two_phase_retriever.py`

Interpretation:

- `src/rag/*` is relatively clean from runtime loader/path mutation behavior
- path mutation and dynamic loading live mostly in adapter/test glue and archived evaluation compatibility scripts

## Confirmed Relations

### `RUNS_WITH_RUNPY`

Confirmed at:

- `scripts/eval_rerank5_3mode_only_2026-03-10-14-05.py`

Call:

- `runpy.run_path`

### `MUTATES_SYS_PATH`

Confirmed at:

- `scripts/eval_rerank5_3mode_only_2026-03-10-14-05.py`
- `scripts/test_pinecone_rerank_integration_2026-03-10-17-30.py`
- `tests/rag/test_hete_parent_cluster.py`
- `tests/rag/test_hete_window_inject.py`
- `tests/rag/test_two_phase_retriever.py`

Observed call:

- `sys.path.insert`

### `LOADS_WITH_IMPORTLIB`

Confirmed at:

- `tests/rag/test_hete_parent_cluster.py`
- `tests/rag/test_hete_window_inject.py`

Observed module:

- `importlib.util`

## Loop Issue Encountered Again

The extractor succeeded, but the first summary command again failed to resolve the raw artifact path.

Cause:

- post-processing step used a relative path that was not resolved in the expected workspace root

Fix:

- rerun with an absolute path to the raw artifact

Repeated-task implication:

- fast extraction loops should prefer one of:
  - explicit absolute path for raw artifact reads
  - or a mandatory `ROOT = Path(...)` bootstrap before every summary pass

This is not a design decision. It is an execution hygiene rule candidate.

## Immediate Procedural Implication

The codebase analysis procedure can now split more cleanly:

### cleaner active core

- `src/rag/*`
- exporter/sanitizer/resume utilities that do not mutate import paths

### runtime adapter / compatibility cluster

- path-mutating tests
- `runpy` launcher script
- importlib-based test loaders

This supports a later slice decision, but no slice decision is required yet.

## Next Non-Decision Step

The next fast loop should target one of:

1. explicit local edge resolution for unresolved modules
   - `mode_registry`
   - `retrieval_strategies`
   - `raglab.*`
2. manifest/file-artifact relation extraction
3. wrapper/generator relation extraction from archived experiment scripts

The cleanest next step is `mode_registry` / `retrieval_strategies` / `raglab.*` resolution, because those unresolved imports are already blocking a more faithful local graph.
