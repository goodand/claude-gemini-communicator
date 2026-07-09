# doc-code-sync-checker KB-Code 정합성 평가 결과

- date: `2026-03-16`
- priority: `knowledge_base <-> codebase`
- checklist: [consistency-checklist.md](./consistency-checklist.md)

## Summary

- 핵심 분류:
  - `구현 깊이 부족`
  - `KB canonical slice 정리 필요`
  - `scope inflation`

## Findings by Section

### A. Canonical Source 고정

- `A-01` pass
  - KB 전체와 codebase와 직접 대조할 `Canonical Design Takeaways` slice가 구분됐다.
- `A-02` partial
  - intent는 참고용으로 분리하려는 방향은 보이지만, 문서 맵에 여전히 메모리 복원 문서가 함께 노출된다.
- `A-03` partial
  - code는 과장하지 않지만, SKILL/ref 쪽 설명은 code보다 앞서 있다.
- `A-04` pass
  - KB가 URL 인덱스만이 아니라 설계 takeaways와 현재 구현 상태를 포함하도록 보강됐다.

### B. Skill 정체성 정합

- `B-01` pass
  - KB와 code 모두 drift 검사 계열 도구를 가리킨다.
- `B-02` fail
  - KB는 repo-wide consistency tooling 사례까지 넓게 가져오고, code는 현재 pairwise scaffold뿐이다.
- `B-03` pass
  - code 결과 필드는 `missing_in_code / missing_in_doc / mismatch`를 이미 가진다.
- `B-04` fail
  - 현재 문서 묘사는 smoke-test checker보다 일반화된 diff engine 쪽에 가깝다.

### C. Workflow 정합

- `C-01` partial
  - 연구 메모에는 `normalize` 단계가 있으나, KB 본문에는 설계 단계 요약이 없다.
- `C-02` pass
  - `extract-doc`, `extract-code`, `compare`, `report` CLI는 존재한다.
- `C-03` fail
  - `normalize`는 code에도 없고, "내부 단계로 deferred"라는 설명도 없다.
- `C-04` fail
  - 현재 `compare`는 normalization 이후 rule-set compare라는 의미를 아직 구현하지 못했다.

### D. Rule Model 정합

- `D-01` partial
  - code에 `rules: []` 형태는 있으나 실제 rule schema는 없다.
- `D-02` fail
  - 문서 표현과 코드 표현을 공통 계약으로 정규화하는 로직이 없다.
- `D-03` fail
  - `mismatch` 내부 분류가 없다.
- `D-04` pass
  - `missing_in_code`, `missing_in_doc`는 분리돼 있다.

### E. Output Contract 정합

- `E-01` pass
  - `extract-doc`는 rules artifact 자리(`rules`)를 반환한다.
- `E-02` pass
  - `extract-code`도 같은 구조를 반환한다.
- `E-03` pass
  - `compare` 출력 필드는 존재한다.
- `E-04` fail
  - `report`는 아직 실제 drift 보고로 변환하지 않는다.

### F. Scope Guardrail 정합

- `F-01` pass
  - 로컬, 네트워크 비의존 도구다.
- `F-02` pass
  - 입력 형태는 기본적으로 문서 1개와 스크립트 1개다.
- `F-03` fail
  - smoke test용 의미 있는 결과를 아직 만들지 못한다.
- `F-04` pass
  - claim-verifier와의 역할 경계는 문서상 분리돼 있다.

### G. 현재 구현 단계 명시

- `G-01` pass
  - script에 scaffold가 명시돼 있다.
- `G-02` pass
  - 미구현 메시지가 TODO로 노출된다.
- `G-03` fail
  - 사용자는 현재 동작보다 미래 기능을 더 크게 읽을 가능성이 있다.

## Core Diagnosis

### 1. 가장 큰 문제는 code 부족보다 KB 부족이다

초기 KB는 URL 인덱스로는 유용했지만, code와 직접 대조할 설계 문장들이 부족했다.
현재는 KB 전체와 codebase 대조용 canonical slice를 분리해 이 문제를 줄였다.

### 2. 두 번째 문제는 normalize 단계의 공백이다

연구 메모에서는 `normalize`가 핵심인데, code에는 별도 단계도 없고 내부 구현 설명도 없다.
이 공백 때문에 `compare`의 의미가 약해진다.

### 3. 세 번째 문제는 scope inflation이다

KB가 들고 온 외부 사례가 넓어서 현재 scaffold보다 skill이 더 커 보인다.
지금 단계에서는 pairwise smoke-test checker로 더 좁게 정의하는 편이 맞다.

## Immediate Alignment Actions

1. `knowledge_base 전체`와 `codebase와 직접 대조할 canonical slice`를 계속 분리 유지한다.
2. `normalize`는 v0.1에서 별도 CLI가 아니라 internal compare stage라는 점을 문서로 유지한다.
3. 다음 정합성 평가는 `Canonical Design Takeaways`와 `scripts/doc_code_sync.py`를 직접 비교 기준으로 삼는다.
