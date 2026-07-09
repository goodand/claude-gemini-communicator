# semantic-slice-mapper 현재 이슈

- date: `2026-03-16`
- role: `개념 공간 전용 skill 후보`

## 왜 필요한가

- 지금 논의에서는 `개념 공간 / 실행 계약 공간 / 관측·증거 공간`이 계속 섞여서 다뤄진다.
- 사용자 관점 표현은 자연어, Mermaid, LaTeX, 수도코드처럼 형식이 다양하다.
- 이 표현들을 바로 code나 checklist로 내리면 경계와 의미가 흔들리기 쉽다.

## 현재 이슈

1. `semantic slice relation`이라는 개념은 나왔지만, 아직 표준 산출물 형식이 없다.
2. 상위 개념과 하위 개념의 포함 관계를 일관되게 표현하는 방식이 없다.
3. 개념 공간 내부 정합성을 평가하는 전용 skill이 없다.
4. 사람 친화적 표현과 agent 친화적 표현 사이를 잇는 중간 산출물이 부족하다.

## v0.1에서 다룰 핵심

- 입력:
  - 자연어 설명
  - Mermaid
  - LaTeX 수식
  - 수도코드
- 출력:
  - concept graph
  - boundary map
  - semantic slice list

## 비목표

- 코드 생성
- JSON schema 설계
- 실행 로그 분석
