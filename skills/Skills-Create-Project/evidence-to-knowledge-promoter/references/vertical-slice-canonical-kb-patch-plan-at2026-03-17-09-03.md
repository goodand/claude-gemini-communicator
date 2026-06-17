# Vertical Slice: canonical_kb_patch_plan

## Goal

- `canonical_candidate_evaluation` 결과를 읽고
- `canonical_design_kb`로 실제로 옮길 lesson candidate만
- narrow patch plan으로 정리한다.

## Fixed Inputs

- `promotion_candidate_summary`
- `canonical_candidate_evaluation`
- target canonical KB path

## Fixed Rule

- `canonical_decision = candidate`일 때만 patch plan을 만든다
- `lesson_candidate`이면서 `promotion_decision = candidate`인 항목만 대상으로 삼는다
- `candidate_lessons`에 포함된 이름만 canonical 대상이 된다
- `delta`나 단발 `finding`은 canonical KB patch plan에 포함하지 않는다

## Output Shape

- `contract_family = canonical_kb_patch_plan`
- `patch_decision`
- `canonical_decision`
- `planned_operations`

## Non-Goal

- canonical KB에 실제 적용하지 않는다
- 새로운 canonical 승격 규칙을 추가하지 않는다
- hybrid KB patch 규칙과 섞지 않는다
