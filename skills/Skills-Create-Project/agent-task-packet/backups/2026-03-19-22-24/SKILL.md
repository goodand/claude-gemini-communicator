---
name: agent-task-packet
description: >-
  Use this skill when assigning a task to a Codex worker or sub-agent —
  standardizes the handoff packet with goal, scope, non-goals, done-definition,
  and required checks so the worker stays within bounds.
  Codex worker에게 작업을 할당할 때 표준화된 패킷으로 범위·비목표·완료 조건을 명시한다.
---

# Agent Task Packet

worker에게 넘기는 불변 작업 계약서. 범위 이탈과 handoff 품질 저하를 방지한다.

## When to use

- Codex worker에게 구현 작업을 할당할 때
- 여러 sub-agent에게 병렬 작업을 분배할 때
- 작업 완료 조건을 기계적으로 검증해야 할 때
- worker가 엉뚱한 범위를 건드리는 문제가 반복될 때

## Workflow

1. **패킷 생성** — `scripts/packet_builder.py new --task-id TASK-0001 --title "제목"` → scaffold JSON 생성 후 goal, allowed_paths, done_definition 채움
2. **비목표 분류** — non_goals에 Case 태그 부여: `state`, `type`, `performance:null|over|under` (→ `references/packet-fields.md` non_goals 구조)
3. **패킷 검증** — `scripts/packet_builder.py validate <file>` → 필수 필드, 금지 필드, 경로 겹침, 비목표 형식 확인
4. **경로 겹침 검사** — 병렬 작업 시 `scripts/packet_builder.py check-paths <file1> <file2>` → allowed_paths 충돌 감지
5. **worker 프롬프트 생성** — `scripts/packet_builder.py render-prompt <file>` → 3블록 compact prompt (Goal / Scope / Done Definition)
6. **완료 검증** — worker 결과물을 done_definition + required_checks 기준으로 판정

## Scripts

- `scripts/packet_builder.py` — new/validate/show/render-prompt/list/check-paths/update-revision 통합 래퍼. `python3 scripts/packet_builder.py --help`

## References

- `references/packet-fields.md` — 전체 필드 정의, constraints/non_goals/required_checks/deliverables 구조
- `references/packet-examples.md` — 5개 예시 (최소/파일수정/분석/의존성/비목표)
- `references/legacy-safe-handoff-clause-at2026-03-19-21-34.md` — delete/move/overwrite 전에 backup을 강제하는 공용 clause
- `references/Boundary-of-Responsibility-2026-03-15-00-55.md` — task-packet vs worktree-dispatch 책임 경계표
- `references/task-reference-at2026-03-15-00-52.md` — 유사 오픈소스 10개 사례 조사
- `references/checklist.md` — v0.1 구현 체크리스트 (Phase 0-17)
- `references/troubleshooting.md` — Codex 실전 테스트에서 발견된 버그 케이스

## Notes

- packet은 **불변 계약서** — 수정 시 revision 증가, task_id는 유지 (→ `references/packet-fields.md`)
- non_goals는 "중요하지 않은 것"이 아니라 **이번 태스크의 책임 경계를 확정하는 장치** (→ `references/packet-fields.md` 비목표 가이드)
- runtime 상태(status, pid, session_id 등)는 packet에 넣지 않는다 — dispatch가 관리 (→ `references/Boundary-of-Responsibility-2026-03-15-00-55.md`)
- allowed_paths 밖 파일 수정은 패킷 위반 — worker에게 명시적으로 금지
- delete/move/rename/overwrite가 조금이라도 있으면 `references/legacy-safe-handoff-clause-at2026-03-19-21-34.md`를 packet에 같이 붙인다
- done_definition은 기계 검증 가능한 형태로 작성 (exit code, 파일 존재, 패턴 매칭)
- 필수 필드는 "존재" 뿐 아니라 "의미 있는 값" 검증 필수 — `why` 최소 5자 (→ `references/troubleshooting.md` CASE-001)
- `dict.get(key, default)`는 키가 없을 때만 default 반환 — 빈 문자열은 별도 분기 처리 (→ `references/troubleshooting.md` CASE-002)
