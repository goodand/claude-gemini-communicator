# Troubleshooting

---

## EPERM — 분기 진단 (먼저 읽을 것)

**증거 없이 chmod -R / chown -R / xattr -cr / rm -rf .claude 실행 금지.**
macOS TCC/provenance 보호 속성이 원인일 때 이 명령들은 무효하거나 파일 무결성을 파괴한다.

### Decision Tree (이 순서로 진단)

```
1. Claude가 프로젝트 밖($HOME 등)에서 정상 실행되는가?
   → NO: binary 문제 (분기 4)
   → YES: 다음으로

2. cwd가 readable인가?
   test -r "$PWD" && echo OK || echo UNREADABLE
   → UNREADABLE: cwd/TCC 문제 (분기 1) ← hook EPERM의 근본 원인일 가능성 높음
   → OK: 다음으로

3. session jsonl이 readable인가?
   ls -la ~/.claude/projects/.../
   → EPERM: session 문제 (분기 2)
   → OK: 다음으로

4. .claude settings/hook 파일이 readable인가?
   ls -la <hook_path>
   → EPERM: hook/config 문제 (분기 3)
   → OK: agent 등록·cache 문제 → 세션 재시작
```

> hook EPERM(`hook_pre_tool.py: Operation not permitted`)은 cwd/TCC 보호의 **증상**일 수 있다.
> hook 경로를 바꾸기 전에 반드시 분기 1부터 확인한다.

### 분기 1 — cwd unreadable (macOS Desktop/TCC 보호)

증거:
- `test -r "$PWD"` → UNREADABLE
- `ls -ldeO@ "$PWD"` → Unix mode `drwxr-xr-x`이나 `com.apple.macl`, `com.apple.provenance` xattr 존재
- `claude --version` in project cwd → EPERM, `cd ~ && claude --version` → 정상

원인: macOS Desktop/Documents 디렉토리에 TCC entitlement 기반 접근 제어 적용.
`chmod`/`chown`으로 해제 불가 — Unix mode와 무관한 보호 계층.

안전한 대응:
```bash
# 옵션 A: Terminal에 Full Disk Access 부여
# System Settings > Privacy & Security > Full Disk Access > Terminal 추가

# 옵션 B: 프로젝트를 보호 디렉토리 밖으로 이동
mv ~/Desktop/my-project ~/Developer/my-project
```

### 분기 2 — session unreadable

증거:
- session jsonl 접근 불가
- `ls -la ~/.claude/projects/...` → EPERM

대응: 세션을 `$HOME` 하위 비보호 디렉토리에서 새로 시작.

### 분기 3 — hook/config unreadable

증거:
- `hook_pre_tool.py: [Errno 1] Operation not permitted`
- hook 경로가 macOS 보호 디렉토리 내부에 있음 (분기 1이 근본 원인인 경우가 많음)

진단:
```bash
cat ~/.claude/settings.json | grep -A5 hook
cat ~/.claude/settings.local.json | grep -A5 hook
ls -la <hook_path>
```

대응: 분기 1 먼저 해소. cwd가 정상인데 hook만 EPERM이면 hook 경로를 비보호 디렉토리로 이동.

즉시 우회책:
- 파일 생성/수정 → `Write` / `Edit` 도구
- 검증 명령 → 사용자에게 `! <command>` 형식 터미널 직접 실행 요청

### 분기 4 — Claude binary 문제

증거:
- `claude --version` → EPERM (cwd 무관, `$HOME`에서도 실패)

대응:
```bash
which claude
ls -la $(which claude)
# 재설치: npm install -g @anthropic-ai/claude-code
```

---

## 심링크 target EPERM

증상: `~/.claude/agents/` 심링크는 존재하는데 Claude가 agent를 읽지 못하거나 EPERM 발생.

원인: 심링크 target이 TCC-protected 디렉토리(`~/Desktop/`, `~/Documents/` 등) 안에 있음.

진단:
```bash
readlink ~/.claude/agents/<name>.md          # target 경로 확인
test -r "$(readlink ~/.claude/agents/<name>.md)" && echo OK || echo EPERM
```

대응: target 파일을 `~/.codex/skills/` 또는 `~/Developer/` 등 비보호 경로로 이동 후 심링크 재생성.

## Agent 등록 후 현재 세션에서 미인식

증상: `~/.claude/agents/`에 심링크 추가했으나 Agent 호출 시 `not found`

원인: Claude Code는 세션 시작 시에만 `~/.claude/agents/`를 스캔함.

해결: Claude Code 재시작. 재시작 후 system-reminder에 agent 목록 확인.

settings/hook 변경도 동일하게 세션 재시작 필요.

---

## `ssh ${M5_SSH_ALIAS}` times out

Tailscale 먼저 확인:

```bash
tailscale status
tailscale ping <M5_TAILSCALE_IP>
nc -vz -G 5 <M5_TAILSCALE_IP> 22
```

Tailscale ping 성공 + SSH timeout → 원격 Mac System Settings > Sharing > Remote Login 확인.

## Host key verification fails

```bash
ssh -o StrictHostKeyChecking=accept-new "${M5_SSH_ALIAS}" 'zsh -lc "hostname && whoami"'
```

`known_hosts` 전체 삭제 금지.

## `python3`가 system path로 해석됨

`zsh -lc "..."` 형식으로 실행하는지 확인.
원격 `~/.zprofile`에 Homebrew PATH 확인:

```bash
ssh "${M5_SSH_ALIAS}" 'zsh -lc "echo $PATH"'
```

`/opt/homebrew/opt/python@3.13/libexec/bin`이 PATH 앞에 있어야 한다.

## verify fails — bootstrap not run

```bash
bash scripts/m5_verify.sh
```

m5_verify.sh는 bootstrap을 포함한다.

## tmux confusion

```bash
ssh "${M5_SSH_ALIAS}" 'zsh -lc "tmux ls"'
ssh "${M5_SSH_ALIAS}" "tmux new -A -s ${M5_TMUX_SESSION}"
```

기존 세션 강제 종료 금지.
