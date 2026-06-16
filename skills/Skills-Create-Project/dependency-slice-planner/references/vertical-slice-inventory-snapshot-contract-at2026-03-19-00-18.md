# inventory_snapshot_contract vertical slice

- timestamp: `2026-03-19-00-18`
- source_of_truth: [../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md](../knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md)
- checklist: [../checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md)

## Goal

Phase 0 inventory output인 `inventory_snapshot.json`의 minimal contract와 validator를 먼저 고정한다.

## Implemented Commands

- `emit-inventory-snapshot-contract`
- `validate-inventory-snapshot`

## Minimal Required Fields

- `root_path`
- `file_count`
- `total_bytes`
- `language_buckets`
- `manifest_files`
- `known_entrypoints`

## Validation Rules

- `root_path`는 non-empty `str`
- `file_count`, `total_bytes`는 non-negative `int`
- `language_buckets`는 `dict[str,int]`
- `manifest_files`, `known_entrypoints`는 `list[str]`

## Evidence

- positive sample: [inventory-snapshot-sample-at2026-03-19-00-18.json](inventory-snapshot-sample-at2026-03-19-00-18.json)
- invalid sample: [inventory-snapshot-invalid-sample-at2026-03-19-00-18.json](inventory-snapshot-invalid-sample-at2026-03-19-00-18.json)
