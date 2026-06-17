---
name: codex-tmux-orchestrator
description: >-
  worktree-parallel family의 runtime-launch specialist. Use this skill when a
  ready dispatch must be launched into a Codex CLI tmux session with runtime
  registry, heartbeat/stale detection, and restart/cleanup/status support.
  broader multi-agent orchestration은 worktree-parallel을 사용하라.
---

# Codex Tmux Orchestrator

ready dispatch → tmux session → Codex CLI 실행 → 런타임 추적의 **launch/session/log ownership layer**.

## When to use

- dispatch status=ready인 작업을 Codex CLI로 실행할 때
- 실행 중인 세션의 상태(running/stale/failed)를 확인할 때
- 실패한 세션을 재시작하거나 stale 세션을 정리할 때
- 완료된 세션의 로그와 결과를 수집할 때

## Workflow

1. **preflight** — `scripts/orchestrator.py launch --dispatch <dispatch.json> --packet <packet.json>` → 12항목 사전 검증 (→ `references/codex-tmux-orchestrator-reference` §9)
2. **launch** — tmux session 생성 + Codex CLI 실행 + runtime registry 기록 + start marker 출력
3. **status** — `scripts/orchestrator.py status [--dispatch-id <id>]` → runtime 상태 + heartbeat + 마지막 출력
4. **restart** — `scripts/orchestrator.py restart --dispatch-id <id>` → failed/stale만 가능, attempt 증가
5. **kill** — `scripts/orchestrator.py kill --dispatch-id <id>` → 세션 종료 + runtime record 갱신
6. **cleanup** — `scripts/orchestrator.py cleanup` → stale/orphan 세션 탐지·정리

## Scripts

- `scripts/orchestrator.py` — launch/status/restart/kill/cleanup 통합 래퍼. `python3 scripts/orchestrator.py --help`

## References

- `references/codex-tmux-orchestrator-reference-2026-03-15-03-12.md` — 상세 설계: 정체성, 의존성, 책임 경계, launch contract, 상태 머신, marker protocol
- `references/codex-tmux-orchestrator-reference-2026-03-15-02-47.md` — 초기 사례 조사
- `references/codex-tmux-orchestrator-knowledge_base-2026-03-15-02-49.md` — 외부 참조 URL KB
- `references/codex-tmux-orchestrator-checklist-2026-03-15-02-51.md` — 구현 정합성 체크리스트
- `references/troubleshooting.md` — 실전 버그 케이스

## Notes

- **dispatch-first** — session 이름이 아니라 dispatch_id가 모든 조작의 출발점
- **session 존재 ≠ worker 건강** — heartbeat + marker로 실제 상태 판정 (→ reference §12)
- **preflight 전부 통과 전 launch 금지** — worktree 불일치, 중복 runtime, branch mismatch 등 12항목
- **이 skill은 worktree를 생성하지 않는다** — worktree-parallel/dispatch가 준비한 것을 소비만 한다
- **packet read-only** — packet은 불변 계약서이며 runtime이 수정하지 않는다. runtime은 tmux session, heartbeat, stdout/stderr/log ownership만 가진다
- **dispatch 대체 금지** — runtime은 dispatch의 canonical mutable status를 대체하지 않는다. status transition ownership은 dispatch에 있다
