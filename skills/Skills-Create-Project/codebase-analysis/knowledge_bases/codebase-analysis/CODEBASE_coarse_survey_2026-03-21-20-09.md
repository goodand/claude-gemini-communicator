# Codebase Coarse Survey

Date: 2026-03-21 20:09 KST
Scope: `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity`
Goal: decision이 불필요한 1차 코드베이스 분석 절차의 coarse survey를 고정한다.

## Top-Level Layout

Top-level directories and files observed at repo root:

- `.claude`
- `.codex`
- `.history`
- `configs`
- `datasets`
- `logs`
- `plans`
- `scripts`
- `skills`
- `src`
- `template`
- `tests`
- `tmp`
- root files: `.env`, `.env.example`, `.gitignore`, `.mcp.json`, `pyproject.toml`, `uv.lock`

## File Counts By Major Area

Counts were re-collected from the current workspace and include all files under each directory.

- `src`: 13 files
- `scripts`: 37 files
- `tests`: 22 files
- `plans`: 1734 files
- `configs`: 1 file
- `datasets`: 13 files
- `skills`: 19 files

Interpretation:

- `plans/` is the dominant archive and experiment layer.
- `src/` is still small and represents the current reusable library core.
- `scripts/` is the main execution surface for ad hoc experiments, utilities, and smoke tooling.
- `tests/` is modest but now contains both retrieval tests and exporter smoke tests.

## Python Surface By Top-Level Area

Python file counts excluding `.venv`, `.git`, `node_modules`, `__pycache__`, `.mypy_cache`, `.pytest_cache`:

- `.claude`: 43
- `.history`: 3
- `plans`: 135
- `scripts`: 21
- `skills`: 3
- `src`: 6
- `tests`: 8

Interpretation:

- active executable Python lives mostly in `plans/` and `scripts/`
- reusable code is concentrated in `src/rag/`
- many historical and skill-side scripts exist, but they are not the current production library core

## Major Module Clusters

### 1. Reusable library core

- `src/rag/bootstrap.py`
- `src/rag/candidates.py`
- `src/rag/graph.py`

This looks like the smallest stable core worth graphing first.

### 2. Current repo utility / execution layer

Representative files:

- `scripts/export_canonical_graph.py`
- `scripts/run_export_canonical_graph_smoke.sh`
- `scripts/fix_jsonl.py`
- `scripts/resume_precheck.py`
- `scripts/claude_sniffer.py`
- retrieval/eval utilities under `scripts/eval_*`

This layer is the current executable surface for smoke, recovery, and experiment helpers.

### 3. Experiment archive / algorithm layer

Representative files:

- `plans/codex/algorithms/*.py`
- `plans/codex/scripts/*.py`

This is the largest code volume and contains wrappers, evaluators, builders, and archived experiment entrypoints.

### 4. Test layer

Representative files:

- `tests/test_export_canonical_graph.py`
- `tests/rag/test_candidate_bundle.py`
- `tests/rag/test_hete_parent_cluster.py`
- `tests/rag/test_hete_window_inject.py`
- `tests/rag/test_hyde_variant.py`
- `tests/rag/test_two_phase_retriever.py`

This gives a compact initial validation surface for the current reusable RAG core and the canonical graph exporter.

## Entrypoint Candidate Clusters

Entrypoint candidates were collected by searching for:

- `if __name__ == "__main__"`
- `argparse.ArgumentParser(...)`
- `def main(...)`

### Current repo scripts

- `scripts/export_canonical_graph.py`
- `scripts/claude_sniffer.py`
- `scripts/fix_jsonl.py`
- `scripts/resume_precheck.py`
- `scripts/eval_chunks_grid.py`
- `scripts/eval_semscore_top4.py`
- `scripts/eval_summary_parent_child.py`
- `scripts/eval_topic_parent_child.py`
- `scripts/eval_topic3_parent_child.py`
- `scripts/eval_topic_soft_variants.py`
- `scripts/sufficient_context_autorater.py`

### Library/bootstrap entry

- `src/rag/bootstrap.py`

### Experiment/archive entrypoints

Large volume under:

- `plans/codex/algorithms/`
- `plans/codex/scripts/`
- `plans/codex/third_party/HeteRAG/`

These should be treated as a separate graph slice from the current repo utility layer.

## Immediate Implication For Codebase Analysis Procedure

The next non-decision step should not jump to synthesis.

Recommended next procedural step:

1. collect dependency/connection evidence
2. separate current core from archived experiment surface
3. treat `src/rag`, `scripts/`, `tests/` as the first active slice
4. treat `plans/codex` as a second large experiment slice

This keeps the first graph pass small and avoids mixing active code with historical experiment archive too early.
