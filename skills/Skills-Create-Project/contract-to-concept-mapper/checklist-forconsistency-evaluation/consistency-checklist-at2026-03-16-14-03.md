# contract-to-concept-mapper 정합성 평가 체크리스트

> 목적: `knowledge_bases/`가 정의한 방향과 현재 skill/codebase가 같은 문제를 다루는지 구현 전에 점검한다.
> 우선순위: `knowledge_base <-> codebase`

## A. Skill 정체성 정합

- [ ] **A-01**: 이 skill의 핵심 목적이 `실행 계약 공간 -> 개념 공간` 복원으로 일치한다
- [ ] **A-02**: `개념 -> 실행 계약`과 혼동되지 않는다
- [ ] **A-03**: codebase 정합성 평가 도구와 직접 동일시되지 않는다
- [ ] **A-04**: 단순 summarizer가 아니라 `설명 가능한 lifting system`이라는 점이 유지된다

## B. Input Contract 정합

- [ ] **B-01**: 기본 입력이 `checklist`, `task`, `schema`, `CLI contract`, `함수 시그니처`로 정의돼 있다
- [ ] **B-02**: checklist를 1급 입력으로 다룬다
- [ ] **B-03**: `정합성 평가용 checklist`와 `구현용 checklist`를 서로 다른 contract artifact로 구분한다
- [ ] **B-04**: 단일 항목이 아니라 skill/project context를 함께 볼 필요가 반영돼 있다

## C. Output Contract 정합

- [ ] **C-01**: 최소 출력이 `concept summary`, `boundary description`, `semantic relation map`으로 정의돼 있다
- [ ] **C-02**: render target으로 `Mermaid`, `pseudocode` 같은 사람이 읽는 형식이 포함된다
- [ ] **C-03**: 벡터 인덱스/벡터 값은 보조 출력으로 취급된다
- [ ] **C-04**: 출력은 traceability 없이 자연어만 남기지 않는다

## D. Lifting Workflow 정합

- [ ] **D-01**: 핵심 단계가 `collect contracts -> segment units -> lift concepts -> render concepts`로 유지된다
- [ ] **D-02**: `contract unit` 계층이 중간 표현으로 필요하다는 점이 반영돼 있다
- [ ] **D-03**: `concept unit` 또는 동등한 상위 의미 단위가 필요하다는 점이 반영돼 있다
- [ ] **D-04**: render 이전에 relation/boundary 정리가 선행된다

## E. Explainability / Traceability 정합

- [ ] **E-01**: 어떤 contract unit이 어떤 concept summary로 lift됐는지 남긴다
- [ ] **E-02**: 요약만 있고 근거 링크가 없는 출력을 실패 사례로 본다
- [ ] **E-03**: uncertainty 또는 weak support를 표시할 수 있다
- [ ] **E-04**: project context가 부족한 경우 과도한 개념 복원을 경계한다

## F. Scope Guardrail 정합

- [ ] **F-01**: 이 skill은 코드 수정 도구가 아니다
- [ ] **F-02**: 이 skill은 실행 로그 수집기가 아니다
- [ ] **F-03**: 외부 검색 자동화 자체가 목적이 아니다
- [ ] **F-04**: `semantic-slice-mapper`, `execution-contract-mapper`, `evidence-trace-auditor`와 책임이 구분된다

## G. Current Stage 정합

- [ ] **G-01**: 현재는 scaffold 단계라는 점이 분명하다
- [ ] **G-02**: future output과 current capability가 혼동되지 않는다
- [ ] **G-03**: KB가 넓더라도 현재 v0.1 범위를 별도로 읽어낼 수 있다

## H. 최종 판정

- [ ] **H-01**: KB와 codebase는 같은 최소 제품 정의를 가리킨다
- [ ] **H-02**: 현재 불일치는 구현 공백인지, 개념 혼동인지, scope inflation인지 분류 가능하다
- [ ] **H-03**: 다음 단계 구현이 `traceable lifting`을 강화하는 방향으로 이어진다
