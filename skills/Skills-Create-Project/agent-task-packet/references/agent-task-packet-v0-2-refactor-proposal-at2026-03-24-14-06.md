# agent-task-packet v0.2 Refactor Proposal

## Purpose

이 문서는 `agent-task-packet`을 즉시 교체하지 않고, 현재 `v0.1` core contract를 유지한 채 `v0.2 extended profile`과 orchestration boundary를 재정렬하기 위한 설계 초안이다.

핵심 방향은 다음과 같다.

- `v0.1` packet core는 계속 유효하다.
- packet은 계속 **불변 작업 계약서**여야 한다.
- mutable execution state는 packet 바깥으로 밀어낸다.
- richer metadata는 core breaking change가 아니라 **extended profile**로 제안한다.
- `dispatch`와 `runtime`의 ownership을 다시 명확히 한다.

## Problem Statement

`agent-task-packet`은 현재 여러 작업 흐름의 공용 계약이 되면서 영향력이 과도하게 커졌다.

실제 운영에서는 다음 압력이 packet 본체로 들어오고 있다.

- worktree/branch 할당 정보
- launch/runtime 정보
- phase progression과 local progress
- richer reporting/env/source-of-truth metadata
- Langfuse/trace/reporting 연결

이 압력을 packet 본체에 그대로 흡수하면 다음 문제가 생긴다.

- `packet`과 `dispatch`의 책임 경계가 흐려진다.
- `packet`과 `runtime registry`가 경쟁한다.
- 기존 `v0.1` consumer가 깨진다.
- local extension과 canonical contract가 섞여 drift가 생긴다.

## Design Goals

1. `v0.1` packet core 호환성을 유지한다.
2. packet을 immutable contract로 계속 유지한다.
3. `dispatch`를 canonical mutable execution-prep state로 고정한다.
4. `runtime`을 launch/session/log ownership layer로 고정한다.
5. richer metadata는 optional extended profile로 수용한다.
6. local task progress가 필요해도 dispatch canonical state와 경쟁하지 않게 한다.

## Non-Goals

- `v0.1` packet contract를 즉시 폐기하지 않는다.
- `dispatch`의 canonical mutable state를 packet으로 옮기지 않는다.
- `runtime/session` 정보를 packet에 넣지 않는다.
- 기존 `render-prompt` consumer를 깨는 breaking change를 바로 도입하지 않는다.
- actual runtime example을 그대로 standard schema source of truth로 승격하지 않는다.

## Boundary Table

| Layer | Canonical Owner | Core Question | Must Contain | Must Not Contain | Notes |
|---|---|---|---|---|---|
| `packet core` | `agent-task-packet` | 이 작업은 무엇을 왜 어디까지 하는가 | immutable task contract, scope, non-goals, done-definition, required checks, deliverables | runtime status, worktree allocation, session/process state | `v0.1` 유지 대상 |
| `packet extended` | `agent-task-packet` | core를 깨지 않고 어떤 추가 metadata를 실을 것인가 | optional env/source-of-truth/reporting/stop-condition hints | canonical dispatch status, tmux/process ownership, runtime logs | opt-in profile, local adoption 가능 |
| `dispatch` | `codex-worktree-dispatch` | 누가 어느 branch/worktree에서 어떻게 배치되는가 | branch, worktree_path, status, locked_paths, assignment, transition history | packet goal/done_definition 원문 중복, runtime engine ownership | canonical mutable execution-prep state |
| `runtime` | `codex-tmux-orchestrator` | ready dispatch를 실제로 어떻게 실행하고 추적하는가 | tmux session, runtime registry, heartbeat, launch/restart/kill/cleanup, live logs | packet contract mutation, dispatch ownership 대체 | execution/session layer |

## Proposed Ownership Model

### 1. Packet Core

`packet core`는 계속 `v0.1` contract를 따른다.

대표 필드:

