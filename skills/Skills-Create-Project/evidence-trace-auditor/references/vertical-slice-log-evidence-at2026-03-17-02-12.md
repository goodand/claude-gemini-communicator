# evidence-trace-auditor vertical slice: log_evidence

- generated_at: `2026-03-17T02:12:00+09:00`
- status: `implemented`
- source_of_truth: [evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md)
- sample_input:
  - [log-evidence-sample-at2026-03-17-02-08.jsonl](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/log-evidence-sample-at2026-03-17-02-08.jsonl)
- smoke_outputs:
  - [log-evidence-ledger-smoke-at2026-03-17-02-12.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/log-evidence-ledger-smoke-at2026-03-17-02-12.json)
  - [log-evidence-ledger-smoke-at2026-03-17-02-12.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/log-evidence-ledger-smoke-at2026-03-17-02-12.md)
  - [log-support-audit-smoke-at2026-03-17-02-12.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/log-support-audit-smoke-at2026-03-17-02-12.json)
  - [log-support-audit-smoke-at2026-03-17-02-12.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-trace-auditor/references/log-support-audit-smoke-at2026-03-17-02-12.md)

## Intent

- OpenTelemetry-style 공통 필드를 흉내 낸 JSONL log record를 evidence ledger entry로 정규화한다.
- `attributes.observed_bucket`이 있으면 현재 diff basis에 바로 매핑한다.
- log line은 timestamp, severity, body를 합쳐 code evidence로 보존한다.

## Result

- ledger entry_count: `2`
- support audit supported_count: `2`
- support audit missing_evidence_count: `0`
- support audit residual_uncertainty_count: `0`
- support ratio: `1.0`

## Interpretation

- current `contract_diff_basis`와 직접 맞는 observed bucket이 있으면 log도 support evidence로 바로 사용할 수 있다.
- log layer는 `missing_contract_unit`과 `contract_value_changed` 같은 typed bucket을 evidence-first로 보강하는 데 적합하다.
