---
name: mermaid-authoring-strategy
description: >-
  Use this skill when an agent needs to author, debug, or convert Mermaid
  diagrams with Claude-level judgment. Codex가 Claude처럼 Mermaid를
  단계적으로 작성·디버깅·도구 선택하는 전략 skill.
---

# Mermaid Authoring Strategy

Claude가 Mermaid를 잘 쓰는 습관을 Codex에 이식하기 위한 전략 skill.
parser-safe authoring은 핵심 guardrail이지만 이 skill의 전부가 아니다.

## When to use

- Mermaid 다이어그램을 처음 설계하거나 작성할 때
- `Syntax error in text` 등 렌더 실패를 디버깅할 때
- DOT/Graphviz 자산을 Mermaid로 변환하거나 도구 선택을 판단할 때
- 복잡한 관계(contains, feeds, constrains 등)를 Mermaid로 모델링할 때

## 4축 전략

1. **Authoring** — 인접리스트 먼저, 최소 `graph TD` 먼저, 점진 확장 (→ `references/authoring-workflow.md`)
2. **Debugging** — 렌더 실패 = 구문 먼저, 스타일 나중, 축소·격리 (→ `references/troubleshooting.md`)
3. **Relation Modeling** — contains=subgraph, feeds/constrains/escalates_to=edge (→ `references/relation-modeling.md`)
4. **Conversion/Tooling** — 도구 선택을 늦추고, 변환 출력도 재검증 (→ `knowledge_bases/graphviz-mermaid-conversion-tools-kb.md`)

## Knowledge Bases

- `knowledge_bases/mermaid-safe-authoring-kb.md` — **core canonical KB**: parser-safe 작성 규칙 (T-1~T-8)
- `knowledge_bases/graphviz-mermaid-conversion-tools-kb.md` — conversion/tooling strategy (hybrid KB)
- `knowledge_bases/codebase-graph-analysis-tools-kb.md` — visualization ecosystem (hybrid KB)

## Notes

- 이 skill의 상위 목적은 "더 예쁘게 그리기"가 아니라 **단계적 생성, 최소 문법 우선, 실패 시 축소/격리, 도구 선택을 늦추는 습관**을 이식하는 것이다
- parser-safe rules는 이 전략의 하위 규율이다 — 전략 전체를 대표하지 않는다
- document-first skill이다. `scripts/`는 의도적으로 두지 않는다
