# Doc-Code Sync Applied Smoke Report

- date: `2026-03-16-18-42`
- target skill: `doc-code-sync-checker`
- canonical source: [doc-code-sync-canonical-design-at2026-03-16-18-18.md](../knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md)
- consistency checklist: [consistency-checklist.md](../checklist-forconsistency-evaluation/consistency-checklist.md)
- codebase: [doc_code_sync.py](../scripts/doc_code_sync.py)

## Commands Run

1. `python3 doc-code-sync-checker/scripts/doc_code_sync.py extract-doc --doc doc-code-sync-checker/references/sync-targets.md`
2. `python3 doc-code-sync-checker/scripts/doc_code_sync.py extract-code --script doc-code-sync-checker/scripts/doc_code_sync.py`
3. `python3 doc-code-sync-checker/scripts/doc_code_sync.py compare --doc-rules doc-code-sync-checker/references/smoke-doc-rules.json --code-rules doc-code-sync-checker/references/smoke-code-rules.json`
4. `python3 doc-code-sync-checker/scripts/doc_code_sync.py report --results doc-code-sync-checker/references/smoke-compare-results.json`
5. `python3 doc-code-sync-checker/scripts/test_doc_code_sync.py`
6. `python3 ../super-skill-creator/scripts/quick_validate.py doc-code-sync-checker`

## Observed Results

- `extract-doc`
  - `status: scaffold`
  - `rules: []`
  - message: `TODO: 표/목록/규칙 문장 파싱 구현`
- `extract-code`
  - `status: scaffold`
  - `rules: []`
  - message: `TODO: validate/상수/전이 dict 추출 구현`
- `compare`
  - `status: scaffold`
  - `missing_in_code`, `missing_in_doc`, `mismatch` 필드는 존재
  - `normalization.mode = internal_compare_stage`
  - `normalization.implemented = false`
- `report`
  - `status: scaffold`
  - 사람이 읽는 drift 보고는 아직 생성하지 않음
- tests
  - `3 tests OK`
- quick validate
  - `Validation passed`

## Alignment Verdict

### Pass

- canonical KB가 정의한 최소 제품 범위와 codebase scope는 일치한다.
  - `문서 1개 + 코드 1개` pairwise smoke-test checker
- workflow entrypoint는 일치한다.
  - `extract-doc`, `extract-code`, `compare`, `report`
- output contract의 최소 bucket 이름은 일치한다.
  - `missing_in_code`, `missing_in_doc`, `mismatch`
- `normalize`를 compare 내부 단계로 둔 설계와 scaffold payload가 일치한다.
- lint/TDD 기준은 현재 구조에서 통과한다.

### Partial

- rule object 중심 비교라는 설계는 문서에 고정돼 있지만, code에서는 빈 `rules` shell까지만 구현돼 있다.
- smoke test는 성공하지만, 실제 drift 증거를 계산하는 smoke test는 아직 아니다.

### Not Yet Implemented

- 문서 규칙 추출
- 코드 규칙 추출
- 공통 rule schema와 normalization
- 실제 mismatch 판정
- 사람이 읽는 drift 보고 생성

## Core Diagnosis

- 이번 적용 실험 기준으로 가장 큰 불일치는 `설계/정체성 drift`가 아니라 `구현 깊이 부족`이다.
- canonical KB, consistency checklist, scaffold code는 같은 최소 제품 정의를 가리킨다.
- 따라서 다음 단계는 문서 축소나 scope 재설정보다 `extract-doc -> extract-code -> compare`의 실제 rule artifact 구현이다.

## Next Action

1. `extract-doc`와 `extract-code`의 공통 rule schema를 정의한다.
2. 최소 4개 규칙 유형(필수 필드, enum/상수, 상태 전이표, 경로 규칙) 중 1개부터 실제 추출을 구현한다.
3. 그 artifact를 입력으로 `compare`의 첫 번째 real drift 판정을 만든다.
