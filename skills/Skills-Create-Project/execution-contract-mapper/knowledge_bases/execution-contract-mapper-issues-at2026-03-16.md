# execution-contract-mapper 현재 이슈

- date: `2026-03-16`
- role: `실행 계약 공간 전용 skill 후보`

## 왜 필요한가

- 개념 공간과 codebase 사이에 중간층이 없으면, 의미가 바로 구현으로 떨어지면서 drift가 생긴다.
- 실제 agent는 checklist, JSON schema, CLI contract, 함수 시그니처, rule schema 같은 형식적 계약을 더 안정적으로 따른다.
- 현재 `doc-code-sync-checker` 논의에서도 이 중간층의 부재가 계속 문제였다.

## 현재 이슈

1. knowledge_base 전체와 codebase 사이를 직접 비교하면 범위가 너무 넓다.
2. `정합성 평가용 checklist`와 `구현용 checklist`의 역할 차이가 명확히 관리되지 않는다.
3. `rule schema` 같은 핵심 계약이 명시적으로 추출되지 않으면 compare 단계가 공중에 뜬다.
4. codebase가 따르는 계약과 runtime evidence가 지지하는 계약을 분리해서 봐야 한다.

## v0.1에서 다룰 핵심

- 입력:
  - knowledge_base의 핵심 설계 요약
  - 정합성 평가용 checklist
  - 구현용 checklist
- 출력:
  - contract map
  - rule schema
  - codebase comparison basis

## 비목표

- 실제 로그 수집
- 테스트 실행
- 사람 친화적 개념 시각화 자체
