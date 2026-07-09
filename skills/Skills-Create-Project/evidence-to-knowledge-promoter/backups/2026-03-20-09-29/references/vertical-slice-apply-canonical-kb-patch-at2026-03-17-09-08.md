# Vertical Slice: apply-canonical-kb-patch

## Goal

- `canonical_kb_patch_plan`을 읽고
- target canonical KB copy에만 patch를 적용해
- `canonical_kb_patch_apply_result`를 남긴다.

## Fixed Inputs

- `canonical_kb_patch_plan`
- target canonical KB path
- output canonical KB copy path

## Fixed Rule

- `append` operation만 실제 적용한다
- `hold` operation은 적용하지 않고 skip으로 기록한다
- 중복 bullet이 있으면 다시 적용하지 않는다
- target canonical KB 원본은 수정하지 않고 output copy에만 쓴다

## Output Shape

- `contract_family = canonical_kb_patch_apply_result`
- `patch_decision`
- `applied_count`
- `skipped_count`
- `operations`

## Non-Goal

- canonical candidate gate를 우회하지 않는다
- KB 섹션을 새로 만들지 않는다
- source canonical KB를 직접 덮어쓰지 않는다
