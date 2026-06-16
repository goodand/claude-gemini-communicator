# doc-code-sync-checker mismatch semantics 구현용 체크리스트

> 위치: `mismatch semantics knowledge_base` 아래, `typed mismatch codebase` 위
> 역할: mismatch semantics KB와 정합성 평가용 checklist를 현재 구현 가능한 typed mismatch slice로 낮춘다.
> source of truth: `checklist-forconsistency-evaluation/mismatch-semantics-consistency-checklist-at2026-03-16-22-32.md`

## A. Scope 고정

- [ ] v0.1 mismatch 범위를 `pairwise local analysis`로 고정한다
- [ ] `missing_in_code`, `missing_in_doc`와 별도 결과 field로 `typed_mismatch`를 둔다
- [ ] 네트워크 호출, 외부 judge, repo-wide semantic diff는 제외한다
- [ ] mismatch는 full semantic verdict가 아니라 typed detector로 유지한다

## B. Typed Contract 최소 스키마

- [ ] typed mismatch object 최소 필드를 정한다
  - `kind`
  - `name`
  - `doc_evidence`
  - `code_evidence`
  - `reason`
- [ ] `typed_mismatch`는 stable category 이름을 사용한다
- [ ] `missing` 계열과 `changed` 계열을 같은 bucket으로 섞지 않는다

## C. First Slice 선정

- [ ] 첫 mismatch slice는 이미 구현된 rule kind 위에서 확장한다
- [ ] 첫 mismatch slice를 `enum_value_set_changed`로 고정한다
- [ ] 두 번째 mismatch slice를 `transition_rule_set_changed`로 고정한다
- [ ] 세 번째 mismatch slice를 `path_rule_condition_changed`로 고정한다
- [ ] 첫 slice는 exact pair matching이 가능한 규칙만 대상으로 삼는다
- [ ] free-form semantic explanation은 review note로만 둔다

## D. Evidence 연결

- [ ] mismatch 후보는 문서 rule과 코드 rule이 모두 존재할 때만 평가한다
- [ ] 문서 쪽 evidence를 결과 object에 남긴다
- [ ] 코드 쪽 evidence를 결과 object에 남긴다
- [ ] traceability가 약한 항목은 `review queue`로 내리고 자동 확정하지 않는다

## E. compare 확장

- [ ] 기존 출력 필드
  - `missing_in_code`
  - `missing_in_doc`
  - `mismatch`
  를 유지한다
- [ ] `typed_mismatch` field를 새로 추가할지, 기존 `mismatch`를 typed list로 승격할지 하나로 고정한다
- [ ] 결과 category별 count를 계산 가능하게 한다
- [ ] typed mismatch는 rule-pair 기준으로만 생성한다

## F. report 확장

- [ ] 기계용 artifact에 typed mismatch 목록을 남긴다
- [ ] 사람용 report에 category별 요약을 남긴다
- [ ] 각 mismatch 항목에 후속 액션 1줄을 붙인다
- [ ] `missing`과 `changed`를 분리 표기한다

## G. TDD

- [ ] `scripts/test_doc_code_sync.py`에 typed mismatch fixture를 추가한다
- [ ] positive case 1개를 만든다
- [ ] negative case 1개를 만든다
- [ ] 기존 zero-drift slice를 깨지 않는 회귀 테스트를 유지한다

## H. 비목표

- [ ] 자연어 의미 유사도만으로 mismatch를 확정하지 않는다
- [ ] LLM judge를 필수 전제로 두지 않는다
- [ ] 현재 단계에서 자동 수정까지 확장하지 않는다

## I. 완료 조건

- [ ] 첫 typed mismatch slice가 실제 pair 1개에서 재현된다
- [ ] smoke report가 사람이 읽는 typed mismatch 요약을 만든다
- [ ] KB -> consistency checklist -> implementation checklist -> code 후보 흐름이 유지된다
