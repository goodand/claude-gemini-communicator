# evidence-trace-auditor support audit summary

- generated_at: `2026-03-18T23:12:27+09:00`
- input_evidence_ledger: `evidence-trace-auditor/references/attestation-evidence-ledger-smoke-at2026-03-18-23-02.json`
- input_contract_diff_basis: `execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json`
- entry_count: `3`
- supported_count: `1`
- missing_evidence_count: `1`
- residual_uncertainty_count: `1`
- support_ratio: `0.3333333333333333`

## Recommended Diff Buckets

- `missing_contract_unit`
- `extra_contract_unit`
- `contract_value_changed`
- `requiredness_changed`
- `cli_argument_surface_changed`

## Supported Entries

- `attestation:verified-attested-step` -> `contract_value_changed`

## Missing Evidence Entries

- `attestation:missing-output-step`

## Residual Uncertainty Entries

- `attestation:residual-attested-step` -> `contract_value_changed`
