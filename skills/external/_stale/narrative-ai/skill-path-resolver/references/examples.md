# Skill Path Resolver - Examples

## Example 1: 새 환경에서 처음 설정

```bash
# 1. 환경 감지
cd /path/to/your/skills/skill-path-resolver/scripts
python resolver.py detect

# Output:
# Environment Detection Report
# ========================================
# Detected SKILLS_ROOT: /home/user/.gemini/skills
# Environment: Gemini CLI (global)
# Detection Method: directory_scan
# Confidence: HIGH
#
# Found Skills:
#   ✓ codebase-architecture-mapper
#   ✓ class-hierarchy-classifier
#   ✓ graph-structure-classifier

# 2. 환경변수 설정 스크립트 생성
python resolver.py export --shell bash > ~/.skills_config.sh

# 3. 쉘 설정에 추가
echo 'source ~/.skills_config.sh' >> ~/.bashrc
source ~/.bashrc
```

## Example 2: 스킬에서 "path not found" 오류 해결

```bash
# 오류 상황
$ python bridge.py arch.json --analyze
# Error: No such file or directory: $SKILLS_ROOT/class-hierarchy-classifier/scripts

# 해결
$ cd $SKILLS_ROOT/skill-path-resolver/scripts
$ python resolver.py fix --skill codebase-architecture-mapper

# Output:
# codebase-architecture-mapper/scripts/bridge.py:
#   - sys.path.insert(0, "$SKILLS_ROOT/class-hierarchy-classifier/scripts")
#   + sys.path.insert(0, os.path.join(get_skills_root(), "class-hierarchy-classifier/scripts"))
#   ✓ Fixed 1 path(s)
```

## Example 3: 모든 스킬 일괄 수정 (Dry-run 먼저)

```bash
# 1. 미리보기
$ python resolver.py fix-all --dry-run

# Output:
# codebase-architecture-mapper: 2 change(s)
#   bridge.py: 2 change(s)
# class-hierarchy-classifier: 1 change(s)
#   hierarchy_classifier.py: 1 change(s)
#
# ========================================
# Total: Would fix 3 path(s) in 2 skill(s)

# 2. 실제 적용
$ python resolver.py fix-all

# Output:
# ...
# Total: Fixed 3 path(s) in 2 skill(s)
```

## Example 4: 스킬 간 상대경로 계산

```bash
$ python resolver.py resolve \
    --from codebase-architecture-mapper/scripts \
    --to class-hierarchy-classifier/scripts

# Output:
# Resolved Path: ../../class-hierarchy-classifier/scripts
```

## Example 5: JSON 형식으로 설정 내보내기

```bash
$ python resolver.py export --format json

# Output:
# {
#   "SKILLS_ROOT": "/home/user/.gemini/skills",
#   "environment": {
#     "name": "Gemini CLI (global)",
#     "skills_root": "/home/user/.gemini/skills",
#     "detection_method": "directory_scan",
#     "confidence": "HIGH",
#     "found_skills": [
#       "codebase-architecture-mapper",
#       "class-hierarchy-classifier",
#       "graph-structure-classifier"
#     ]
#   }
# }
```

## Example 6: Fish Shell 사용자

```fish
# Fish 설정 생성
python resolver.py export --shell fish > ~/.config/fish/conf.d/skills.fish

# 적용
source ~/.config/fish/conf.d/skills.fish

# 확인
echo $SKILLS_ROOT
```

## Example 7: PowerShell 사용자 (Windows)

```powershell
# PowerShell 설정 생성
python resolver.py export --shell powershell > $PROFILE.CurrentUserAllHosts

# 적용
. $PROFILE.CurrentUserAllHosts

# 확인
echo $env:SKILLS_ROOT
```

## Example 8: Bash 스크립트에서 소스로 사용

```bash
#!/bin/bash
# my_script.sh

# resolver.sh를 소스로 로드
source /path/to/skills/skill-path-resolver/scripts/resolver.sh

# 헬퍼 함수 사용
MAPPER_PATH=$(get_skill_path "codebase-architecture-mapper" "scripts/mapper.py")
python "$MAPPER_PATH" /project --class-nodes
```

## Example 9: Python에서 API로 사용

```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '/path/to/skills/skill-path-resolver/scripts')

from resolver import SkillPathResolver

# 리졸버 초기화
resolver = SkillPathResolver()

# 환경 감지
env = resolver.detect_environment()
print(f"Skills Root: {env.skills_root}")
print(f"Found: {env.found_skills}")

# 스킬 경로 가져오기
mapper_path = resolver.get_skill_path('codebase-architecture-mapper', 'scripts/mapper.py')
print(f"Mapper: {mapper_path}")

# 상대경로 계산
relative = resolver.resolve_relative_path(
    'codebase-architecture-mapper', 
    'class-hierarchy-classifier'
)
print(f"Relative: {relative}")
```

## Example 10: CI/CD 파이프라인에서 사용

```yaml
# .github/workflows/test-skills.yml
name: Test Skills

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Skills Environment
        run: |
          export SKILLS_ROOT="${{ github.workspace }}/.gemini/skills"
          python $SKILLS_ROOT/skill-path-resolver/scripts/resolver.py detect
          
      - name: Fix Paths if Needed
        run: |
          python $SKILLS_ROOT/skill-path-resolver/scripts/resolver.py fix-all
          
      - name: Run Tests
        run: |
          cd $SKILLS_ROOT/codebase-architecture-mapper/scripts
          python mapper.py ${{ github.workspace }} --class-nodes
```
