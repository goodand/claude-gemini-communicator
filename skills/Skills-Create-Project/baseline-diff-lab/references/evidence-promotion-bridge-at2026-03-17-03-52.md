# Evidence Promotion Bridge

## When To Handoff

다음 조건이면 `baseline-diff-lab`의 diff report에서 끝내지 말고 `evidence-to-knowledge-promoter`로 넘긴다.

- before/after delta를 KB insight로 승격하고 싶을 때
- `delta`를 `lesson_candidate`나 `adoption rule` 후보로 올리고 싶을 때
- diff 결과를 `hybrid_kb` 또는 `canonical_design_kb` 규칙으로 연결해야 할 때

## Required Inputs

- `pre/post diff` JSON
- 같은 실험의 `support_audit` 또는 `evidence_ledger`
- upstream planner를 썼다면 `references/execution-evidence-handoff-at2026-03-17-08-54.md`의 payload mapping을 먼저 따른다
- `evidence-to-knowledge-promoter` 입력 구조는 `../../evidence-to-knowledge-promoter/references/evidence-promotion-handoff-at2026-03-17-08-57.md`를 따른다

## Handoff Order

1. `metricize -> planner -> compute`를 끝낸다
2. 실제 delta가 있는지 확인한다
3. [evidence-to-knowledge-promoter](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/SKILL.md)로 넘긴다
4. `references/evidence-promotion-handoff-at2026-03-17-08-57.md`의 field mapping으로 `build-promotion-summary` 입력을 고정한다
5. `promotion summary -> trigger evaluation -> KB patch plan` 순서를 따른다

## Non-Goal

- 이 bridge는 diff 계산 자체를 바꾸지 않는다
- `baseline-diff-lab` 안에서 KB 승격 문서를 직접 수정하지 않는다
