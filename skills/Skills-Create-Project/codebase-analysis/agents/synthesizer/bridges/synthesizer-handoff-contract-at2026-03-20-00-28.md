# Synthesizer Handoff Contract

## Required Inputs

- `worker_results[]`
  - `agent_name`
  - `scope`
  - `summary_path`
  - `artifact_paths[]`
  - `open_questions[]`
- `fan_in_gap_register`
- `contradiction_register`
- `target_output_path`

## Required Outputs

- `final_synthesis_report.md`
- `deduplicated_finding_map.json`
- `contradiction_resolution_notes.md`
- `residual_gap_register.md`

## Completion Definition

A run is complete when:
- every major worker packet is represented or explicitly excluded
- duplicate findings are collapsed
- contradictions are either resolved or preserved as open issues
- unresolved gaps are listed separately from confirmed findings
