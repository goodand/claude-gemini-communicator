# Pipeline Integration Guide

## Skill Ecosystem

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Architecture Analysis Pipeline                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────┐                                           │
│  │ codebase-           │                                           │
│  │ architecture-mapper │ ◄── 정적 분석 (Static)                    │
│  └──────────┬──────────┘                                           │
│             │                                                       │
│             │ edge_list / JSON                                      │
│             │                                                       │
│  ┌──────────┼──────────┬──────────────────┐                        │
│  ▼          ▼          ▼                  ▼                        │
│ ┌────────┐ ┌────────┐ ┌────────┐  ┌──────────────┐                │
│ │graph-  │ │context │ │bridge  │  │(future)      │                │
│ │struct- │ │_gener- │ │.py     │  │runtime-flow- │                │
│ │ure-    │ │ator.py │ │        │  │tracer        │                │
│ │classi- │ │        │ │        │  │              │                │
│ │fier    │ │        │ │        │  │              │                │
│ └────┬───┘ └────┬───┘ └────┬───┘  └──────────────┘                │
│      │          │          │                                       │
│      ▼          ▼          ▼                                       │
│  Structure   PROJECT_   class-                                     │
│  Type        ARCH.md    hierarchy-                                 │
│  (DAG/Tree)             visualizer                                 │
│                         (MRO 검증)                                  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Integration Patterns

### Pattern 1: Structure Classification

**Use Case**: "이 프로젝트가 Tree인지 DAG인지 알려줘"

```bash
python mapper.py /project --format edge-list | python classifier.py -
```

**Output**:
```json
{
  "structure_type": "MultiEdgeDAG",
  "has_cycle": false,
  "reason": "Multi-parent nodes exist"
}
```

**Trigger Keywords**: "구조 판별", "DAG", "Tree", "cycle", "순환"

---

### Pattern 2: LLM Context Document

**Use Case**: "이 프로젝트 아키텍처 문서 만들어줘"

```bash
python mapper.py /project --class-nodes --package-level | \
  python context_generator.py - -o PROJECT_ARCHITECTURE.md
```

**Output**: Structured markdown with:
- Layer-based node organization
- Hub/Connector analysis
- Critical paths
- Mermaid diagram

**Trigger Keywords**: "아키텍처 문서", "PROJECT_ARCHITECTURE", "LLM 컨텍스트"

---

### Pattern 3: Inheritance Verification

**Use Case**: "상속 관계 맞는지 확인해줘"

```bash
python mapper.py /project --class-nodes | \
  python bridge.py - --verify-all --project-root /project
```

**Output**:
```
✓ Yes, LoginService IS a subclass of BaseAuth
  경로 (MRO): BaseAuth → LoginService
```

**Trigger Keywords**: "상속 확인", "MRO", "issubclass", "포함관계"

---

### Pattern 4: Full Analysis Pipeline

**Use Case**: "프로젝트 전체 분석해줘"

```bash
# Step 1: Extract architecture
python mapper.py /project --class-nodes --package-level -o arch.json

# Step 2: Classify structure
python mapper.py /project --format edge-list | python classifier.py -

# Step 3: Generate documentation
python context_generator.py arch.json -o PROJECT_ARCHITECTURE.md

# Step 4: Verify inheritance (optional)
python bridge.py arch.json --verify-all --project-root /project
```

---

## Skill Synergy Matrix

| Mapper Output | Connected Skill | Synergy |
|---------------|-----------------|---------|
| `--format edge-list` | graph-structure-classifier | ⭐⭐⭐⭐⭐ |
| `--class-nodes` JSON | bridge.py → class-hierarchy-visualizer | ⭐⭐⭐⭐ |
| Full JSON | context_generator.py | ⭐⭐⭐⭐⭐ |
| `--format graphml` | External graph tools | ⭐⭐⭐ |
| `--format mermaid` | Documentation rendering | ⭐⭐⭐ |

---

## Trigger Routing

When user says... → Route to:

| User Query | Primary Skill | Secondary |
|------------|---------------|-----------|
| "의존성 분석" | codebase-architecture-mapper | - |
| "구조가 DAG인지" | graph-structure-classifier | mapper (data source) |
| "아키텍처 문서" | mapper + context_generator | - |
| "상속 관계 확인" | mapper + bridge | class-hierarchy-visualizer |
| "순환 의존성" | mapper + classifier | - |
| "hub 모듈" | mapper (analysis section) | - |

---

## Error Handling

### Common Integration Errors

**Error**: `classifier.py: Invalid input format`
**Cause**: Using JSON instead of edge-list
**Fix**: Add `--format edge-list`

**Error**: `bridge.py: Cannot import class`
**Cause**: Missing --project-root
**Fix**: Add `--project-root /path/to/project`

**Error**: `context_generator: No analysis section`
**Cause**: Using minimal output
**Fix**: Remove `--no-layers` flag
