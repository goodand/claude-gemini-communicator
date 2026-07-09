# doc-code-sync-checker 정합성 평가 체크리스트

> 목적: `knowledge_bases/`와 현재 `codebase(scripts/)`가 같은 skill을 가리키는지 구현 전에 점검한다.
> 우선순위: `knowledge_base <-> codebase`

## A. Canonical Source 고정

- [ ] **A-01**: `knowledge_base` 전체와 `codebase와 직접 대조할 canonical design slice`가 구분돼 있다
- [ ] **A-02**: `intent`는 참고용이고 구현 기준이 아님이 분리돼 있다
- [ ] **A-03**: KB에 없는 기능을 code가 먼저 주장하지 않는다
- [ ] **A-04**: KB가 단순 URL 인덱스인지, 설계 takeaways/제약/현 구현 상태까지 포함하는지 구분돼 있다

## B. Skill 정체성 정합

- [ ] **B-01**: KB의 핵심 목적이 "문서 규칙과 코드 구현의 drift 검사"로 일치한다
- [ ] **B-02**: code는 repo-wide 범용 엔진이 아니라 pairwise checker라는 경계를 유지한다
- [ ] **B-03**: 출력 단위가 `missing_in_code / missing_in_doc / mismatch`로 고정돼 있다
- [ ] **B-04**: runtime smoke test용 도구인지, 대규모 semantic diff 엔진인지 경계가 명확하다

## C. Workflow 정합

- [ ] **C-01**: KB/연구 메모의 핵심 단계 `extract-doc -> extract-code -> normalize -> compare -> report`가 정의돼 있다
- [ ] **C-02**: code에 최소한 `extract-doc`, `extract-code`, `compare`, `report` CLI가 존재한다
- [ ] **C-03**: `normalize` 단계가 code에 구현돼 있거나, 미구현이면 명시적으로 deferred 처리돼 있다
- [ ] **C-04**: `compare`는 normalization 이후의 rule set 비교라는 의미를 유지한다

## D. Rule Model 정합

- [ ] **D-01**: code가 규칙(rule) 단위를 기본 데이터 모델로 사용한다
- [ ] **D-02**: 문서 표현(표/목록/다이어그램)과 코드 표현(validate/상수/전이표)을 같은 계약으로 다룰 준비가 돼 있다
- [ ] **D-03**: `mismatch`가 단순 문자열 차이와 계약 차이를 구분할 수 있게 설계돼 있다
- [ ] **D-04**: `missing_in_code`와 `missing_in_doc`가 분리된 결과 필드로 남는다

## E. Output Contract 정합

- [ ] **E-01**: `extract-doc` 출력은 추후 `compare`가 소비 가능한 rules artifact를 만든다
- [ ] **E-02**: `extract-code` 출력도 같은 형태의 rules artifact를 만든다
- [ ] **E-03**: `compare` 출력에 `missing_in_code`, `missing_in_doc`, `mismatch`가 존재한다
- [ ] **E-04**: `report`는 비교 결과를 사람이 읽을 수 있는 drift 보고로 변환한다

## F. Scope Guardrail 정합

- [ ] **F-01**: 네트워크 비의존 로컬 분석 도구로 유지된다
- [ ] **F-02**: 입력 범위는 기본적으로 `reference 문서 1개 + script 1개` 쌍이다
- [ ] **F-03**: code 변경 없이 smoke test/검증 보고만 만드는 사용 시나리오가 가능하다
- [ ] **F-04**: claim-verifier와 역할이 섞이지 않는다

## G. 현재 구현 단계 명시

- [ ] **G-01**: code가 scaffold 상태이면 문서/KB 어디선가 명시돼 있다
- [ ] **G-02**: 현재 구현된 것과 아직 미구현인 것이 구분돼 있다
- [ ] **G-03**: "가능한 미래 기능"과 "현재 동작"이 혼동되지 않는다

## H. 최종 판정

- [ ] **H-01**: KB와 codebase는 같은 최소 제품 정의를 가리킨다
- [ ] **H-02**: 현재 불일치는 구현 깊이 부족인지, scope inflation인지 분류 가능하다
- [ ] **H-03**: 다음 단계는 `정합성 유지 하 구현`인지, `문서 축소`인지 결정 가능하다
