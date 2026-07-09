# Paper Search Report — kb-to-consistency-check

## 사용자 의도 파악

- 목표: `knowledge_base -> 정합성 평가용 checklist` 변환을 어떻게 평가할지에 대한 학술적 기준을 찾는다.
- 초점:
  - requirements traceability
  - coverage / completeness
  - human-vetted candidate matrix
  - structured artifact links

## Shortlist

### 1. Automated Requirements Traceability: The Study of Human Analysts
- URL: https://digitalcommons.calpoly.edu/theses/317/
- 선택 이유:
  - traceability matrix는 자동 생성 후에도 사람이 vetting해야 한다는 점을 명확히 보여준다
  - `kb_to_consistency_check.py`는 “완전 자동 판정기”보다 candidate inconsistency detector로 보는 편이 맞다

### 2. Automating Requirements Traceability: Two Decades of Learning from KDD
- URL: https://ieeexplore.ieee.org/document/8595127
- 선택 이유:
  - 요구사항 traceability를 precision/recall 중심으로 보되, 실제 사용은 human-in-the-loop로 닫아야 함을 보여준다
  - KB-checklist 정합성도 `coverage`와 `unsupported item`의 균형 문제로 볼 수 있다

### 3. Traceability Matrix in Requirements Gathering: A Systematic Review of the Literature
- URL: https://perspectivas.espoch.edu.ec/RCP_ESPOCH/en/article/view/221
- 선택 이유:
  - standardized traceability matrix 부재가 completeness / consistency 문제를 낳는다고 정리한다
  - checklist 항목 구조와 traceability 필드 표준화의 필요성 근거가 된다

### 4. Blockchain Technology for Requirement Traceability in Systems Engineering
- URL: https://www.sciencedirect.com/science/article/abs/pii/S0306437924000425
- 선택 이유:
  - dual-level traceability(artifact level / object level)를 구분한다
  - `knowledge_base 전체`와 `KB unit`을 따로 보는 설계에 참고가 된다

### 5. StrictDoc SRS Traceability Template
- URL: https://strictdoc-project.github.io/strictdoc-templates/strictdoc-templates/templates/ECSS-E-ST-40C/TS/SRS-TRACE.html
- 선택 이유:
  - requirement마다 고유 id와 상위 문서 유래 정보를 남기는 방식이 명시돼 있다
  - checklist 항목도 `derived_from` 또는 동등 필드를 가져야 한다는 근거가 된다

## Design Takeaways

- `kb_to_consistency_check.py`는 checklist의 “정답 여부”를 완전히 판정하기보다,
  **candidate traceability gaps**를 보고하는 도구로 잡는 것이 더 타당하다.
- 최소 측정 축은 아래 5개가 적절하다.
  - `coverage`: KB canonical unit 중 checklist에 반영된 비율
  - `unsupported_item_rate`: checklist 항목 중 KB 근거가 빈약한 비율
  - `traceability_presence`: checklist 항목이 KB unit을 역참조하는 비율
  - `boundary_preservation`: KB의 non-goal / guardrail이 checklist에 유지되는지
  - `scope_inflation`: checklist가 KB보다 더 큰 요구를 새로 만들었는지
- precision/recall 비유를 적용하면:
  - `coverage`는 recall 쪽
  - `unsupported_item_rate`는 precision 반대 축
- 따라서 출력도 score 1개보다 아래 형태가 더 낫다.
  - per-unit table
  - summary metrics
  - human review needed items

## Reject / Hold

- pure summarization 논문은 KB-checklist 정합성의 핵심인 traceability를 잘 다루지 못한다.
- requirement traceability 연구를 그대로 복사하는 것도 과하다.
  현재는 project-scale RM tool이 아니라 skill-level KB-checklist checker가 목적이다.
