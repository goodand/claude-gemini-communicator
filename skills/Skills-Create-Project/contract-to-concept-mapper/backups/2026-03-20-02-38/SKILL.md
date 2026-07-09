---
name: contract-to-concept-mapper
description: >-
  Use this skill when execution-space artifacts such as checklists, tasks,
  schemas, CLI contracts, or signatures must be lifted back into concept-space
  summaries, boundary maps, and semantic descriptions. 실행 계약 공간을 개념
  공간으로 다시 올려서 해석한다.
---

# Contract To Concept Mapper

실행 계약 공간을 읽고 개념 공간 설명으로 되올리는 스캐폴드. 지금은 `router -> family -> canonical KB -> checklist/scripts` 흐름으로 읽는 것이 맞다.

## When to use

- checklist나 task 정의가 실제로 어떤 개념을 뜻하는지 역으로 파악할 때
- 구현 체크리스트와 사용자 개념 모델의 차이를 설명할 때
- schema, CLI contract, 함수 시그니처에서 상위 의미를 재구성할 때

## Workflow

1. broad research를 보고 싶으면 `references/indexes/contract-to-concept-family-index-at2026-03-16-18-06.md`를 읽어 family를 고른다
2. 현재 채택 설계를 보려면 `knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md`를 읽는다
3. 정합성 평가는 `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md`와 scripts를 기준으로 한다
4. traceability gap이나 문서 체인 문제는 scripts로 검증한다

## Scripts

- `scripts/verify_artifact_order.py` — KB/정합성 checklist/구현용 checklist의 생성 순서와 우선순위 검증
- `scripts/kb_to_consistency_check.py` — KB canonical unit과 consistency checklist item의 traceability gap 검사
- `scripts/consistency_to_implementation_check.py` — consistency checklist의 핵심 anchor가 implementation checklist에 유지되는지 검사
- `scripts/artifact_link_audit.py` — SKILL/KB/checklist/reference 사이의 로컬 경로 참조 무결성 검사
- `scripts/test_kb_to_consistency_check.py` — `kb_to_consistency_check.py` TDD 테스트 세트

## Knowledge Bases

- `knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md` — 현재 채택 설계의 canonical source of truth
- `knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` — GitHub/논문 URL KB (`research_index_kb`)
- `knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md` — kb_to_consistency_check 설계용 KB
- `knowledge_bases/contract-to-concept-mapper-issues-at2026-03-16.md` — 현재 이슈와 필요성

## References

- `references/indexes/contract-to-concept-family-index-at2026-03-16-18-06.md` — family 선택용 index
- `references/families/lifting-core-family-at2026-03-16-18-06.md` — lifting core family
- `references/families/explainability-traceability-family-at2026-03-16-18-06.md` — explainability / traceability family
- `references/families/output-contract-family-at2026-03-16-18-06.md` — output contract family
- `references/measurement-strategy-from-eval-runner-rag-bench-at2026-03-16-18-47.md` — metric 실행/해석/fixed-point 분리 전략
- `references/contract-to-concept-mapper-github-search-at2026-03-16.md` — GitHub 레퍼런스 shortlist
- `references/contract-to-concept-mapper-paper-search-at2026-03-16.md` — 논문/학술 레퍼런스 shortlist
- `references/troubleshooting.md` — 향후 실험 중 발견된 문제 기록

## Notes

- `contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md`는 canonical KB가 아니라 research index KB다
- 개념 공간 자체의 slice 정리는 semantic-slice-mapper가 맡고, codebase와의 직접 정합성 평가는 execution-contract-mapper나 증거 계열 skill이 더 가깝다
