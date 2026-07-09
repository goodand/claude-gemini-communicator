# KB-To-Consistency Coverage Report

- kb: `contract-to-concept-mapper/knowledge_bases/contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md`
- checklist: `contract-to-concept-mapper/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md`
- kb_profile: `research_index_kb`

## Metrics

- coverage_ratio: `n/a`
- unsupported_item_ratio: `0.3`
- traceability_ratio: `0.7`
- boundary_preservation_ratio: `1.0`

## Warnings

- KB canonical unit이 없습니다. 이 결과에서는 coverage_ratio를 해석하지 말고 KB를 canonical takeaway 중심으로 다시 정리해야 합니다.
- 현재 KB profile은 research_index_kb입니다. 이 pair는 reference inventory 중심이므로 canonical KB를 먼저 만든 뒤 checklist와 비교하는 것이 맞습니다.

## Support KB Units

- support: `24`

## Ignored KB Units

- metadata: `8`
- reference_inventory: `98`
- toc: `2`

## missing_from_checklist

- 없음

## unsupported_in_checklist

- codebase 정합성 평가 도구와 직접 동일시되지 않는다
- 벡터 인덱스/벡터 값은 보조 출력으로 취급된다
- 핵심 단계가 `collect contracts -> segment units -> lift concepts -> render concepts`로 유지된다
- render 이전에 relation/boundary 정리가 선행된다
- 외부 검색 자동화 자체가 목적이 아니다
- `semantic-slice-mapper`, `execution-contract-mapper`, `evidence-trace-auditor`와 책임이 구분된다
- 현재는 scaffold 단계라는 점이 분명하다
- future output과 current capability가 혼동되지 않는다
- KB가 넓더라도 현재 v0.1 범위를 별도로 읽어낼 수 있다

## scope_inflation

- 없음

## boundary_loss

- 없음

## Human Review Queue

- low-confidence mapping: key_idea: contract-to-concept 문제는 단순 summarization이 아니라 explainability task라는 점을 뒷받침한다.
- low-confidence mapping: key_idea: 코드/계약과 자연어 설명을 공통 표현 공간에서 다룰 수 있다는 기본 관점을 제공한다.
- low-confidence mapping: execution_conditions: diff나 변경된 contract unit을 입력으로 취급할 수 있어야 함
- low-confidence mapping: execution_conditions: contract artifact를 텍스트나 구조화 표현으로 정규화할 중간 계층 필요
- low-confidence mapping: taxonomy: `[[change_context]] · context-aware description`
- low-confidence mapping: key_idea: AST/path 같은 구조화 입력에서 요약 시퀀스를 생성하는 접근이 contract-to-concept lifting의 기술적 비유가 된다.
- low-confidence mapping: key_idea: 코드에서 상위 모델과 다이어그램을 추출하되 traceability를 유지하는 관점이 핵심이다.
- low-confidence mapping: execution_conditions: contract artifact를 텍스트나 구조화 표현으로 정규화할 중간 계층 필요
- low-confidence mapping: key_idea: 변화 집합에서 상위 설명을 복원하는 방식이 실행 계약 변화나 checklist 변화를 개념 설명으로 올리는 데 유용하다.
- low-confidence mapping: key_idea: 개별 함수/항목이 아니라 project-level context를 넣어야 summary의 의미 왜곡이 줄어든다.
- low-confidence mapping: execution_conditions: 생성 결과와 근거 unit 간 명시적 연결 필요
- low-confidence mapping: execution_conditions: project context 또는 neighboring contract context를 함께 읽어야 함
- low-confidence mapping: execution_conditions: project context 또는 neighboring contract context를 함께 읽어야 함
- low-confidence mapping: key_idea: 코드/계약과 자연어 설명을 공통 표현 공간에서 다룰 수 있다는 기본 관점을 제공한다.
- low-confidence mapping: key_idea: 변화 집합에서 상위 설명을 복원하는 방식이 실행 계약 변화나 checklist 변화를 개념 설명으로 올리는 데 유용하다.
- low-confidence mapping: key_idea: AST/path 같은 구조화 입력에서 요약 시퀀스를 생성하는 접근이 contract-to-concept lifting의 기술적 비유가 된다.

## Metric Metadata

- fixed point: [kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.md](../knowledge_bases/kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.md)
- `coverage_ratio`
  - class: `proxy-profile`
  - formula: `matched_canonical_kb_units / total_canonical_kb_units`
  - interpretation: canonical unit이 없으므로 이 리포트에서는 `n/a`
- `unsupported_item_ratio`
  - class: `project-custom`
  - formula: `unsupported_checklist_items / total_checklist_items`
- `traceability_ratio`
  - class: `proxy-profile`
  - interpretation: strict proof가 아니라 heuristic mapping 존재 기준
- `boundary_preservation_ratio`
  - class: `proxy-profile`
  - interpretation: 현재는 heuristic guardrail unit 기준
- low-confidence mapping: key_idea: 변화 집합에서 상위 설명을 복원하는 방식이 실행 계약 변화나 checklist 변화를 개념 설명으로 올리는 데 유용하다.
- low-confidence mapping: key_idea: AST/path 같은 구조화 입력에서 요약 시퀀스를 생성하는 접근이 contract-to-concept lifting의 기술적 비유가 된다.
