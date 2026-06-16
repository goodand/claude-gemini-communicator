---
name: codex-worktree-dispatch
description: >-
  worktree-parallel family의 dispatch-state specialist. Use this skill when a
  task-packet must be assigned to a Codex worker via git worktree and dispatch
  state (branch, worktree, locked_paths, status) must be managed from queued to
  merged. broader multi-agent orchestration은 worktree-parallel을 사용하라.
---

# Codex Worktree Dispatch

task-packet(계약서)을 받아 "누가, 어디서, 어떤 상태인지"를 관리하는 mutable runtime 상태 레이어.

## When to use

- task-packet을 실제 worktree + branch로 배정할 때
- 병렬 작업 간 경로 충돌(locked_paths)을 사전 감지할 때
- worker 완료 후 merge 가능 여부를 판정할 때
- 오래된 dispatch/worktree를 정리할 때

## Workflow

1. **dispatch 생성** — `scripts/dispatch_manager.py new --packet <packet.json>` → packet 읽고 branch/worktree/dispatch 상태 파일 생성
2. **경로 선점 검사** — `scripts/dispatch_manager.py check-overlap` → 활성 dispatch 전체의 locked_paths 충돌 감지
3. **의존성·준비 확인** — `scripts/dispatch_manager.py ready <dispatch_id>` → depends_on 완료 + 경로 점유 확인 → status=ready
4. **상태 전이** — `scripts/dispatch_manager.py transition <dispatch_id> <new_status>` → 유효 전이만 허용, history 기록
5. **merge 판정** — `scripts/dispatch_manager.py merge-check <dispatch_id>` → status=complete + clean worktree + branch 존재 확인
6. **정리** — `scripts/dispatch_manager.py cleanup` → orphan dispatch/worktree 탐지·정리

## Scripts

- `scripts/dispatch_manager.py` — new/validate/status/show/list/check-overlap/ready/transition/merge-check/cleanup 통합 래퍼. `python3 scripts/dispatch_manager.py --help`

## References

- `references/dispatch-fields.md` — 전체 필드 정의, 상태 머신, locked_paths 규칙
- `references/dispatch-examples.md` — 4개 예시 (최소/병렬/의존성/완료→merge)
- `references/codex-worktree-dispatch-reference-2026-03-15-01-05.md` — 유사 오픈소스 7개 사례 조사
- `references/codex-worktree-dispatch-knowledge_base-2026-03-15-01-07.md` — URL Knowledge Base
- `references/codex-worktree-dispatch-checklist-2026-03-15-01-11.md` — v0.1 구현 체크리스트 (A-O)
- `references/troubleshooting.md` — Codex 실전 테스트에서 발견된 버그 케이스
- `references/clean-worktree-and-tracked-release-rules-at2026-06-15-20-22.md` — dispatch ownership, dirty-worktree reference-only, tracked-file(git ls-files) release scope, 의존성 ready gate, merge-after-review loop

## Notes

- dispatch는 **mutable 상태** — packet(불변 계약서)과 반대. 상태 전이마다 history에 기록
- 1:1:1 원칙 — 하나의 dispatch = 하나의 task = 하나의 branch = 하나의 worktree
- locked_paths ⊆ allowed_paths — dispatch가 packet의 허용 범위를 확장할 수 없다
- worktree 생성 성공 **전에** dispatch 파일을 쓰지 않는다 — orphan 방지 (→ `references/dispatch-fields.md`)
- goal/done_definition은 packet에만 존재 — dispatch에 중복 저장 금지 (→ Boundary-of-Responsibility)
- session_id/heartbeat_path/log_path는 예약 필드 — tmux-orchestrator가 채움
- locked_paths에 `..`, 절대경로, symlink 포함 시 validate 거부 — 경로 정규화 3종 검증 (→ `references/troubleshooting.md` CASE-001, CASE-003)
- 예외를 던질 수 있는 검증은 상태 변경 **전**에 수행 — "검증 → 변경" 순서 (→ `references/troubleshooting.md` CASE-002)
