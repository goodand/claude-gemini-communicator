# Contract-To-Concept Family Index

## Purpose

이 문서는 `contract-to-concept-mapper`의 넓은 reference 공간에서
어떤 family 문서를 먼저 읽어야 하는지 고르는 index다.

## Read Order

1. family를 고른다
2. family 문서에서 현재 관심사를 좁힌다
3. `knowledge_bases/contract-to-concept-canonical-design-at2026-03-16-18-06.md`로 내려간다
4. 그 다음 checklist / scripts로 이동한다

## Family Map

| Family | Use this when | Current script/output mapping |
|---|---|---|
| `lifting-core-family-at2026-03-16-18-06.md` | checklist/task/schema를 concept-space로 올리는 핵심 흐름을 정리할 때 | 현재는 설계 중심, 구현 스크립트 없음 |
| `explainability-traceability-family-at2026-03-16-18-06.md` | 근거 링크, weak support, traceability를 정리할 때 | `scripts/kb_to_consistency_check.py` |
| `output-contract-family-at2026-03-16-18-06.md` | concept summary / boundary map / Mermaid / pseudocode 출력 규칙을 정리할 때 | 현재는 canonical KB + checklist 기준 |

## Router Rule

- broad research가 필요하면 family 문서를 읽는다
- 현재 채택 설계를 보려면 canonical KB를 읽는다
- 실제 정합성 확인은 consistency checklist와 scripts를 읽는다
