# Codebase Connection Evidence Seed

Date: 2026-03-21 20:09 KST
Scope: `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity`
Goal: codebase analysis procedure의 2단계인 연결 증거 수집을 시작하기 위한 seed 목록을 남긴다.

## Why This Exists

coarse survey 다음 단계는 해석이 아니라 evidence collection이다.

The first pass should focus on:

- `import`
- wrapper / generated launcher
- `runpy`
- `sys.path`
- manifest-like metadata use

This document records the initial hotspots so the next pass can be targeted.

## `runpy` Hotspots

Detected `runpy` usage count: 17

Representative hotspots:

- `plans/codex/algorithms/eval_nonrerank5_artifacts.py`
- `plans/codex/algorithms/eval_ragas_llmjudge_10modes_kgrid.py`
- `plans/codex/algorithms/eval_rerank5_artifacts.py`
- `plans/codex/algorithms/eval_rerank5_artifacts_sweep.py`
- `plans/codex/algorithms/preflight_experiment.py`
- `plans/codex/algorithms/run_experiment_chain.py`
- `plans/codex/scripts/generate_legacy_wrappers.py`
- `scripts/eval_rerank5_3mode_only_2026-03-10-14-05.py`

Interpretation:

- `runpy` is concentrated in the archived experiment orchestration layer.
- this suggests wrapper-driven execution chains already exist and should be modeled explicitly as relations, not hidden inside generic script nodes.

## `sys.path` Mutation Hotspots

Detected `sys.path` mutation count: 17

Representative hotspots:

- `plans/codex/scripts/_bootstrap.py`
- `plans/codex/scripts/build_embedding_store_large_parsed_multistrategy_2026-03-14.py`
- `plans/codex/scripts/build_hete_evidence_alignment_2026-03-16.py`
- `plans/codex/scripts/eval_nonrerank5_artifacts.py`
- `plans/codex/scripts/eval_ragas_llmjudge_10modes_kgrid.py`
- `plans/codex/scripts/eval_rerank5_artifacts.py`
- `plans/codex/scripts/preflight_experiment.py`
- `plans/codex/scripts/run_experiment_chain.py`
- `tests/rag/test_hete_parent_cluster.py`
- `tests/rag/test_hete_window_inject.py`
- `tests/rag/test_two_phase_retriever.py`

Interpretation:

- path mutation is not isolated to one bootstrap file
- both execution scripts and tests depend on mutable import routing
- this should be captured as a first-class edge type, not treated as ordinary import

## `importlib` Hotspots

Detected `importlib` usage count: 11

Representative hotspots:

- `plans/codex/algorithms/build_embedding_store_large.py`
- `plans/codex/algorithms/calc_top100_cosine_same_embedding.py`
- `plans/codex/scripts/eval_ragas_llmjudge_10modes_kgrid.py`
- `plans/codex/scripts/preflight_experiment.py`
- `plans/codex/third_party/HeteRAG/retrieval/run_chunked_eval.py`
- `tests/rag/test_hete_parent_cluster.py`
- `tests/rag/test_hete_window_inject.py`

Interpretation:

- dynamic import exists in both experiment code and tests
- this is another reason direct static import graphs alone will be incomplete

## `manifest` Hotspots

Detected manifest-like references count: 2

Hotspots:

- `plans/codex/scripts/build_embedding_store_large_parsed_multistrategy_2026-03-14.py`
- `plans/codex/scripts/build_html_compact_map_2026-03-14.py`

Interpretation:

- manifest handling is narrower than `runpy` or `sys.path`
- likely good candidate for a small, clean sub-slice

## Next Non-Decision Tasks

### A. Active slice evidence collection

Target first:

- `src/rag/`
- `scripts/`
- `tests/rag/`

Reason:

- smaller surface
- lower archive noise
- more likely to represent the reusable current core

### B. Experiment slice evidence collection

Target second:

- `plans/codex/scripts/`
- `plans/codex/algorithms/`

Reason:

- high volume
- wrapper/runpy/path-mutation density
- likely to contain many cross-slice edges

## Edge Types To Prepare

For the next pass, these relation candidates should be extracted explicitly:

- `IMPORTS`
- `CALLS`
- `RUNS_WITH_RUNPY`
- `MUTATES_SYS_PATH`
- `LOADS_WITH_IMPORTLIB`
- `READS_MANIFEST`
- `GENERATES_WRAPPER`

This keeps the next step evidence-first and avoids premature graph interpretation.
