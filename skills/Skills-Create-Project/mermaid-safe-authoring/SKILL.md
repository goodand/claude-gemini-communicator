---
name: mermaid-safe-authoring
description: >-
  Use this skill when producing Mermaid diagrams that must render
  successfully on Mermaid 11.13.0. Adjacency-list-first, minimal syntax
  first, incremental enrichment. 파서 안전한 Mermaid 작성 워크플로우.
---

# Mermaid Safe Authoring

Mermaid 다이어그램을 파서 에러 없이 생산하기 위한 점진적 작성 절차.

## When to use

- Mermaid `graph TD`/`flowchart` 다이어그램을 처음 작성할 때
- `Syntax error in text` 렌더 실패를 디버깅할 때
- 복잡한 관계를 Mermaid로 옮기려 할 때

## Workflow

1. **인접리스트 작성** — 노드와 엣지를 plain text로 먼저 정리 (→ `references/authoring-workflow.md` Step 1)
2. **최소 graph TD** — `-->` 만 사용, 라벨·스타일 없이 렌더 확인 (→ `references/parser-safe-subset.md`)
3. **엣지 라벨 추가** — 카테고리별로 한 종류씩 추가 (→ `references/relation-modeling.md`)
4. **subgraph 추가** — `contains` 관계를 subgraph membership으로 변환
5. **스타일 추가** — `classDef`, `linkStyle`은 구조가 안정된 후에만 (→ `references/parser-safe-subset.md` Style)

## Scripts

- document-first skill이다. 현재 `scripts/`는 의도적으로 두지 않는다.

## References

- `references/authoring-workflow.md`
- `references/parser-safe-subset.md`
- `references/relation-modeling.md`
- `references/troubleshooting.md`

## Notes

- 렌더 실패는 스타일 문제가 아니라 구문 문제로 먼저 의심한다 (→ `references/troubleshooting.md`)
- `scripts/` 자동화보다 parser-safe writing rule을 먼저 재사용한다
- `contains`는 edge가 아니라 subgraph membership으로 표현한다
- 긴 라벨, 슬래시, 특수문자는 최소 그래프가 렌더된 후에 추가한다
