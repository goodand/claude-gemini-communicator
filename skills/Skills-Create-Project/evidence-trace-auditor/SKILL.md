---
name: evidence-trace-auditor
description: >-
  verification-decision-gate family의 evidence-audit specialist. Use this
  skill when runtime logs, test outputs, JSON artifacts, and other execution
  evidence must be collected and audited against expected contracts. broader
  multi-concern consistency judgment는 verification-decision-gate를 사용하라.
---

# Evidence Trace Auditor

실제 실행에서 나온 증거를 모아 계약과 대조하는 스캐폴드.

## When to use

- runtime log, test output, JSON artifact 같은 실행 증거를 contract 기준으로 감사할 때
- execution evidence ledger와 support audit를 정리할 때
- agent self-report 대신 trace status와 support-gap를 contract 기준으로 판정할 때
- image evidence와 text judgment가 함께 있는 review artifact 전에 machine-truth evidence layer를 먼저 정리할 때

## Workflow

1. `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md`의 `Canonical Design Takeaways`를 source of truth로 읽는다
2. `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-52.md`로 evidence audit의 경계와 trace status를 먼저 고정한다
3. `checklist-forimplementation/implementation-checklist-at2026-03-17-01-52.md`로 첫 slice를 `raw_smoke_report -> evidence_ledger -> support_audit`로 내린다
4. `references/evidence-status-rules-at2026-03-17-02-36.md`를 읽고 `verified_evidence / missing_evidence / residual_uncertainty` 판정 규칙을 먼저 고정한다
5. `execution-contract-mapper`의 `contract_diff_basis`와 raw smoke report를 연결해 support / gap / residual uncertainty를 출력한다

## Knowledge Bases

- `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md` — local artifact를 기반으로 canonical slice를 함께 담는 hybrid_kb
- `knowledge_bases/evidence-trace-auditor-issues-at2026-03-16.md` — 현재 이슈와 필요성

## Checklists

- `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-52.md` — evidence audit 정합성 기준
- `checklist-forimplementation/implementation-checklist-at2026-03-17-01-52.md` — 첫 구현 slice 기준

## Scripts

- `scripts/evidence_trace_auditor.py` — raw smoke report를 evidence ledger로 정규화하고 support audit를 계산
- `scripts/evidence_trace_auditor.py build-test-result-ledger` — JUnit XML test result를 evidence ledger로 정규화
- `scripts/evidence_trace_auditor.py build-log-evidence-ledger` — JSONL log record를 evidence ledger로 정규화
- `scripts/evidence_trace_auditor.py build-artifact-path-ledger` — artifact path manifest를 evidence ledger로 정규화
- `scripts/evidence_trace_auditor.py build-attestation-ledger` — tool execution attestation manifest를 evidence ledger로 정규화
- `scripts/evidence_trace_auditor.py build-tool-call-ledger` — tool call manifest를 evidence ledger로 정규화
- `scripts/test_evidence_trace_auditor.py` — 첫 vertical slice TDD

## References

- `references/evidence-status-rules-at2026-03-17-02-36.md` — trace status 판정 규칙과 artifact_path_evidence 해석 기준
- `references/execution-evidence-handoff-at2026-03-17-08-54.md` — `execution_evidence_planner.py` payload를 evidence audit 입력으로 읽는 규칙
- `references/evidence-promotion-bridge-at2026-03-17-03-52.md` — audit 결과를 KB insight 승격으로 넘기는 handoff
- `references/troubleshooting.md` — 구현/실험 중 나온 반복 버그 기록
- `references/release-evidence-bundle-at2026-06-15-20-22.md` — remote release evidence bundle 수집 규칙(clean worktree, git ls-files, no-op=not-verified, doc-code-sync handoff)

## Notes

- v0.1은 raw smoke report와 contract_diff_basis를 연결하는 evidence audit slice를 구현했다
- 두 번째 slice로 `test_result_evidence`를 추가했다
- 세 번째 slice로 `log_evidence`를 추가했다
- 네 번째 slice로 `artifact_path_evidence`를 추가했다
- 다섯 번째 slice로 `attestation_evidence`를 추가했다
- 여섯 번째 slice로 `tool_call_evidence`를 추가했다
- concept/contract 정합성은 별도 skill에서 선행한다
- planner handoff를 받을 때는 `references/execution-evidence-handoff-at2026-03-17-08-54.md`의 payload mapping을 따른다
- audit 결과를 KB insight로 올릴 때는 `evidence-to-knowledge-promoter`로 handoff한다
- human-facing markdown와 machine-truth manifest를 함께 설계하는 multimodal review structuring은 `image-text-cot-review`로 handoff한다
