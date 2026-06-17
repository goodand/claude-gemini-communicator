# Doc-Code Sync Family Index

## Purpose

`doc-code-sync-checker`에서 어떤 reference 층을 먼저 읽을지 고르는 family index다.

## Families

| family | use when | script/output mapping |
|---|---|---|
| `pairwise-sync` | 문서 1개와 스크립트 1개의 기본 workflow를 고정할 때 | `extract-doc`, `extract-code`, `compare`, `report` |
| `rule-taxonomy` | 어떤 규칙 유형을 우선 지원할지 정할 때 | rule schema, compare buckets |
| `drift-report` | 결과 분류와 보고 형식을 고정할 때 | `missing_in_code`, `missing_in_doc`, `mismatch` |

## Read Path

1. pairwise workflow가 필요하면 `pairwise-sync-family-at2026-03-16-18-18.md`
2. rule kind와 evidence 단위가 필요하면 `rule-taxonomy-family-at2026-03-16-18-18.md`
3. 출력 계약과 후속 액션 규칙이 필요하면 `drift-report-family-at2026-03-16-18-18.md`
4. 실제 source of truth는 `knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md`
