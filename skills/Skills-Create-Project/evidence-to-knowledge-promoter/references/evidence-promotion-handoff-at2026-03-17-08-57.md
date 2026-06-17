# Evidence Promotion Handoff

## Purpose

`evidence-trace-auditor`와 `baseline-diff-lab` 결과를 `evidence-to-knowledge-promoter` 입력으로 읽는 최소 handoff schema를 고정한다.

## Required Inputs

- `support_audit`
  - `build-promotion-summary --support-audit`
- `baseline_diff`
  - `build-promotion-summary --baseline-diff`

## Optional Supporting Inputs

- `evidence_ledger`
  - `support_audit` 해석 보조
- `troubleshooting` note
  - `lesson_candidate` 보류 사유 설명 보조
- planner payload
  - upstream이 `execution_evidence_planner.py`를 썼다면 target, experiment, suggested output naming을 참고한다

## Minimal Mapping

- `support_audit.contract_family == support_audit`
  - verified evidence, missing evidence, residual uncertainty를 `finding`/`residual_uncertainty` 후보로 바꾼다
- `baseline_diff.contract_family == baseline_diff`
  - metric delta와 reduction 신호를 `delta` 후보로 바꾼다
- `support_audit + baseline_diff`
  - 둘 다 있어야 `lesson_candidate` 평가를 시도한다

## Consumption Order

1. `support_audit`를 먼저 읽는다
2. `baseline_diff`를 읽는다
3. `build-promotion-summary`로 `finding / delta / lesson_candidate / residual_uncertainty`를 만든다
4. `evaluate-promotion-trigger`로 `hybrid_kb`와 `canonical_design_kb` 결정을 만든다
5. `build-hybrid-kb-patch-plan` 또는 `evaluate-canonical-candidate`로 내려간다

## Hold Rules

- `support_audit`가 없으면 승격 판단을 시작하지 않는다
- `baseline_diff`가 없으면 `delta`와 `lesson_candidate`를 강하게 주장하지 않는다
- `residual_uncertainty > 0`이면 `hybrid_kb`도 기본적으로 `hold`

## Non-Goal

- 이 handoff 문서는 evidence 수집 규칙을 바꾸지 않는다
- diff 계산 규칙을 새로 정의하지 않는다
- KB patch를 바로 적용하는 결정을 대신하지 않는다
