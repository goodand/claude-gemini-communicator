# execution-contract-mapper contract_diff_basis summary

- generated_at: `2026-03-17T01:41:48+09:00`
- rule_schema: `execution-contract-mapper/references/rule-schema-smoke-at2026-03-17-01-06.json`
- schema_contract: `execution-contract-mapper/references/schema-contract-smoke-at2026-03-17-01-11.json`
- cli_contract: `execution-contract-mapper/references/cli-contract-smoke-at2026-03-17-01-29.json`
- basis_count: `3`

## Recommended Diff Buckets

- `missing_contract_unit`
- `extra_contract_unit`
- `contract_value_changed`
- `requiredness_changed`
- `cli_argument_surface_changed`

## Diff Bases

- `rule_schema`
  - unit_name: `rule`
  - unit_count: `15`
  - identity_keys: `['name']`
  - compare_fields: `['kind', 'value.expectation', 'value.section', 'value.checklist_role']`
  - candidate_buckets: `['missing_contract_unit', 'extra_contract_unit', 'contract_value_changed']`
- `schema_contract`
  - unit_name: `schema_property`
  - unit_count: `9`
  - identity_keys: `['property_name']`
  - compare_fields: `['type', 'const', 'format', 'minLength', 'minimum', 'required_membership']`
  - candidate_buckets: `['missing_contract_unit', 'extra_contract_unit', 'requiredness_changed', 'contract_value_changed']`
- `cli_contract`
  - unit_name: `cli_subcommand_or_argument`
  - unit_count: `3`
  - identity_keys: `['subcommand.name', 'argument.dest']`
  - compare_fields: `['usage', 'required', 'option_strings', 'choices', 'nargs', 'help']`
  - candidate_buckets: `['missing_contract_unit', 'extra_contract_unit', 'cli_argument_surface_changed', 'contract_value_changed']`
