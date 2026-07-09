# Mismatch Semantics Web Research

- generated_at: `2026-03-16-22-18`
- scope: `doc-code-sync-checker`의 다음 slice인 `mismatch` 설계 참고

## Source URLs

- OpenAPI-diff: https://github.com/OpenAPITools/openapi-diff
- oasdiff checks: https://github.com/oasdiff/oasdiff
- pydoclint: https://github.com/jsh9/pydoclint
- StrictDoc traceability: https://github.com/strictdoc-project/strictdoc

## Why These Sources

- `openapi-diff`, `oasdiff`는 계약 간 차이를 단순 집합 차이와 `breaking / changed / checks`로 나누는 대표 사례다.
- `pydoclint`는 문서와 코드 사이의 파라미터/반환/예외 불일치를 lint category로 분리하는 사례다.
- `StrictDoc`은 requirements와 implementation을 traceability 기반으로 연결하는 사례다.

## Reusable Takeaways

### 1. `mismatch`는 `missing`과 분리된 bucket이어야 한다

- `missing_in_code`, `missing_in_doc`는 존재 여부 문제다.
- `mismatch`는 양쪽에 모두 규칙이 있는데 의미나 속성이 다른 경우다.

### 2. `mismatch`는 value-level/constraint-level로 시작하는 것이 안전하다

- 문서와 코드에 둘 다 같은 rule name이 있을 때만 `mismatch`를 계산한다.
- v0.1에서는 자연어 semantic diff보다
  - 값 집합 차이
  - 조건 차이
  - severity/strictness 차이
  같은 구조적 속성 차이를 먼저 다루는 편이 낫다.

### 3. 설명 문장 전체 비교보다 `typed mismatch`가 먼저다

- `pydoclint`처럼 mismatch를 카테고리화해야 후속 액션이 명확해진다.
- `doc-code-sync-checker`에 적합한 첫 mismatch 분류 예:
  - `enum_value_set_changed`
  - `transition_condition_changed`
  - `constraint_threshold_changed`
  - `guardrail_strength_changed`

### 4. `mismatch`는 evidence pair를 함께 남겨야 한다

- 단일 evidence가 아니라
  - `doc_evidence`
  - `code_evidence`
  쌍이 같이 있어야 사람이 바로 판단할 수 있다.

### 5. strict semantic judge로 바로 가면 과하다

- 현재 `doc-code-sync-checker`의 강점은 pairwise, local, rule-object 기반이다.
- 따라서 다음 step도 LLM semantic judge보다
  - exact match
  - normalized value compare
  - typed mismatch
  순서로 가는 것이 일관된다.

## Recommended Next Design

`mismatch`의 첫 구현은 아래 제한으로 시작하는 것이 적절하다.

- rule 종류별로 `comparable attributes`를 따로 둔다
- 양쪽에 같은 `rule name`이 있을 때만 mismatch 계산
- 출력 shape:

```json
{
  "kind": "enum_value",
  "name": "status",
  "mismatch_type": "enum_value_set_changed",
  "doc_evidence": "...",
  "code_evidence": "...",
  "doc_value": ["queued", "ready"],
  "code_value": ["queued", "ready", "blocked"]
}
```

## Immediate Fit To Current Skill

- `required_field`: 현재는 `mismatch`보다 `missing` 중심이 맞다
- `path_safety`: 다음 후보는 `guardrail_strength_changed`
- `transition_rule`: 다음 후보는 `transition_condition_changed`
- `enum_value`: 다음 후보는 `enum_value_set_changed`
