# execution-contract-mapper 구현용 체크리스트

> 목적: 정합성 평가용 checklist를 기준으로 `execution-contract-mapper`의 첫 구현 slice를 `rule_schema`로 내린다.
> 선행조건: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-00.md`

## A. Input Lock

- [ ] `knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md`의 `Canonical Design Takeaways`를 source of truth로 읽는다
- [ ] consistency checklist 항목을 구현 입력으로 내린다

## B. First Vertical Slice

- [ ] 첫 vertical slice를 `rule_schema`로 고정한다
- [ ] checklist item을 `kind`, `name`, `source`, `value`, `evidence` 구조의 rule schema object로 내리는 출력을 정의한다
- [ ] machine-readable artifact와 human-readable summary를 함께 출력하는 형식을 정의한다

## C. Script + TDD

- [ ] `scripts/`에 첫 mapper script를 만든다
- [ ] script를 만들기 전에 대응하는 TDD 파일 이름과 위치를 먼저 고정한다
- [ ] `--help`, exit code, stdout/stderr 계약을 먼저 설계한다

## D. Smoke + Evidence

- [ ] 최소 smoke input 1개와 expected contract artifact 1개를 고정한다
- [ ] 첫 smoke 결과를 `references/`에 evidence로 남긴다
- [ ] 반복 버그가 생기면 `references/troubleshooting.md`에 케이스로 추가한다

## E. Follow-up Slices

- [ ] `schema_contract`를 두 번째 slice 후보로 유지한다
- [ ] `cli_contract`를 세 번째 slice 후보로 유지한다
- [ ] `contract_diff_basis`는 stable contract artifact 이후 단계로 둔다
