# Vertical Slice: Execution Handoff Validator

- generated_at: `2026-03-18-22-52`
- target skill: `skill-creation-process`
- slice kind: `execution_handoff_schema_validator`

## Purpose

`execution_evidence_planner.py`가 만든 planner payload가
downstream handoff contract와 실제로 맞는지 기계 검증한다.

## Scope

- 입력:
  - planner payload JSON
  - workspace root
- 검증 대상:
  - top-level required field
  - `inputs.*` required field
  - stage별 required artifact 존재
  - `evidence-trace-auditor` handoff 규칙
  - `baseline-diff-lab` handoff 규칙
  - ready-for-diff 시 `adapter` 필요 여부

## Stage Rules

### `pre_execution`

- `smoke_artifacts`는 비어 있어야 한다
- `pre_fix` / `post_fix`는 없어야 한다
- `evidence-trace-auditor` handoff는 `after smoke`여야 한다

### `post_smoke`

- `smoke_artifacts`가 1개 이상 있어야 한다
- smoke 파일이 실제로 존재해야 한다
- `evidence_ledger_*`, `support_audit_*` suggested output key가 있어야 한다
- `evidence-trace-auditor` handoff는 `now`여야 한다

### `ready_for_diff`

- `pre_fix`, `post_fix` 파일이 실제로 존재해야 한다
- `baseline-diff-lab` handoff는 `now`여야 한다
- `diff_json`, `diff_md` suggested output key가 있어야 한다
- pre/post artifact에 `metrics` dict가 없으면 `adapter`가 있어야 한다

## Output Shape

validator는 아래를 JSON/Markdown으로 출력한다.

- `status`
- `skill`
- `stage`
- `error_count`
- `warning_count`
- `errors[]`
- `warnings[]`
- `validated_handoffs[]`

## Non-Goal

- evidence 자체의 참/거짓 판정은 하지 않는다
- metric semantics를 새로 정의하지 않는다
- KB 승격 판단을 대신하지 않는다
