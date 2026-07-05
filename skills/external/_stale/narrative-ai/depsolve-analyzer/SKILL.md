---
name: depsolve-analyzer
description: codebase-architecture-mapper family의 dependency analysis specialist. 패키지 매니저/manifest 기반 phantom, circular, diamond 의존성 탐지 전용 direct call. 전체 아키텍처 분석은 codebase-architecture-mapper를 사용하라.
---

# depsolve-analyzer

`codebase-architecture-mapper` family의 **dependency analysis specialist**.

> **전체 아키텍처 분석이 필요하면 `codebase-architecture-mapper`를 먼저 사용하세요.** 이 skill은 패키지 의존성 분석 전용 direct call입니다.

Phantom 의존성 탐지 및 의존성 그래프 분석 도구.

## When to use directly

패키지 매니저/manifest 기반 의존성 분석만 필요할 때 직접 호출:
- phantom / undeclared dependency 탐지
- circular / diamond dependency 탐지
- package.json / requirements.txt / go.mod / Cargo.toml 검증
- 단일 파일 import 추출

## Do not use for

- **전체 아키텍처 분석** → `codebase-architecture-mapper`
- **클래스 상속 구조** → `class-hierarchy-classifier`
- **generic 그래프 구조 분류만** → `graph-structure-classifier`

## 빠른 시작

```bash
# 의존성 전체 분석
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

## 지원 생태계

- **JavaScript**: package.json, node_modules
- **Python**: requirements.txt, pyproject.toml
- **Go**: go.mod (파싱만)
- **Rust**: Cargo.toml (파싱만)

## 출력 형식

`--format` 옵션: `console` (기본), `json`, `markdown`

JSON 출력 구조 → [API_REFERENCE.md](references/API_REFERENCE.md)

## 브릿지 통합

다른 스킬과 연동 시 → [BRIDGE_INTEGRATION.md](references/BRIDGE_INTEGRATION.md)

| 연동 대상 | 브릿지 | 용도 |
|:----------|:-------|:-----|
| codebase-architecture-mapper | depsolve_mapper_bridge.py | Phantom-소스 매핑 |
| graph-structure-classifier | depsolve_bridge_ext.py | 그래프 구조 분류 |
| 전체 파이프라인 | codebase_orchestrator.py | 통합 분석 |

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
