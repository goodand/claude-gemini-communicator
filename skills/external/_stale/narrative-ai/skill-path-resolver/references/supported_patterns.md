# Supported Path Patterns

## 감지 및 수정 대상 패턴

### Python (.py)

#### sys.path.insert
```python
# Before
sys.path.insert(0, "$SKILLS_ROOT/class-hierarchy-classifier/scripts")

# After
sys.path.insert(0, os.path.join(get_skills_root(), "class-hierarchy-classifier/scripts"))
```

#### 문자열 경로
```python
# Before
classifier_path = "$SKILLS_ROOT/graph-structure-classifier/scripts/classifier.py"

# After  
classifier_path = f"{get_skills_root()}/graph-structure-classifier/scripts/classifier.py"
```

### Bash (.sh, .bash)

#### 절대경로
```bash
# Before
python $SKILLS_ROOT/codebase-architecture-mapper/scripts/mapper.py

# After
python $SKILLS_ROOT/codebase-architecture-mapper/scripts/mapper.py
```

#### 파이프라인
```bash
# Before
python $SKILLS_ROOT/class-hierarchy-classifier/scripts/hierarchy_classifier.py --output-edges | \
    python $SKILLS_ROOT/graph-structure-classifier/scripts/classifier.py -

# After
python $SKILLS_ROOT/class-hierarchy-classifier/scripts/hierarchy_classifier.py --output-edges | \
    python $SKILLS_ROOT/graph-structure-classifier/scripts/classifier.py -
```

### Markdown (.md)

#### 코드 블록 내 경로
```markdown
# Before
```bash
python $SKILLS_ROOT/mapper.py
```

# After
```bash
python $SKILLS_ROOT/mapper.py
```
```

#### 인라인 경로
```markdown
# Before
스크립트 위치: `$SKILLS_ROOT/codebase-architecture-mapper/scripts/mapper.py`

# After
스크립트 위치: `$SKILLS_ROOT/codebase-architecture-mapper/scripts/mapper.py`
```

## 알려진 경로 루트 패턴

| 패턴 | 환경 | 예시 |
|------|------|------|
| `$SKILLS_ROOT/` | Claude Container | `$SKILLS_ROOT/mapper/scripts/mapper.py` |
| `/mnt/skills/public/` | Claude Container (public) | `/mnt/skills/public/docx/scripts/...` |
| `~/.gemini/skills/` | Gemini CLI (global) | `/home/user/.gemini/skills/mapper/...` |
| `.gemini/skills/` | Gemini CLI (local) | `./project/.gemini/skills/mapper/...` |
| `$SKILLS_ROOT/` | 환경변수 | Any custom path |

## 상대경로 변환 규칙

### 스킬 간 참조
```
From: skills_root/skill_a/scripts/script.py
To:   skills_root/skill_b/scripts/other.py

Relative: ../../skill_b/scripts/other.py
```

### 스킬 내부 참조
```
From: skills_root/skill_a/scripts/main.py
To:   skills_root/skill_a/scripts/utils.py

Relative: ./utils.py (또는 그냥 utils.py)
```

### 깊은 경로
```
From: skills_root/skill_a/scripts/sub/deep.py
To:   skills_root/skill_b/scripts/other.py

Relative: ../../../skill_b/scripts/other.py
```

## 수정하지 않는 패턴

다음 패턴은 의도적으로 수정하지 않습니다:

1. **시스템 경로**
   - `/usr/bin/python`
   - `/bin/bash`
   - `/etc/...`

2. **일반적인 절대경로**
   - `/tmp/...`
   - `/home/user/projects/...` (skills 경로가 아닌 경우)

3. **URL**
   - `https://example.com/...`
   - `file:///...`

4. **상대경로 (이미 상대경로인 경우)**
   - `./scripts/...`
   - `../other-skill/...`

## 커스텀 패턴 추가

`resolver.py`의 `HARDCODED_PATTERNS` 딕셔너리를 수정하여 새 패턴 추가 가능:

```python
HARDCODED_PATTERNS = {
    'python': [
        # 기존 패턴...
        
        # 새 패턴 추가
        (r'your_pattern_regex', 'replacement_template'),
    ],
    # 새 언어 추가
    'ruby': [
        (r'require\s+["\'](/[^"\']+/skills/[^"\']+)["\']',
         'require "{resolved_path}"'),
    ],
}
```
