# Decision Framework

작업 착수 전에 "무엇을 먼저 고칠지", "수정 범위를 어디까지 가져갈지"를 빠르게 고르기 위한 템플릿.

## Template 1: Minimal Patch First

작은 validator 누락이나 단일 출력 포맷 버그처럼 영향 범위가 좁을 때 사용.

### 1. Trigger

- 어떤 실패/버그가 관찰되었는가?

### 2. Problem Statement

- 지금 실패하는 동작 1문장
- 사용자 영향 1문장

### 3. Options

- A. 최소 코드 수정만 수행
- B. 코드 + 문서 + 회귀 검증까지 함께 수행

### 4. Decision Criteria

- 수정 범위가 작은가?
- source of truth가 명확한가?
- 후속 리스크가 낮은가?

### 5. Choice

- 선택안:
- 이유:

### 6. Execution

1. 코드 수정
2. 최소 smoke test
3. 필요 시 troubleshooting만 갱신


## Template 2: Contract Sync + Regression First

validator, schema, reference 문서, edge-case 결과가 같이 얽힌 "계약 정합성" 문제에 사용.

### 1. Trigger

- 어떤 검증 누락 또는 문서-코드 불일치가 발견되었는가?
- 이 이슈를 누가 발견했는가? (`edge-case-generator`, 리뷰, 실사용 등)

### 2. Contract Boundary

- 계약의 주체: 어떤 파일이 계약을 정의하는가?
- 구현의 주체: 어떤 코드가 계약을 집행하는가?
- 증거의 주체: 어떤 테스트/도구가 문제를 재현하는가?

### 3. Options

- A. 코드만 고치고 문서는 나중에 맞춘다
- B. 코드 + 문서 + troubleshooting + 회귀 검증을 한 번에 맞춘다

### 4. Decision Criteria

- 계약 위반이 재발하기 쉬운가?
- 문서와 validate가 같이 맞아야 하는가?
- 후속 skill이 이 계약에 의존하는가?
- 회귀 검증을 바로 돌릴 수 있는가?

### 5. Choice

- 선택안:
- 이유:

### 6. Execution Sequence

1. validate 수정
2. reference 문서 동기화
3. troubleshooting 기록
4. edge-case / regression 재실행
5. 잔여 리스크 분리

### 7. Evidence

- 수정 파일:
- 검증 명령:
- 결과:


## Applied Example: agent-task-packet / empty task_id

`Template 2`를 선택한다.

### 1. Trigger

- `edge-case-generator`가 빈 `task_id`가 `validate_packet()`을 통과하는 unexpected pass를 발견했다.

### 2. Contract Boundary

- 계약의 주체: `agent-task-packet/references/packet-fields.md`
- 구현의 주체: `agent-task-packet/scripts/packet_builder.py`
- 증거의 주체: `edge-case-generator/scripts/edgegen.py` 실행 결과

### 3. Options

- A. `validate_packet()`에 빈 문자열 검사만 추가
- B. `validate_packet()` 수정 + packet-fields 동기화 + troubleshooting 기록 + edge-case 회귀 실행

### 4. Decision Criteria

- packet은 불변 계약서라서 문서-코드 drift를 남기면 안 된다.
- `codex-worktree-dispatch` 등 후속 skill이 `task_id`를 전제로 동작한다.
- `edge-case-generator`가 이미 재현 케이스를 제공하므로 회귀 검증 비용이 낮다.

### 5. Choice

- 선택안: B
- 이유: 이번 이슈는 단순 문자열 검사 누락처럼 보여도, 실제로는 packet contract의 빈 값 허용 여부를 결정하는 문제라 코드만 고치면 정합성이 다시 깨진다.

### 6. Execution Sequence

1. `packet_builder.py`에 `task_id.strip()` 검증 추가
2. `packet-fields.md`에 "비어있지 않은 고유 식별자" 반영
3. `troubleshooting.md`에 CASE 추가
4. `edgegen.py run`으로 회귀 확인

### 7. Evidence

