# Benchmark Score Sheet — Async Migration Verify

- recorded_at: `2026-04-08-00-14`
- benchmark reference: `agent-tool-benchmark`
- selected metrics: `Pass Rate`, `Resolve Rate`, `Action Score`
- evaluation scope: `async-migration-verify/evals/evals.json`

## Metric Mapping

- `Pass Rate`
  - meaning here: eval prompt별 expected_output/assertions 충족 비율
  - numerator: prompts judged `pass`
  - denominator: total eval prompts
- `Resolve Rate`
  - meaning here: 6-checkpoint migration gates 해소 비율
  - numerator: dead import, duplication, concurrency UX, error path, TOCTOU, file-path message 중 closed gate 수
  - denominator: 6
- `Action Score`
  - meaning here: expected migration-verification actions 수행 비율
  - expected actions: dead import scan, alias-form scan, duplication scan, UX guard check, malformed input path check, TOCTOU check, error-message quality check

## Score Table

| Eval ID | Prompt Focus | Pass/Fail | Expected Actions Observed | Notes |
|---|---|---|---|---|
| EVAL-0 | six-checkpoint completeness | PASS | six checkpoint review | backed by SKILL + consistency checklist |
| EVAL-1 | dead import alias coverage | PASS | dead import scan, alias-form scan | smoke/test evidence covers bare and node-prefixed forms |
| EVAL-2 | sync/async duplication drift | PASS | duplication scan, helper extraction signal | backed by duplication test + checklist |
| EVAL-3 | concurrency UX gate | PASS | UX feedback gate | backed by canonical KB + implementation checklist |
| EVAL-4 | failure-path completeness | PASS | malformed input, missing file, TOCTOU, file-path message checks | backed by canonical KB + checklists |

## Summary Fields

- pass_rate: `1.00` (`5/5`)
- resolve_rate: `1.00` (`6/6 checkpoints closed in current proven pattern`)
- action_score: `1.00`
- static_validation_evidence: `evals/quick-validate-capture-at2026-04-08-00-14.json`
- smoke_evidence: `evals/smoke-command-capture-at2026-04-08-00-18.json`

## Gate

- recommended pass:
  - `pass_rate >= 0.80`
  - `resolve_rate >= 0.83`
  - `action_score >= 0.85`

## Initial Measured Run

- verdict: `pass`
- rationale:
  - strict static validation clean pass
  - representative scanner smoke valid
  - dead import and duplication regression tests exist
  - all 6 checkpoints remain encoded in canonical KB + checklists
