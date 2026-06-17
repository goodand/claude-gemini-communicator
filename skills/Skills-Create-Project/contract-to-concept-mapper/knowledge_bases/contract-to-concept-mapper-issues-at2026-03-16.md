# contract-to-concept-mapper 현재 이슈

- date: `2026-03-16`
- role: `실행 계약 공간 -> 개념 공간 전용 skill 후보`

## 왜 필요한가

- 개념 공간은 추상적이라 직접 실행 계약으로 내릴 때 의미 손실이 발생하기 쉽다.
- 반대로 실행 계약 공간은 checklist, schema, task, CLI contract처럼 구조가 있으므로 상위 개념을 역으로 복원하기가 상대적으로 쉽다.
- 사용자는 이 방향을 우선 만드는 것이 더 실용적이라고 판단했다.

## 현재 이슈

1. checklist와 task가 어떤 상위 개념을 대표하는지 명시적으로 설명하는 도구가 없다.
2. `정합성 평가용 checklist`와 `구현용 checklist`가 어떤 의미 차이를 가지는지 상위 수준에서 복원하기 어렵다.
3. 실행 계약 공간을 Mermaid, 수도코드, 분석철학적 묘사, 인접행렬 같은 개념 표현으로 다시 올리는 표준 절차가 없다.
4. `실행 계약 -> 개념` 방향의 정합성 평가는 `개념 -> 실행 계약`보다 덜 손실적일 수 있는데, 이를 다루는 전용 skill이 없다.

## v0.1에서 다룰 핵심

- 입력:
  - checklist
  - task packet / task definition
  - JSON schema
  - CLI contract
  - 함수 시그니처
- 출력:
  - concept summary
  - boundary description
  - semantic relation map
  - pseudocode / Mermaid 초안

## 비목표

- 코드 수정
- 실행 로그 수집
- 외부 검색 자동화
