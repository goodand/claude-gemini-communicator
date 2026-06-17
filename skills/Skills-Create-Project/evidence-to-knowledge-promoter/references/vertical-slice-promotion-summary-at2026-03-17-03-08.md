# Vertical Slice: promotion candidate summary

## Purpose

`support_audit + baseline diff -> promotion candidate summary`를 첫 end-to-end slice로 고정한다.

## Input

- support audit JSON
- baseline diff JSON

## Output

- machine-readable `promotion_candidate_summary` JSON
- human-readable Markdown summary

## Minimum Categories

- `finding`
- `delta`
- `lesson_candidate`
- `residual_uncertainty`

## Current Rule

- verified evidence가 있으면 `finding`
- before/after diff가 수치로 닫히면 `delta`
- verified evidence와 positive delta가 함께 있고 residual uncertainty가 없으면 `lesson_candidate`
- missing evidence 또는 unresolved mapping이 있으면 `residual_uncertainty`

## Smoke Artifacts

- [promotion-candidate-summary-smoke-at2026-03-17-03-08.json](./promotion-candidate-summary-smoke-at2026-03-17-03-08.json)
- [promotion-candidate-summary-smoke-at2026-03-17-03-08.md](./promotion-candidate-summary-smoke-at2026-03-17-03-08.md)
