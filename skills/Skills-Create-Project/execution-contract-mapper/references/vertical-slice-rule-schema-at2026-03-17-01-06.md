# execution-contract-mapper vertical slice — rule_schema

## Purpose

- 첫 구현 slice로 `rule_schema`를 고정한다.
- consistency checklist checkbox item을 machine-readable contract object로 내린다.

## Input

- source KB:
  - `knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md`
- consistency checklist:
  - `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-00.md`

## Output

- JSON artifact:
  - `references/rule-schema-smoke-at2026-03-17-01-06.json`
- Markdown summary:
  - `references/rule-schema-smoke-at2026-03-17-01-06.md`

## Contract Shape

- `kind`
- `name`
- `source`
- `value`
- `evidence`

## Current Result

- `rule_count = 15`
- section-scoped rule name 생성 확인
- machine-readable artifact와 human-readable summary를 함께 생성함

## Follow-up

- 두 번째 slice는 `schema_contract`
- 세 번째 slice는 `cli_contract`
