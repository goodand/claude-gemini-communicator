# M5 Runtime Contract

## Canonical Access

- SSH alias: `${M5_SSH_ALIAS}` — M1 `~/.ssh/config`에 정의됨, local `.env`에서 로드.
- one-shot: `ssh ${M5_SSH_ALIAS} 'zsh -lc "..."'`
- interactive: `tmux new -A -s ${M5_TMUX_SESSION}`

## Host Values

실제 값은 M1 `~/.ssh/config`와 local `.env`에만 보관한다. 이 파일에 적지 않는다.

- MagicDNS hostname: `<M5_MAGICDNS_HOST>` — `~/.ssh/config` Host 블록의 HostName
- Tailscale IPv4 fallback: `<M5_TAILSCALE_IP>` — Tailscale admin console 확인
- LAN fallback: 같은 네트워크 내 보조 수단만. 기본값으로 사용하지 말 것.
- Remote user: `<M5_USER>`

## Runtime Paths (원격 측 — script 내부에서 remote-side $HOME 기준)

- Repo: `$HOME/Developer/claude-gemini-communicator`
- Skills root: `$HOME/Developer/claude-gemini-communicator/skills/Skills-Create-Project`
- Python: `/opt/homebrew/opt/python@3.13/libexec/bin/python3` (Homebrew keg-only)
  - bootstrap PYTHON_BIN resolution priority:
    1. `/opt/homebrew/opt/python@3.13/libexec/bin/python3`
    2. `/opt/homebrew/bin/python3.13`
    3. `command -v python3` (fallback)

## Verification Pass Criteria

```text
bootstrap: exit 0
verify: ALL GATES PASS
verify summary: FAIL 0
dep-preflight: pytest, pydantic present
smoke: no failures
unit: no failures
audit: exit 0
no-abs-path: PASS
git status --short: 출력 없음 (clean)
.env: gitignored
.mcp.json: gitignored
```

## Mutation Scope of m5_verify.sh

허용 (원격 local 파일):
- `.venv/` 생성 (bootstrap)
- `.runtime/python_bin` 생성 (bootstrap)
- `.env` 생성 (bootstrap, .env.example 존재 시)
- `.mcp.json` 생성 (bootstrap, .mcp.example.json 존재 시)

금지:
- git tracked files 변경
- git index 변경
- branch 변경
