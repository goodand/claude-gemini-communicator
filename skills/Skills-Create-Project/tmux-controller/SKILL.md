---
name: tmux-controller
description: >-
  Use this skill when the user wants to run, stop, restart, or debug
  user-facing apps in interactive tmux sessions — including log capture,
  multi-service monitoring, and debugging loops with process isolation.
  AI가 사용자 앱용 tmux 세션을 제어하여 실행/중지/재시작, 로그 캡처, 디버깅을 수행한다.
---

# TMUX Controller

tmux 세션을 통한 앱 실행·디버깅·모니터링. 격리된 소켓으로 안전하게 운용한다.

## When to use

- 앱/서버를 백그라운드에서 실행하고 로그를 AI가 분석할 때
- 에러 발견 → 코드 수정 → 재시작 디버깅 루프가 필요할 때
- 여러 서비스를 동시에 모니터링할 때
- 장시간 프로세스의 출력을 파일로 저장해야 할 때

## Workflow

1. **격리 소켓 생성** — 기존 tmux 환경과 충돌 방지를 위해 전용 소켓으로 세션 생성 (`tmux -S /tmp/ai.sock new-session -d -s <name>`). 기본 소켓 사용 시 stale socket 문제 주의
2. **앱 실행** — `send-keys`로 명령 전송. **반드시 `Enter` 포함**. 출력 대기 시 프로그램 출력 기준으로 판단 — echo된 명령 문자열이 먼저 매치되는 함정 주의 (→ cheatsheet wait-for 항목)
3. **로그 캡처** — `capture-pane -p -S -N`으로 히스토리 범위 지정. 현재 화면만 캡처되므로 `-S` 옵션 필수
4. **디버깅 루프** — `C-c` → 코드 수정 → 재실행 → 캡처 확인 반복. `scripts/tmux_helper.py`의 `restart` 서브커맨드 활용
5. **정리** — `kill-session` 전 파괴적 작업 확인. 격리 소켓이면 `kill-server`로 완전 정리

## Scripts

- `scripts/tmux_helper-at2026-03-13.py` — create/run/capture/wait/stop/restart/kill/list 통합 래퍼. `--socket`으로 격리 소켓 지원, `wait`로 출력 패턴 대기. `python3 scripts/tmux_helper-at2026-03-13.py --help`
- `scripts/tmux_verify.py` — 환경 검증 (tmux 설치/버전/소켓 상태/stale 세션 감지). `python3 scripts/tmux_verify.py --help`

## References

- `references/tmux-commands-cheatsheet-at2026-03-13.md` — 전체 커맨드, 디버깅 패턴 4종, 격리 소켓 예시, 주의사항 테이블
- `references/TMUX-교시-Skills-분석-at2026-03-13-20-30.md` — tmux 제어 오픈소스 스킬 사례 (term-cli 추천, socket mismatch 발견)
- `references/control-tmux-at2026-03-13-20-32.md` — GitHub 저장소 10개 심층 비교 (Agent Deck, MCP 서버, 보안 고려사항)
- `references/checklist.md` — tmux 제어 스킬 구현 상세 체크리스트 (요구사항~배포, §1-§10)
- `references/troubleshooting.md` — 실행 중 발견된 오류·해결 사례 (wait 패턴 함정, Codex 옵션 변경 등)

## Notes

- 세션 이름에 점(`.`) 사용 금지 — tmux가 소켓으로 해석
- `-S`(소켓 경로)와 `-L`(소켓 이름) 혼용 주의 — ref1에서 mitsuhiko/agent-stuff 불일치 발견
- 파괴적 작업(kill) 시 명시적 확인 필요 — ref2 mcp-tmux의 `confirm=true` 패턴 참고
- `pipe-pane`으로 전체 출력을 파일 저장 가능 (장시간 프로세스 감시용)
- `wait` 패턴은 echo된 명령 문자열에 먼저 매칭됨 — 출력 전용 고유 문자열 사용 (→ `references/troubleshooting.md` CASE-001)
- Codex CLI는 `codex exec --full-auto` 사용 — `--approval-mode` 폐기됨
- Codex 한글 경로 UTF-8 header 경고는 무시 가능 — 자동 재연결됨
