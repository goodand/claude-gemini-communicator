# dependency-slice-planner vertical slice - final_slice_proposal_generator

- created_at: `2026-03-19-17-49`
- source_of_truth: `knowledge_bases/dependency-slice-planner-algorithm-kb-at2026-03-18-23-02.md`
- implementation_target: `final_slice_proposal_generator`

## Goal

`stop_rule_evaluator` 결과를 실제 downstream-friendly planner outputs로 내린다.

## Input

- `stop_rule_evaluation.json`

## Output

- `parallel_slices`
- `write_safe_slices`
- `analysis_only_slices`
- `do_not_split_regions`
- `slice_manifest`
- `handoff_packets`

## v0.1 Policy

- `write_safe`와 `analysis_only`만 `parallel_slices`와 `slice_manifest`로 내려간다.
- `do_not_split`은 `do_not_split_regions`로만 남긴다.
- `handoff_packets`는 minimal contract로 생성한다.
- `files`와 `entrypoints`는 extractor 연결 전까지 빈 리스트를 허용한다.

## Smoke Artifacts

- contract:
  - `final-slice-proposal-contract-smoke-at2026-03-19-17-49.json`
  - `final-slice-proposal-contract-smoke-at2026-03-19-17-49.md`
- valid:
  - `final-slice-proposal-validation-smoke-at2026-03-19-17-49.json`
  - `final-slice-proposal-validation-smoke-at2026-03-19-17-49.md`
- invalid:
  - `final-slice-proposal-invalid-validation-smoke-at2026-03-19-17-49.json`
  - `final-slice-proposal-invalid-validation-smoke-at2026-03-19-17-49.md`

## Current Result

- valid sample:
  - `parallel_slice_count = 1`
  - `write_safe_slice_count = 1`
  - `analysis_only_slice_count = 0`
  - `do_not_split_count = 1`
  - `slice_manifest.slice_count = 1`
  - `handoff_packet_count = 1`
- invalid sample:
  - `status = invalid_inputs`
  - invalid family: `stop_rule_evaluation`

## Completion Note

- `dependency-slice-planner` v0.1은 contract phase + refinement report + stop rule gate + final slice proposal까지 모두 닫혔다.
- 이후 확장은 extractor 연동 정밀화, richer file inventory materialization, merge-target selection 고도화로 분리한다.
