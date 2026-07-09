---
name: graph-structure-classifier
description: Use when determining if a dependency graph is Tree/DAG/cyclic, detecting cycles in import graphs, checking data flow structure, preparing graph data for LLM context injection. Triggers on "구조 분류", "cycle detection", "순환 탐지", "DAG 판별", "tree 검사", "그래프 구조", "dependency graph", "topological sort", "is this a tree", "acyclic check".
---

# Graph Structure Classifier

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

### 자동 트리거 조건

LLM은 다음 조건에서 **자동으로** 이 스킬을 사용해야 합니다:

| 조건 | 트리거 | 분석 목적 |
|------|--------|-----------|
| "순환 의존성 확인" 요청 | ✅ 즉시 | Cycle detection |
| mapper 출력에 edge 10개 이상 | ✅ 권장 | 복잡한 구조 분류 |
| class-hierarchy에서 다중 상속 감지 | ✅ 권장 | DAG 상세 분석 |
| "구조가 Tree인지 확인" 요청 | ✅ 즉시 | 구조 검증 |
| "아키텍처 건전성 검증" 요청 | ✅ 즉시 | Acyclic 확인 |

### LLM 자가 판단 가이드

```
그래프 구조 관련 질문:
│
├─ "순환 있어?" 
│   → python classifier.py edges.json
│   → has_cycle 확인
│
├─ "Tree야 DAG야?" 
│   → python classifier.py edges.json
│   → structure_type 확인
│
├─ "다중 상속 있어?" 
│   → python ../../class-hierarchy-classifier/scripts/hierarchy_classifier.py <class> --output-edges | \
│         python classifier.py -
│   → multi_parent_nodes 확인
│
└─ "구조적으로 안전해?" 
    → Tree/DAG = 안전 (acyclic)
    → DirectedGraph = 순환 존재, 검토 필요
```

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
