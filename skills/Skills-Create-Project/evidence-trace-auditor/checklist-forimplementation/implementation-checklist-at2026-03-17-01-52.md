# evidence-trace-auditor 구현용 체크리스트

> 목적: 정합성 평가용 checklist를 기준으로 `evidence-trace-auditor`의 첫 구현 slice를 `raw_smoke_report -> evidence_ledger -> support_audit`로 내린다.
> 선행조건: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-52.md`

## A. Input Lock

- [ ] `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md`의 `Canonical Design Takeaways`를 source of truth로 읽는다
- [ ] `execution-contract-mapper`의 `contract_diff_basis`를 선행 입력으로 고정한다
- [ ] raw smoke report JSON을 첫 evidence input으로 고정한다

## B. First Vertical Slice

- [ ] 첫 vertical slice를 `build-evidence-ledger`로 고정한다
- [ ] evidence ledger entry를 `finding_family`, `kind`, `name`, `observed_bucket`, `evidence`, `trace_status`, `action` 구조로 정의한다
- [ ] 두 번째 subcommand를 `audit-support`로 두고 `supported`, `missing_evidence`, `residual_uncertainty`를 계산한다
- [ ] artifact path slice에서는 file exists -> `verified_evidence`, required path missing -> `missing_evidence` 규칙을 구현한다

## C. Script + TDD

- [ ] `scripts/`에 첫 auditor script를 만든다
- [ ] 대응 TDD 파일을 먼저 고정한다
- [ ] `--help`, exit code, stdout/stderr 계약을 먼저 설계한다

## D. Smoke + Evidence

- [ ] 실제 raw smoke report 1개와 contract_diff_basis 1개를 smoke input으로 고정한다
- [ ] evidence ledger JSON/MD와 support audit JSON/MD를 `references/`에 남긴다
- [ ] 반복 버그가 생기면 `references/troubleshooting.md`에 케이스로 추가한다

## E. Follow-up Slices

- [ ] `test_result_evidence`를 두 번째 slice로 구현하고 JUnit XML 기반 smoke evidence를 남긴다
- [ ] `log_evidence`를 세 번째 slice로 구현하고 JSONL log 기반 smoke evidence를 남긴다
- [ ] `artifact_path_evidence`를 네 번째 slice로 구현하고 manifest 기반 smoke evidence를 남긴다
- [ ] `attestation_evidence`를 다섯 번째 slice로 구현하고 tool execution attestation 기반 smoke evidence를 남긴다
- [ ] `tool_call_evidence`를 여섯 번째 slice로 구현하고 command/args/stdout-stderr/output 기반 smoke evidence를 남긴다

## F. Current Progress

- [x] 첫 slice `raw_smoke_report -> evidence_ledger -> support_audit`를 구현했다
- [x] 두 번째 slice `test_result_evidence`를 구현했다
- [x] 세 번째 slice `log_evidence`를 구현했다
- [x] 네 번째 slice `artifact_path_evidence`를 구현했다
- [x] 다섯 번째 slice `attestation_evidence`를 구현했다
- [x] 여섯 번째 slice `tool_call_evidence`를 구현했다
