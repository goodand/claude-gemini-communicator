---
name: codebase-architecture-mapper
description: Architecture analysis family의 workflow owner. Multi-concern 아키텍처 분석, specialist 라우팅, LLM context 문서 생성 전용. Single-concern(의존성만, 클래스만, 그래프만)은 각 specialist를 직접 사용하라.
---

# Codebase Architecture Mapper

**Architecture analysis workflow owner.** Extract architecture from source code as structured data for LLM context injection.

## Family role

이 skill은 architecture analysis family의 **hub/workflow owner**입니다.

| Specialist | Role | When to use directly |
|---|---|---|
| `class-hierarchy-classifier` | 클래스 상속 분석, MRO, 다중상속 감지 | 단일 클래스 상속 구조만 분석할 때 |
| `graph-structure-classifier` | 그래프 구조 분류 (Tree/DAG/cyclic) | edge list가 이미 있고 구조 분류만 필요할 때 |
| `depsolve-analyzer` | Phantom/circular/diamond 의존성 탐지 | 패키지 매니저 기반 의존성 분석만 필요할 때 |

**원칙**: "전체 아키텍처 분석" 또는 "의존성 + 클래스 + 구조 통합 분석"이 필요하면 이 skill을 먼저 사용. 개별 specialist는 atomic 작업에만 직접 호출.

## 📍 Path Configuration

```bash
export SKILLS_ROOT="/path/to/your/skills"
# 예: export SKILLS_ROOT="$HOME/.gemini/skills"
# 예: export SKILLS_ROOT="/mnt/skills/user"
```

## Quick Start

```bash
cd $SKILLS_ROOT/codebase-architecture-mapper/scripts

# Basic analysis
python mapper.py /path/to/project

# With class nodes
python mapper.py /path/to/project --class-nodes

# Generate LLM context document
python mapper.py /path/to/project | python context_generator.py - -o PROJECT_ARCHITECTURE.md
```

---

## 🔗 Pipeline Integration

### Pipeline Overview

```
mapper.py ──► [JSON/edge-list output via stdout]
    │
    ├──► context_generator.py (LLM 문서)
    │         stdin 지원: python mapper.py ... | python context_generator.py -
    │
    ├──► graph-structure-classifier (모듈 의존성 구조 분류)
    │         stdin 지원: python mapper.py ... --format edge-list | python classifier.py -
    │
    └──► bridge.py ──► class-hierarchy-classifier (클래스 상속 분석)
              stdin 지원: python mapper.py ... --class-nodes | python bridge.py - --analyze
```

**핵심 원칙: 모든 도구가 stdin(`-`)을 지원하므로 임시 파일 없이 파이프로 연결**

### 파이프라인 내 specialist 위임

> 이 owner가 실행 중에 specialist로 위임하는 조건. Single-concern 직접 호출은 LLM 라우팅 가이드 참조.

| 조건 | 위임 대상 | 파이프라인 명령어 |
|------|----------|------------------|
| `--class-nodes` 사용 시 | class-hierarchy-classifier | `mapper.py ... --class-nodes \| bridge.py - --analyze` |
| INHERITANCE edge 3개 이상 | class-hierarchy-classifier | `mapper.py ... --class-nodes \| bridge.py - --analyze --classify-structure` |
| 순환 의존성 의심 시 | graph-structure-classifier | `mapper.py ... --format edge-list \| classifier.py -` |
| multi-concern 분석 요청 | 전체 파이프라인 | 아래 예시 참조 |

### LLM 라우팅 가이드

```
사용자 요청 분석:
│
├─ single-concern (specialist 직접 호출)
│   ├─ "의존성만 보여줘"        → depsolve-analyzer
│   ├─ "클래스 상속 구조만"     → class-hierarchy-classifier
│   └─ "순환 있어? / DAG야?"   → graph-structure-classifier
│
└─ multi-concern 또는 routing uncertain (이 owner 사용)
    ├─ "전체 아키텍처 분석해줘"
    ├─ "의존성 + 클래스 구조 통합 분석"
    └─ "프로젝트 구조 파악해줘"
```

### 파이프라인 예시

**표준 파이프라인 (임시 파일 없이):**

```bash
cd $SKILLS_ROOT/codebase-architecture-mapper/scripts

# 클래스 상속 분석
python mapper.py /path/to/project --class-nodes | python bridge.py - --analyze

# 모듈 의존성 구조 분류
python mapper.py /path/to/project --format edge-list | \
    python ../../graph-structure-classifier/scripts/classifier.py -

# 클래스 상속 + 구조 분류
python mapper.py /path/to/project --class-nodes | \
    python bridge.py - --analyze --classify-structure --project-root /path/to/project
```

**파일 저장이 필요한 경우 (드문 경우):**

```bash
# 여러 분석을 반복 실행해야 할 때
# 결과를 다른 도구와 공유할 때
python mapper.py /path/to/project --class-nodes > /tmp/arch.json
python bridge.py /tmp/arch.json --analyze
python bridge.py /tmp/arch.json --verify-all
```

---

## Output Formats

| Format | Command | Use Case |
|--------|---------|----------|
| JSON | (default) | Full analysis, bridge.py input |
| Edge List | `--format edge-list` | graph-structure-classifier input |
| Mermaid | `--format mermaid` | Visualization |

---

## Virtual Environment 주의사항

프로젝트에 pydantic 등 외부 의존성이 있는 경우:

```bash
# 프로젝트의 venv 사용
/path/to/project/.venv/bin/python bridge.py - --analyze --project-root /path/to/project
```

---

## Common Mistakes

**❌ 불필요한 임시 파일 생성**
```bash
# BAD: 임시 파일 사용
python mapper.py /project --class-nodes > /tmp/arch.json
python bridge.py /tmp/arch.json --analyze
```
- Fix: 파이프라인으로 직접 연결
```bash
# GOOD: 파이프 사용
python mapper.py /project --class-nodes | python bridge.py - --analyze
```

**❌ Large codebase without filters**
- Fix: `--exclude node_modules,venv,__pycache__`

**❌ Missing class/package info in docs**
- Fix: Use `--class-nodes --package-level`

**❌ Import 실패 (pydantic 등)**
- Fix: `--project-root` 옵션으로 프로젝트 루트 지정, 또는 프로젝트 venv 사용

**❌ 스크립트를 못 찾음**
- Fix: `SKILLS_ROOT` 환경변수 설정 또는 상대경로 사용

---

## References

- **Output Format**: `references/OUTPUT_FORMAT.md`
- **Integration**: `references/INTEGRATION.md`
- **Testing**: `references/TESTING.md`
