# dependency-slice-planner unobserved_path_register slice

- generated_at: `2026-03-19-22-10`
- implementation_target: `unobserved_path_register`
- source_of_truth: `knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md`

## Goal

runtime_overlay의 unobserved path 정보를 seed refinement 이전에 bounded register 형태로 정규화한다.

## Input

- `runtime_overlay.json`

## Output

- `unobserved_path_register` (algorithm output)
- top-level `next_candidate = seed_to_refinement_report`
- per-register:
  - `root_path`
  - `unobserved_paths` (<= `8`)
  - `suggested_probe_entrypoints` (<= `4`)
  - `reason`

## Smoke Artifacts

- contract:
  - `unobserved-path-register-contract-smoke-at2026-03-19-22-10.json`
  - `unobserved-path-register-contract-smoke-at2026-03-19-22-10.md`
- build:
  - `unobserved-path-register-build-smoke-at2026-03-19-22-10.json`
- valid:
  - `unobserved-path-register-sample-at2026-03-19-22-10.json`
  - `unobserved-path-register-validation-smoke-at2026-03-19-22-10.json`
  - `unobserved-path-register-validation-smoke-at2026-03-19-22-10.md`
- invalid:
  - `unobserved-path-register-invalid-sample-at2026-03-19-22-10.json`
  - `unobserved-path-register-invalid-validation-smoke-at2026-03-19-22-10.json`
  - `unobserved-path-register-invalid-validation-smoke-at2026-03-19-22-10.md`

## Non-Goals

- runtime probe 실행은 하지 않는다.
