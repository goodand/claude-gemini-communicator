# agent-task-packet 엔트리포인트 상세 안내

이 문서는 [agent-task-packet/SKILL.md](../SKILL.md)에서 생략된 상세 운영 절차만 유지한다.

## When to use

- Codex worker에게 구현 작업을 할당할 때
- 여러 sub-agent에게 병렬 작업을 분배할 때
- 작업 완료 조건을 기계적으로 검증해야 할 때
- worker가 엉뚱한 범위를 건드리는 문제가 반복될 때

## Workflow

1. **패킷 생성** — `scripts/packet_builder.py new --task-id TASK-0001 --title "제목"` → scaffold JSON 생성 후 goal, allowed_paths, done_definition 채움
2. **비목표 분류** — `non_goals`에 case 태그 부여: `state`, `type`, `performance:null|over|under` (→ [references/packet-fields.md](packet-fields.md))
3. **패킷 검증** — `scripts/packet_builder.py validate <file>` → 필수 필드, 금지 필드, 경로 겹침, 비목표 형식 확인
4. **경로 겹침 검사** — 병렬 작업 시 `scripts/packet_builder.py check-paths <file1> <file2>` 사용
5. **worker 프롬프트 생성** — `scripts/packet_builder.py render-prompt <file>` → Goal / Scope / Done Definition 블록
6. **완료 검증** — worker 산출물을 done_definition + required_checks로 판정

## Notes

- packet은 **불변 작업 계약서 (immutable task contract)** 다. 수정할 때는 revision 증가, task_id 유지
- non_goals는 이번 태스크의 책임 경계를 확정하는 장치
- **runtime/session/process field 금지** — `status`, `session_id`, `pid`, `heartbeat`, `log_path`는 packet에 넣지 않는다
- **dispatch 항목 중복 금지** — dispatch가 canonical owner인 branch/worktree allocation, mutable status를 packet에 중복 저장하지 않는다
- **hint only** — `branch_hint`, `worktree_hint`, `launch_hint`는 dispatch/runtime에 대한 힌트일 뿐, 실제 ownership은 packet에 없다
- **local progress companion** — worker-local phase note나 scratch metric이 필요해도 dispatch canonical state를 대체하지 않는다
- delete/move/rename/overwrite가 있으면 백업을 먼저 남긴다 ([references/legacy-safe-handoff-clause-at2026-03-19-21-34.md](legacy-safe-handoff-clause-at2026-03-19-21-34.md))
- `why`는 최소 5자 이상, `goal`은 최소 10자 이상을 요구한다
