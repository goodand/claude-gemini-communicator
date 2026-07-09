# quick_validate artifact bridge slice

- timestamp: `2026-03-19-01-07`
- source_of_truth: [../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md](../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md)
- checklist: [../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md)

## Goal

`quick_validate_capture` artifact를 사람이 다시 읽지 않고 canonical experiment bundle의 `quick_validate_status`로 연결하는 bridge를 추가한다.

## Implemented Command

- `bridge-quick-validate-artifact`

## What It Does

- bundle draft의 `quick_validate_artifact`를 읽는다
- `contract_family == quick_validate_capture`인지 확인한다
- `status == passed|failed`를 canonical `quick_validate_status`로 정규화한다
- 필요하면 evaluator가 바로 읽을 수 있는 normalized bundle JSON을 별도 output으로 남긴다

## Smoke Artifacts

- positive bridge:
  - [quick-validate-artifact-bundle-bridge-smoke-at2026-03-19-01-07.json](quick-validate-artifact-bundle-bridge-smoke-at2026-03-19-01-07.json)
  - [quick-validate-artifact-bundle-bridge-smoke-at2026-03-19-01-07.md](quick-validate-artifact-bundle-bridge-smoke-at2026-03-19-01-07.md)
- normalized bundle:
  - [quick-validate-artifact-bundle-normalized-smoke-at2026-03-19-01-07.json](quick-validate-artifact-bundle-normalized-smoke-at2026-03-19-01-07.json)
- follow-up evaluation:
  - [quick-validate-artifact-bundle-evaluation-smoke-at2026-03-19-01-07.json](quick-validate-artifact-bundle-evaluation-smoke-at2026-03-19-01-07.json)
  - [quick-validate-artifact-bundle-evaluation-smoke-at2026-03-19-01-07.md](quick-validate-artifact-bundle-evaluation-smoke-at2026-03-19-01-07.md)
- invalid bridge:
  - [quick-validate-artifact-bundle-invalid-bridge-smoke-at2026-03-19-01-07.json](quick-validate-artifact-bundle-invalid-bridge-smoke-at2026-03-19-01-07.json)
  - [quick-validate-artifact-bundle-invalid-bridge-smoke-at2026-03-19-01-07.md](quick-validate-artifact-bundle-invalid-bridge-smoke-at2026-03-19-01-07.md)

## Result

- positive bridge: `status = ok`, `quick_validate_status = passed`
- normalized bundle evaluation: `workflow_status = ready_for_next_slice`
- invalid bridge: `status = invalid`, `normalized_bundle = null`

## Next Candidate

- `captured_smoke_to_bundle_adapter`
