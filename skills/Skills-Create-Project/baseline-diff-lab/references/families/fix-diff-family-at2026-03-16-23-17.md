# Baseline Diff Lab Family: fix-diff

## Core Flow

1. pre-fix baseline 생성
2. debug evidence 저장
3. fix 적용
4. post-fix baseline 생성
5. before/after diff report 작성
6. reduction metric 기록

## Required Artifacts

- pre-fix JSON
- post-fix JSON
- before/after diff JSON
- before/after diff MD

## Adapter Rule

- upstream artifact가 raw smoke report면 `metricize_smoke_report.py`로 `metrics` dict artifact를 먼저 만든다
- planner와 compute는 `metrics` dict를 source input으로 본다

## Output Contract

- before와 after는 같은 metric set을 써야 한다
- delta는 숫자로 남겨야 한다
- report는 사람용 해석을 포함해야 한다
