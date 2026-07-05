# Skills Bridge Integration Guide

## Overview

이 문서는 depsolve-analyzer와 codebase-architecture-mapper를 연결하는 브릿지 시스템의 사용법을 설명합니다.

### Reference-only dependency graph links

새 스크립트를 추가하지 않고, mixed repo dependency graph 분석은 아래 reference를 따른다.

- `analyze_dependency_graph` 계약: [ANALYZE_DEPENDENCY_GRAPH_CONTRACT_2026-03-18-21-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/references/ANALYZE_DEPENDENCY_GRAPH_CONTRACT_2026-03-18-21-22.md)
- MECE subagent fan-in: [MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/references/MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md)
- 현재 방침: 위 둘은 구현 스크립트가 아니라 reference contract다. 기존 `depsolve-analyzer`, `codebase-architecture-mapper`, `graph-structure-classifier`를 조합해 사용한다.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Skills Integration Architecture                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│  │   depsolve   │◀───────▶│    Bridge    │◀───────▶│    mapper    │        │
│  │   analyzer   │         │    Layer     │         │              │        │
│  └──────┬───────┘         └──────┬───────┘         └──────┬───────┘        │
│         │                        │                        │                │
│         │ edge-list              │ import-map             │ edge-list      │
│         │ import-map             │ tagged-edges           │ class-nodes    │
│         ▼                        ▼                        ▼                │
│  ┌──────────────┐         ┌──────────────┐         ┌──────────────┐        │
│  │    graph     │         │ orchestrator │         │   hierarchy  │        │
│  │  classifier  │         │   (unified)  │         │  classifier  │        │
│  └──────────────┘         └──────────────┘         └──────────────┘        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Bridge 1: Dependency-Module Mapper

### Purpose
Package-level 의존성(depsolve)과 Module-level 코드(mapper) 사이의 간극을 메움

### Features
1. **Phantom 패키지 추적**: phantom이 어떤 소스 파일에서 import되는지 매핑
2. **Import 안정성 검사**: 모듈이 참조하는 외부 라이브러리의 설치 상태 확인
3. **External/Internal 분류**: 의존성을 외부 라이브러리와 내부 모듈로 분류

### Usage

```bash
# Basic: 두 분석 결과 결합
python depsolve_mapper_bridge.py --depsolve analysis.json --mapper arch.json

# Pipeline: stdin으로 depsolve 결과 받기
python -m depsolve_ext analyze /project --format json | \
    python depsolve_mapper_bridge.py --mapper arch.json -

# Full analysis: 프로젝트 경로만으로 통합 분석
python depsolve_mapper_bridge.py --project /path/to/project --full-analysis

# Output formats
python depsolve_mapper_bridge.py ... --format json      # 기본
python depsolve_mapper_bridge.py ... --format markdown  # 리포트
python depsolve_mapper_bridge.py ... --format mermaid   # 시각화
```

### Output Example

```json
{
  "summary": {
    "total_phantoms": 3,
    "files_with_phantoms": 5,
    "avg_stability": 0.85
  },
  "phantom_mappings": [
    {
      "package": "axios",
      "ecosystem": "javascript",
      "status": "PHANTOM",
      "used_in": ["src/api/client.ts", "src/utils/http.ts"],
      "usage_count": 2
    }
  ],
  "stability_report": [
    {
      "source_file": "src/api/client.ts",
      "stability_score": 0.75,
      "stable_imports": 3,
      "unstable_imports": 1
    }
  ]
}
```

---

## Bridge 2: Integrated Codebase Orchestrator

### Purpose
모든 스킬을 순차 실행하여 "구조-의존성-위험요소" 통합 리포트 생성

### Pipeline Steps

| Step | Tool | Output | Purpose |
|------|------|--------|---------|
| 1 | mapper | nodes, edges | 모듈 그래프 추출 |
| 2 | depsolve | issues | 패키지 문제 탐지 |
| 3 | classifier | structure_type | DAG/Cyclic 판별 |
| 4 | bridge | phantom_mappings | 상호 보완 분석 |
| 5 | report | markdown | 통합 리포트 |

### Usage

```bash
# Full pipeline (markdown report)
python codebase_orchestrator.py /path/to/project

# JSON output for programmatic use
python codebase_orchestrator.py /project --format json

# Save to file
python codebase_orchestrator.py /project -o analysis_report.md

# Skip specific steps
python codebase_orchestrator.py /project --skip-classifier
python codebase_orchestrator.py /project --skip-depsolve --skip-bridge
```

### Health Score

Orchestrator는 프로젝트 건전성 점수(0-100)를 계산합니다:

