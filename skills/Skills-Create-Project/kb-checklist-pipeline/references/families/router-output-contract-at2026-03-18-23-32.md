# KB Checklist Pipeline Router Output Contract

- source script: [../../scripts/pipeline_router.py](../../scripts/pipeline_router.py)
- entrypoint: [../../SKILL.md](../../SKILL.md)

## Output Shape

- `target`
- `artifact_kind`
- `branch`
- `tdd_required`
- `read_order`
- `next_actions`
- `execution_evidence_handoff`
- `baseline_diff_handoff`

## execution_evidence_handoff

- `target_skill`: `evidence-trace-auditor`
- `pattern_doc`: `../skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md`
- `planner_script`: `../skill-creation-process/scripts/execution_evidence_planner.py`
- `sequence`
  - preserve raw smoke artifact
  - build evidence ledger
  - audit support against contract_diff_basis
  - record troubleshooting and residual uncertainty

## baseline_diff_handoff

- `target_skill`: `baseline-diff-lab`
- `bridge_doc`: `references/families/baseline-diff-bridge-at2026-03-16-23-17.md`
- `requires_metricize_when`: upstream artifact is raw smoke report without metrics dict
- `metricize_script`: `../baseline-diff-lab/scripts/metricize_smoke_report.py`
- `sequence`
  - metricize raw smoke report if needed
  - plan baseline diff artifacts
  - compute before/after diff

## Branch Guarantees

- `document_output`
  - `execution_evidence_handoff = null`
  - `baseline_diff_handoff = null`
- `script_output`
  - both handoffs present
  - `tdd_required = true`
- `implementation_output`
  - both handoffs present
  - `tdd_required = true`
