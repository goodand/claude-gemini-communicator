# Bridge: codebase-architecture-mapper → class-hierarchy-classifier

`codebase-architecture-mapper`의 출력에서 클래스 정보를 추출하여 `class-hierarchy-classifier`로 분석합니다.

## Quick Start

```bash
# mapper 출력에서 클래스 추출 → hierarchy 분석
python $SKILLS_ROOT/codebase-architecture-mapper/scripts/bridge.py arch.json --analyze

# 특정 클래스만 분석
python $SKILLS_ROOT/codebase-architecture-mapper/scripts/bridge.py arch.json \
    --classes UserService,BaseRepository --analyze

# 구조 분류 포함
python $SKILLS_ROOT/codebase-architecture-mapper/scripts/bridge.py arch.json \
    --output-specs | python -c "
import json, sys
specs = json.load(sys.stdin)
# hierarchy_classifier로 전달
"
```

## Workflow

```
┌─────────────────────────────────┐
│  codebase-architecture-mapper   │
│  (static analysis)              │
└─────────────────────────────────┘
              │
              │ JSON output (nodes, edges)
              ▼
┌─────────────────────────────────┐
│  bridge.py                      │
│  - Extract class nodes          │
│  - Convert to import paths      │
│  - Build component_specs        │
└─────────────────────────────────┘
              │
              │ component_specs dict
              ▼
┌─────────────────────────────────┐
│  class-hierarchy-classifier     │
│  - Analyze MRO                  │
│  - Detect multi-inheritance     │
│  - Classify structure           │
└─────────────────────────────────┘
```

## bridge.py Output Format

```json
{
  "component_specs": {
    "UserService": "src.auth.user_service.UserService",
    "BaseRepository": "src.db.base.BaseRepository"
  },
  "relationships": [
    ["UserService", "BaseService"],
    ["BaseRepository", "ABC"]
  ],
  "metadata": {
    "source": "codebase-architecture-mapper",
    "total_classes": 15,
    "total_inheritance": 12
  }
}
```

## Python API

```python
from codebase_architecture_mapper.scripts.bridge import ArchitectureBridge

# Load mapper output
with open("arch.json") as f:
    data = json.load(f)

bridge = ArchitectureBridge(data)

# Get specs for hierarchy_classifier
specs = bridge.get_component_specs()

# Run analysis
from class_hierarchy_classifier.scripts.hierarchy_classifier import analyze_hierarchy
analyze_hierarchy(specs, classify=True)
```

## CLI Pipe

```bash
# Full pipeline: mapper → bridge → classifier
python mapper.py /project --class-nodes | \
    python bridge.py - --output-specs | \
    python -c "
import json, sys
sys.path.insert(0, '$SKILLS_ROOT/class-hierarchy-classifier/scripts')
from hierarchy_classifier import analyze_hierarchy
specs = json.load(sys.stdin)
analyze_hierarchy(specs, classify=True)
"
```

## Notes

- `bridge.py`는 `codebase-architecture-mapper/scripts/` 내에 위치
- Import path 변환: `src/auth/user.py::UserService` → `src.auth.user.UserService`
- 프로젝트 루트를 PYTHONPATH에 추가해야 동적 import 가능
