# GitHub Search Report — kb-to-consistency-check

## 사용자 의도 파악

- 목표: `knowledge_base -> 정합성 평가용 checklist` 변환의 정합성을 기계적으로 점검할 수 있는 방법과 도구 패턴을 찾는다.
- 초점:
  - traceability matrix
  - requirement/spec -> checklist derivation
  - coverage / unsupported item detection
  - 문서/계약 간 차이를 itemized diagnostics로 내는 lint 패턴
- 제외:
  - 단순 링크 체커
  - repo-wide crawler
  - 최종 코드 구현 검증 도구

## Shortlist

### 1. StrictDoc
- URL: https://github.com/strictdoc-project/strictdoc
- 참고 문서: https://strictdoc.readthedocs.io/en/stable/stable/docs/strictdoc_21_L2_StrictDoc_Requirements-DEEP-TRACE.html
- 선택 이유:
  - requirement traceability matrix를 정식 산출물로 본다
  - forward / backward traceability, uncovered requirement report를 분리한다
  - `knowledge_base -> checklist`에서도 `coverage gap`과 `unjustified checklist item`을 분리하는 기준이 된다

### 2. Sphinx-Needs
- URL: https://github.com/useblocks/sphinx-needs
- 참고 문서: https://www.sphinx-needs.com/
- 선택 이유:
  - requirement, specification, test case 같은 need object를 링크 가능한 단위로 관리한다
  - traceability를 표, flow, filterable view로 표현한다
  - KB 문장/섹션을 “need-like unit”으로 분해하는 발상에 참고가 된다

### 3. Coral RepoDocConsistencyChecker Agent
- URL: https://github.com/Coral-Protocol/Coral-RepoDocConsistencyChecker-Agent
- 선택 이유:
  - diff 결과를 단순 pass/fail이 아니라 itemized inconsistency로 보고한다
  - `missing`, `stale`, `misaligned` 같은 분류형 diagnostics 패턴을 참고할 수 있다

### 4. OpenAPI-diff
- URL: https://github.com/OpenAPITools/openapi-diff
- 선택 이유:
  - 두 계약 문서 간 차이를 structured diff로 만든다
  - KB와 checklist 비교도 holistic score보다 `항목 단위 structured diff`가 더 적절하다는 점을 보여준다

### 5. oasdiff
- URL: https://github.com/oasdiff/oasdiff
- 선택 이유:
  - diff, breaking, changelog, checks를 분리한다
  - `kb_to_consistency_check.py`도 `coverage`, `unsupported`, `scope inflation`, `notes` 같은 여러 출력 채널로 나누는 게 좋다

### 6. pydoclint
- URL: https://github.com/jsh9/pydoclint
- 선택 이유:
  - 문서와 시그니처 간 정합성을 lint 규칙으로 작은 항목 단위로 검사한다
  - `항목별 rule + 명시적 오류 메시지` 방식이 KB-checklist 정합성 검사에도 잘 맞는다

## Design Takeaways

- 핵심은 단일 점수보다 **traceable item-level diagnostics**다.
- 최소 비교 방향은 두 개다.
  - `forward`: KB 핵심 takeaways가 checklist에 반영됐는가
  - `backward`: checklist 항목이 KB 근거를 갖는가
- 최소 분류는 아래 4개가 적절하다.
  - `covered`
  - `missing_from_checklist`
  - `unsupported_in_checklist`
  - `scope_inflation`
- `traceability matrix` 또는 동등한 테이블이 필요하다.
  - KB unit id
  - checklist item id
  - relation type
  - evidence
- 출력은 최소 두 층으로 나누는 편이 좋다.
  - machine-readable JSON
  - human-readable markdown report

## Reject / Hold

- 단순 markdown link checker는 KB-checklist 의미 정합성을 측정하지 못한다.
- repo 전체를 스캔하는 도구는 현재 목적보다 범위가 너무 넓다.
- 생성형 요약만 제공하고 근거를 남기지 않는 도구는 `kb_to_consistency_check.py` 설계 기준으로 부적합하다.
