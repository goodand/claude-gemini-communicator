# Vertical Slice: tool_call_evidence

## Goal

- tool execution provenance보다 한 단계 아래의 실제 호출 결과를 evidence ledger로 정규화한다.
- `command`, `args`, `exit_code`, `stdout/stderr`, `output_paths`를 기준으로 `verified_evidence`, `missing_evidence`, `residual_uncertainty`를 나눈다.

## Input

- `tool_call_manifest` JSON

## Output

- `evidence_ledger` JSON/MD
- `support_audit` JSON/MD

## Trace Rules

- `tool_name` 또는 `command`가 없으면 `missing_evidence`
- `output_paths` 중 required path가 없으면 `missing_evidence`
- `exit_code != 0`이면 `residual_uncertainty`
- `exit_code == 0`이고 `stdout/stderr/output artifact` 신호가 있으면 `verified_evidence`

## Position

- `attestation_evidence` 다음 slice
- `audit-support`에는 별도 adapter 없이 바로 연결된다
