# Execution Contract To Evidence Pattern

## Purpose

`execution contract -> coding/test execution -> observable evidence` 흐름을 고정한다.

## Use This Pattern When

- `rule_schema`, `schema_contract`, `cli_contract`, `contract_diff_basis` 같은 실행 계약 artifact가 이미 있다
- 이제 구현/TDD/smoke/evidence를 같은 contract 기준으로 닫아야 한다
- code 수정 결과를 나중에 `evidence-trace-auditor`, `baseline-diff-lab`, `evidence-to-knowledge-promoter`까지 넘길 가능성이 있다

## Fixed Sequence

1. 실행 계약 artifact를 먼저 고정한다
2. implementation checklist와 TDD를 확정한다
3. 구현을 진행한다
4. raw smoke artifact를 남긴다
5. evidence ledger를 만든다
6. `support / missing_evidence / residual_uncertainty` audit를 계산한다
7. fix 효과를 주장해야 하면 before/after diff를 만든다
8. reusable lesson이면 `evidence-to-knowledge-promoter`로 handoff한다

## Required Inputs

- implementation checklist
- stable execution contract artifact
  - 예: `rule_schema`, `schema_contract`, `cli_contract`, `contract_diff_basis`
- 최소 1개 smoke scenario
- evidence sink
  - 예: raw smoke report, JUnit XML, log JSONL, artifact path manifest

## Decision Rules

- single-run support 확인이 목적이면 `evidence-trace-auditor`를 먼저 쓴다
- before/after improvement 주장까지 필요하면 `baseline-diff-lab`도 같이 쓴다
- raw smoke artifact만 있으면 audit/diff 전에 먼저 그대로 저장하고 필요 시 metricize한다
- reusable lesson 승격은 audit와 diff가 모두 닫힌 뒤에만 시도한다

## Handoff Pattern

### execution-contract-mapper -> implementation branch

- payload:
  - implementation checklist path
  - stable contract artifact paths
  - target fixture 또는 pair

### implementation branch -> evidence-trace-auditor

- payload:
  - raw smoke artifact 또는 normalized evidence input
  - `contract_diff_basis`

### implementation branch -> baseline-diff-lab

- payload:
  - pre-fix artifact
  - post-fix artifact
  - metric set 또는 raw smoke artifact

## Expected Outputs

- smoke artifact
- evidence ledger
- support audit
- optional before/after diff
- troubleshooting case

## Planner

- 공용 handoff planning이 필요하면 `skill-creation-process/scripts/execution_evidence_planner.py --help`를 사용한다
- planner output이 downstream contract와 실제로 맞는지 확인하려면 `skill-creation-process/scripts/execution_handoff_validator.py --help`를 사용한다

## Anti-Patterns

- contract artifact 없이 바로 smoke만 남김
- TDD 없이 구현 후 evidence를 해석함
- audit 없이 lesson을 KB로 바로 승격함
- post-fix만 있고 pre-fix baseline이 없음
