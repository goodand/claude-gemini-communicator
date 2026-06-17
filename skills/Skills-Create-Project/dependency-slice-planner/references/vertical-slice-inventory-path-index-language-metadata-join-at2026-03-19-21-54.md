# dependency-slice-planner extension - inventory path index language metadata join

- created_at: `2026-03-19-21-54`
- extended_target: `inventory_path_index_contract` + `final_slice_proposal_generator`

## Goal

`inventory_path_index.json`의 per-file optional metadata를 받아서, planner final proposal이 slice-level `language_buckets`와 `total_bytes`를 함께 materialize하도록 만든다.

## Added Input

- `inventory_path_index.json`
  - required:
    - `path`
    - `is_entrypoint`
  - optional:
    - `language`
    - `byte_count`

## Behavior

- 기존 path index는 그대로 유효하다.
- optional metadata가 없으면 language bucket은 `{}`이고 byte total은 `0`으로 유지된다.
- metadata가 있으면 root_dir prefix 기준으로 slice별 `language_buckets`와 `total_bytes`를 집계한다.
- 집계 결과는 `parallel_slices`, `slice_manifest`, `handoff_packets`에 함께 내려간다.

## Evidence

- contract:
  - `inventory-path-index-metadata-contract-smoke-at2026-03-19-21-54.json`
  - `inventory-path-index-metadata-contract-smoke-at2026-03-19-21-54.md`
- valid:
  - `inventory-path-index-metadata-validation-smoke-at2026-03-19-21-54.json`
  - `inventory-path-index-metadata-validation-smoke-at2026-03-19-21-54.md`
- invalid:
  - `inventory-path-index-metadata-invalid-validation-smoke-at2026-03-19-21-54.json`
  - `inventory-path-index-metadata-invalid-validation-smoke-at2026-03-19-21-54.md`
- materialized final proposal:
  - `final-slice-proposal-metadata-materialized-validation-smoke-at2026-03-19-21-54.json`
  - `final-slice-proposal-metadata-materialized-validation-smoke-at2026-03-19-21-54.md`

## Current Result

- `slice_01.language_buckets`
  - `markdown: 1`
  - `python: 3`
- `slice_01.total_bytes`
  - `3448`
- `slice_02.language_buckets`
  - `python: 1`
- `slice_02.total_bytes`
  - `512`

## Note

- 이 확장은 extractor가 아니라 planner-side materializer다.
- 기존 v0.1 commands는 그대로 유지된다.
