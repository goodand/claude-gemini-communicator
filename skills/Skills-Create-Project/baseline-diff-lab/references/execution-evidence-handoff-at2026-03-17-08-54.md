# Execution Evidence Handoff For Baseline Diff Lab

## Purpose

`execution_evidence_planner.py`가 만든 handoff payload를 `baseline-diff-lab` 입력으로 어떻게 읽을지 고정한다.

## Expected Planner Fields

- `stage`
  - `ready_for_diff`일 때 `baseline-diff-lab`을 바로 호출할 수 있다
- `inputs.pre_fix`
- `inputs.post_fix`
- `inputs.metrics`
- `suggested_outputs.diff_json`
- `suggested_outputs.diff_md`
- `handoffs[*].adapter`
  - 있으면 raw smoke artifact를 먼저 metric artifact로 정규화해야 한다

## Consumption Rule

1. planner payload의 `stage`가 `ready_for_diff`인지 먼저 확인한다
2. `handoffs`에 `adapter`가 있으면 `metricize_smoke_report.py`를 먼저 실행한다
3. 그 다음 `baseline_diff_planner.py` 또는 `baseline_diff_compute.py`에 pre/post artifact를 넘긴다
4. diff 결과 파일명은 planner의 `suggested_outputs.diff_json`, `suggested_outputs.diff_md` 패턴을 따른다

## Minimal Mapping

- planner `inputs.pre_fix`
  -> `baseline_diff_planner.py --pre`
- planner `inputs.post_fix`
  -> `baseline_diff_planner.py --post`
- planner `inputs.metrics[*]`
  -> `baseline_diff_planner.py --metric`
- planner `suggested_outputs.diff_json`
  -> diff JSON output path
- planner `suggested_outputs.diff_md`
  -> diff Markdown output path

## Non-Goal

- planner payload가 metric set을 새로 정의하지는 않는다
- `baseline-diff-lab`이 evidence audit 없이 lesson 승격까지 직접 수행하지는 않는다
