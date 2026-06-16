# slice_seed_candidates_contract vertical slice

- timestamp: `2026-03-19-00-22`
- source_of_truth: [../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md)
- checklist: [../checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md)

## Goal

Phase 1 coarse seed output인 `slice_seed_candidates.json`의 minimal contract와 validator를 고정한다.

## Implemented Commands

- `emit-slice-seed-candidates-contract`
- `validate-slice-seed-candidates`

## Minimal Required Shape

- top-level: `candidate_count`, `candidates`
- candidate: `candidate_id`, `root_dir`, `file_count`, `total_bytes`, `max_depth`, `seed_action`, `tags`, `reason`

## Seed Action Enum

- `keep`
- `merge_candidate`
- `split_candidate`
- `stop_candidate`

## Evidence

- positive sample: [slice-seed-candidates-sample-at2026-03-19-00-22.json](slice-seed-candidates-sample-at2026-03-19-00-22.json)
- invalid sample: [slice-seed-candidates-invalid-sample-at2026-03-19-00-22.json](slice-seed-candidates-invalid-sample-at2026-03-19-00-22.json)
