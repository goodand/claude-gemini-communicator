# Mermaid Safe Authoring Knowledge Base

**역할**: `mermaid-authoring-strategy`의 **core canonical KB**. parser-safe 작성 규칙의 source of truth.
이 KB는 authoring/debugging 축의 guardrail을 정의한다. conversion/tooling 판단은 `graphviz-mermaid-conversion-tools-kb.md`가, 분석 생태계는 `codebase-graph-analysis-tools-kb.md`가 담당한다.

인접리스트 기반 점진적 Mermaid 작성법의 채택된 설계 원칙.

## Source

- 로컬 `mermaid-kb-layer-edge-types-at2026-03-20-11-50.html` 실험 결과
- Mermaid 11.13.0 파서 동작 관찰
- 반복된 `Syntax error in text` 실패 패턴 분석

## Canonical Design Takeaways

### T-1: 인접리스트 선행 원칙

다이어그램을 작성하기 전에 반드시 plain text 인접리스트를 먼저 작성한다.
이유: 관계 유형 분류가 Mermaid 구문 선택보다 선행되어야 한다.

### T-2: 최소 구문 우선 원칙

첫 번째 Mermaid 코드는 `graph TD` + 짧은 노드 ID + `-->` 만 사용한다.
이유: 파서 에러의 80%는 라벨, 스타일, subgraph에서 발생한다. 최소 구문이 렌더되어야 점진 확장이 의미 있다.

### T-3: contains = subgraph membership

`contains` 관계는 Mermaid edge로 표현하지 않고 subgraph 안에 노드를 배치하여 표현한다.
이유: edge로 표현하면 데이터 흐름과 구조적 포함이 시각적으로 구분되지 않는다.

### T-4: 점진적 엣지 타입 추가

엣지 타입(feeds, constrains, escalates_to)은 한 카테고리씩 추가하고 매번 렌더를 확인한다.
이유: 여러 엣지 타입을 동시에 추가하면 실패 원인 특정이 어렵다.

### T-5: 스타일 최후 추가 원칙

`classDef`, `linkStyle`, 색상, 두께 등 스타일은 구조가 완전히 안정된 후에만 추가한다.
이유: `linkStyle` 인덱스는 엣지 선언 순서에 의존하므로, 구조 변경 시 인덱스가 밀린다.

### T-6: 렌더 실패 = 구문 디버깅

렌더 실패 시 스타일을 조정하지 않고, 스타일을 모두 제거한 최소 그래프에서 디버깅을 시작한다.
이유: 스타일 문제와 구문 문제를 동시에 디버깅하면 원인 특정이 불가능하다.

### T-7: 노드 ID 안전 규칙

노드 ID는 영문 대소문자 + 숫자만 사용하며, 2~4자를 권장한다.
이유: 공백, 특수문자, 한국어 ID는 파서 호환성 문제를 일으킨다.

### T-8: 위험 구문 지연 규칙

다음은 최소 그래프가 렌더된 후에만 도입한다:
- 점선 엣지 (`-.->`)
- 굵은 엣지 (`==>`)
- 긴 라벨 (20자 초과)
- 특수문자가 포함된 라벨
- 중첩 subgraph
- `classDef` / `linkStyle`

## Evidence

성공 증거: `mermaid-kb-layer-edge-types-at2026-03-20-11-50.html`
- 6개 subgraph, 14개 노드, 3종 엣지 타입의 복합 그래프
- 인접리스트 선행 → 최소 구문 → 점진 확장 순서로 작성
- Mermaid 11.13.0에서 렌더 성공
