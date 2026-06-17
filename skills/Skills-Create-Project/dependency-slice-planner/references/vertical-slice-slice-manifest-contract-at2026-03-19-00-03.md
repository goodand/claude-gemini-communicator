# Vertical Slice: slice_manifest_contract

## Goal

- `dependency-slice-planner`의 첫 구현 slice로 canonical `slice_manifest.json` contract를 machine-readable artifact로 고정한다.

## Input

- canonical synthesis KB의 `Canonical Output Contract`
- sample `slice_manifest.json`

## Output

- `slice_manifest_contract` JSON/MD
- `slice_manifest_validation` JSON/MD

## Rules

- top-level required fields는 `slice_count`, `slices`
- per-slice required fields는 `slice_id`, `root_dirs`, `files`, `entrypoints`, `classification`, `reason`
- `classification`은 `write_safe`, `analysis_only`만 허용
- `slice_count`는 `len(slices)`와 일치해야 한다
