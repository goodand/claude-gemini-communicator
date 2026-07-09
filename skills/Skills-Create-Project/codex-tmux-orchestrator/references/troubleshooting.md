# Troubleshooting — codex-tmux-orchestrator

> 케이스 형식: CASE-XXX (증상 → 원인 → 해결 → 교훈)

## CASE-001: _session_exists가 서버 없을 때 True 반환

- **증상**: tmux 서버가 없는데도 preflight에서 "session 이름 충돌" 오류
- **원인**: `_tmux()` 함수에 `check=False`로 호출 시, returncode != 0이어도 `(stdout, None)` 반환. `_session_exists`가 `err is None`으로 판정하여 항상 True
- **해결**: `_session_exists`를 직접 `subprocess.run` + `returncode == 0`으로 변경
- **교훈**: `check=False` 래퍼의 반환값 의미를 정확히 이해하고 사용. 존재 확인은 returncode 직접 검사
