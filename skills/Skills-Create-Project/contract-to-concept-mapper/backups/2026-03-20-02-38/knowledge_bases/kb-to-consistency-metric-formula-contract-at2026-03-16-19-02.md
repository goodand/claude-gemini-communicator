# KB-To-Consistency Metric Formula Contract

이 문서는 `contract-to-concept-mapper`의 `kb_to_consistency_check.py`가 사용하는 4개 metric의
이름, 분자/분모, strict-vs-proxy 해석을 고정하는 local fixed-point 문서다.

원칙:
- report-facing key는 현재 codebase의 이름을 유지한다
- 현재 v0.1 metric은 대부분 `strict`보다 `proxy-profile`에 가깝다
- 이름과 로직이 다르면 이 문서가 먼저 수정되고, 그 다음 KB/checklist/scripts가 따라온다

## 1. coverage_ratio

- class: `proxy-profile`
- semantic:
  - canonical KB unit 중 checklist에 매핑된 비율
- formula:
  - `coverage_ratio = matched_canonical_kb_units / total_canonical_kb_units`
- current-execution-note:
  - human review 전 heuristic mapping 결과를 사용한다
  - low-confidence mapping도 현재는 분자에 포함된다
- interpretation:
  - canonical unit이 없으면 `n/a`로 본다

## 2. unsupported_item_ratio

- class: `project-custom`
- semantic:
  - checklist item 중 KB 근거를 찾지 못한 비율
- formula:
  - `unsupported_item_ratio = unsupported_checklist_items / total_checklist_items`
- current-execution-note:
  - `scope_inflation`은 현재 `unsupported`와 별도 bucket이라 분자에 포함하지 않는다
- interpretation:
  - scope inflation이 따로 있으면 이 수치만으로 checklist noise를 전부 해석하지 않는다

## 3. traceability_ratio

- class: `proxy-profile`
- semantic:
  - KB 근거를 역참조 가능한 checklist item 비율
- formula:
  - `traceability_ratio = traceable_checklist_items / total_checklist_items`
- current-execution-note:
  - 현재 `traceable`은 strict proof가 아니라 mapping 존재 기준이다
  - low-confidence mapping도 현재는 traceable로 계산된다
- interpretation:
  - report에서는 `candidate traceability coverage`로 읽는 것이 안전하다

## 4. boundary_preservation_ratio

- class: `proxy-profile`
- semantic:
  - guardrail unit이 checklist에서 보존된 비율
- formula:
  - `boundary_preservation_ratio = preserved_guardrails / total_guardrails`
- current-execution-note:
  - 현재 `boundary` 전체가 아니라 heuristic으로 검출된 `guardrail unit`만 분모로 쓴다
- interpretation:
  - 더 정확히는 `guardrail_preservation_ratio`에 가까운 성격이다

## Report Rule

- 이 4개 metric은 단일 truth score가 아니다
- 항상 아래와 함께 본다
  - `kb_profile`
  - `covered`
  - `missing_from_checklist`
  - `unsupported_in_checklist`
  - `scope_inflation`
  - `boundary_loss`
  - `human_review_queue`

## Update Rule

metric 이름 또는 formula를 바꾸려면 순서는 아래다.

1. 이 contract 수정
2. KB/checklist의 interpretation 문구 수정
3. `kb_to_consistency_check.py` 수정
4. baseline diff 재측정
