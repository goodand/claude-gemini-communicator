# execution-contract-mapper vertical slice — schema_contract

## Purpose

- 두 번째 구현 slice로 `schema_contract`를 고정한다.
- `rule_schema` artifact를 다음 checker/validator가 읽을 수 있는 JSON Schema 계약으로 내린다.

## Input

- source artifact:
  - `references/rule-schema-smoke-at2026-03-17-01-06.json`

## Output

- JSON artifact:
  - `references/schema-contract-smoke-at2026-03-17-01-11.json`
- Markdown summary:
  - `references/schema-contract-smoke-at2026-03-17-01-11.md`

## Contract Shape

- top-level artifact schema
- required field list
- nested `rules[]` item schema
- nested `value` object schema

## Current Result

- `contract_family = schema_contract`
- `field_count = 9`
- required top-level fields와 nested rule object required fields를 함께 고정함

## Follow-up

- 세 번째 slice는 `cli_contract`
- 그 다음은 `contract_diff_basis`
