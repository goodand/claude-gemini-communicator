# Packet / Dispatch / Progress Companion — 경계와 구조화 검증 규칙

세 계층의 소유권이 섞이면 packet이 mutable 상태를 끌어들이거나 dispatch가 계약 내용을
수정하는 오염이 발생한다. 이 문서는 경계를 확정하고 구조화 검증 규칙과 의존성 표현 방식을 정의한다.

---

## 1. 세 계층 소유권

| 계층 | 역할 | 변경 가능성 |
|------|------|------------|
| **packet** | 불변 작업 계약 (goal, why, scope, done_definition, required_checks, deliverables) | revision 발행으로만 변경 |
| **dispatch** | 런타임 할당 및 가변 실행 상태 — `codex-worktree-dispatch` 소유 | 상시 갱신 |
| **task_progress_state** | 선택적 로컬 진행 동반자 (ephemeral 메모) — 정식 진실 아님 | 세션 종료 시 폐기 가능 |

### 필드 소유 계층 표

| 필드 | 소유 계층 |
|------|-----------|
| `goal`, `why`, `allowed_paths`, `non_goals`, `done_definition`, `required_checks`, `deliverables` | packet |
| `depends_on` (의존성 의도 선언) | packet |
| `branch_hint`, `worktree_hint`, `launch_hint` | packet (hint only — 실제 allocation은 dispatch) |
| `branch`, `worktree_path`, `locked_paths`, `assigned_agent`, `status`, `history` | dispatch |
| `pid`, `session_id`, `heartbeat_path`, `log_path` | dispatch / runtime — **packet에 절대 금지** |
| 임시 메모, 진행률 초안 | task_progress_state |

> **[R3 — Option A + C1] 로컬리티 vs 소유권 구분:** dispatch 계약의 EXECUTION-CANONICAL 소유자는 `codex-worktree-dispatch` 내 레지스트리(`dispatch_contract_v0_1.json`)이다. `agent-task-packet/scripts/packet_builder.py`에 물리적으로 위치한 `DISPATCH_*` 상수 및 `validate_dispatch` 심볼은 해당 레지스트리의 감사된 projection(`_shared/scripts/audit_contract_sync.py` 검사 대상)이며 소유자가 아니다 — in-packet 위치는 projection-locality 세부사항일 뿐, 소유권을 의미하지 않는다.

---

## 2. v0.2 — standard / extended는 프로파일이다

`standard`와 `extended`는 `packet_profile` 필드로 선택하는 프로파일이며 별도 스킬이 아니다.
`packet_version`은 두 프로파일 모두 `"0.1"`을 유지한다. `packet_profile`이 없는 기존 packet은
standard로 간주한다. extended 프로파일은 orchestration 힌트(`repo_root`, `source_of_truth`,
`env_requirements`, `failure_guide`, `report_format`)를 opt-in으로 수용하지만,
runtime 상태 소유권을 가져가지 않는다.

---

## 3. 구조화된 `required_checks`

자연어 문자열만으로 채우면 기계 검증이 불가능하다. 가능한 경우 항상 구조화 형식을 사용한다.

```json
{
  "type": "command",
  "target": "python3 -m pytest tests/test_env_gate.py -v",
  "operator": "exit_code",
  "expected": 0,
  "required": true,
  "evidence_path": ".codex/reports/env-gate-result.txt",
  "done_ref": "D-1"
}
```

| 필드 | 필수 | 설명 |
|------|------|------|
| `type` | O | `command` \| `file_exists` \| `pattern_match` |
| `target` | O | 명령어, 파일 경로, 또는 패턴 소스 |
| `operator` | X | `exit_code`, `contains`, `match`, `exists` |
| `expected` | X | operator가 비교할 기댓값 |
| `required` | O | 필수 통과 여부 |
| `evidence_path` | X | 검증 결과를 기록할 파일 경로 |
| `done_ref` | X | `done_definition` 항목 연결 (`D-<n>` 형식) |

`done_ref`(`"D-1"` 레이블)와 `done_index`(0-based 정수)는 같은 목적이다. done_ref와 done_index를 함께 쓰고 값이 서로 다르면 validator가 에러를 낸다; done_ref만 쓰면 (저장 형태는 그대로 두고) done_index 위치로 해석한다.

