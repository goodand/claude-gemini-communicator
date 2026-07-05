---
name: m5-ssh-codex-operator
description: 원격 Mac의 Codex runtime을 SSH alias로 운영한다. Tailscale MagicDNS, zsh PATH 로딩, tmux, claude-gemini-communicator skill runtime bootstrap/verify gate를 포함한다. 원격 명령 실행, tmux 세션 복구/attach, runtime 상태 검증, SSH/PATH/verify 실패 트러블슈팅이 필요할 때 사용한다.
---

# M5 SSH Codex Operator

## Core Rules

- canonical access: `ssh ${M5_SSH_ALIAS} 'zsh -lc "..."'` — 원격 zsh PATH 로딩 보장.
- long-running / interactive: `ssh ${M5_SSH_ALIAS}` 접속 후 `tmux new -A -s ${M5_TMUX_SESSION}`.
- host 값(MagicDNS, Tailscale IP, LAN IP, username)은 M1 `~/.ssh/config`와 local `.env`에만 둔다.
- `git add -A` 금지.
- `.env`, `.mcp.json`, `.venv/`, `.runtime/`은 원격 local-only — commit/push 금지.
- **Claude Code 등록**: `~/.claude/agents/<name>.md` → `~/.codex/skills/<name>/SKILL.md` 심링크. 세션 시작 시 스캔됨 — 등록/변경 후 반드시 **세션 재시작**.
- 심링크 target은 반드시 `$HOME` 하위 비보호 디렉토리(`~/.codex/`, `~/Developer/` 등). `~/Desktop/`, `~/Documents/` 등 TCC-protected 경로를 target으로 지정하면 Claude가 읽을 때 EPERM 발생.
- settings/agent/hook 변경(`.claude/agents/`, `settings.json`, hook 스크립트)은 기존 세션에 캐시됨 — 변경 후 반드시 **세션 재시작** 후 적용 확인.
- Claude 시작 실패 시 cwd 가독성 먼저 확인: `test -r "$PWD" && echo OK || echo UNREADABLE` — UNREADABLE이면 EPERM으로 시작 단계에서 죽을 수 있음. `references/troubleshooting.md` → EPERM 분기 참조.

## SSH Health Check

```bash
source .env
ssh -o BatchMode=yes -o ConnectTimeout=5 "${M5_SSH_ALIAS}" \
  'zsh -lc "hostname && whoami && which python3 && python3 --version"'
```

기대 형식: `references/runtime-contract.md` 참조.

## Runtime Verification (no git mutation)

```bash
cd ~/.codex/skills/m5-ssh-codex-operator
bash scripts/m5_verify.sh
```

bootstrap + verify를 현재 원격 checkout 상태에서 실행한다.
bootstrap은 `.venv`, `.runtime/python_bin`, `.env`, `.mcp.json`을 생성/갱신할 수 있다 — 원격 local 파일 한정, git mutation 없음.

## Sync to main (명시 요청 시에만)

```bash
cd ~/.codex/skills/m5-ssh-codex-operator
bash scripts/m5_sync_main.sh
```

원격 repo가 dirty이면 중단한다. git checkout main + pull만 수행한다.
sync 후 검증이 필요하면 `m5_verify.sh`를 별도 실행한다.

## Remote File Read (M5 원격 — SSH 경유 전용)

**적용 범위:**
- M1 로컬 macOS EPERM에는 적용하지 않음.
- 원격 host에서 agent/tool이 파일에 직접 접근 불가할 때만 사용.
- `find` 자체가 EPERM을 반환하면 즉시 중단 — M5 측 TCC 문제이므로 이 패턴으로 해결 불가.

```bash
source .env
# 디렉토리 탐색
ssh -o BatchMode=yes -o ConnectTimeout=10 "${M5_SSH_ALIAS}" \
  'zsh -lc "find ~ -type d -name <target> 2>/dev/null"'

# 파일 목록 + 내용 읽기
ssh -o BatchMode=yes -o ConnectTimeout=10 "${M5_SSH_ALIAS}" \
  'zsh -lc "ls <path>/*.md && echo === && cat <path>/*.md"'
```

Agent 위임: `subagent_type: m5-ssh-codex-operator` — M5 측 TCC 문제가 없을 때만 유효.

## Troubleshooting

`references/troubleshooting.md` 참조.
