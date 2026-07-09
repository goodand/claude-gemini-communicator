# evidence-trace-auditor evidence_ledger summary

- generated_at: `2026-03-17T01:52:49+09:00`
- source_report: `doc-code-sync-checker/references/typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json`
- source_report_type: `raw_smoke_report`
- entry_count: `3`

## Entries

- `missing_in_code:status:ready`
  - finding_family: `missing_in_code`
  - name: `status:ready`
  - observed_bucket: `missing_contract_unit`
  - trace_status: `verified_evidence`
  - doc_evidence_count: `1`
  - code_evidence_count: `0`
- `missing_in_doc:status:running`
  - finding_family: `missing_in_doc`
  - name: `status:running`
  - observed_bucket: `extra_contract_unit`
  - trace_status: `verified_evidence`
  - doc_evidence_count: `0`
  - code_evidence_count: `1`
- `typed_mismatch:status`
  - finding_family: `typed_mismatch`
  - name: `status`
  - observed_bucket: `contract_value_changed`
  - trace_status: `verified_evidence`
  - doc_evidence_count: `2`
  - code_evidence_count: `2`