- `packet_version`
- `task_id`
- `title`
- `goal`
- `why`
- `allowed_paths`
- `context_files`
- `priority`
- `constraints`
- `done_definition`
- `required_checks`
- `deliverables`
- `revision`
- `created_at`
- `created_by`
- `updated_at`

현재 optional field 중 계속 core에 둘 수 있는 것:

- `forbidden_paths`
- `depends_on`
- `parallel_group`
- `non_goals`
- `handoff_notes`
- `branch_hint`
- `worktree_hint`
- `launch_hint`
- `trace_id`
- `parent_task_id`

강한 규칙:

- `branch_hint`, `worktree_hint`, `launch_hint`는 계속 **hint only**다.
- 실제 branch/worktree/session ownership은 packet에 없다.
- `done_definition`은 당분간 `string[]`를 유지한다.
- `non_goals`의 canonical shape는 현재 object form을 유지한다.

### 2. Packet Extended Profile

`packet extended`는 core를 깨지 않고 richer metadata를 추가하기 위한 opt-in profile이다.

후보 필드:

- `packet_profile`
- `repo_root`
- `source_of_truth`
- `env_requirements`
- `stop_conditions`
- `failure_guide`
- `report_format`
- `timeout_minutes`

제안 원칙:

- `v0.1` packet이 계속 canonical minimal packet이다.
- extended packet은 core 위에 덧붙는 optional profile이다.
- consumer는 `standard`와 `extended`를 구분해 읽을 수 있어야 한다.
- extended profile도 runtime/state ownership을 가져가면 안 된다.

### 3. Dispatch

`dispatch`는 계속 canonical mutable execution-prep state다.

대표 필드:

- `dispatch_id`
- `task_id`
- `packet_path`
- `branch`
- `worktree_path`
- `assigned_agent`
- `status`
- `locked_paths`
- `history`
- `retry_count`
- `merge_target`

강한 규칙:

- dispatch는 packet의 `goal`, `why`, `done_definition`, `required_checks`, `deliverables`를 canonical source로 다시 소유하지 않는다.
- dispatch는 packet scope를 넓히지 않는다.
- dispatch는 branch/worktree allocation의 owner다.
- dispatch는 mutable status transition의 owner다.

### 4. Runtime

`runtime`은 실제 launch/session/log/heartbeat layer다.

대표 책임:

- ready dispatch preflight
- tmux session 생성
- launch/restart/kill/cleanup
- runtime registry 유지
- heartbeat/stale detection
- stdout/stderr/log ownership

강한 규칙:

- runtime은 packet contract를 수정하지 않는다.
- runtime은 dispatch를 대체하지 않는다.
- runtime은 session/process/log ownership을 가진다.
- dispatch는 runtime linkage를 참조할 수 있어도 execution engine owner는 아니다.

### 5. Optional Task-Local Progress Companion

local mutable progress가 필요하면 별도 companion file로 둘 수 있다.

다만 이 companion은 다음 경계를 넘으면 안 된다.

- dispatch canonical status ownership 대체 금지
- merge readiness ownership 대체 금지
- worktree allocation ownership 대체 금지
- tmux/session ownership 대체 금지

즉 이 companion은 다음 수준까지만 허용하는 편이 안전하다.

- worker-local phase note
- local observations
- temporary metric scratchpad
- local phase history

권장 명칭:

- `task-local progress companion`

비권장 명칭:

- generic `task_state`를 canonical mutable state처럼 부르는 것

## Compatibility Decisions

### Keep

- `packet_version: "0.1"` core packets
- current `done_definition: string[]`
- current `required_checks: object[]`
- current `deliverables: object[]`
- current `branch_hint/worktree_hint/launch_hint` semantics

### Do Not Change Immediately

- `done_definition`을 object array로 바꾸지 않는다.
- `non_goals` canonical object form을 즉시 폐기하지 않는다.
- `packet_builder render-prompt` consumer를 깨는 field change를 넣지 않는다.