| Factor | Deduction | Condition |
|--------|-----------|-----------|
| Circular Dependency | -30 | 순환 의존성 발견 |
| Phantom Dependencies | -5 each | phantom 패키지 발견 |
| Import Instability | -20 | stability < 80% |
| High Coupling | -10 | edge density > 5 |

---

## Depsolve Bridge Extensions

### New Output Formats

depsolve-analyzer에 브릿지 연동용 출력 포맷 추가

#### edge-list (for graph-structure-classifier)

```bash
# depsolve 결과를 edge-list로 변환
python depsolve_bridge_ext.py analysis.json --format edge-list

# 파이프라인: depsolve → classifier
python -m depsolve_ext analyze /project --format json | \
    python depsolve_bridge_ext.py - --format edge-list | \
    python classifier.py -
```

Output:
```json
[["lodash", "express"], ["express", "body-parser"]]
```

#### import-map (패키지별 위치 정보)

```bash
python depsolve_bridge_ext.py analysis.json --format import-map
```

Output:
```json
{
  "metadata": {
    "project": "/path/to/project",
    "ecosystem": "npm",
    "total_packages": 5,
    "phantom_count": 2
  },
  "packages": [
    {
      "package": "axios",
      "ecosystem": "javascript",
      "is_phantom": true,
      "usage_count": 3,
      "locations": [
        {"file": "src/api/client.ts", "line": 5, "context": "source"},
        {"file": "src/utils/http.ts", "line": 2, "context": "source"}
      ]
    }
  ]
}
```

---

## Mapper Edge Tagging

### External/Internal Classification

mapper의 edge에 타겟 타입 태그 추가:

```bash
python depsolve_bridge_ext.py analysis.json --format tagged-mapper --mapper arch.json
```

태그 유형:
- `internal`: 프로젝트 내부 모듈
- `internal_relative`: 상대 경로 import
- `external_declared`: manifest에 선언된 외부 패키지
- `external_unknown`: 미선언 외부 패키지 (stdlib 포함)

---

## Complete Pipeline Examples

### Example 1: NPM Project Analysis

```bash
cd /path/to/npm-project

# 1. mapper 실행
python $SKILLS_ROOT/codebase-architecture-mapper/scripts/mapper.py . > /tmp/arch.json

# 2. depsolve 실행
python -m depsolve_ext analyze . --format json > /tmp/deps.json

# 3. bridge로 결합
python depsolve_mapper_bridge.py --depsolve /tmp/deps.json --mapper /tmp/arch.json --format markdown

# 또는 한 번에:
python codebase_orchestrator.py . -o report.md
```

### Example 2: Hybrid (JS + Python) Project

```bash
# Orchestrator가 자동으로 두 생태계 분석
python codebase_orchestrator.py /hybrid-project --format markdown
```

### Example 3: CI/CD Integration

```yaml
# .github/workflows/analyze.yml
- name: Run Codebase Analysis
  run: |
    python codebase_orchestrator.py . --format json -o analysis.json
    
    # Health score 체크
    HEALTH=$(jq '.insights.health_score' analysis.json)
    if [ "$HEALTH" -lt 60 ]; then
      echo "Health score too low: $HEALTH"
      exit 1
    fi
```

---

## Trigger Conditions for LLM

LLM은 다음 조건에서 자동으로 브릿지를 사용해야 합니다:

| User Request | Bridge to Use |
|--------------|---------------|
| "phantom이 어디서 쓰이는지 알려줘" | depsolve_mapper_bridge |
| "전체 코드베이스 분석해줘" | codebase_orchestrator |
| "의존성 문제와 코드 구조를 함께 봐줘" | codebase_orchestrator |
| "패키지별 import 위치 알려줘" | depsolve_bridge_ext --format import-map |
| "외부/내부 의존성 분류해줘" | depsolve_bridge_ext --format tagged-mapper |

---

## File Structure

```
bridges/
├── depsolve_mapper_bridge.py     # Bridge 1: Phantom-Source 매핑
├── codebase_orchestrator.py      # Bridge 2: 통합 파이프라인
├── depsolve_bridge_ext.py        # depsolve 출력 포맷 확장
└── BRIDGE_INTEGRATION.md         # 이 문서

skills/
├── depsolve-analyzer/
│   └── scripts/
│       └── depsolve_ext/         # 코어 분석기
├── codebase-architecture-mapper/
│   └── scripts/
│       ├── mapper.py             # 모듈 그래프 추출
│       └── bridge.py             # 기존 hierarchy bridge
└── graph-structure-classifier/
    └── scripts/
        └── classifier.py         # DAG/Cyclic 분류
```
