# evidence-to-knowledge-promoter promotion trigger evaluation

- generated_at: `2026-03-17T03:08:10+09:00`
- input_summary: `evidence-to-knowledge-promoter/references/promotion-candidate-summary-positive-smoke-at2026-03-17-03-14.json`

## Summary Counts

- finding: `3`
- delta: `3`
- lesson_candidate: `1`
- residual_uncertainty: `0`

## Decisions

- hybrid_kb: `promote`
  - reason: lesson_candidate가 있고 residual uncertainty가 없어 hybrid_kb source of truth slice로 승격 가능하다.
- canonical_design_kb: `hold`
  - reason: v0.1에서는 반복 검증 신호가 명시될 때만 canonical_design_kb 후보로 본다.
