# Dispatch Examples

## TOC

1. [최소 dispatch](#1-최소-dispatch)
2. [병렬 작업 dispatch](#2-병렬-작업-dispatch)
3. [의존성 있는 dispatch](#3-의존성-있는-dispatch)
4. [완료 → merge 준비 dispatch](#4-완료--merge-준비-dispatch)

---

## 1. 최소 dispatch

단일 packet을 worktree로 배정하는 가장 단순한 dispatch.

```json
{
  "dispatch_version": "0.1",
  "dispatch_id": "DISPATCH-0001",
  "task_id": "TASK-0001",
  "packet_path": ".codex/packets/TASK-0001.json",
  "branch": "feat/codex-readme-fix",
  "worktree_path": ".worktrees/readme-fix",
  "assigned_agent": "codex",
  "status": "queued",
  "locked_paths": ["README.md"],
  "history": [
    {
      "from": null,
      "to": "queued",
      "at": "2026-03-15T02:30:00+09:00",
      "by": "claude",
      "reason": "dispatch 생성"
    }
  ],
  "created_at": "2026-03-15T02:30:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T02:30:00+09:00"
}
```

> **1:1:1 원칙**: TASK-0001 → DISPATCH-0001 → feat/codex-readme-fix → .worktrees/readme-fix. 각각 하나씩만.

---

## 2. 병렬 작업 dispatch

같은 parallel_group에서 서로 다른 경로를 점유하는 2개 dispatch.

```json
{
  "dispatch_version": "0.1",
  "dispatch_id": "DISPATCH-0010",
  "task_id": "TASK-0010",
  "packet_path": ".codex/packets/TASK-0010.json",
  "branch": "feat/codex-auth-module",
  "worktree_path": ".worktrees/auth-module",
  "assigned_agent": "codex",
  "owner_model": "gpt-5.3-codex",
  "status": "running",
  "locked_paths": ["src/auth/", "tests/test_auth.py"],
  "history": [
    {"from": null, "to": "queued", "at": "2026-03-15T02:30:00+09:00", "by": "claude", "reason": "dispatch 생성"},
    {"from": "queued", "to": "ready", "at": "2026-03-15T02:30:05+09:00", "by": "claude", "reason": "경로 점유 없음"},
    {"from": "ready", "to": "running", "at": "2026-03-15T02:30:10+09:00", "by": "claude", "reason": "Codex 시작"}
  ],
  "created_at": "2026-03-15T02:30:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T02:30:10+09:00"
}
```

```json
{
  "dispatch_version": "0.1",
  "dispatch_id": "DISPATCH-0011",
  "task_id": "TASK-0015",
  "packet_path": ".codex/packets/TASK-0015.json",
  "branch": "feat/codex-logging",
  "worktree_path": ".worktrees/logging",
  "assigned_agent": "codex",
  "status": "running",
  "locked_paths": ["src/logging/", "tests/test_logging.py"],
  "history": [
    {"from": null, "to": "queued", "at": "2026-03-15T02:30:00+09:00", "by": "claude", "reason": "dispatch 생성"},
    {"from": "queued", "to": "ready", "at": "2026-03-15T02:30:05+09:00", "by": "claude", "reason": "DISPATCH-0010과 경로 겹침 없음"},
    {"from": "ready", "to": "running", "at": "2026-03-15T02:30:12+09:00", "by": "claude", "reason": "Codex 시작"}
  ],
  "created_at": "2026-03-15T02:30:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T02:30:12+09:00"
}
```

> **경로 겹침 없음**: `src/auth/`와 `src/logging/`은 prefix-level에서 충돌하지 않으므로 병렬 실행 가능.

---

## 3. 의존성 있는 dispatch

DISPATCH-0010 완료 후에만 ready로 전이 가능.

```json
{
  "dispatch_version": "0.1",
  "dispatch_id": "DISPATCH-0012",
  "task_id": "TASK-0011",
  "packet_path": ".codex/packets/TASK-0011.json",
  "branch": "feat/codex-auth-routes",
  "worktree_path": ".worktrees/auth-routes",
  "assigned_agent": "codex",
  "status": "blocked",
  "status_reason": "DISPATCH-0010 미완료",
  "depends_on_dispatch_ids": ["DISPATCH-0010"],
  "locked_paths": ["src/routes/", "tests/test_routes.py"],
  "history": [
    {"from": null, "to": "queued", "at": "2026-03-15T02:30:00+09:00", "by": "claude", "reason": "dispatch 생성"},
    {"from": "queued", "to": "blocked", "at": "2026-03-15T02:30:05+09:00", "by": "claude", "reason": "의존성 DISPATCH-0010 미완료"}
  ],
  "created_at": "2026-03-15T02:30:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T02:30:05+09:00"
}
```

> **의존성 게이트**: `ready` 명령 실행 시 depends_on_dispatch_ids의 status가 모두 `complete` 또는 `merged`인지 확인.

---

## 4. 완료 → merge 준비 dispatch

worker가 done_definition을 충족하고 merge-check을 기다리는 상태.

```json
{
  "dispatch_version": "0.1",
  "dispatch_id": "DISPATCH-0010",
  "task_id": "TASK-0010",
  "packet_path": ".codex/packets/TASK-0010.json",
  "branch": "feat/codex-auth-module",
  "worktree_path": ".worktrees/auth-module",
  "assigned_agent": "codex",
  "owner_model": "gpt-5.3-codex",
  "status": "complete",
  "merge_target": "main",
  "locked_paths": ["src/auth/", "tests/test_auth.py"],
  "retry_count": 0,
  "history": [
    {"from": null, "to": "queued", "at": "2026-03-15T02:30:00+09:00", "by": "claude", "reason": "dispatch 생성"},
    {"from": "queued", "to": "ready", "at": "2026-03-15T02:30:05+09:00", "by": "claude", "reason": "경로 점유 없음"},
    {"from": "ready", "to": "running", "at": "2026-03-15T02:30:10+09:00", "by": "claude", "reason": "Codex 시작"},
    {"from": "running", "to": "complete", "at": "2026-03-15T03:15:00+09:00", "by": "codex", "reason": "done_definition 충족, pytest 통과"}
  ],
  "created_at": "2026-03-15T02:30:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T03:15:00+09:00"
}
```

> **merge-check 순서**: `merge-check DISPATCH-0010` → (1) status=complete 확인, (2) worktree clean 확인, (3) branch 존재 확인, (4) merge conflict 예측. 모두 통과 시 merge 진행 가능.
