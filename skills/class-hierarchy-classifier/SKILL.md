---
name: class-hierarchy-classifier
description: Analyze and classify class inheritance hierarchies with structure detection. Use when users ask about containment relationships ("Is X also a Y object?"), class structures, inheritance verification, direct parents, MRO analysis, or when multi-inheritance graphs need structure classification. Triggers on "포함관계", "~도 ~객체", "is X also Y", "직계 부모", "direct parent", "issubclass", "class hierarchy", "inheritance", "MRO", "상속", "다중 상속", "inheritance structure".
---

# Class Hierarchy Classifier

Analyze class inheritance with merged common paths, clear branching, direct parent identification, and structure classification.

## 📍 Path Configuration (경로 설정)

### 환경변수 (권장)
```bash
export SKILLS_ROOT="/path/to/your/skills"
# 예: export SKILLS_ROOT="$HOME/.gemini/skills"
# 예: export SKILLS_ROOT="/mnt/skills/user"
```

### 상대경로 사용
스킬 디렉토리에서 실행 시 상대경로 자동 감지:
```bash
cd /path/to/skills/class-hierarchy-classifier/scripts
python hierarchy_classifier.py ...
```

### 스크립트 위치
```
<SKILLS_ROOT>/class-hierarchy-classifier/
├── SKILL.md
├── scripts/
│   └── hierarchy_classifier.py   # 메인 스크립트
└── references/
    ├── examples.md
    ├── BRIDGE_FROM_MAPPER.md
    └── BRIDGE_TO_CLASSIFIER.md
```

---

## Quick Start

```bash
# 스킬 디렉토리로 이동 (상대경로 사용)
cd $SKILLS_ROOT/class-hierarchy-classifier/scripts

# 기본 분석
python hierarchy_classifier.py collections.OrderedDict

# 구조 분류 포함
python hierarchy_classifier.py pandas.DataFrame --classify-structure

# 관계 검증
python hierarchy_classifier.py pandas.DataFrame pandas.core.generic.NDFrame \
    --check DataFrame NDFrame

# Edge 출력 (graph-structure-classifier 연동)
python hierarchy_classifier.py pandas.DataFrame --output-edges
```

---

## 🔗 Pipeline Integration (파이프라인 연동)

### Pipeline Position
```
codebase-architecture-mapper
        │
        └── bridge.py ──► class-hierarchy-classifier ◄── YOU ARE HERE
                                    │
                                    │ --output-edges
                                    ▼
                          graph-structure-classifier
```

### 자동 트리거 조건

LLM은 다음 조건에서 **자동으로** 이 스킬을 사용해야 합니다:

| 조건 | 트리거 | 연동 옵션 |
|------|--------|-----------|
| "상속 구조 분석해줘" | ✅ 즉시 | 기본 실행 |
| "다중 상속인지 확인해줘" | ✅ 즉시 | `--classify-structure` |
| "X가 Y의 서브클래스야?" | ✅ 즉시 | `--check X Y` |
| mapper 출력에 클래스 노드 3개 이상 | ✅ 권장 | bridge.py --analyze |
| INHERITANCE edge 존재 | ✅ 권장 | bridge.py --analyze --classify-structure |

### LLM 자가 판단 가이드

```
사용자 요청 분석:
│
├─ "클래스 구조 보여줘" 
│   → python hierarchy_classifier.py <class>
│
├─ "다중 상속이야?" 
│   → python hierarchy_classifier.py <class> --classify-structure
│   → 결과가 DAG면 다중 상속, Tree면 단일 상속
│
├─ "DataFrame이 NDFrame의 서브클래스야?"
│   → python hierarchy_classifier.py pandas.DataFrame pandas.core.generic.NDFrame --check DataFrame NDFrame
│
├─ "상속 구조가 복잡한지 분석해줘"
│   → python hierarchy_classifier.py <classes> --classify-structure
│   → DAG + multi_parent_nodes 있으면 복잡
│
└─ "graph-structure-classifier로 상세 분석"
    → python hierarchy_classifier.py <class> --output-edges | \
          python ../../graph-structure-classifier/scripts/classifier.py -
```

### 연동 예시

#### From codebase-architecture-mapper
```bash
cd $SKILLS_ROOT/codebase-architecture-mapper/scripts

# mapper 출력을 bridge로 연결
python mapper.py /project --class-nodes > /tmp/arch.json
python bridge.py /tmp/arch.json --analyze --classify-structure --project-root /project
```

#### To graph-structure-classifier
```bash
cd $SKILLS_ROOT/class-hierarchy-classifier/scripts

# 상속 edge 추출 후 구조 분류
python hierarchy_classifier.py pandas.DataFrame --output-edges | \
    python ../../graph-structure-classifier/scripts/classifier.py -
```

---

## Output Interpretation (결과 해석)

### 구조 분류 결과
| 타입 | 의미 | 복잡도 |
|------|------|--------|
| **Tree** | 모든 클래스가 단일 부모 | 낮음 ✅ |
| **DAG** | 일부 클래스가 다중 부모 (다중 상속) | 중간 ⚠️ |
| **DirectedGraph** | 순환 존재 | 높음 ❌ (Python에서 거의 없음) |

### 출력 예시
```
공통 경로:
── object  [DataFrame, Series]
  └─ BaseModel  [DataFrame, Series]

분기:
  [DataFrame] - Multiple Inheritance (2 parents)
    직계 부모 (__bases__): NDFrame, OpsMixin
    
======================================================================
구조 분류 (Structure Classification)
======================================================================
타입: DAG
이유: Multi-parent nodes (다중 상속): ['DataFrame']
======================================================================
```

---

## Virtual Environment 주의사항

프로젝트에 pydantic 등 외부 의존성이 있는 경우:
```bash
# 프로젝트의 venv 사용
/path/to/project/.venv/bin/python hierarchy_classifier.py <class>

# 또는 bridge.py의 --project-root 옵션 사용
python bridge.py arch.json --analyze --project-root /path/to/project
```

---

## References

- **Examples**: `references/examples.md`
- **Bridge from mapper**: `references/BRIDGE_FROM_MAPPER.md`
- **Bridge to classifier**: `references/BRIDGE_TO_CLASSIFIER.md`
