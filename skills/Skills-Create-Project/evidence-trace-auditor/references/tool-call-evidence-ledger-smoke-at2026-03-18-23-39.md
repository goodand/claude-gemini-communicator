# evidence-trace-auditor evidence_ledger summary

- generated_at: `2026-03-18T23:42:43+09:00`
- source_report: `evidence-trace-auditor/references/tool-call-manifest-sample-at2026-03-18-23-39.json`
- source_report_type: `tool_call_manifest`
- entry_count: `3`

## Entries

- `tool_call:validated-rule-schema`
  - finding_family: `tool_call`
  - name: `validated-rule-schema`
  - observed_bucket: `contract_value_changed`
  - trace_status: `verified_evidence`
  - doc_evidence_count: `0`
  - code_evidence_count: `1`
- `tool_call:missing-output-call`
  - finding_family: `tool_call`
  - name: `missing-output-call`
  - observed_bucket: `missing_contract_unit`
  - trace_status: `missing_evidence`
  - doc_evidence_count: `0`
  - code_evidence_count: `1`
- `tool_call:failing-call`
  - finding_family: `tool_call`
  - name: `failing-call`
  - observed_bucket: `contract_value_changed`
  - trace_status: `residual_uncertainty`
  - doc_evidence_count: `0`
  - code_evidence_count: `1`
