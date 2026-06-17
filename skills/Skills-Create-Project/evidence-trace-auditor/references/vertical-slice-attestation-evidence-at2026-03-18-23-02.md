# Vertical Slice: attestation_evidence

- generated_at: `2026-03-18-23-02`
- target skill: `evidence-trace-auditor`
- slice kind: `attestation_evidence`

## Purpose

tool 실행 사실과 output artifact 존재를 함께 읽어
`step_attestation` 성격의 evidence ledger entry로 정규화한다.

## Input

- attestation manifest JSON
- 각 entry는 아래 필드를 가질 수 있다
  - `name`
  - `tool_name`
  - `command`
  - `cwd`
  - `actor`
  - `started_at`
  - `finished_at`
  - `exit_code`
  - `input_paths[]`
  - `output_paths[]`
  - `observed_bucket`
  - `action`
  - `reason`

## Trace Rules

- `verified_evidence`
  - command 존재
  - `exit_code == 0`
  - required output path 존재

- `missing_evidence`
  - command 없음
  - 또는 required output path가 실제로 없음

- `residual_uncertainty`
  - command는 있지만 output path로 attestation을 닫지 못함
  - 또는 `exit_code != 0`

## Output

- machine-readable `evidence_ledger`
- `finding_family = attestation`
- `kind = step_attestation`
- `attestation.*` metadata를 entry에 보존

## Audit Effect

- `audit-support`는 이제 `trace_status`를 직접 읽는다.
- 즉 evidence 본문이 있어도
  - `missing_evidence`는 missing bucket으로
  - `residual_uncertainty`는 residual bucket으로
  우선 처리한다.
