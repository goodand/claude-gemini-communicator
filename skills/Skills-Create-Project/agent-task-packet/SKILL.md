---
name: agent-task-packet
description: >-
  worktree-parallel family의 handoff-packet specialist. Use this skill when a
  task must be assigned to a Codex worker or sub-agent with a standardized
  packet containing goal, scope, non-goals, done-definition, and required checks.
  broader multi-agent orchestration은 worktree-parallel을 사용하라.
---

# Agent Task Packet

worker에게 넘기는 **불변 작업 계약서 (immutable task contract)**. 범위 이탈과 handoff 품질 저하를 방지한다.

**Boundary rule** — packet은 `status`, `session_id`, `pid`, `heartbeat`, `log_path` 등 runtime/session/process field를 포함하지 않는다. `branch_hint`, `worktree_hint`, `launch_hint`는 hint only이며 실제 allocation ownership은 dispatch에 있다.

`scripts/packet_builder.py`는 아래 3개 명령으로 운영한다.

- `packet_builder.py new --task-id TASK-0001 --title "..."`
- `packet_builder.py validate <packet-json>`
- `packet_builder.py render-prompt <packet-json>`

상세 워크플로와 필드 규칙은 [entrypoint 상세 안내](references/agent-task-packet-entrypoint-details-at2026-03-19-22-24.md)를 따른다.

## References

- [references/packet-fields.md](references/packet-fields.md)
- [references/packet-examples.md](references/packet-examples.md)
- [references/legacy-safe-handoff-clause-at2026-03-19-21-34.md](references/legacy-safe-handoff-clause-at2026-03-19-21-34.md)
- [references/Boundary-of-Responsibility-2026-03-15-00-55.md](references/Boundary-of-Responsibility-2026-03-15-00-55.md)
- [references/task-reference-at2026-03-15-00-52.md](references/task-reference-at2026-03-15-00-52.md)
- [references/checklist.md](references/checklist.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/packet-dispatch-boundary-and-checks-at2026-06-15-20-22.md](references/packet-dispatch-boundary-and-checks-at2026-06-15-20-22.md) — packet(불변 계약)/dispatch(런타임 상태)/progress companion 경계, 구조화 required_checks, 의존성 표현 규칙

## Scripts

- [scripts/packet_builder.py](scripts/packet_builder.py) — new / validate / show / render-prompt / list / check-paths / update-revision
