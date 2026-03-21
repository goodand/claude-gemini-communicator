# Active Slice Import Seed

Date: 2026-03-21 20:09 KST
Scope: `src/rag`, `scripts`, `tests/rag`
Raw artifact: `CODEBASE_active_slice_import_seed_2026-03-21-20-09.json`

## Summary

- parsed import rows: 230
- files with import evidence: 29

## Top Import Heads

- `pathlib`: 22
- `json`: 18
- `typing`: 16
- `os`: 14
- `sys`: 12
- `langchain_openai`: 10
- `langchain_chroma`: 9
- `time`: 9
- `re`: 9
- `shutil`: 9
- `__future__`: 8
- `collections`: 8
- `src`: 7
- `sanitize_utils`: 6
- `tiktoken`: 6
- `raglab`: 6
- `datetime`: 5
- `mode_registry`: 5
- `unittest`: 5
- `pytest`: 5

## Files With Highest Import Density

- `scripts/eval_topic3_parent_child.py`: 13
- `scripts/eval_topic_soft_variants.py`: 13
- `scripts/eval_semscore_top4.py`: 12
- `scripts/eval_summary_parent_child.py`: 12
- `scripts/eval_topic_parent_child.py`: 12
- `tests/rag/test_two_phase_retriever.py`: 12
- `scripts/claude_sniffer.py`: 11
- `scripts/eval_chunks_grid.py`: 11
- `tests/rag/test_hete_parent_cluster.py`: 10
- `scripts/autonomous_scheduler_2026-03-10.py`: 9
- `tests/rag/test_hete_window_inject.py`: 9
- `scripts/export_canonical_graph.py`: 8
- `scripts/generate_eval_dataset.py`: 8
- `scripts/sufficient_context_autorater.py`: 8
- `src/rag/graph.py`: 8

## Immediate Reading

- `src/rag/*` imports are compact and suited for the first active graph slice.
- `scripts/*` imports are broad and include utility, evaluation, smoke, and environment dependencies.
- `tests/rag/*` already reveal bridge imports into `raglab`, `mode_registry`, and `retrieval_strategies`; tests are useful for discovering hidden runtime coupling.
- next pass should extract explicit local edges for `src.*`, `sanitize_utils`, `mode_registry`, `retrieval_strategies`, and `raglab.*`.