> 참고: `target`은 기존 `references/packet-fields.md`의 `value` 필드에 대응한다(검사 대상). `operator`/`expected`/`evidence_path`는 `value`-only 형식에 없던 **신규 확장 필드**이며 동의어가 아니다 (operator=비교 연산, expected=기댓값, evidence_path=증거 경로). 현재 validator는 이들을 강제하지 않고 보존만 하며(render는 출력), canonical 필드명 통일은 doc-code-sync 단계 과제다.

---

## 4. 의존성 표현 규칙

`depends_on`은 packet 안의 **의도 선언**이다. 런타임 시퀀싱과 상태 블로킹은 dispatch가 담당한다.
packet은 다른 packet의 status를 읽거나 변경할 수 없다.

TASK-0003이 TASK-0002 Env Gate 통과를 요구하는 경우:

**packet (의도 선언):**
```json
{
  "task_id": "TASK-0003",
  "depends_on": ["TASK-0002"],
  "required_checks": [
    {"type": "command", "target": "python3 -m pytest tests/test_env_gate.py",
     "operator": "exit_code", "expected": 0, "required": true, "done_ref": "D-1"}
  ]
}
```

**dispatch state (런타임 강제):**
```json
{
  "dispatch_id": "DISPATCH-0003",
  "task_id": "TASK-0003",
  "status": "blocked",
  "depends_on_dispatch_ids": ["DISPATCH-0002"],
  "status_reason": "upstream DISPATCH-0002 Env Gate 미통과 — ready 보류"
}
```

> 런타임 강제는 `dispatch_manager.py ready <dispatch_id>`가 수행한다 — upstream dispatch가 `complete`/`merged`에 도달해야 `blocked`→`ready` 전이가 허용된다. (`blocked_by`/`unblock_condition`은 실제 dispatch schema가 아니며, canonical은 `depends_on_dispatch_ids` + status machine이다.)

---

## 5. 동일 태스크의 세 계층 예시 (TASK-0005)

**(a) 불변 packet 계약**
```json
{
  "packet_version": "0.1", "packet_profile": "standard",
  "task_id": "TASK-0005", "title": "설정 파일 검증 스크립트 구현",
  "goal": "config.yaml 필수 키 검증 스크립트를 작성한다",
  "allowed_paths": ["scripts/validate_config.py", "tests/test_validate_config.py"],
  "depends_on": ["TASK-0004"],
  "done_definition": ["D-1: validate_config.py가 존재한다", "D-2: pytest가 통과한다"],
  "required_checks": [
    {"type": "file_exists", "target": "scripts/validate_config.py", "required": true, "done_ref": "D-1"},
    {"type": "command", "target": "python3 -m pytest tests/test_validate_config.py",
     "operator": "exit_code", "expected": 0, "required": true, "done_ref": "D-2"}
  ],
  "revision": 1, "created_by": "claude"
}
```

**(b) 가변 dispatch 상태**
```json
{
  "task_id": "TASK-0005", "status": "running",
  "assigned_agent": "codex-worker-03",
  "branch": "feat/codex-task-0005",
  "worktree_path": ".worktrees/task-0005",
  "pid": 48291, "session_id": "sess-a1b2c3",
  "heartbeat_path": ".codex/heartbeat/task-0005.json",
  "log_path": ".codex/logs/task-0005.log"
}
```

**(c) 선택적 로컬 진행 동반자**
```json
{
  "task_id": "TASK-0005", "ephemeral": true,
  "note": "validate_config.py 초안 완료 — pytest 2개 통과, 1개 미통과",
  "scratch": "required_keys 누락 시 ValueError 확인 필요"
}
```

> (c)는 정식 진실이 아니다. merge 판단에 사용되지 않으며 세션 종료 시 폐기될 수 있다.

---

## 6. 런타임 할당 소유권 교차 참조

런타임 allocation 소유권의 전체 동작은
[codex-worktree-dispatch 스킬](../codex-worktree-dispatch/SKILL.md)을 참조한다.
