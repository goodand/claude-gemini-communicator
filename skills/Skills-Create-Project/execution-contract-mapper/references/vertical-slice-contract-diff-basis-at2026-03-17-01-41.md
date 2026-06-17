# execution-contract-mapper vertical slice: contract_diff_basis

- generated_at: `2026-03-17T01:41:00+09:00`
- status: `implemented`
- source_of_truth: [execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md)
- upstream_artifacts:
  - [rule-schema-smoke-at2026-03-17-01-06.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/rule-schema-smoke-at2026-03-17-01-06.json)
  - [schema-contract-smoke-at2026-03-17-01-11.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/schema-contract-smoke-at2026-03-17-01-11.json)
  - [cli-contract-smoke-at2026-03-17-01-29.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/cli-contract-smoke-at2026-03-17-01-29.json)
- smoke_outputs:
  - [contract-diff-basis-smoke-at2026-03-17-01-40.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json)
  - [contract-diff-basis-smoke-at2026-03-17-01-40.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.md)

## Intent

- `contract_diff_basis`는 already-stable contract artifact를 future diff skill이 읽을 공통 비교 기준으로 정리하는 slice다.
- 이 slice는 raw text diff를 하지 않는다.
- 대신 family별 `identity_keys`, `compare_fields`, `candidate_buckets`, `evidence_fields`를 고정한다.

## Scope

- input family:
  - `rule_schema`
  - `schema_contract`
  - `cli_contract`
- output family:
  - `contract_diff_basis`

## Fixed Basis

- `rule_schema`
  - unit: `rule`
  - identity: `name`
  - buckets: `missing_contract_unit`, `extra_contract_unit`, `contract_value_changed`
- `schema_contract`
  - unit: `schema_property`
  - identity: `property_name`
  - buckets: `missing_contract_unit`, `extra_contract_unit`, `requiredness_changed`, `contract_value_changed`
- `cli_contract`
  - unit: `cli_subcommand_or_argument`
  - identity: `subcommand.name`, `argument.dest`
  - buckets: `missing_contract_unit`, `extra_contract_unit`, `cli_argument_surface_changed`, `contract_value_changed`

## Result

- basis_count: `3`
- compare_order: `rule_schema -> schema_contract -> cli_contract`
- downstream_consumers:
  - `baseline-diff-lab`
  - `evidence-trace-auditor`
  - `codebase-doc-alignment`

## Notes

- 이 slice는 diff를 계산하지 않는다.
- diff를 위한 stable compare basis를 제공하는 중간 artifact다.
