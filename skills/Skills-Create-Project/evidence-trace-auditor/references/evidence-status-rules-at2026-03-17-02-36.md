# evidence-trace-auditor evidence status rules

- generated_at: `2026-03-17T02:36:00+09:00`
- applies_to:
  - `raw_smoke_report`
  - `test_result_evidence`
  - `log_evidence`
  - `artifact_path_evidence`
  - `attestation_evidence`
  - `tool_call_evidence`

## Purpose

- `trace_status`를 어떤 조건에서 `verified_evidence`, `missing_evidence`, `residual_uncertainty`로 볼지 빠르게 확인하는 규칙 문서다.
- [SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/SKILL.md)에서 바로 따라갈 수 있는 실무용 기준이다.

## Core Rules

- `verified_evidence`
  - evidence payload가 실제로 존재하고
  - 현재 entry에 대응하는 `doc` 또는 `code` evidence가 비어 있지 않으며
  - 필요하면 실제 artifact path도 존재할 때

- `missing_evidence`
  - 기대한 evidence가 비어 있거나
  - required artifact path가 실제로 존재하지 않거나
  - evidence entry는 생성됐지만 증거 본문을 확보하지 못했을 때

- `residual_uncertainty`
  - evidence는 존재하지만
  - 현재 `contract_diff_basis.recommended_diff_buckets`에 직접 매핑되지 않거나
  - 현재 규칙 집합만으로 supported/missing을 단정하기 어려울 때

## Artifact Path Rule

- `artifact_path_evidence`에서 file path가 실제로 존재하면 `verified_evidence`
- `artifact_path_evidence`에서 required path가 없거나 실제로 존재하지 않으면 `missing_evidence`
- path는 존재하지만 현재 bucket 체계와 연결이 없으면 `residual_uncertainty`

## Examples

- existing file:
  - path: `execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json`
  - status: `verified_evidence`

- missing required file:
  - path: `evidence-trace-auditor/references/missing-artifact-for-smoke.json`
  - status: `missing_evidence`

- skipped test:
  - evidence text exists
  - current bucket mapping is absent
  - status: `residual_uncertainty`

- attested tool execution with required output:
  - command exists
  - exit_code: `0`
  - required output path exists
  - status: `verified_evidence`

- attested tool execution with missing output:
  - command exists
  - required output path missing
  - status: `missing_evidence`

- attested tool execution without verifiable output:
  - command exists
  - output path 없음 또는 exit_code 비정상
  - status: `residual_uncertainty`

- tool call with stdout or output artifact:
  - tool_name / command 존재
  - exit_code: `0`
  - stdout_excerpt 또는 output path 존재
  - status: `verified_evidence`

- tool call with missing required output:
  - tool_name / command 존재
  - output path missing
  - status: `missing_evidence`

- tool call with non-zero exit:
  - tool_name / command 존재
  - exit_code 비정상
  - status: `residual_uncertainty`

## Notes

- 이 규칙은 global process 전반 규칙이라기보다 `evidence-trace-auditor`의 skill-local audit rule이다.
- 더 일반화가 필요하면 나중에 `skill-creation-process`로 승격할 수 있다.
- release evidence bundle(검증기/pytest/git diff/tracked-file/stale scan/PR·commit) 수집 규칙은 [release-evidence-bundle-at2026-06-15-20-22.md](release-evidence-bundle-at2026-06-15-20-22.md) 참고
