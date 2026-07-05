---
name: skill-path-resolver
description: Use when skills fail due to path issues like "No such file or directory" or "ModuleNotFoundError", when migrating skills between environments (Claude Container, Gemini CLI, local), or when setting up $SKILLS_ROOT environment variable. Provides common path resolution module that other skills can import. Triggers on path errors, skill setup, environment configuration, SKILLS_ROOT setup, skill migration.
---

# Skill Path Resolver

경로 해석 + 하드코딩 경로 수정 스킬.

## 스크립트 역할

| 스크립트 | 용도 | 사용 방식 |
|----------|------|-----------|
| `skill_paths.py` | **핵심 모듈** - 다른 스킬에서 import | `from skill_paths import SkillPaths` |
| `resolver.py` | **CLI 도구** - 환경 감지 + 하드코딩 수정 | `python resolver.py detect` |
| `workspace_manager.py` | 중간 파일 정리 | `python workspace_manager.py cleanup` |

## Quick Start

### 다른 스킬에서 import (skill_paths.py)

```python
from skill_paths import SkillPaths, get_skill_script, setup_skill_environment

paths = SkillPaths()

# 다른 스킬의 스크립트 경로
tracer = paths.get_script('runtime-flow-tracer', 'tracer.py')
subprocess.run([sys.executable, tracer, 'python', 'app.py'])

# 다른 스킬 모듈 import
setup_skill_environment('class-hierarchy-classifier')
from hierarchy_classifier import analyze
```

### CLI로 환경 확인 (resolver.py)

```bash
# 환경 감지
python scripts/resolver.py detect

# 하드코딩 경로 수정
python scripts/resolver.py fix --skill some-skill --dry-run
python scripts/resolver.py fix-all

# 환경변수 설정
eval "$(python scripts/resolver.py export --shell bash)"
```

### 중간 파일 정리 (workspace_manager.py)

```bash
python scripts/workspace_manager.py cleanup --dry-run
python scripts/workspace_manager.py cleanup --keep 'final_*'
```

## API Reference

### skill_paths.py (핵심 모듈)

```python
from skill_paths import SkillPaths

paths = SkillPaths()
paths.root                          # SKILLS_ROOT 경로
paths.get_skill_dir('name')         # 스킬 디렉토리
paths.get_script('skill', 'file')   # 스크립트 경로
paths.get_reference('skill', 'doc') # 참조 문서 경로
paths.list_skills()                 # 스킬 목록
paths.detect_environment()          # 환경 정보
```

### resolver.py (CLI 도구)

```bash
resolver.py detect              # 환경 감지
resolver.py fix --skill NAME    # 특정 스킬 하드코딩 수정
resolver.py fix-all [--dry-run] # 모든 스킬 수정
resolver.py export --shell bash # 환경변수 export
resolver.py resolve --from A --to B  # 상대 경로 계산
```

### workspace_manager.py

```python
from workspace_manager import skill_workspace, cleanup_skill_artifacts

# 임시 워크스페이스 (자동 정리)
with skill_workspace(keep=['*.mmd']) as ws:
    trace = ws.temp_file('trace.json')
    # ... 작업 ...
# 자동 정리됨

# 기존 디렉토리 정리
cleanup_skill_artifacts(patterns=['*.log'], keep=['final_*'])
```

## 지원 환경

자동 탐지 우선순위:
1. `$SKILLS_ROOT` 환경변수
2. `/mnt/skills/user` (Claude Container)
3. `~/.gemini/skills` (Gemini CLI global)
4. `./.gemini/skills`, `./.claude/skills` (프로젝트 로컬)

## 연동 구조

```
skill_paths.py (핵심)
      ↑
      └── resolver.py (사용) ← CLI 실행
      
workspace_manager.py (독립)
```

resolver.py는 내부적으로 skill_paths.py를 사용하여 경로 탐지를 수행합니다.
둘 중 하나만 있어도 작동하지만, 함께 사용하면 일관성이 보장됩니다.
