# captured smoke to bundle slice

- timestamp: `2026-03-19-13-16`
- source_of_truth: [../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md](../knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md)
- checklist: [../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md](../checklist-forimplementation/implementation-checklist-at2026-03-19-00-45.md)

## Goal

`capture-smoke-command` artifact를 canonical experiment bundle input으로 브리지해서 evaluator가 같은 bundle contract로 계속 동작하도록 한다.

## Implemented Command

- `bridge-captured-smoke-to-bundle`

## What It Does

- bundle draft의 `smoke_capture_artifact`를 읽는다
- `contract_family == smoke_command_capture`인지 확인한다
- `status == valid|invalid|capture_failed`를 bundle metadata로 보존한다
- evaluator가 읽을 수 있는 canonical bundle JSON을 별도 output으로 남긴다

## Smoke Artifacts

- positive bridge:
  - [captured-smoke-bundle-bridge-smoke-at2026-03-19-13-16.json](captured-smoke-bundle-bridge-smoke-at2026-03-19-13-16.json)
  - [captured-smoke-bundle-bridge-smoke-at2026-03-19-13-16.md](captured-smoke-bundle-bridge-smoke-at2026-03-19-13-16.md)
- normalized bundle:
  - [captured-smoke-bundle-normalized-smoke-at2026-03-19-13-16.json](captured-smoke-bundle-normalized-smoke-at2026-03-19-13-16.json)
- follow-up evaluation:
  - [captured-smoke-bundle-evaluation-smoke-at2026-03-19-13-16.json](captured-smoke-bundle-evaluation-smoke-at2026-03-19-13-16.json)
  - [captured-smoke-bundle-evaluation-smoke-at2026-03-19-13-16.md](captured-smoke-bundle-evaluation-smoke-at2026-03-19-13-16.md)
- invalid bridge:
  - [captured-smoke-bundle-invalid-bridge-smoke-at2026-03-19-13-16.json](captured-smoke-bundle-invalid-bridge-smoke-at2026-03-19-13-16.json)
  - [captured-smoke-bundle-invalid-bridge-smoke-at2026-03-19-13-16.md](captured-smoke-bundle-invalid-bridge-smoke-at2026-03-19-13-16.md)

## Result

- positive bridge: `status = ok`, `smoke_capture_status = valid`
- normalized bundle evaluation: `workflow_status = ready_for_next_slice`
- invalid bridge: `status = invalid`, `normalized_bundle = null`

## Next Candidate

- `strict_warning_policy_gate`
