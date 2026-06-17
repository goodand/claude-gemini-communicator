# evidence-trace-auditor 정합성 평가 체크리스트

> 목적: `evidence-trace-auditor`가 stored claim과 verified evidence를 분리하고 contract-aware evidence audit를 수행하는지 점검한다.
> source of truth: `knowledge_bases/evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md`의 `Canonical Design Takeaways`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `runtime/test/json/file evidence를 구조화해 contract와 대조 가능한 evidence object로 정리`하는 것으로 고정돼 있다
- [ ] 이 skill이 contract 설계가 아니라 evidence normalization/audit 중간층으로 정의돼 있다

## B. Boundary

- [ ] contract artifact 설계는 `execution-contract-mapper`의 선행 책임으로 분리돼 있다
- [ ] code/doc drift 추출은 `doc-code-sync-checker`의 선행 책임으로 분리돼 있다
- [ ] code 수정 자동화는 이 skill의 비목표로 남아 있다

## C. Source Of Truth Order

- [ ] source of truth 순서가 `Canonical Design Takeaways 또는 더 좁은 canonical KB -> consistency checklist -> implementation checklist -> scripts`로 고정돼 있다
- [ ] `contract_diff_basis`가 evidence audit의 선행 입력임이 명시돼 있다

## D. Evidence Unit

- [ ] 최소 evidence ledger entry가 `finding_family`, `kind`, `name`, `observed_bucket`, `evidence`, `trace_status`, `action`을 가진다고 명시돼 있다
- [ ] machine-readable evidence ledger와 human-readable summary를 함께 남긴다고 명시돼 있다

## E. Audit Semantics

- [ ] `trace_status` 최소 값이 `verified_evidence`, `missing_evidence`, `residual_uncertainty`로 고정돼 있다
- [ ] `artifact_path_evidence`에서 파일이 실제로 존재하면 `verified_evidence`, required path가 없으면 `missing_evidence`로 분류한다고 명시돼 있다
- [ ] evidence는 있지만 현재 bucket 체계와 직접 연결되지 않으면 `residual_uncertainty`로 남긴다고 명시돼 있다
- [ ] support audit가 `recommended_diff_buckets`와 실제 evidence entry를 대조하는 방식으로 정의돼 있다
- [ ] raw smoke report JSON이 v0.1 첫 입력으로 고정돼 있다

## F. Follow-up Scope

- [ ] 후속 slice 후보가 `test_result_evidence`, `log_evidence`, `artifact_path_evidence` 순서로 유지돼 있다
