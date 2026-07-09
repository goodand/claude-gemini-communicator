# agent-task-packet v0.2 Refactor Worklist

## Scope

이 문서는 [agent-task-packet-v0-2-refactor-proposal-at2026-03-24-14-06.md](agent-task-packet-v0-2-refactor-proposal-at2026-03-24-14-06.md)를 실제 수정 순서로 번역한 작업표다.

목표는 다음 두 가지를 동시에 만족하는 것이다.

- 기존 `v0.1` packet consumer를 깨지 않는다.
- `core / extended / dispatch / runtime` 경계를 문서와 코드에서 더 명확히 한다.

## Priority Order

### P0. Boundary Wording First

먼저 바꿔야 할 것은 schema가 아니라 **ownership wording**이다.

대상 문서:

- [agent-task-packet/SKILL.md](../SKILL.md)
- [Boundary-of-Responsibility-2026-03-15-00-55.md](Boundary-of-Responsibility-2026-03-15-00-55.md)
- [agent-task-packet-entrypoint-details-at2026-03-19-22-24.md](agent-task-packet-entrypoint-details-at2026-03-19-22-24.md)
- [codex-worktree-dispatch/references/dispatch-fields.md](../../codex-worktree-dispatch/references/dispatch-fields.md)
- [codex-tmux-orchestrator/SKILL.md](../../codex-tmux-orchestrator/SKILL.md)

해야 할 일:

- `packet`은 immutable contract라고 다시 고정
- `dispatch`는 canonical mutable execution-prep state라고 다시 고정
- `runtime`은 launch/session/log ownership layer라고 다시 고정
- `branch_hint`, `worktree_hint`, `launch_hint`가 hint only라는 점을 분명히 적기
- local progress/state가 필요해도 dispatch canonical state를 대체하지 않는다고 못박기

완료 기준:

- packet 문서에 runtime/session/process field 금지 규칙이 더 선명해짐
- dispatch 문서에 packet contract 원문 중복 저장 금지 규칙이 유지됨
- runtime 문서에 packet read-only 원칙이 더 명시됨

### P1. Core vs Extended Profile Spec

두 번째는 `v0.1 core`와 `extended profile`의 문서상 분리다.

대상 문서:

- [packet-fields.md](packet-fields.md)
- [packet-examples.md](packet-examples.md)
- [checklist.md](checklist.md)

해야 할 일:

- `packet core` 필드와 `extended profile` 후보 필드를 구분
- `v0.1` core canonical field set을 유지
- extended 후보 필드는 별도 섹션으로 문서화
- `packet_profile: standard | extended` 같은 구분자를 도입할지 결정
- `repo_root`, `source_of_truth`, `env_requirements`, `stop_conditions`, `failure_guide`, `report_format`, `timeout_minutes`를 core가 아니라 extended 쪽으로 정리

완료 기준:

- `packet-fields.md`에서 무엇이 core이고 무엇이 extended candidate인지 한눈에 보임
- `packet-examples.md`에서 standard packet 예시와 extended packet 예시를 분리 가능
- `checklist.md`가 더 이상 runtime/state field를 packet schema에 섞지 않음

### P2. Consumer Compatibility Lock

세 번째는 existing consumer를 깨지 않는 호환성 고정이다.

대상 코드:

- [scripts/packet_builder.py](../scripts/packet_builder.py)

대상 문서:

- [packet-fields.md](packet-fields.md)
- [packet-examples.md](packet-examples.md)

해야 할 일:

- `done_definition`을 당분간 `string[]`로 유지
- `required_checks`, `deliverables` consumer가 current shape를 계속 읽게 유지
- `render-prompt`가 standard packet에 대해 그대로 동작하는지 확인
- extended field가 추가돼도 render path가 깨지지 않게 방어

완료 기준:

- 현재 `v0.1` packet 파일이 계속 validate 가능
- `render-prompt` 출력이 regression 없이 유지
- `done_definition` object-array 전환은 proposal-only 상태로 남음

### P3. Builder / Validator Extension Path

네 번째는 extended profile을 실제로 읽을 수 있는 코드 경로를 여는 일이다.

대상 코드:

- [scripts/packet_builder.py](../scripts/packet_builder.py)
- packet builder tests

해야 할 일:

- standard packet과 extended packet을 모두 읽는 validator 전략 정의
- extended-only field가 있어도 current commands가 fail하지 않게 처리
- 필요하면 `validate --profile standard|extended` 같은 분기 검토
- scaffold 생성 시 standard 기본값과 extended 템플릿 분리 검토

완료 기준:

- standard packet은 계속 zero-regression
- extended packet은 opt-in 방식으로 validate 가능
- builder가 extended field를 runtime/state owner처럼 해석하지 않음

