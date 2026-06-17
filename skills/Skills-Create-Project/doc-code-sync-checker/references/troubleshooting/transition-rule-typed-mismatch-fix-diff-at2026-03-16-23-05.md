# transition_rule typed mismatch fix diff

- measured_at: `2026-03-16T23:06:10+09:00`
- experiment: `transition_rule typed mismatch reduction after fix`

## Before

- artifact: [typed-mismatch-transition-rule-smoke-report-at2026-03-16-22-57.json](./typed-mismatch-transition-rule-smoke-report-at2026-03-16-22-57.json)
- `missing_in_code = 1`
- `missing_in_doc = 1`
- `typed_mismatch = 1`

## After

- artifact: [typed-mismatch-transition-rule-post-fix-smoke-report-at2026-03-16-23-05.json](./typed-mismatch-transition-rule-post-fix-smoke-report-at2026-03-16-23-05.json)
- `missing_in_code = 0`
- `missing_in_doc = 0`
- `typed_mismatch = 0`

## Delta

- `missing_in_code: -1`
- `missing_in_doc: -1`
- `typed_mismatch: -1`

## Metric

- `typed_mismatch_reduction_after_fix = 1.0`
  - class: `strict-on-experiment`
  - formula: `(typed_mismatch_before_fix - typed_mismatch_after_fix) / typed_mismatch_before_fix`
