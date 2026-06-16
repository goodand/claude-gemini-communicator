# execution-contract-mapper 정합성 평가 체크리스트

> 목적: `execution-contract-mapper`가 개념 공간을 실행 계약 공간으로 내리는 중간층 역할을 올바르게 고정하는지 점검한다.
> source of truth: `knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md`의 `Canonical Design Takeaways`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `개념 공간 -> 실행 계약 공간` 변환으로 고정돼 있다
- [ ] 이 skill이 checklist, schema, CLI surface, rule schema 같은 contract artifact를 만드는 중간층으로 정의돼 있다

## B. Boundary

- [ ] runtime evidence 수집/해석은 `evidence-trace-auditor`의 후행 책임으로 분리돼 있다
- [ ] concept-space 역방향 lifting은 `contract-to-concept-mapper`의 인접 책임으로 분리돼 있다
- [ ] implementation checklist가 consistency checklist보다 먼저 source of truth처럼 취급되지 않는다

## C. Source Of Truth Order

- [ ] source of truth 순서가 `Canonical Design Takeaways 또는 더 좁은 canonical KB -> consistency checklist -> implementation checklist -> scripts`로 고정돼 있다
- [ ] consistency checklist가 implementation checklist의 입력임이 명시돼 있다

## D. Contract Family Priority

- [ ] v0.1 우선 contract family가 `rule_schema`, `schema_contract`, `cli_contract`로 명시돼 있다
- [ ] `contract_diff_basis`는 stable contract artifact 이후의 후속 층으로 분리돼 있다
- [ ] 첫 vertical slice가 `rule_schema`로 고정돼 있다

## E. Contract Unit

- [ ] 최소 contract unit이 `kind`, `name`, `source`, `value`, `evidence`를 가진다고 명시돼 있다
- [ ] machine-readable contract artifact와 human-readable contract summary를 분리해 남긴다고 명시돼 있다

## F. Compareability

- [ ] rule schema가 checklist item을 codebase와 compare 가능한 구조적 object로 내리는 층으로 정의돼 있다
- [ ] schema contract가 `field`, `type`, `required`, `constraint`를 구조화한다고 명시돼 있다
- [ ] CLI contract가 `subcommand`, `option`, `argument`, `help`, `exit behavior`를 안정적으로 추출 가능한 surface로 정의돼 있다
