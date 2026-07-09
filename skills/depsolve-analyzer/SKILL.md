---
name: depsolve-analyzer
description: Analyze project dependencies to detect phantom dependencies, circular dependencies, diamond dependencies, manifest drift, wrapper indirection, and mixed-repo boundary risks. Use when analyzing npm/pip/Go/Rust projects, auditing hybrid JS+Python repositories, generating Mermaid dependency graphs, or running MECE multi-subagent dependency analysis.
---

# depsolve-analyzer

Phantom 의존성, 순환 의존성, 다이아몬드 의존성, mixed-repo boundary drift를 분석하는 메인 dependency skill.

## 트리거

다음 키워드가 포함된 요청 시 사용:
- "phantom", "팬텀", "유령 의존성"
- "의존성 분석", "dependency analysis"
- "순환 의존성", "circular dependency"
- "다이아몬드 의존성", "diamond dependency"
- "manifest drift", "package boundary"
- "import graph", "dependency graph"
- "hybrid JS+Python", "mixed repo"

## 빠른 시작

```bash
# 전체 분석
python $SKILL_PATH/scripts/run_depsolve.py analyze /project

# JSON 출력
python $SKILL_PATH/scripts/run_depsolve.py analyze /project --format json

# Phantom만 탐지
python $SKILL_PATH/scripts/run_depsolve.py phantoms /project --verify
```

## 핵심 기능

| 기능 | 명령어 | 심각도 |
|:-----|:-------|:------:|
| Phantom 탐지 | `analyze`, `phantoms` | HIGH |
| 순환 의존성 | `analyze`, `graph` | HIGH |
| 다이아몬드 | `analyze`, `graph` | MEDIUM |
| Import 추출 | `imports <file>` | - |
| Mixed repo graph synthesis | `analyze_dependency_graph` contract | HIGH |

## 지원 생태계

- **JavaScript**: package.json, node_modules
- **Python**: requirements.txt, pyproject.toml
- **Go**: go.mod (파싱만)
- **Rust**: Cargo.toml (파싱만)
- **Mixed repo**: package graph + source graph + wrapper/path mutation synthesis

## 출력 형식

`--format` 옵션: `console` (기본), `json`, `markdown`

JSON 출력 구조 → [API_REFERENCE.md](references/API_REFERENCE.md)

## 하위 계약

### `analyze_dependency_graph`
의존성 그래프를 mixed codebase 기준으로 MECE하게 추출/정리하는 하위 계약.

현재 방침:
- 새 전용 스크립트를 추가하지 않는다
- 아래 문서는 reference-only contract로 유지한다
- 기존 `depsolve-analyzer`, `codebase-architecture-mapper`, `graph-structure-classifier`를 조합해 수행한다

참고:
- [ANALYZE_DEPENDENCY_GRAPH_CONTRACT_2026-03-18-21-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/references/ANALYZE_DEPENDENCY_GRAPH_CONTRACT_2026-03-18-21-22.md)
- [MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/references/MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md)

## 브릿지 통합

다른 스킬과 연동 시 → [BRIDGE_INTEGRATION.md](references/BRIDGE_INTEGRATION.md)

| 연동 대상 | 브릿지 | 용도 |
|:----------|:-------|:-----|
| codebase-architecture-mapper | depsolve_mapper_bridge.py | Phantom-소스 매핑 |
| graph-structure-classifier | depsolve_bridge_ext.py | 그래프 구조 분류 |
| 전체 파이프라인 | codebase_orchestrator.py | 통합 분석 |
| subagent fan-in | MECE subagent fan-in reference | graph/risk/slice 합성 |

## CLI 옵션

```
analyze <path>     전체 분석
  --verify, -v     런타임 검증
  --verbose        상세 출력
  --format, -f     출력 형식
  --no-dev         devDependencies 제외

phantoms <path>    Phantom만 탐지
graph <path>       그래프 분석 (--mermaid)
imports <file>     파일 import 추출
```

## Notes

- `dependency-graph-analyzer`는 active skill에서 제외됐다. graph analysis는 이 skill의 하위 계약으로 통합한다.
- `dependency-risk-auditor`는 top-level skill이 아니라 optional subagent 역할로 둔다.
- mixed repo에서는 manifest graph와 source import graph를 먼저 분리하고, 그 뒤 wrapper/path-mutation layer를 합친다.
