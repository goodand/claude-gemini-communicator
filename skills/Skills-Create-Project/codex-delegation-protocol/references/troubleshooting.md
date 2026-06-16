# Troubleshooting — codex-delegation-protocol

> 케이스 형식: CASE-XXX (증상 → 원인 → 해결 → 교훈)

## CASE-001: 한국어 경로 tmux 인코딩 오류

- **증상**: tmux send-keys로 codex exec 커맨드 전송 시 `x-codex-turn-metadata` UTF-8 인코딩 에러
- **원인**: 프로젝트 경로에 한국어 포함 (`Project_____현재_진행중인/`)
- **해결**: 비치명적 에러 — Codex가 WebSocket에서 HTTPS로 자동 폴백. worktree_path에는 ASCII만 사용 권장
- **교훈**: worktree 경로명에 한국어를 포함하지 않는다 (`.worktrees/auth-module` 형태)
