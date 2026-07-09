# Vertical Slice: promotion trigger evaluator

## Purpose

`promotion_candidate_summary`를 읽고 `hybrid_kb` 또는 `canonical_design_kb` 승격 가능 여부를 판정한다.

## Input

- `promotion_candidate_summary` JSON

## Output

- machine-readable `promotion_trigger_evaluation` JSON
- human-readable Markdown summary

## Current Rule

- `lesson_candidate >= 1` 이고 `residual_uncertainty = 0`이면 `hybrid_kb = promote`
- `repetition_count >= 2` 같은 반복 검증 신호가 추가로 있어야 `canonical_design_kb`를 자동 candidate로 본다
- 위 조건이 없으면 `hold`

## Smoke Artifacts

- Hold case:
  - [promotion-trigger-evaluation-hold-smoke-at2026-03-17-03-14.json](./promotion-trigger-evaluation-hold-smoke-at2026-03-17-03-14.json)
- Positive case:
  - [promotion-trigger-evaluation-positive-smoke-at2026-03-17-03-14.json](./promotion-trigger-evaluation-positive-smoke-at2026-03-17-03-14.json)
