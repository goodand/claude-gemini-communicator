# Vertical Slice: canonical candidate evaluator

## Purpose

`promotion_candidate_summary`와 `promotion_trigger_evaluation`을 읽고 `canonical_design_kb` 후보 여부와 부족한 조건을 구조화한다.

## Input

- `promotion_candidate_summary`
- `promotion_trigger_evaluation`

## Output

- machine-readable `canonical_candidate_evaluation`
- human-readable Markdown summary

## Current Rule

- `hybrid_kb`가 먼저 `promote` 상태여야 한다
- `residual_uncertainty = 0` 이어야 한다
- `lesson_candidate`가 있어야 한다
- `repetition_count >= 2` 같은 반복 검증 신호가 있어야 `canonical_design_kb = candidate`
- 위 조건이 부족하면 `hold`하고 `missing_requirements`를 남긴다

## Smoke Artifacts

- Hold case:
  - [canonical-candidate-evaluation-hold-smoke-at2026-03-17-03-36.json](./canonical-candidate-evaluation-hold-smoke-at2026-03-17-03-36.json)
- Candidate case:
  - [canonical-candidate-evaluation-positive-smoke-at2026-03-17-03-36.json](./canonical-candidate-evaluation-positive-smoke-at2026-03-17-03-36.json)
