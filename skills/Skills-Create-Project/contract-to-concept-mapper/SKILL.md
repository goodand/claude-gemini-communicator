---
name: contract-to-concept-mapper
description: >-
  design-planning-orchestrator family의 reverse-lift specialist. Use this
  skill when execution-space artifacts such as checklists, tasks, schemas, CLI
  contracts, or signatures must be lifted back into concept-space summaries,
  boundary maps, and semantic descriptions. broader multi-concern planning은
  design-planning-orchestrator를 사용하라.
---

# Contract To Concept Mapper

실행 계약 공간을 읽고 개념 공간 설명으로 되올리는 스캐폴드. 지금은 `family -> canonical KB -> checklist` 흐름으로 읽는 것이 맞다.

## When to use

- checklist나 task 정의가 실제로 어떤 개념을 뜻하는지 역으로 파악할 때
- 구현 체크리스트와 사용자 개념 모델의 차이를 설명할 때
- schema, CLI contract, 함수 시그니처에서 상위 의미를 재구성할 때

## Workflow

1. broad research를 보고 싶으면 `references/indexes/contract-to-concept-family-index-at2026-03-16-18-06.md`를 읽어 family를 고른다
2. 현재 채택 설계를 보려면 `knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md`를 읽는다
3. 정합성 평가는 `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md`를 기준으로 한다
4. mapping이 잘 안 되면 artifact 순서보다 `contract unit`, `concept unit`, `boundary`, `relation` 정의가 충분한지 먼저 점검한다

## Knowledge Bases

- `knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md` — 현재 채택 설계의 canonical source of truth
- `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` — GitHub/논문 URL KB (`research_index_kb`)
- `knowledge_bases/contract-to-concept-mapper-issues-at2026-03-16.md` — 현재 이슈와 필요성

## References

- `references/indexes/contract-to-concept-family-index-at2026-03-16-18-06.md` — family 선택용 index
- `references/families/lifting-core-family-at2026-03-16-18-06.md` — lifting core family
- `references/families/explainability-traceability-family-at2026-03-16-18-06.md` — explainability / traceability family
- `references/families/output-contract-family-at2026-03-16-18-06.md` — output contract family
- `references/contract-to-concept-mapper-github-search-at2026-03-16.md` — GitHub 레퍼런스 shortlist
- `references/contract-to-concept-mapper-paper-search-at2026-03-16.md` — 논문/학술 레퍼런스 shortlist
- `references/troubleshooting.md` — 향후 실험 중 발견된 문제 기록

## Notes

- `contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md`는 canonical KB가 아니라 research index KB다
- artifact order / coverage / chain audit 계열은 제거했고, 이 skill은 다시 concept lifting 자체에만 집중한다
- 개념 공간 자체의 slice 정리는 semantic-slice-mapper가 맡고, codebase와의 직접 정합성 평가는 execution-contract-mapper나 증거 계열 skill이 더 가깝다
