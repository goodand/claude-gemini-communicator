# Mermaid Authoring Strategy Consistency Checklist

4축 전략(authoring, debugging, relation modeling, conversion/tooling) 기반 정합성 평가 항목.
parser-safe rules만이 아니라 전략 전체의 습관을 평가한다.

## Source of Truth

`knowledge_bases/mermaid-safe-authoring-kb.md` — Core Canonical KB (T-1~T-8)
`knowledge_bases/graphviz-mermaid-conversion-tools-kb.md` — Conversion/Tooling Strategy (T-G1~T-G5)

## 축 1: Authoring Strategy

- [ ] **C-01**: 인접리스트가 Mermaid 코드보다 먼저 작성되었는가? (T-1)
- [ ] **C-02**: 첫 번째 Mermaid 코드가 `graph TD` + 짧은 ID + `-->` 만 사용하는가? (T-2)
- [ ] **C-03**: 엣지 타입이 한 카테고리씩 추가되었는가? (T-4)
- [ ] **C-04**: `classDef`/`linkStyle`이 구조 확정 후에만 추가되었는가? (T-5)

## 축 2: Debugging Strategy

- [ ] **C-05**: 렌더 실패 시 스타일 제거를 먼저 시도했는가? (T-6)
- [ ] **C-06**: 점선/굵은 엣지가 최소 그래프 렌더 후에 추가되었는가? (T-8)
- [ ] **C-07**: `linkStyle` 인덱스가 현재 엣지 순서와 일치하는가? (T-5)
- [ ] **C-08**: 디버깅이 "스타일 조정"이 아닌 "구문 축소/격리"로 시작했는가? (T-6)

## 축 3: Relation Modeling

- [ ] **C-09**: `contains` 관계가 edge가 아닌 subgraph membership으로 표현되었는가? (T-3)
- [ ] **C-10**: 모든 `subgraph`에 `end`가 있는가?
- [ ] **C-11**: 한 노드가 하나의 subgraph에만 소속되는가?
- [ ] **C-12**: feeds/constrains/escalates_to가 edge로 유지되고 각각 구분 가능한가?

## 축 4: Conversion/Tooling Judgment

- [ ] **C-13**: 변환 도구(dot2mermaid 등)의 출력을 그대로 쓰지 않고 재검증했는가? (T-G4)
- [ ] **C-14**: 도구 선택을 늦추고, 직접 Mermaid 작성이 먼저 시도되었는가? (T-G5)
- [ ] **C-15**: IR 기반 도구와 직접 변환 도구의 선택 근거가 명시되었는가? (T-G3)

## 구문 안전성 (Core Guardrail)

- [ ] **C-16**: 노드 ID가 영문+숫자만 사용하는가? (T-7)
- [ ] **C-17**: 노드 라벨이 20자 이하인가?
- [ ] **C-18**: 엣지 라벨이 15자 이하인가?
- [ ] **C-19**: 라벨에 `/`, `()`, `[]`, `|` 등 위험 문자가 없는가?
