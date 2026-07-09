# dependency-slice-planner unobserved_path_register contract

- generated_at: `2026-03-19T22:43:50+09:00`
- contract_family: `unobserved_path_register`
- version: `v0.1.0`

## Required Top-Level Fields

- `status`
- `generated_at`
- `algorithm_family`
- `version`
- `input_artifacts`
- `register_count`
- `registers`
- `next_candidate`

## Register Required Fields

- `root_path`
- `unobserved_paths`
- `suggested_probe_entrypoints`
- `reason`

## Bounding Rules

- `max_paths_per_register`: `8`
- `max_suggested_probe_entrypoints`: `4`
