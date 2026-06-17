# KB Checklist Pipeline Branch Index

## Purpose

- 어떤 산출물 분기로 내려갈지 먼저 고른다.
- `document_output`과 `implementation_output`을 섞지 않는다.

## Branches

| branch | when | next document |
|---|---|---|
| `document_output` | 최종 산출물이 `md`, `txt`, `image`일 때 | [document-output-branch-at2026-03-16-23-11.md](../families/document-output-branch-at2026-03-16-23-11.md) |
| `script_output` | 최종 산출물이 실행 코드일 때 | [implementation-output-branch-at2026-03-16-23-11.md](../families/implementation-output-branch-at2026-03-16-23-11.md) |
| `implementation_output` | 최종 산출물이 `md/txt/image`가 아닌 비문서 구현물일 때 | [implementation-output-branch-at2026-03-16-23-11.md](../families/implementation-output-branch-at2026-03-16-23-11.md) |

## Decision Rule

1. 최종 산출물이 문서만이면 `document_output`
2. 실행 코드가 생기면 `script_output`
3. 실행 코드는 아니지만 `md/txt/image`가 아니면 `implementation_output`

## Shared Source Of Truth

- [kb-checklist-pipeline-canonical-design-at2026-03-16-23-11.md](../../knowledge_bases/kb-checklist-pipeline-canonical-design-at2026-03-16-23-11.md)
