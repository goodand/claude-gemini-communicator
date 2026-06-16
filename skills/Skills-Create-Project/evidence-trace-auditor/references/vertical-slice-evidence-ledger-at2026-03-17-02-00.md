# evidence-trace-auditor vertical slice: raw_smoke_report -> evidence_ledger -> support_audit

- generated_at: `2026-03-17T02:00:00+09:00`
- status: `implemented`
- source_of_truth: [evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md)
- upstream_inputs:
  - raw smoke report: [typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/references/typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json)
  - contract diff basis: [contract-diff-basis-smoke-at2026-03-17-01-40.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json)
- smoke_outputs:
  - [evidence-ledger-smoke-at2026-03-17-02-00.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/evidence-ledger-smoke-at2026-03-17-02-00.json)
  - [evidence-ledger-smoke-at2026-03-17-02-00.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/evidence-ledger-smoke-at2026-03-17-02-00.md)
  - [support-audit-smoke-at2026-03-17-02-00.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/support-audit-smoke-at2026-03-17-02-00.json)
  - [support-audit-smoke-at2026-03-17-02-00.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/support-audit-smoke-at2026-03-17-02-00.md)

## Intent

- raw smoke report에 들어 있는 finding을 evidence-first object로 바꾼다.
- `contract_diff_basis`의 recommended bucket과 대조해 어떤 finding이 근거 있는 evidence인지 먼저 판정한다.
- evidence가 없거나 bucket이 정의되지 않으면 `missing_evidence` 또는 `residual_uncertainty`로 남긴다.

## Result

- evidence ledger entry_count: `3`
- support audit supported_count: `3`
- support audit missing_evidence_count: `0`
- support audit residual_uncertainty_count: `0`
- support ratio: `1.0`

## Notes

- v0.1은 raw smoke report JSON만 다룬다.
- 후속 slice에서 `test_result_evidence`, `log_evidence`, `artifact_path_evidence`를 추가한다.
