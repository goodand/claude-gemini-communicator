# KB Checklist Pipeline Family: document_output

## Scope

- 최종 산출물이 `md`, `txt`, `image`일 때 사용하는 branch
- 문서만 정리하고 끝나는 흐름이다

## Read Chain

1. branch index
2. canonical KB
3. consistency checklist
4. implementation checklist
5. 문서 산출물 작성
6. 필요하면 evidence만 추가

## Required Output

- canonical KB에서 내려온 내용이 문서 산출물에 반영돼야 한다
- consistency checklist 기준이 먼저 고정돼야 한다
- implementation checklist는 문서 작업 단위만 포함한다

## Non-goals

- TDD 파일 생성 강제
- 실행 코드 작성
- smoke test CLI 추가
