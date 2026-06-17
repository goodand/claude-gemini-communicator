# evidence-trace-auditor support audit summary

- generated_at: `2026-03-17T01:58:12+09:00`
- input_evidence_ledger: `evidence-trace-auditor/references/test-result-evidence-ledger-smoke-at2026-03-17-02-06.json`
- input_contract_diff_basis: `execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json`
- entry_count: `2`
- supported_count: `1`
- missing_evidence_count: `0`
- residual_uncertainty_count: `1`
- support_ratio: `0.5`

## Recommended Diff Buckets

- `missing_contract_unit`
- `extra_contract_unit`
- `contract_value_changed`
- `requiredness_changed`
- `cli_argument_surface_changed`

## Supported Entries

- `test_result:sync::test_failed` -> `contract_value_changed`

## Missing Evidence Entries


## Residual Uncertainty Entries

- `test_result:sync::test_skipped` -> `None`
