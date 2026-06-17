# Execution Evidence Handoff For Evidence Trace Auditor

## Purpose

`execution_evidence_planner.py`가 만든 handoff payload를 `evidence-trace-auditor` 입력으로 어떻게 읽을지 고정한다.

## Expected Planner Fields

- `stage`
  - `post_smoke` 또는 `ready_for_diff`일 때 `evidence-trace-auditor`를 바로 호출할 수 있다
- `inputs.contract_diff_basis`
  - `audit-support`의 `--contract-diff-basis`로 넘긴다
- `inputs.smoke_artifacts`
  - raw smoke report JSON이면 `build-evidence-ledger`의 `--input-report` 후보로 본다
- `suggested_outputs.evidence_ledger_json`
- `suggested_outputs.evidence_ledger_md`
- `suggested_outputs.support_audit_json`
- `suggested_outputs.support_audit_md`

## Consumption Rule

1. planner payload의 `stage`가 `pre_execution`이면 아직 실행하지 않는다
2. `inputs.smoke_artifacts[0]`를 raw smoke report로 사용한다
3. `build-evidence-ledger`를 먼저 실행한다
4. 그 결과와 `inputs.contract_diff_basis`를 `audit-support`에 넘긴다
5. 결과는 planner가 제안한 `suggested_outputs` 경로 이름 체계를 따른다

## Minimal Mapping

- planner `inputs.smoke_artifacts[0]`
  -> `build-evidence-ledger --input-report`
- planner `inputs.contract_diff_basis`
  -> `audit-support --contract-diff-basis`
- planner `suggested_outputs.evidence_ledger_json`
  -> evidence ledger JSON output path
- planner `suggested_outputs.support_audit_json`
  -> support audit JSON output path

## Non-Goal

- planner가 `evidence-trace-auditor` 내부 evidence 판정 규칙을 바꾸지는 않는다
- planner payload만으로 KB 승격 판단을 하지는 않는다
