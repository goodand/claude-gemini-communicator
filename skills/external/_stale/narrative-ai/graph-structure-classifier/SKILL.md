---
name: graph-structure-classifier
description: codebase-architecture-mapper family의 graph structure specialist. Edge list의 Tree/DAG/cyclic 구조 분류 전용 direct call. 전체 아키텍처 분석은 codebase-architecture-mapper를 사용하라.
---

# Graph Structure Classifier

`codebase-architecture-mapper` family의 **graph structure specialist**.

> **전체 아키텍처 분석이 필요하면 `codebase-architecture-mapper`를 먼저 사용하세요.** 이 skill은 그래프 구조 분류 전용 direct call입니다.

Classify directed graphs: Tree → DAG → MultiEdgeDAG → DirectedGraph (Waterfall algorithm).

## 📍 Path Configuration (경로 설정)

### 환경변수 (권장)
```bash
export SKILLS_ROOT="/path/to/your/skills"
# 예: export SKILLS_ROOT="$HOME/.gemini/skills"
# 예: export SKILLS_ROOT="/mnt/skills/user"
```

### 스크립트 위치
```
<SKILLS_ROOT>/graph-structure-classifier/
├── SKILL.md
├── scripts/
│   ├── classifier.py         # 메인 분류 스크립트
│   └── graphml_formatter.py  # GraphML 출력 포맷터
└── references/
    ├── api_reference.md
    ├── examples.md
    └── BRIDGE_FROM_HIERARCHY.md
```

---

## Quick Start

```bash
cd $SKILLS_ROOT/graph-structure-classifier/scripts

# JSON 파일 입력
python classifier.py edges.json

# stdin 입력
echo '[["A","B"],["B","C"],["C","A"]]' | python classifier.py -

# 출력 형식 지정
python classifier.py edges.json --format mermaid   # 시각화
python classifier.py edges.json --format graphml  # LLM context
```

---

## Structure Types

| Structure | Cycle | In-degree | Roots | Example |
|-----------|-------|-----------|-------|---------|
| **Tree** | ✗ | ≤1 | 1, connected | File system, 단일 상속 |
| **DAG** | ✗ | any | any | Build system, 다중 상속 |
| **MultiEdgeDAG** | ✗ | any (dupes) | any | Weighted deps |
| **DirectedGraph** | ✓ | any | any | State machine, 순환 참조 |

---

## 🔗 Pipeline Integration (파이프라인 연동)

### Pipeline Position
```
codebase-architecture-mapper ──► graph-structure-classifier ◄── YOU ARE HERE
                                        ▲
class-hierarchy-classifier ─────────────┘
        (--output-edges)
```

### Direct-call 조건

이 specialist를 직접 호출하는 경우:

| 조건 | 사용 | 분석 목적 |
|------|------|-----------|
| edge list가 이미 있고 구조 분류만 필요 | direct call | Tree/DAG/cyclic 판별 |
| 단일 순환 의존성 확인만 필요 | direct call | Cycle detection |
| class-hierarchy 출력에서 후속 분류만 필요 | direct call | DAG 상세 분석 |

> **전체 아키텍처 분석**이나 **라우팅 판단**이 필요하면 `codebase-architecture-mapper`가 이 specialist를 자동으로 호출합니다.

### 연동 예시

#### From codebase-architecture-mapper
```bash
cd $SKILLS_ROOT/codebase-architecture-mapper/scripts

# 모듈 의존성 구조 분류
python mapper.py /project --format edge-list | \
    python ../graph-structure-classifier/scripts/classifier.py -
```

#### From class-hierarchy-classifier
```bash
cd $SKILLS_ROOT/class-hierarchy-classifier/scripts

# 클래스 상속 구조 분류
python hierarchy_classifier.py pandas.DataFrame --output-edges | \
    python ../graph-structure-classifier/scripts/classifier.py -
```

---

## Output Interpretation (결과 해석)

```json
{
  "structure_type": "DAG",
  "reason": "Multi-parent nodes: ['DataFrame']",
  "stats": {
    "has_cycle": false,        // 순환 없음 = 안전
    "max_in_degree": 2         // 다중 상속 존재
  },
  "details": {
    "multi_parent_nodes": ["DataFrame"],  // 다중 상속 클래스
    "root_nodes": ["object"]              // 루트 노드
  }
}
```

**해석:**
- `Tree` + `has_cycle: false` → 가장 단순하고 안전한 구조
- `DAG` + `multi_parent_nodes` 있음 → 다중 상속 존재, 복잡도 중간
- `DirectedGraph` + `has_cycle: true` → 순환 참조, 리팩토링 권장

---

## Input Formats

```json
// Array of arrays
[["A", "B"], ["B", "C"]]

// Array of objects
[{"source": "A", "target": "B"}]
```

---

## References

- **API details**: `references/api_reference.md`
- **Examples**: `references/examples.md`
- **Bridge from hierarchy**: `references/BRIDGE_FROM_HIERARCHY.md`
