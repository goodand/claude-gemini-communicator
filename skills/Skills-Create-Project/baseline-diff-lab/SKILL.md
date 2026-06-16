---
name: baseline-diff-lab
description: >-
  measurement-evaluation-orchestrator family의 baseline comparison
  specialist. Use this skill when before/after baseline measurement, debug
  evidence, and fix-diff reporting must be standardized after a smoke test or
  experiment. multi-concern measurement orchestration은
  measurement-evaluation-orchestrator를 사용하라.
---

# Baseline Diff Lab

`pre-fix baseline -> debug evidence -> post-fix baseline -> before/after diff`를 고정한다.

## Read Order

1. `references/indexes/baseline-diff-index-at2026-03-16-23-17.md`
2. `references/families/fix-diff-family-at2026-03-16-23-17.md`
3. `knowledge_bases/baseline-diff-lab-canonical-design-at2026-03-16-23-17.md`
4. `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-17.md`
5. `checklist-forimplementation/implementation-checklist-at2026-03-16-23-17.md`
6. 필요하면 `scripts/baseline_diff_planner.py --help`
7. upstream이 raw smoke report만 만들면 `scripts/metricize_smoke_report.py --help`
8. 실제 계산이 필요하면 `scripts/baseline_diff_compute.py --help`

## Use When

- smoke/evidence 뒤에 debug와 before/after diff가 필요할 때
- pre-fix와 post-fix baseline을 같은 metric으로 비교해야 할 때
- reduction metric이나 improvement report를 남겨야 할 때
- 다른 skill의 implementation branch 후속 단계로 handoff할 때

## Notes

- source of truth는 canonical KB다
- pre-fix artifact 없이 post-fix만 남기지 않는다
- fix effect는 숫자와 report 둘 다 남긴다
- kb-checklist-pipeline의 implementation branch 다음 단계로 이어질 수 있다
- `execution_evidence_planner.py` payload를 받을 때는 `references/execution-evidence-handoff-at2026-03-17-08-54.md`의 mapping을 따른다
- `scripts/baseline_diff_planner.py`는 handoff 입력과 출력 artifact 이름을 먼저 고정한다
- upstream artifact에 `metrics` dict가 없으면 `scripts/metricize_smoke_report.py`로 먼저 metric artifact로 바꾼다
- `scripts/baseline_diff_compute.py`는 planner output 또는 direct args를 받아 diff JSON/MD를 만든다
- diff 결과를 KB insight로 승격할 때는 `references/evidence-promotion-bridge-at2026-03-17-03-52.md`를 따라 `evidence-to-knowledge-promoter`로 넘긴다
