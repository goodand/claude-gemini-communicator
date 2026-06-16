# evidence-trace-auditor support audit summary

- generated_at: `2026-03-17T02:31:29+09:00`
- input_evidence_ledger: `evidence-trace-auditor/references/artifact-path-evidence-ledger-smoke-at2026-03-17-02-20.json`
- input_contract_diff_basis: `execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json`
- entry_count: `3`
- supported_count: `2`
- missing_evidence_count: `1`
- residual_uncertainty_count: `0`
- support_ratio: `0.6666666666666666`

## Recommended Diff Buckets

- `missing_contract_unit`
- `extra_contract_unit`
- `contract_value_changed`
- `requiredness_changed`
- `cli_argument_surface_changed`

## Supported Entries

- `artifact_path:contract-diff-basis-json` -> `contract_value_changed`
- `artifact_path:log-support-audit-md` -> `extra_contract_unit`

## Missing Evidence Entries

- `artifact_path:missing-smoke-artifact`

## Residual Uncertainty Entries