### If We Need Structured Done Definition Later

가능한 안전한 경로:

1. `done_definition`은 core에서 `string[]` 유지
2. extended profile에 auxiliary mapping 추가 검토
3. breaking schema change가 정말 필요하면 아래를 같이 바꾼다

- `references/packet-fields.md`
- `references/packet-examples.md`
- `scripts/packet_builder.py`
- validator / tests

## Recommended Migration Path

### Phase A. Boundary Clarification

- packet / dispatch / runtime ownership wording 먼저 정리
- `v0.1` packet core가 immutable contract라는 점 재강조
- dispatch가 canonical mutable state라는 점 재강조

### Phase B. Extended Profile Spec

- `packet_profile: standard | extended` 같은 구분자 검토
- extended-only field를 별도 섹션으로 문서화
- core validator와 extended validator 경계 정의

### Phase C. Builder / Validator Support

- `packet_builder.py`가 standard packet과 extended packet을 둘 다 읽을 수 있게 조정
- render path는 core field 중심 유지
- optional field는 consumer-safe 방식으로만 반영

### Phase D. Downstream Adoption

- downstream local templates를 standard/extended로 재정렬
- runtime example은 evidence로만 유지
- dispatch/runtime consumer가 boundary wording에 맞는지 재검토

## Documents To Update If Proposal Is Accepted

### Immediate Canonical Docs

- [agent-task-packet/SKILL.md](../SKILL.md)
- [packet-fields.md](packet-fields.md)
- [packet-examples.md](packet-examples.md)
- [checklist.md](checklist.md)
- [Boundary-of-Responsibility-2026-03-15-00-55.md](Boundary-of-Responsibility-2026-03-15-00-55.md)
- [agent-task-packet-entrypoint-details-at2026-03-19-22-24.md](agent-task-packet-entrypoint-details-at2026-03-19-22-24.md)
- [troubleshooting.md](troubleshooting.md)

### Immediate Canonical Code

- [scripts/packet_builder.py](../scripts/packet_builder.py)
- packet builder tests adjacent to the script

### Adjacent Boundary Docs

- [codex-worktree-dispatch/references/dispatch-fields.md](../../codex-worktree-dispatch/references/dispatch-fields.md)
- [codex-worktree-dispatch/SKILL.md](../../codex-worktree-dispatch/SKILL.md)
- [codex-tmux-orchestrator/SKILL.md](../../codex-tmux-orchestrator/SKILL.md)

### Downstream Local Adopters To Revisit After Acceptance

이 경로들은 canonical source of truth가 아니라 downstream adopters / evidence다.

- `my-second-identity/template/task_packet_standard_template.json`
- `my-second-identity/template/task_packet_extended_template.json`
- `my-second-identity/template/task_state_standard_template.json`
- `my-second-identity/template/task_state_extended_template.json`
- `my-second-identity/template/dispatch_template.json`
- `my-second-identity/.codex/packets/TASK-DOCLING-ENV-0001.json`
- `my-second-identity/.codex/dispatch/DISPATCH-0001.json`

## Acceptance Criteria

- `v0.1` packet example and existing packet files continue to validate.
- `render-prompt` output for current standard packets does not regress.
- packet docs clearly say runtime/session/process fields are forbidden in packet.
- dispatch docs clearly say packet contract text is not duplicated canonical state.
- runtime docs clearly say packet is read-only and runtime owns execution/session tracking.
- extended profile is documented as optional, not as a forced replacement of `v0.1`.
- any local progress companion is explicitly described as non-canonical relative to dispatch.

## Recommendation

가장 안전한 리팩토링 방향은 다음 한 줄로 요약된다.

`agent-task-packet`은 더 많은 상태를 먹는 방향으로 커지지 말고, `v0.1` core contract를 유지한 채 `extended profile`과 `dispatch/runtime boundary`를 명시적으로 분리하는 방향으로 갱신한다.
