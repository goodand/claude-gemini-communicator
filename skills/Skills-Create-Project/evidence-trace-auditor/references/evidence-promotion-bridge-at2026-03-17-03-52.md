# Evidence Promotion Bridge

## When To Handoff

다음 조건이면 `evidence-trace-auditor`에서 직접 해석을 끝내지 말고 `evidence-to-knowledge-promoter`로 넘긴다.

- `support_audit` 결과를 reusable insight로 올리고 싶을 때
- `verified_evidence`와 `missing_evidence`를 lesson/finding 규칙으로 승격하고 싶을 때
- `baseline diff`와 함께 KB 승격 판단까지 이어져야 할 때

## Required Inputs

- `evidence_ledger` 또는 `support_audit`
- 가능하면 같은 실험의 `baseline diff`
- upstream planner를 썼다면 `references/execution-evidence-handoff-at2026-03-17-08-54.md`의 payload mapping을 먼저 따른다
- `evidence-to-knowledge-promoter` 입력 구조는 `../../evidence-to-knowledge-promoter/references/evidence-promotion-handoff-at2026-03-17-08-57.md`를 따른다

## Handoff Order

1. `support_audit`를 확정한다
2. 필요하면 같은 실험의 `baseline diff`를 준비한다
3. [evidence-to-knowledge-promoter](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/SKILL.md)로 넘긴다
4. `references/evidence-promotion-handoff-at2026-03-17-08-57.md`의 field mapping으로 `build-promotion-summary` 입력을 고정한다
5. `build-promotion-summary -> evaluate-promotion-trigger -> build-hybrid-kb-patch-plan -> apply-hybrid-kb-patch` 순서를 따른다

## Non-Goal

- 이 bridge는 evidence 수집 규칙을 바꾸지 않는다
- `evidence-trace-auditor` 안에서 KB patch를 직접 수행하지 않는다
