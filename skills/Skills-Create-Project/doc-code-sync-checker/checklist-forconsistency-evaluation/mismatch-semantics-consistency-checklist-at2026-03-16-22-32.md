# doc-code-sync-checker mismatch semantics 정합성 평가 체크리스트

> 목적: `mismatch`를 generic semantic blob이 아니라 typed mismatch contract로 확장할 때, KB와 구현 계획이 같은 방향을 가리키는지 점검한다.
> 우선순위: `knowledge_base <-> future mismatch design`
> source of truth: `knowledge_bases/mismatch-semantics-knowledge_base-at2026-03-16-22-22.md`

## A. Mismatch 역할 구분

- [ ] **A-01**: `mismatch`는 `missing_in_code`, `missing_in_doc`와 다른 결과 category로 분리돼 있다
- [ ] **A-02**: `mismatch`는 단순 자유서술이 아니라 typed result로 다뤄진다
- [ ] **A-03**: mismatch 확장이 현재 pairwise checker 경계를 유지한다

## B. Typed Result 정합

- [ ] **B-01**: mismatch 결과는 stable category 이름을 가진다
- [ ] **B-02**: category 이름은 `changed` 계열과 `missing` 계열을 혼동하지 않는다
- [ ] **B-03**: 최소 v0.1은 구조화된 typed mismatch부터 시작하고, full semantic judge로 바로 가지 않는다
- [ ] **B-04**: 후속 액션이 가능한 typed bucket으로 설계된다

## C. Evidence 정합

- [ ] **C-01**: 각 mismatch 항목은 문서 쪽 evidence를 가진다
- [ ] **C-02**: 각 mismatch 항목은 코드 쪽 evidence를 가진다
- [ ] **C-03**: mismatch 판정은 연결 가능한 rule pair를 기준으로 한다
- [ ] **C-04**: traceability 없는 semantic 추정만으로 mismatch를 확정하지 않는다

## D. Output Contract 정합

- [ ] **D-01**: 사람용 보고와 기계용 artifact가 함께 남는다
- [ ] **D-02**: mismatch 결과는 최소 `kind`, `name`, `doc_evidence`, `code_evidence` 수준의 구조를 가진다
- [ ] **D-03**: `compare` 결과에서 typed mismatch가 stable field로 분리된다
- [ ] **D-04**: `report`는 mismatch category별 요약을 제공한다

## E. Scope Guardrail 정합

- [ ] **E-01**: v0.1 mismatch는 pairwise local analysis에 머문다
- [ ] **E-02**: 네트워크 호출이나 외부 judge를 필수 전제로 두지 않는다
- [ ] **E-03**: mismatch 확장이 곧 repo-wide semantic diff 엔진을 의미하지 않는다
- [ ] **E-04**: mismatch 결과는 evidence 기반 review queue로 이어질 수 있어야 한다

## F. Reference-derived Direction

- [ ] **F-01**: OpenAPI diff 계열처럼 `missing`과 `changed`를 분리하는 방향을 따른다
- [ ] **F-02**: pydoclint처럼 비교 가능한 단위끼리 typed lint를 만드는 방향을 따른다
- [ ] **F-03**: StrictDoc처럼 traceability가 연결된 단위에서 mismatch를 판단하는 방향을 따른다
- [ ] **F-04**: mismatch는 최종 의미 판정기보다 typed detector에 가깝다는 점이 유지된다

## G. 최종 판정

- [ ] **G-01**: KB가 가리키는 mismatch 확장 방향과 구현 후보 방향이 일치한다
- [ ] **G-02**: 다음 구현 단계가 `typed mismatch slice`인지 명확하다
- [ ] **G-03**: mismatch 확장 전에 필요한 추가 KB/체크리스트/증거가 구분된다
