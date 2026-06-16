# evidence-trace-auditor vertical slice: test_result_evidence

- generated_at: `2026-03-17T02:06:00+09:00`
- status: `implemented`
- source_of_truth: [evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md)
- sample_input:
  - [test-result-sample-at2026-03-17-02-05.xml](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/test-result-sample-at2026-03-17-02-05.xml)
- smoke_outputs:
  - [test-result-evidence-ledger-smoke-at2026-03-17-02-06.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/test-result-evidence-ledger-smoke-at2026-03-17-02-06.json)
  - [test-result-evidence-ledger-smoke-at2026-03-17-02-06.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/test-result-evidence-ledger-smoke-at2026-03-17-02-06.md)
  - [test-result-support-audit-smoke-at2026-03-17-02-06.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/test-result-support-audit-smoke-at2026-03-17-02-06.json)
  - [test-result-support-audit-smoke-at2026-03-17-02-06.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/test-result-support-audit-smoke-at2026-03-17-02-06.md)

## Intent

- JUnit XML에서 failing/skipped testcase만 evidence ledger entry로 추출한다.
- failing testcase는 `contract_value_changed` candidate로 본다.
- skipped testcase는 evidence는 있지만 bucket이 고정되지 않아 `residual_uncertainty`로 남긴다.

## Result

- ledger entry_count: `2`
- support audit supported_count: `1`
- support audit missing_evidence_count: `0`
- support audit residual_uncertainty_count: `1`
- support ratio: `0.5`

## Interpretation

- `failed` testcase는 current diff basis와 직접 연결 가능했다.
- `skipped` testcase는 evidence는 있으나 현재 diff bucket 체계에 바로 매핑되지 않아 residual로 남았다.
- 이 residual은 후속 `test_result_evidence` 정교화 또는 별도 bucket 정책이 필요함을 보여준다.
