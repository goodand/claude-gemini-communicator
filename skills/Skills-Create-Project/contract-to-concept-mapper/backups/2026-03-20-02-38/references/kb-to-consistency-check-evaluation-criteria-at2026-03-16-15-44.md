# kb-to-consistency-check 평가 기준 메모

## 목적

`kb_to_consistency_check.py`를 구현하기 전에, 현재 reference에서 바로 채택 가능한 평가 기준을 고정한다.

## 최소 비교 단위

- `knowledge_base 전체`를 바로 checklist 전체와 비교하지 않는다.
- 먼저 KB를 아래 같은 `KB canonical unit`으로 나눈다.
  - 핵심 workflow step
  - input contract rule
  - output contract rule
  - scope guardrail
  - explainability / traceability rule
  - current stage / limitation rule

## 최소 판정 유형

- `covered`
  - KB canonical unit이 checklist 항목 하나 이상으로 내려옴
- `missing_from_checklist`
  - KB canonical unit이 checklist에 반영되지 않음
- `unsupported_in_checklist`
  - checklist 항목이 KB 근거를 찾지 못함
- `scope_inflation`
  - checklist 항목이 KB보다 더 강한 요구를 새로 추가함
- `boundary_loss`
  - KB non-goal / limitation / guardrail이 checklist에서 사라짐

## 최소 측정 지표

- `coverage_ratio`
  - `covered KB units / total KB canonical units`
- `unsupported_item_ratio`
  - `unsupported checklist items / total checklist items`
- `traceability_ratio`
  - `KB 근거를 역참조 가능한 checklist items / total checklist items`
- `boundary_preservation_ratio`
  - `preserved guardrails / total guardrails`

## 출력 형식 제안

### machine-readable
- `coverage.json`
  - `kb_units`
  - `checklist_items`
  - `mappings`
  - `metrics`
  - `human_review_queue`

### human-readable
- `coverage_report.md`
  - missing KB units
  - unsupported checklist items
  - scope inflation candidates
  - boundary loss candidates

## 현재 한계

- 현재 checklist 포맷에는 항목별 `derived_from`이나 `evidence` 필드가 없다.
- 따라서 v0.1은 완전한 semantic validator가 아니라,
  **anchor/keyword + section-level comparison + human review queue 생성기**로 시작하는 것이 현실적이다.

## 다음 구현 전 선행 작업

1. consistency checklist 포맷에 `근거 문서` 또는 `derived_from` 필드를 둘지 결정
2. KB에서 canonical unit을 어떻게 추출할지 규칙화
3. `정합성 평가용 checklist` 항목을 id 단위로 분해하는 규칙 정의

## 직접 참고한 reference

- GitHub:
  - https://github.com/strictdoc-project/strictdoc
  - https://www.sphinx-needs.com/
  - https://github.com/Coral-Protocol/Coral-RepoDocConsistencyChecker-Agent
  - https://github.com/OpenAPITools/openapi-diff
  - https://github.com/oasdiff/oasdiff
  - https://github.com/jsh9/pydoclint
- Papers / spec-like docs:
  - https://digitalcommons.calpoly.edu/theses/317/
  - https://ieeexplore.ieee.org/document/8595127
  - https://perspectivas.espoch.edu.ec/RCP_ESPOCH/en/article/view/221
  - https://www.sciencedirect.com/science/article/abs/pii/S0306437924000425
  - https://strictdoc-project.github.io/strictdoc-templates/strictdoc-templates/templates/ECSS-E-ST-40C/TS/SRS-TRACE.html
