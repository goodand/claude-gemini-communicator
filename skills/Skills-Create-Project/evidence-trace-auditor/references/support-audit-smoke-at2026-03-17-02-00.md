# evidence-trace-auditor support audit summary

- generated_at: `2026-03-17T01:53:11+09:00`
- input_evidence_ledger: `evidence-trace-auditor/references/evidence-ledger-smoke-at2026-03-17-02-00.json`
- input_contract_diff_basis: `execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json`
- entry_count: `3`
- supported_count: `3`
- missing_evidence_count: `0`
- residual_uncertainty_count: `0`
- support_ratio: `1.0`

## Recommended Diff Buckets

- `missing_contract_unit`
- `extra_contract_unit`
- `contract_value_changed`
- `requiredness_changed`
- `cli_argument_surface_changed`

## Supported Entries

- `missing_in_code:status:ready` -> `missing_contract_unit`
- `missing_in_doc:status:running` -> `extra_contract_unit`
- `typed_mismatch:status` -> `contract_value_changed`

## Missing Evidence Entries


## Residual Uncertainty Entries

