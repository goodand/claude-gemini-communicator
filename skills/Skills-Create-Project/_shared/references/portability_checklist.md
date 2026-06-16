# Agent Skill Runtime Portability Checklist

목표: 새 MacBook Air M5 32GB에서 clone + bootstrap + verify만으로 Agent Skill runtime 재현.

---

## Phase 1 — Pre-clone (수동, script 없음)

새 Mac에서 터미널을 열고 아래를 순서대로 실행한다.

```bash
# 1-1. Homebrew 설치 (이미 있으면 skip)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
eval "$(/opt/homebrew/bin/brew shellenv)"   # arm64 PATH 등록

# 1-2. 필수 도구 설치
brew install git gh tmux ripgrep python@3.13 node
brew install astral-sh/tap/uv

# 1-3. Claude Code
npm install -g @anthropic-ai/claude-code
claude --version   # 동작 확인

# 1-4. Codex CLI
npm install -g @openai/codex
codex --version

# 1-5. Gemini CLI — v0.1 BLOCKER (설치 명령 미확정)
#   현재 후보: npm install -g @google/gemini-cli
#   구현 v0.1 완료 전 정확한 설치 명령 확정 필요.
#   이 항목이 미완료여도 bootstrap/verify는 non-blocking으로 통과한다.
```

> **CWD 계약**: 이후 모든 script는 반드시 `skills/Skills-Create-Project/` 에서 실행한다.

---

## Phase 2 — Clone + Bootstrap

```bash
# 2-1. repo clone
git clone git@github.com:<org>/claude-gemini-communicator.git
# 또는 HTTPS: git clone https://github.com/<org>/claude-gemini-communicator.git

# 2-2. CWD 이동 (이 이후 모든 명령의 기준 디렉토리)
cd claude-gemini-communicator/skills/Skills-Create-Project

# 2-3. bootstrap 실행
bash _shared/scripts/bootstrap_agent_runtime_mac.sh
# 기대: exit 0, .env / .mcp.json 생성, no /Users/ ABS-PATH 경고 없음
```

### Bootstrap 후 수동 작업

```bash
# .env에 실제 API key 주입 (bootstrap은 placeholder만 복사)
# nano .env   또는   open .env
```

---

## Phase 3 — Verify

```bash
# 3-1. verify 실행 (CWD = skills/Skills-Create-Project 필수)
bash _shared/scripts/verify_agent_runtime_mac.sh
# 기대: smoke 34/34, unit 446/446, audit PASS, no-abs-path PASS → exit 0
```

개별 gate 수동 실행 (verify script 내부와 동일):

```bash
# smoke
python3 _shared/scripts/smoke_runner.py --skills-root .

# unit (CWD 계약: Skills-Create-Project/ 에서 실행)
# --ignore-glob: skip backups/ on dev machines; no-op on clean clone
python3 -m pytest . -q -p no:cacheprovider --ignore-glob="**/backups/**"

# audit
python3 _shared/scripts/audit_cross_skill_dependencies.py --skills-root .

# no-abs-path
if grep -r "/Users/" . \
     --include="*.py" --include="*.sh" --include="*.json" \
     --exclude-dir=__pycache__ --exclude-dir=.git \
     --exclude-dir=evals --exclude-dir=backups \
     --exclude-dir=references --exclude-dir=.claude -l 2>/dev/null; then
  echo "FAIL: /Users/ absolute path found"
else
  echo "PASS: no absolute paths"
fi
```

---

## Gate 완료 기준

| Gate | 명령 | 기대 결과 |
|------|------|-----------|
| bootstrap | `bash _shared/scripts/bootstrap_agent_runtime_mac.sh` | exit 0 |
| smoke | `smoke_runner.py --skills-root .` | 34/34 PASS |
| unit | `pytest . -q -p no:cacheprovider --ignore-glob="**/backups/**"` | 446 passed |
| audit | `audit_cross_skill_dependencies.py --skills-root .` | exit 0 |
| no-abs-path | grep scan | 출력 없음 |
| verify | `bash _shared/scripts/verify_agent_runtime_mac.sh` | exit 0 |

---

## 주의사항

- **CWD**: `python3 -m pytest`는 반드시 `Skills-Create-Project/` 에서 실행. 상위 디렉토리에서 실행 시 `test_capture_quick_validate` 등 3개 테스트 실패.
- **set -e + grep**: `grep` no-match는 exit 1. script에서 직접 `grep` 사용 시 `|| true` 또는 `if grep; then` 형태 필수.
- **API key 없음**: bootstrap/verify는 API key 없이 exit 0. LLM 호출 skill(slice-experiment-lab 등)은 `.env` 작성 후 사용.
- **Gemini CLI**: v0.1에서 설치 명령 미확정. 이 항목만 완료되지 않아도 다른 gate는 영향 없음.
- **MSI worktree dirty**: MSI repo(`my-second-identity`)는 별도 dirty state — `git add -A`, `git add plans/`, `git add plans/codex/docs/reports/` 금지.
