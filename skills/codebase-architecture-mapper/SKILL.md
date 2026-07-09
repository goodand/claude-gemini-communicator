---
name: codebase-architecture-mapper
description: Use when analyzing project structure, extracting module dependencies, mapping class inheritance, identifying hub modules, or generating architecture documentation. Triggers on "의존성 분석", "아키텍처 추출", "import graph", "코드 구조", "module dependency", "class hierarchy", "프로젝트 구조", "hub 분석", "PROJECT_ARCHITECTURE".
---

# Codebase Architecture Mapper

Extract architecture from source code as structured data for LLM context injection.

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

### 자동 트리거 조건

| 조건 | 연동 스킬 | 파이프라인 명령어 |
|------|----------|------------------|
| `--class-nodes` 사용 시 | class-hierarchy-classifier | `mapper.py ... --class-nodes \| bridge.py - --analyze` |
| INHERITANCE edge 3개 이상 | class-hierarchy-classifier | `mapper.py ... --class-nodes \| bridge.py - --analyze --classify-structure` |
| 순환 의존성 의심 | graph-structure-classifier | `mapper.py ... --format edge-list \| classifier.py -` |
| "전체 아키텍처 분석" 요청 | 전체 파이프라인 | 아래 예시 참조 |

### LLM 자가 판단 가이드

```
사용자 요청 분석:
│
├─ "의존성만 보여줘" 
│   → python mapper.py /project
│
├─ "클래스 구조도 분석해줘" 
│   → python mapper.py /project --class-nodes | python bridge.py - --analyze
│
├─ "순환 의존성 있는지 확인해줘" 
│   → python mapper.py /project --format edge-list | \
│         python ../../graph-structure-classifier/scripts/classifier.py -
│
├─ "전체 아키텍처 분석해줘" 
│   → 전체 파이프라인 실행 (아래 예시 참조)
│
└─ "상속 구조가 복잡한지 확인해줘" 
    → python mapper.py /project --class-nodes | \
          python bridge.py - --analyze --classify-structure
    → (Tree면 단순, DAG면 다중상속 존재)
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
