---
name: cross-repo-product-review
description: >-
  Use this skill when an external or downstream product repo needs milestone
  quality review, bounded Codex handoff, and convergence tracking before
  integration or skill promotion.
---

# Cross-Repo Product Review

외부 repo 제품 리뷰, bounded handoff, convergence closure를 묶는 workflow skill.

## Use This Skill When

- downstream repo가 integration 전에 product-quality review가 필요할 때
- expert review 결과를 bounded Codex handoff로 넘기고 다시 closure 검증해야 할 때
- repeated task/issue를 checklist와 KB로 승격해야 할 때

## Do Not Use This Skill When

- 단일 버그 수정만 필요하고 product review 전체가 필요 없을 때
- target repo 자체 구현/merge가 목적일 때

## Read Order

1. `references/runtime.md`
2. `knowledge_bases/cross-repo-product-review-knowledge_base-at2026-04-08-00-12.md`
3. `checklist-forconsistency-evaluation/review-convergence-consistency-checklist-at2026-04-08-00-13.md`
4. `checklist-forimplementation/review-convergence-implementation-checklist-at2026-04-08-00-14.md`
5. `references/codex-handoff-prompt-template.md`
6. `references/troubleshooting.md`

## Scripts

- `scripts/review_file_classifier.py` — review scope를 canonical role bucket으로 분류

## Outputs

- role-based file classification
- severity-ranked findings + bounded handoff
- convergence verdict + promoted pattern evidence

## Notes

- sibling-field 누락, async/API surface 변경은 `references/review-convergence-guardrails.md` 기준으로 재검토한다.
- 잔여 1-2건이면 direct expert closure가 기본이다.
