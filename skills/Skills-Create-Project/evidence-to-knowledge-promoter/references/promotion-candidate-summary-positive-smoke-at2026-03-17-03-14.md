# evidence-to-knowledge-promoter promotion summary

- generated_at: `2026-03-17T03:07:53+09:00`
- input_support_audit: `evidence-trace-auditor/references/support-audit-smoke-at2026-03-17-02-00.json`
- input_baseline_diff: `baseline-diff-lab/references/doc-code-sync-path-pre-metrics-fix-diff-at2026-03-17-00-10.json`

## Counts

- finding: `3`
- delta: `3`
- lesson_candidate: `1`
- residual_uncertainty: `0`

## Entries

- `finding` / `status:ready`
  - source: `evidence-trace-auditor/references/support-audit-smoke-at2026-03-17-02-00.json`
  - promotion_decision: `observe`
  - evidence: `missing_in_code:status:ready`
  - reason: verified evidence가 있어 reusable finding으로 남길 수 있다.
- `finding` / `status:running`
  - source: `evidence-trace-auditor/references/support-audit-smoke-at2026-03-17-02-00.json`
  - promotion_decision: `observe`
  - evidence: `missing_in_doc:status:running`
  - reason: verified evidence가 있어 reusable finding으로 남길 수 있다.
- `finding` / `status`
  - source: `evidence-trace-auditor/references/support-audit-smoke-at2026-03-17-02-00.json`
  - promotion_decision: `observe`
  - evidence: `typed_mismatch:status`
  - reason: verified evidence가 있어 reusable finding으로 남길 수 있다.
- `delta` / `typed_mismatch_count`
  - source: `baseline-diff-lab/references/doc-code-sync-path-pre-metrics-fix-diff-at2026-03-17-00-10.json`
  - promotion_decision: `candidate`
  - evidence: `typed_mismatch_count`
  - reason: before/after diff가 수치로 닫혀 reusable delta 후보가 된다.
- `delta` / `total_finding_count`
  - source: `baseline-diff-lab/references/doc-code-sync-path-pre-metrics-fix-diff-at2026-03-17-00-10.json`
  - promotion_decision: `candidate`
  - evidence: `total_finding_count`
  - reason: before/after diff가 수치로 닫혀 reusable delta 후보가 된다.
- `delta` / `zero_drift_pair_rate`
  - source: `baseline-diff-lab/references/doc-code-sync-path-pre-metrics-fix-diff-at2026-03-17-00-10.json`
  - promotion_decision: `observe`
  - evidence: `zero_drift_pair_rate`
  - reason: 수치 변화는 있지만 바로 lesson 규칙으로 승격하기엔 추가 반복 검증이 필요하다.
- `lesson_candidate` / `verified-evidence-backed-fix-pattern`
  - source: `baseline-diff-lab/references/doc-code-sync-path-pre-metrics-fix-diff-at2026-03-17-00-10.json`
  - promotion_decision: `candidate`
  - evidence: `typed_mismatch_count`
  - reason: verified evidence와 positive delta가 함께 있어 lesson candidate로 승격할 수 있다.
