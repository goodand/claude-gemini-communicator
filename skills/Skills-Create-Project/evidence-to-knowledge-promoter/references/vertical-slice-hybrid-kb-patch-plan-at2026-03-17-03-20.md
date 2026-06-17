# Vertical Slice: lesson-to-hybrid-kb patch plan

## Purpose

`promotion_trigger_evaluation` 결과를 읽고 실제 `hybrid_kb`에 어떤 섹션 패치를 적용할지 계획으로 내린다.

## Input

- `promotion_candidate_summary`
- `promotion_trigger_evaluation`
- target `hybrid_kb`

## Output

- machine-readable `hybrid_kb_patch_plan` JSON
- human-readable Markdown patch plan

## Current Rule

- `hybrid_kb = hold`이면 patch는 보류하고 troubleshooting 성격의 hold plan만 남긴다
- `hybrid_kb = promote`이면
  - `lesson_candidate`는 `Canonical Design Takeaways`
  - candidate `delta`는 `Current Implementation Target`
  - `finding`은 `Research Focus`
  로 patch plan을 만든다
- `canonical_design_kb`는 아직 자동 패치하지 않는다

## Smoke Artifacts

- Hold case:
  - [hybrid-kb-patch-plan-hold-smoke-at2026-03-17-03-20.json](./hybrid-kb-patch-plan-hold-smoke-at2026-03-17-03-20.json)
- Promote case:
  - [hybrid-kb-patch-plan-positive-smoke-at2026-03-17-03-20.json](./hybrid-kb-patch-plan-positive-smoke-at2026-03-17-03-20.json)
