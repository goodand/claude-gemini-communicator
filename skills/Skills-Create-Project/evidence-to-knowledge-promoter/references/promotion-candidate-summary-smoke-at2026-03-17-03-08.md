# evidence-to-knowledge-promoter promotion summary

- generated_at: `2026-03-17T03:04:42+09:00`
- input_support_audit: `evidence-trace-auditor/references/artifact-path-support-audit-smoke-at2026-03-17-02-20.json`
- input_baseline_diff: `baseline-diff-lab/references/doc-code-sync-path-pre-metrics-fix-diff-at2026-03-17-00-10.json`

## Counts

- finding: `2`
- delta: `3`
- lesson_candidate: `0`
- residual_uncertainty: `1`

## Entries

- `finding` / `contract-diff-basis-json`
  - source: `evidence-trace-auditor/references/artifact-path-support-audit-smoke-at2026-03-17-02-20.json`
  - promotion_decision: `observe`
  - evidence: `artifact_path:contract-diff-basis-json`
  - reason: verified evidence가 있어 reusable finding으로 남길 수 있다.
- `finding` / `log-support-audit-md`
  - source: `evidence-trace-auditor/references/artifact-path-support-audit-smoke-at2026-03-17-02-20.json`
  - promotion_decision: `observe`
  - evidence: `artifact_path:log-support-audit-md`
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
- `residual_uncertainty` / `missing-smoke-artifact`
  - source: `evidence-trace-auditor/references/artifact-path-support-audit-smoke-at2026-03-17-02-20.json`
  - promotion_decision: `hold`
  - evidence: `artifact_path:missing-smoke-artifact`
  - reason: evidence가 부족하거나 bucket 해석이 아직 닫히지 않았다.
