---
name: evidence-to-knowledge-promoter
description: >-
  Use this skill when promoting smoke results, audit findings, and baseline
  diffs into reusable knowledge-base insights or deciding how evidence should
  become hybrid/canonical KB content. 실험 결과와 audit 산출물을 reusable
  insight KB로 승격할 때 사용한다.
---

# Evidence To Knowledge Promoter

증거 공간의 결과를 재사용 가능한 insight KB로 승격하는 규칙을 정리하는 skill.

## When to use

- smoke/audit/diff 결과를 KB insight로 올리고 싶을 때
- 실험 결과를 `research_index_kb`에서 `hybrid_kb`로 승격할지 판단할 때
- 반복된 fix 결과를 lesson learned로 구조화할 때

## Workflow

1. 입력 evidence 범위를 고른다: smoke, support audit, baseline diff, troubleshooting note.
2. 조사 자산은 먼저 `(→ knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md)`에서 확인한다.
3. insight 후보를 `finding`, `delta`, `lesson`, `promotion trigger`로 나눠 본다.
4. KB profile 승격은 `research_index_kb -> (hybrid_kb | canonical_design_kb)` 규칙을 따른다.
5. source of truth는 같은 KB의 `Canonical Design Takeaways`로 고정하고, 다음 단계로 consistency checklist를 만든다.
6. 구현은 `(→ references/vertical-slice-promotion-summary-at2026-03-17-03-08.md)` → `(→ references/vertical-slice-promotion-trigger-evaluator-at2026-03-17-03-14.md)` → `(→ references/vertical-slice-hybrid-kb-patch-plan-at2026-03-17-03-20.md)` → `(→ references/vertical-slice-canonical-candidate-evaluator-at2026-03-17-03-36.md)` → `(→ references/vertical-slice-canonical-kb-patch-plan-at2026-03-17-09-03.md)` 순서로 따른다.
7. 구현 전에는 `references/troubleshooting.md`의 실패 패턴을 먼저 확인한다.

## Scripts

- `scripts/evidence_to_knowledge_promoter.py` — `build-promotion-summary`
- `scripts/evidence_to_knowledge_promoter.py` — `evaluate-promotion-trigger`
- `scripts/evidence_to_knowledge_promoter.py` — `build-hybrid-kb-patch-plan`
- `scripts/evidence_to_knowledge_promoter.py` — `evaluate-canonical-candidate`
- `scripts/evidence_to_knowledge_promoter.py` — `build-canonical-kb-patch-plan`
- `scripts/test_evidence_to_knowledge_promoter.py` — 첫 slice TDD

## References

- `knowledge_bases/evidence-to-knowledge-promoter-knowledge_base-at2026-03-17-02-48.md` — hybrid_kb + canonical takeaways
- `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-17-03-00.md` — 승격 규칙 정합성 판단 기준
- `checklist-forimplementation/implementation-checklist-at2026-03-17-03-00.md` — 첫 구현 slice 작업 단위
- `references/evidence-promotion-handoff-at2026-03-17-08-57.md` — `support_audit + baseline_diff -> promotion summary` 입력 스키마
- `references/vertical-slice-promotion-summary-at2026-03-17-03-08.md` — 첫 promotion summary slice 정의
- `references/vertical-slice-promotion-trigger-evaluator-at2026-03-17-03-14.md` — 승격 판정 slice 정의
- `references/vertical-slice-hybrid-kb-patch-plan-at2026-03-17-03-20.md` — hybrid KB patch plan slice 정의
- `references/vertical-slice-canonical-candidate-evaluator-at2026-03-17-03-36.md` — canonical KB 후보 판정 slice 정의
- `references/vertical-slice-canonical-kb-patch-plan-at2026-03-17-09-03.md` — canonical KB patch plan slice 정의
- `references/troubleshooting.md` — 승격 실패/과승격 방지 메모

## Notes

- 이 skill의 현재 단계는 `hybrid_kb`다.
- upstream handoff는 `references/evidence-promotion-handoff-at2026-03-17-08-57.md`의 payload mapping을 따른다.
- 현재는 `build-canonical-kb-patch-plan`까지 구현됐고, 실제 KB apply/mutation은 이 skill의 범위에서 제거했다.
