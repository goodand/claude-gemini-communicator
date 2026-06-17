# dependency-slice-planner extension - inventory path index materialization

- created_at: `2026-03-19-21-13`
- extended_target: `final_slice_proposal_generator`

## Goal

optional `inventory_path_index`를 받아 `parallel_slices`, `slice_manifest`, `handoff_packets`의 `files`와 `entrypoints`를 실제 경로로 채운다.

## Added Input

- `inventory_path_index.json`
  - `path`
  - `is_entrypoint`

## Behavior

- path index가 없으면 기존 v0.1처럼 빈 리스트를 유지한다.
- path index가 있으면 `root_dir` prefix 기준으로 `files`를 모은다.
- `is_entrypoint = true`인 경로만 `entrypoints`로 올린다.

## Evidence

- contract:
  - `inventory-path-index-contract-smoke-at2026-03-19-21-13.json`
  - `inventory-path-index-contract-smoke-at2026-03-19-21-13.md`
- valid:
  - `inventory-path-index-validation-smoke-at2026-03-19-21-13.json`
  - `inventory-path-index-validation-smoke-at2026-03-19-21-13.md`
- invalid:
  - `inventory-path-index-invalid-validation-smoke-at2026-03-19-21-13.json`
  - `inventory-path-index-invalid-validation-smoke-at2026-03-19-21-13.md`
- materialized final proposal:
  - `final-slice-proposal-materialized-validation-smoke-at2026-03-19-21-13.json`
  - `final-slice-proposal-materialized-validation-smoke-at2026-03-19-21-13.md`

## Current Result

- `slice_01.files`
  - `src/core/__init__.py`
  - `src/core/service.py`
  - `src/core/bootstrap.py`
- `slice_01.entrypoints`
  - `src/core/bootstrap.py`

## Note

- 이 확장은 extractor가 아니라 planner-side materializer다.
- richer path metadata나 language bucket join은 이후 optional 확장으로 남긴다.
