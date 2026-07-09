# evidence-trace-auditor 현재 이슈

- date: `2026-03-16`
- role: `관측·증거 공간 전용 skill 후보`

## 왜 필요한가

- 지금까지도 문서에 적힌 주장과 실제 실행 증거를 혼동한 적이 있었다.
- agent self-report보다 로그, 테스트 결과, JSON 산출물, runtime artifact가 더 강한 증거다.
- 실행 결과를 구조화해 계약과 대조하는 전용 skill이 없다.

## 현재 이슈

1. `stored claim`과 `verified evidence`를 분리하는 표준 절차가 없다.
2. 실행 로그, 테스트 결과, 산출 파일을 같은 evidence ledger로 묶는 방식이 없다.
3. codebase 정합성과 runtime truth를 따로 봐야 하는데, 현재는 종종 섞여서 해석된다.
4. "실행 증거가 있는 것 / 없는 것"을 자동 분류하는 도구가 없다.

## v0.1에서 다룰 핵심

- 입력:
  - 로그
  - 테스트 결과
  - JSON 출력
  - 산출 파일 경로
- 출력:
  - evidence ledger
  - support / missing evidence 분류
  - residual uncertainty 목록

## 비목표

- 개념 모델 설계
- schema/checklist 설계
- code 수정 자동화
