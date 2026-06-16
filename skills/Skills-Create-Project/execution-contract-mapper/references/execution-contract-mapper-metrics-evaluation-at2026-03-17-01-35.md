# execution-contract-mapper metrics evaluation

- generated_at: `2026-03-17T01:35:00+09:00`
- source_of_truth: [execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/knowledge_bases/execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md)
- input_checklist: [consistency-checklist-at2026-03-17-01-00.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-01-00.md)
- smoke_artifacts:
  - [rule-schema-smoke-at2026-03-17-01-06.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/rule-schema-smoke-at2026-03-17-01-06.json)
  - [schema-contract-smoke-at2026-03-17-01-11.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/schema-contract-smoke-at2026-03-17-01-11.json)
  - [cli-contract-smoke-at2026-03-17-01-29.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/cli-contract-smoke-at2026-03-17-01-29.json)

## Metrics

- `implemented_slice_ratio = 0.75`
  - formula: `implemented_slices / planned_slices`
  - value: `3 / 4`
  - interpretation: `rule_schema`, `schema_contract`, `cli_contract` are implemented; `contract_diff_basis` remains.

- `checklist_to_rule_schema_coverage = 1.0`
  - formula: `rule_schema.rule_count / checklist_checkbox_count`
  - value: `15 / 15`
  - interpretation: every checklist checkbox item was emitted into a `rule_schema` object.

- `schema_contract_required_field_count = 8`
  - formula: `len(schema.required)`
  - interpretation: the emitted top-level schema requires 8 fields.

- `schema_contract_required_field_ratio = 0.8889`
  - formula: `len(schema.required) / field_count`
  - value: `8 / 9`
  - interpretation: `source_kb` is optional; the rest of the top-level fields are required.

- `cli_subcommand_coverage = 1.0`
  - formula: `captured_subcommands / implemented_slices`
  - value: `3 / 3`
  - interpretation: the CLI contract captures all implemented subcommands.

- `artifact_pair_completeness_ratio = 1.0`
  - formula: `implemented_slices_with_json_and_md / implemented_slices`
  - value: `3 / 3`
  - interpretation: each implemented slice has both JSON and Markdown smoke evidence.

- `verification_pass_rate = 1.0`
  - formula: `passed_verifications / executed_verifications`
  - value: `3 / 3`
  - checks: `unit_tests`, `py_compile`, `quick_validate`
  - interpretation: runtime and structural verification currently pass.

## Interpretation

- 좋은 점: `rule_schema`, `schema_contract`, `cli_contract`의 core v0.1 chain은 닫혀 있습니다.
- 좋은 점: checklist coverage, CLI coverage, artifact completeness, verification pass rate가 모두 `1.0`입니다.
- 남은 gap: `contract_diff_basis`가 아직 구현되지 않아 `implemented_slice_ratio`는 `0.75`입니다.
- 현재 판단: `execution-contract-mapper`는 `healthy_v0_1` 상태이며, 다음 구현 우선순위는 `contract_diff_basis`입니다.
