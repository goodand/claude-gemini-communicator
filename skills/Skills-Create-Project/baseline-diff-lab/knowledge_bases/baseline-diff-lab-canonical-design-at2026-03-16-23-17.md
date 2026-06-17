# Baseline Diff Lab Canonical Design

- ver: `v0.1.0`
- generated_at: `2026-03-16-23-17`
- canonical_role: `before/after baseline measurement and diff reporting source of truth`
- source_of_truth_for: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-17.md`

## Canonical Design Takeaways

- baseline diff는 `pre-fix -> debug -> post-fix -> diff` 순서를 따른다.
- pre-fix artifact 없이 improvement claim을 만들지 않는다.
- before와 after는 같은 metric set을 써야 한다.
- JSON artifact와 MD report를 함께 남긴다.
- reduction metric은 수치와 공식이 함께 있어야 한다.
- debug evidence는 diff와 분리된 입력으로 취급한다.
- 다른 skill의 implementation branch 후속 단계로 handoff될 수 있다.
- `kb-checklist-pipeline`은 baseline diff 단계로 이어지는 bridge를 둘 수 있다.
- planner script는 handoff 입력과 suggested output file names를 먼저 고정한다.
- raw smoke report만 있으면 metricize script가 `metrics` dict artifact를 먼저 만든다.
- compute script는 같은 metric set으로 before/after delta를 계산한다.

## Current Implementation Target

- 현재는 문서형 skill scaffold 단계다.
- branch handoff와 artifact contract를 먼저 고정한다.
- planner script와 TDD를 먼저 둔다.
- raw smoke report를 다루는 adapter script와 TDD를 둔다.
- compute script와 TDD를 이어서 둔다.
