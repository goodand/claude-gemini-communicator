# Remaining Slice Roadmap

- generated_at: `2026-03-18-23-02`
- scope: `core six-flow system`
- purpose: `남은 slice를 큰 묶음으로 다시 정리하고 summary 역할 slice를 backlog에서 제거`

## Removed From Remaining Backlog

- `provenance_summary`
  - 이유: summary 역할이 강하고, 현재 필요한 건 provenance를 다시 요약하는 기능보다 evidence의 신뢰성과 호출 사실을 먼저 구조화하는 기능이다.
  - 처리: `attestation_evidence`와 `tool_call_evidence` 우선으로 대체한다.

- `debug_trace_evidence`
  - 이유: 독립 slice로 두기보다 `tool_call_evidence` 안의 trace/debug field로 흡수하는 편이 낫다.
  - 처리: 별도 남은 slice로 유지하지 않는다.

## Remaining Slice Groups

### 1. Evidence Trust Group

- owner:
  - [evidence-trace-auditor](../../evidence-trace-auditor/SKILL.md)
- slices:
  - `attestation_evidence`
  - `tool_call_evidence`
- 이유:
  - summary를 더 만드는 것보다
  - “누가 어떤 tool을 어떻게 실행했고 그 결과 artifact가 무엇인지”
  - “self-report가 아니라 검증 가능한 실행 증거인지”
  - 를 먼저 닫는 편이 전체 시스템에 더 직접적이다.

### 2. Promotion Strength Group

- owner:
  - [evidence-to-knowledge-promoter](../../evidence-to-knowledge-promoter/SKILL.md)
- slices:
  - `repetition_count_collector`
  - `apply_to_source_kb_with_lifecycle_bridge`
- 이유:
  - canonical candidate gate의 반복 검증 신호를 자동화해야 하고
  - patched copy에서 끝나지 않고 source KB 갱신 절차와 lifecycle bridge를 더 닫아야 한다.

### 3. Execution Integration Group

- owner:
  - [skill-creation-process](../../skill-creation-process/SKILL.md)
  - [execution-contract-mapper](../../execution-contract-mapper/SKILL.md)
- slices:
  - `contract_aware_coding_executor`
- 이유:
  - planner와 validator는 생겼지만
  - contract를 받아 실제 coding/tool-calling을 더 구조화해 주는 executor 계층은 아직 약하다.

### 4. Domain Expansion Group

- owner:
  - [doc-code-sync-checker](../../doc-code-sync-checker/SKILL.md)
- slices:
  - `additional_typed_mismatch_family`
- 예:
  - 새로운 typed mismatch family
  - 기존 rule family 확장
- 이유:
  - 핵심 프레임은 닫혔고, 이제 남은 일은 domain family를 늘리는 쪽이다.

## Priority

1. `attestation_evidence`
2. `tool_call_evidence`
3. `repetition_count_collector`
4. `apply_to_source_kb_with_lifecycle_bridge`
5. `contract_aware_coding_executor`

## Rule

- 앞으로 남은 slice를 적을 때 `summary 역할`만 하는 후보는 backlog에 새로 올리지 않는다.
- 같은 목적의 세분화 후보가 있으면 큰 group 아래에 흡수하고 별도 slice 이름은 제거한다.
