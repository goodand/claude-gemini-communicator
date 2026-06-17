# Bridge: kb-checklist-pipeline -> baseline-diff-lab

## Use This Bridge When

- implementation branch에서 `smoke/evidence`까지 끝냈다
- 이제 debug와 before/after diff를 별도 skill로 넘기고 싶다

## Handoff Condition

- TDD와 구현이 끝났다
- smoke artifact가 있다
- debug 메모를 남길 수 있다

## Handoff Payload

- target skill: `baseline-diff-lab`
- 필요한 입력:
  - pre-fix baseline artifact
  - debug evidence
  - post-fix baseline artifact
  - metric set 이름

## Adapter Rule

- upstream artifact에 `metrics` dict가 있으면 planner로 바로 넘긴다
- upstream artifact가 raw smoke report면 `baseline-diff-lab/scripts/metricize_smoke_report.py`로 먼저 metric artifact를 만든다
- baseline-diff-lab은 `metricized artifact -> planner -> compute` 순서로 받는다

## Next Read

1. [baseline-diff-lab/SKILL.md](../../../baseline-diff-lab/SKILL.md)
2. [baseline-diff-index-at2026-03-16-23-17.md](../../../baseline-diff-lab/references/indexes/baseline-diff-index-at2026-03-16-23-17.md)
3. [baseline-diff-lab-canonical-design-at2026-03-16-23-17.md](../../../baseline-diff-lab/knowledge_bases/baseline-diff-lab-canonical-design-at2026-03-16-23-17.md)
