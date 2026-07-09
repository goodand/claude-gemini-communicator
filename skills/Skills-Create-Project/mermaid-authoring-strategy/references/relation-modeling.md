# Mermaid Relation Modeling

관계 유형별 Mermaid 표현 가이드. 인접리스트에서 Mermaid 엣지로의 변환 규칙.

## 4가지 관계 유형

### 1. contains (구조적 포함)

**Mermaid 표현: subgraph membership**

`contains`는 edge가 아니다. subgraph 안에 노드를 배치하여 표현한다.

```
인접리스트:
  Paper KB contains Identity
  Paper KB contains Guardrail

Mermaid:
  subgraph PKG[Paper KB]
      ID[Identity]
      GR[Guardrail]
  end
```

왜 edge로 쓰지 않는가:
- `Paper KB --> Identity` 는 "포함"이 아니라 "데이터 흐름"처럼 보인다
- subgraph는 시각적으로 소속 관계를 명확하게 표현한다
- Mermaid 레이아웃 엔진이 subgraph 내 노드를 자연스럽게 묶어준다

### 2. feeds (데이터 흐름)

**Mermaid 표현: 실선 화살표 + 라벨**

```
A -->|feeds| B
```

의미: A가 B에게 입력을 공급한다.
시각: 굵은 실선 (기본 `-->` 또는 `==>`)

### 3. constrains (제약)

**Mermaid 표현: 점선 화살표 + 라벨**

```
A -.->|constrains| B
```

의미: A가 B의 행동 범위를 제한한다.
시각: 점선으로 제약의 비직접적 성격을 표현.

주의: 점선 엣지는 최소 그래프가 렌더된 후에 추가한다. `-.->` 구문은 `-->` 보다 파서 실패 확률이 약간 높다.

### 4. escalates_to (에스컬레이션)

**Mermaid 표현: 점선 굵은 화살표 + 라벨**

```
A -.->|escalates_to| B
```

의미: 자동 처리 한계를 넘겨 HITL(Human-in-the-loop)로 올린다.
시각: 점선 + 별도 색상 (linkStyle로 마지막에 추가).

## 변환 순서

1. 인접리스트에서 `contains`를 분리 → subgraph로 변환
2. 나머지 관계(`feeds`, `constrains`, `escalates_to`)를 `-->` 로 먼저 작성
3. 렌더 확인
4. `feeds`에 `-->|feeds|` 라벨 추가
5. 렌더 확인
6. `constrains`를 `-.->|constrains|` 로 변경
7. 렌더 확인
8. `escalates_to`를 `-.->|escalates_to|` 로 변경
9. 렌더 확인
10. 스타일(색상, 굵기) 추가

## 엣지 타입 요약

| 관계 | Mermaid 표현 | 추가 시점 |
|---|---|---|
| contains | `subgraph` membership | Step 5 (subgraph 단계) |
| feeds | `-->\|feeds\|` | Step 4 (엣지 라벨 단계) |
| constrains | `-.->\|constrains\|` | Step 4 이후 (렌더 확인 후) |
| escalates_to | `-.->\|escalates_to\|` | Step 4 이후 (렌더 확인 후) |
