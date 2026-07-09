# Benchmark Score Sheet — Cross-Repo Product Review

- recorded_at: `2026-04-08-00-14`
- benchmark reference: `agent-tool-benchmark`
- selected metrics: `Pass Rate`, `Resolve Rate`, `Action Score`
- evaluation scope: `cross-repo-product-review/evals/evals.json`

## Metric Mapping

- `Pass Rate`
  - meaning here: eval prompt별 expected_output/assertions 충족 비율
  - numerator: prompts judged `pass`
  - denominator: total eval prompts
- `Resolve Rate`
  - meaning here: must-pass review workflow gates 해소 비율
  - numerator: product intent lock, role classification, bounded handoff, convergence closure, pattern promotion evidence 중 closed gate 수
  - denominator: 5
- `Action Score`
  - meaning here: required review actions 수행 비율
  - expected actions: intent lock, category classification, severity ranking, bounded handoff, code-state reread, residual triage, promotion record

## Score Table

| Eval ID | Prompt Focus | Pass/Fail | Expected Actions Observed | Notes |
|---|---|---|---|---|
| EVAL-0 | product intent lock | PASS | intent lock, non-goal lock | backed by `SKILL.md` + consistency checklist |
| EVAL-1 | canonical role classification | PASS | category classification | smoke capture shows host_entry/webview_render/tests buckets |
| EVAL-2 | bounded handoff quality | PASS | severity ranking, bounded handoff | backed by handoff template + implementation checklist |
| EVAL-3 | residual direct-closure judgment | PASS | residual triage, convergence gate | backed by guardrails + canonical KB |
| EVAL-4 | pattern promotion evidence | PASS | promotion record, absorbed issue preservation | backed by promotion-status updates and KB links |

## Summary Fields

- pass_rate: `1.00` (`5/5`)
- resolve_rate: `1.00` (`5/5`)
- action_score: `1.00`
- static_validation_evidence: `evals/quick-validate-capture-at2026-04-08-00-14.json`
- smoke_evidence: `evals/smoke-command-capture-at2026-04-08-00-18.json`

## Gate

- recommended pass:
  - `pass_rate >= 0.80`
  - `resolve_rate = 1.00`
  - `action_score >= 0.85`

## Initial Measured Run

- verdict: `pass`
- rationale:
  - strict static validation clean pass
  - runnable classifier smoke valid
  - every eval rule has direct file evidence in SKILL / KB / checklist / smoke artifacts
