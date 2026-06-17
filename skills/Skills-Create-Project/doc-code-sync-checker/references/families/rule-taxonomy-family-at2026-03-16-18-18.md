# Rule Taxonomy Family

## Priority Rule Types

- 필드/필수값
- enum/상수 집합
- 상태 전이표
- 경로 규칙 (`..`, 절대경로, symlink)

## Evidence Mapping

- 문서 쪽 evidence:
  - 표
  - bullet 목록
  - 규칙 문장
- 코드 쪽 evidence:
  - `validate_*`
  - 상수 집합
  - transition dict / table

## Mapping

- reference seed: `references/sync-targets.md`
- compare unit: rule object
- canonical KB: `doc-code-sync-canonical-design-at2026-03-16-18-18.md`
