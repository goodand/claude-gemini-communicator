---
name: evidence-to-knowledge-promoter
description: >-
  workspace-artifact-production-process family의 evidence-promotion
  specialist. Use this skill when smoke results, audit findings, and baseline
  diffs must be promoted into reusable knowledge-base insights or hybrid/canonical
  KB content. broader artifact production order는
  workspace-artifact-production-process를 사용하라.
---

# Evidence To Knowledge Promoter

증거 공간의 결과를 재사용 가능한 insight KB로 승격하는 규칙을 정리하는 skill.

## When to use

- smoke/audit/diff 결과를 KB insight로 올리고 싶을 때
- 실험 결과를 `research_index_kb`에서 `hybrid_kb`로 승격할지 판단할 때
- 반복된 fix 결과를 lesson learned로 구조화할 때
- `image-text-cot-review` 결과를 reusable rule이나 repeated pattern insight로 승격할 때

## Workflow

1. 입력 evidence 범위를 고른다: smoke, support audit, baseline diff, troubleshooting note, image-text review manifest.
2. 조사 자산은 먼저 `(→ knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md)`에서 확인한다.
3. insight 후보를 `finding`, `delta`, `lesson`, `promotion trigger`로 나눠 본다.
4. KB profile 승격은 `research_index_kb -> (hybrid_kb | canonical_design_kb)` 규칙을 따른다.
5. source of truth는 같은 KB의 `Canonical Design Takeaways`로 고정하고, 다음 단계로 consistency checklist를 만든다.
6. 구현은 `(→ references/vertical-slice-promotion-summary-at2026-03-17-03-08.md)` → `(→ references/vertical-slice-promotion-trigger-evaluator-at2026-03-17-03-14.md)` → `(→ references/vertical-slice-hybrid-kb-patch-plan-at2026-03-17-03-20.md)` → `(→ references/vertical-slice-canonical-candidate-evaluator-at2026-03-17-03-36.md)` → `(→ references/vertical-slice-canonical-kb-patch-plan-at2026-03-17-09-03.md)` 순서로 따른다.
7. 구현 전에는 `references/troubleshooting.md`의 실패 패턴을 먼저 확인한다.
8. scripts, reference map, current status는 `(→ references/skill-entrypoint-details-at2026-03-20-09-33.md)`에서 확인한다.
