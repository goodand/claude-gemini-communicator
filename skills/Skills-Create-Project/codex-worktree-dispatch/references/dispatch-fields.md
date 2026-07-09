# Dispatch Fields Reference

dispatch는 **canonical mutable execution-prep state**다. branch/worktree allocation과 mutable status transition의 canonical owner이며, packet의 계약 내용을 중복 소유하지 않는다.

> 정합성 메모(R3): 이 문서는 dispatch 계약의 **reference owner**다. 실행용(machine) canonical은 레지스트리 `references/contracts/dispatch_contract_v0_1.json`이며, 코드의 dispatch 상태머신 사본(`dispatch_manager.py`의 `VALID_*`/`validate_dispatch`, `agent-task-packet/scripts/packet_builder.py`의 `DISPATCH_*`)은 그 레지스트리의 projection으로 `_shared/scripts/audit_contract_sync.py`가 감사한다(`dispatch_mgr_*` facts 포함). projection-locality 경계는 [`../../agent-task-packet/references/packet-dispatch-boundary-and-checks-at2026-06-15-20-22.md`](../../agent-task-packet/references/packet-dispatch-boundary-and-checks-at2026-06-15-20-22.md) 참고.

## 필수 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `dispatch_version` | string | 스키마 버전 (현재 "0.1") |
| `dispatch_id` | string | 고유 식별자 (예: "DISPATCH-0001") |
| `task_id` | string | 대응하는 task-packet의 task_id |
| `packet_path` | string | task-packet JSON 경로 (repo root 상대) |
| `branch` | string | 생성된 git branch명 |
| `worktree_path` | string | git worktree 경로 |
| `assigned_agent` | string | 배정된 agent (예: "codex", "claude") |
| `status` | enum | 현재 상태 (아래 상태 머신 참조) |
| `locked_paths` | string[] | 이 dispatch가 점유하는 경로 (⊆ allowed_paths) |
| `history` | object[] | 상태 전이 이력 (append-only) |
| `created_at` | string | ISO-8601 생성 시각 |
| `created_by` | string | 작성자 |
| `updated_at` | string | ISO-8601 최종 수정 시각 |

## 선택 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `owner_model` | string | agent 모델명 (예: "gpt-5.3-codex") |
| `status_reason` | string | 현재 상태 사유 |
| `depends_on_dispatch_ids` | string[] | 선행 dispatch_id 목록 |
| `merge_target` | string | merge 대상 branch (기본: main) |
| `retry_count` | integer | 재시도 횟수 (0부터) |
| `max_retries` | integer | 최대 재시도 (기본 3) |
| `tmux_session_hint` | string | tmux 세션명 힌트 |
| `launch_command_hint` | string | 실행 명령 힌트 |
| `error_log` | object[] | 에러 이력 (append-only). 각 항목은 phase, message, at 포함 |
| `escalated` | boolean | 상위 agent에 에스컬레이션 여부 (기본 false) |
| `escalation_reason` | string\|null | 에스컬레이션 사유 |

## 예약 필드 (dispatch가 생성하되, 다른 skill이 채움)

tmux-orchestrator, session-monitor가 런타임에 채우는 필드.

| 필드 | 채우는 주체 | 설명 |
|------|-------------|------|
| `session_id` | tmux-orchestrator | tmux 세션 ID |
| `heartbeat_path` | session-monitor | heartbeat 파일 경로 |
| `log_path` | tmux-orchestrator | 로그 파일 경로 |

## 금지 필드 (dispatch에 넣지 않는다)

packet의 계약 내용을 canonical source처럼 중복 저장하지 않는다. dispatch는 `packet_path`로 참조만 한다.

`goal`, `why`, `done_definition`, `required_checks`, `deliverables`, `constraints`, `non_goals`, `context_files`, `priority`

## Local Progress Companion 경계

worker-local phase note, observations, scratch metric 등 local mutable progress가 필요하면 별도 companion file로 둘 수 있다. 단, 이 companion은 dispatch canonical state를 대체하지 않는다. merge readiness, branch/worktree allocation, status transition ownership은 dispatch에만 있다.

## 상태 머신 (Status Machine)

```
queued → ready → running → complete → merged
  │        │        │          │
  │        │        ├→ failed ─┤
  │        │        │          │
  │        ├→ blocked ─→ ready │
  │        │                   │
  └→ abandoned                 └→ abandoned
```

### 유효 전이 테이블

| From | To | 조건 |
|------|----|------|
| `queued` | `ready` | 의존성 완료 + 경로 점유 없음 |
| `queued` | `blocked` | 의존성 미완료 또는 경로 충돌 발견 |
| `queued` | `abandoned` | 수동 취소 |
| `ready` | `running` | agent 시작 |
| `ready` | `blocked` | 경로 충돌 또는 의존성 미완료 재발견 |
| `running` | `complete` | worker가 done_definition 충족 보고 |
| `running` | `failed` | worker 실패 |
| `running` | `abandoned` | 수동 취소 |
| `blocked` | `ready` | 차단 해소 |
| `failed` | `running` | 재시도 (retry_count < max_retries) |
| `complete` | `merged` | merge-check 통과 후 실제 merge |
| `complete` | `abandoned` | merge 포기 |

### history 구조

```json
{
  "from": "queued",
  "to": "ready",
  "at": "2026-03-15T02:30:00+09:00",
  "by": "claude",
  "reason": "의존성 DISPATCH-0001 완료, 경로 점유 없음"
}
```

## locked_paths 규칙

- locked_paths ⊆ packet의 allowed_paths — 범위 확장 불가
- 경로 겹침 검사는 **prefix-level** — `src/auth/`는 `src/auth/login.py`와 충돌
- 경로 정규화: trailing `/` 통일
- **forbid_path_traversal**: `..` 포함 경로 금지
- **forbid_absolute_path**: `/`로 시작하는 절대경로 금지 — 모든 경로는 repo root 상대경로
- **forbid_symlink**: symlink 경로 금지 — 실제 경로로 해제 후 비교
- status가 `merged` 또는 `abandoned`이면 locked_paths 해제

## 파일 저장 규칙

- 위치: `.codex/dispatch/DISPATCH-####.json`
- worktree 생성 성공 **이후**에만 dispatch 파일 작성
- dispatch 파일은 1 task = 1 file
- 재시도 시 같은 dispatch 파일의 retry_count 증가 (새 파일 생성 아님)