- 수정 파일:
  - `agent-task-packet/scripts/packet_builder.py`
  - `agent-task-packet/references/packet-fields.md`
  - `agent-task-packet/references/troubleshooting.md`
- 검증 명령:
  - `python3 edge-case-generator/scripts/edgegen.py generate --script agent-task-packet/scripts/packet_builder.py --output /tmp/edgegen-agent-task-packet-step1`
  - `python3 edge-case-generator/scripts/edgegen.py run --script agent-task-packet/scripts/packet_builder.py --cases /tmp/edgegen-agent-task-packet-step1`
- 결과:
  - `56/56 OK`, unexpected pass 0건


## Applied Example: codex-worktree-dispatch / linter-reverted contract checks

`Template 2`를 선택한다.

### 1. Trigger

- 외부 피드백 검증과 후속 확인 과정에서 `dispatch_manager.py`의 일부 계약 검증이 린터 수정 이후 되돌아간 것이 확인됐다.
- 되돌아간 항목은 `queued -> blocked`, `locked_paths ⊆ allowed_paths`, `symlink 금지`였다.

### 2. Contract Boundary

- 계약의 주체: `codex-worktree-dispatch/references/dispatch-fields.md`
- 구현의 주체: `codex-worktree-dispatch/scripts/dispatch_manager.py`
- 증거의 주체:
  - 직접 fixture 기반 validate/transition 실행
  - `edge-case-generator/scripts/edgegen.py` 회귀 실행 결과

### 3. Options

- A. `dispatch_manager.py` 코드만 복구
- B. reference를 source of truth로 고정하고, 코드 복구 + 직접 재현 테스트 + edge-case 회귀까지 수행

### 4. Decision Criteria

- dispatch는 packet/orchestrator/tmux 흐름의 중간 계약이라 drift가 전파되기 쉽다.
- 이번 문제는 "문서가 틀렸다"가 아니라 "코드가 문서에서 이탈했다"는 유형이다.
- 상태 전이와 경로 검증은 실사용 중 객체 오염이나 경로 충돌로 이어질 수 있어 회귀 확인이 필수다.

### 5. Choice

- 선택안: B
- 이유: 이 이슈는 단순 validator 누락 1건이 아니라, 상태 전이표와 경로 계약이 함께 흔들린 경우라서 source of truth를 먼저 고정하고 증거 기반으로 코드 복구를 확인해야 한다.

### 6. Execution Sequence

1. `dispatch-fields.md`를 source of truth로 재확인
2. `dispatch_manager.py`에 `queued -> blocked` 전이 복구
3. `locked_paths ⊆ allowed_paths`와 symlink 차단 복구
4. 직접 fixture로 validate/transition 재현
5. `edgegen.py run`으로 전체 회귀 확인
6. tool 한계와 실제 코드 결함을 분리

### 7. Evidence

- 수정 파일:
  - `codex-worktree-dispatch/scripts/dispatch_manager.py`
- 확인한 reference:
  - `codex-worktree-dispatch/references/dispatch-fields.md`
  - `codex-worktree-dispatch/references/troubleshooting.md`
- 검증 명령:
  - `python3 codex-worktree-dispatch/scripts/dispatch_manager.py validate /tmp/dispatch-recheck-step3/subset_violation.json`
  - `python3 codex-worktree-dispatch/scripts/dispatch_manager.py validate /tmp/dispatch-recheck-step3/symlink_violation.json`
  - `python3 codex-worktree-dispatch/scripts/dispatch_manager.py transition DISPATCH-0001 blocked --reason test-blocked`
  - `python3 edge-case-generator/scripts/edgegen.py run --script codex-worktree-dispatch/scripts/dispatch_manager.py --cases /tmp/edgegen-dispatch-step3`
- 결과:
  - 직접 fixture 기준으로 `queued -> blocked`, subset 위반, symlink 위반 모두 정상 차단
  - `edge-case-generator`는 `49/50 OK`
  - 남은 1건 `symlink_path`는 실제 symlink fixture가 없는 generic 케이스라서, 현재는 target 코드 결함보다 test fixture 한계로 분류