### P4. Optional Task-Local Progress Companion

다섯 번째는 local progress companion을 다룰지 결정하는 것이다.

주의:

- 이 단계는 `dispatch` canonical state와 경쟁하지 않는다는 문구가 먼저 닫힌 뒤에만 진행한다.

대상 인접 문서:

- [Boundary-of-Responsibility-2026-03-15-00-55.md](Boundary-of-Responsibility-2026-03-15-00-55.md)
- [codex-worktree-dispatch/references/dispatch-fields.md](../../codex-worktree-dispatch/references/dispatch-fields.md)

해야 할 일:

- `task-local progress companion`이 canonical state가 아님을 명시
- worker-local phase note, local observations, scratch metric 정도까지만 허용
- merge readiness, branch/worktree allocation, runtime session ownership은 금지

완료 기준:

- local state가 필요해도 `dispatch` owner와 충돌하지 않음
- naming이 generic `task_state canonical`처럼 읽히지 않음

### P5. Downstream Adoption Review

마지막은 downstream local adopter를 다시 맞추는 일이다.

대상:

- `my-second-identity/template/task_packet_standard_template.json`
- `my-second-identity/template/task_packet_extended_template.json`
- `my-second-identity/template/task_state_standard_template.json`
- `my-second-identity/template/task_state_extended_template.json`
- `my-second-identity/template/dispatch_template.json`

해야 할 일:

- standard packet template이 canonical `v0.1 core`와 충돌하지 않는지 재검토
- extended packet template은 local extension임을 명시
- state template이 dispatch canonical state를 침범하는지 재검토
- actual runtime examples는 evidence로만 취급

완료 기준:

- downstream template이 canonical source of truth를 넘어서지 않음
- local extension과 canonical contract가 명확히 구분됨

## Concrete Edit Order

가장 안전한 실제 수정 순서는 이렇다.

1. [Boundary-of-Responsibility-2026-03-15-00-55.md](Boundary-of-Responsibility-2026-03-15-00-55.md)
2. [agent-task-packet/SKILL.md](../SKILL.md)
3. [agent-task-packet-entrypoint-details-at2026-03-19-22-24.md](agent-task-packet-entrypoint-details-at2026-03-19-22-24.md)
4. [packet-fields.md](packet-fields.md)
5. [packet-examples.md](packet-examples.md)
6. [checklist.md](checklist.md)
7. [scripts/packet_builder.py](../scripts/packet_builder.py)
8. packet builder tests
9. [codex-worktree-dispatch/references/dispatch-fields.md](../../codex-worktree-dispatch/references/dispatch-fields.md)
10. [codex-tmux-orchestrator/SKILL.md](../../codex-tmux-orchestrator/SKILL.md)
11. downstream local templates

## Suggested Change Bundles

### Bundle 1. Boundary-only docs

포함:

- `Boundary-of-Responsibility`
- `agent-task-packet/SKILL.md`
- `entrypoint details`
- `dispatch-fields`
- `codex-tmux-orchestrator/SKILL.md`

목적:

- ownership wording 정리

### Bundle 2. Core vs Extended packet docs

포함:

- `packet-fields.md`
- `packet-examples.md`
- `checklist.md`

목적:

- `v0.1 core`와 `extended profile` 문서 분리

### Bundle 3. Builder compatibility

포함:

- `scripts/packet_builder.py`
- tests

목적:

- standard packet zero-regression 유지
- extended packet opt-in 수용

### Bundle 4. Downstream template alignment

포함:

- local templates
- local runtime examples review

목적:

- canonical source와 local adopter 정렬

## Red Flags

다음은 리팩토링 중 피해야 한다.

- `done_definition`을 문서만 바꾸고 builder를 안 바꾸는 것
- `task_state`를 dispatch canonical state처럼 부르는 것
- packet에 `status`, `session_id`, `pid`, `heartbeat`, `log_path`를 다시 넣는 것
- dispatch에 `goal`, `why`, `done_definition` 원문을 canonical source처럼 중복 저장하는 것
- runtime example을 표준 schema source of truth로 승격하는 것

## Minimal Success Definition

이번 리팩토링이 성공했다고 볼 최소 조건은 이렇다.

- `agent-task-packet`은 계속 immutable contract skill로 읽힌다.
- `codex-worktree-dispatch`는 계속 canonical mutable state owner로 읽힌다.
- `codex-tmux-orchestrator`는 계속 runtime owner로 읽힌다.
- `v0.1` packet file과 current builder는 깨지지 않는다.
- richer metadata 요구는 breaking core change가 아니라 extended profile로 수용된다.
