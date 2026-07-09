# doc-code-sync-checker 구현용 체크리스트

> 위치: `knowledge_base` 아래, `codebase` 위
> 역할: KB의 설계 takeaways를 현재 구현 가능한 작업 항목으로 낮춘다.
> source of truth: `checklist-forconsistency-evaluation/consistency-checklist.md`

## A. Scope 고정

- [ ] v0.1 범위를 `문서 1개 + 코드 1개` pairwise checker로 고정한다
- [ ] repo-wide scan, semantic diff engine, 자동 수정 기능은 제외한다
- [ ] 네트워크 비의존 로컬 CLI로 유지한다

## B. Rule Model 최소 스키마

- [ ] rule object 최소 필드를 정한다
  - `kind`
  - `source`
  - `value`
  - `evidence`
- [ ] `extract-doc`와 `extract-code`가 같은 rule shape를 반환하게 한다
- [ ] `mismatch` 내부 세부 분류가 필요한지 정한다

## C. extract-doc

- [ ] 문서에서 최소 4종 규칙을 추출한다
  - 필수 필드
  - enum/상수 집합
  - 상태 전이표
  - 경로 규칙
- [ ] 표/목록/문장 중 어떤 패턴을 우선 지원할지 정한다
- [ ] 출력은 JSON rules artifact로 고정한다

## D. extract-code

- [ ] script에서 최소 3종 근거를 읽는다
  - `validate_*` 함수
  - 상수 집합
  - transition dict / table
- [ ] AST 기반으로 갈지, 정규식 기반으로 갈지 정한다
- [ ] 출력은 `extract-doc`와 같은 rule shape로 고정한다

## E. normalize

- [ ] 별도 CLI를 만들지 않고 compare 내부 단계로 둔다
- [ ] 문서 rule과 코드 rule을 공통 tuple/object로 바꾼다
- [ ] 표현 차이와 계약 차이를 분리하는 기준을 정한다

## F. compare

- [ ] 출력 필드 3개를 유지한다
  - `missing_in_code`
  - `missing_in_doc`
  - `mismatch`
- [ ] compare는 normalize 이후 결과만 사용한다
- [ ] `mismatch`에 최소 설명 문자열을 남긴다

## G. report

- [ ] 사람이 읽을 수 있는 drift 요약을 만든다
- [ ] 각 항목에 후속 액션 1줄을 붙인다
- [ ] smoke test용으로 과한 장문 보고는 피한다

## H. Scaffold 명시

- [ ] 구현 전까지 `status: scaffold`를 유지한다
- [ ] 미구현 단계는 TODO 메시지로 숨기지 말고 명시한다
- [ ] `normalize`가 internal compare stage라는 점을 help/docstring에 유지한다
