---
name: class-hierarchy-classifier
description: codebase-architecture-mapper family의 class inheritance specialist. 단일 클래스 상속 분석, 다중 상속 여부 확인, issubclass 검증 전용 direct call. 전체 아키텍처 분석은 codebase-architecture-mapper를 사용하라.
---

# Class Hierarchy Classifier

`codebase-architecture-mapper` family의 **class inheritance specialist**.

> **전체 아키텍처 분석이 필요하면 `codebase-architecture-mapper`를 먼저 사용하세요.** 이 skill은 클래스 상속 분석 전용 direct call입니다.

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

### Direct-call 조건

이 specialist를 직접 호출하는 경우:

| 조건 | 사용 | 연동 옵션 |
|------|------|-----------|
| 단일 클래스 상속 구조만 필요 | direct call | 기본 실행 |
| 다중 상속 여부만 확인 | direct call | `--classify-structure` |
| X가 Y의 서브클래스인지 확인 | direct call | `--check X Y` |
| mapper 출력이 이미 있고 후속 분석만 필요 | direct call | bridge.py --analyze |

> **전체 아키텍처 분석**이나 **라우팅 판단**이 필요하면 `codebase-architecture-mapper`가 이 specialist를 자동으로 호출합니다.

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
