# Fact Owner Map

> 각 사실(fact)의 정의 권한이 어디에 있는지 명시한다.
> 재정의 충돌(drift)을 방지하기 위한 단일 소유권 원칙 문서.

---

## 1. 소유권 규칙

1. **재정의 금지** — canonical owner가 아닌 곳에서 fact를 재정의하면 안 된다. consumer는 값을 복제하지 않고 참조만 한다.
2. **consumer는 registry를 import/참조만** — builder의 상수, template의 enum 등은 machine registry(`.json`)를 단일 출처로 삼는다. 하드코딩된 중복 값은 drift의 원인이다.
3. **drift는 audit script로 탐지** — registry 값과 consumer 값의 불일치를 자동 검사한다. 수동 확인에 의존하지 않는다.

---

## 2. Fact Owner Table

### 기본 원칙

| 유형 | 역할 | 파일 패턴 |
|------|------|-----------|
| reference (`.md`) | 설명용 canonical — 사람이 읽는 정의 | `references/*.md` |
| machine registry (`.json`) | 실행용 canonical — 코드가 읽는 정의 | `references/contracts/*_contract_*.json` |
| template / code / test | consumer — 재정의 금지, 참조만 허용 | `templates/*.json`, `scripts/*.py`, `tests/*.py` |

### Fact 소유권 맵

| Fact | Canonical Owner (설명용) | Machine Registry (실행용) | Consumers |
|------|------------------------|--------------------------|-----------|
| packet required/optional/extended/forbidden fields | `agent-task-packet/references/packet-fields.md` | `agent-task-packet/references/contracts/packet_contract_v0_1.json` | template: `task_packet_standard/extended_template.json`, `task_packet_template.json`; builder: `packet_builder.py` (`REQUIRED_FIELDS`, `OPTIONAL_FIELDS`, `EXTENDED_FIELDS`, `FORBIDDEN_FIELDS`); test: `test_packet_builder.py` |
| packet enums (priority, non_goals_case, check_types, deliverables_type) | `agent-task-packet/references/packet-fields.md` | `agent-task-packet/references/contracts/packet_contract_v0_1.json` | template: `$schema_notes.enums`; builder: `VALID_PRIORITIES`, `NON_GOAL_CASES`, `VALID_CHECK_TYPES`; test assertions |
| packet_profile policy (always_explicit, backward_compat) | `agent-task-packet/references/packet-fields.md` | `agent-task-packet/references/contracts/packet_contract_v0_1.json` | builder: `make_scaffold()`, `_detect_profile()`; template: `$schema_notes`; examples: `packet-examples.md` |
| constraints.allowed_tools/forbidden_tools rules | `agent-task-packet/references/packet-fields.md` | `agent-task-packet/references/contracts/packet_contract_v0_1.json` | builder: `validate_packet()`; template: constraints block |
| dispatch status enum + transitions | `codex-worktree-dispatch/references/dispatch-fields.md` | `codex-worktree-dispatch/references/contracts/dispatch_contract_v0_1.json` | template: `dispatch_state_*_template.json` `$schema_notes`; builder: `DISPATCH_STATUSES`, `DISPATCH_TRANSITIONS`; test assertions |
| dispatch required/optional/reserved/forbidden fields | `codex-worktree-dispatch/references/dispatch-fields.md` | `codex-worktree-dispatch/references/contracts/dispatch_contract_v0_1.json` | template: `dispatch_state_*_template.json` top-level keys; builder: `validate_dispatch()` required set, `DISPATCH_FORBIDDEN_FIELDS` |
| phase model (phase_enum, phase_transitions, phase_status_enum) | `task_progress_state_template.json` `$schema_notes` | (별도 registry 없음 — template 자체가 canonical) | legacy alias: `task_state_template.json` migration note |
| metric registry (9 metrics, phase_metric_mapping) | `agent-tool-benchmark` SKILL | `task_progress_state_template.json` `$schema_notes.metric_registry` | `aggregate_metrics` 필드; test assertions |

---

## 3. 수정 순서

fact 정의를 변경할 때 반드시 아래 순서를 따른다.

```
1. reference (.md)   — 설명용 canonical 먼저 수정
2. registry (.json)  — 실행용 canonical에 반영
3. consumer          — template, builder, test 순으로 동기화
4. audit             — drift 검사 실행하여 불일치 없음 확인
```

순서를 건너뛰면 설명과 실행이 분리되어 drift가 발생한다.

---

## 4. Consumer 동기화 방법

| 동기화 대상 | 방법 |
|------------|------|
| builder 상수 (`REQUIRED_FIELDS`, `VALID_PRIORITIES` 등) | registry `.json`에서 import하거나, audit script에서 parity check로 일치 확인 |
| template `$schema_notes` | registry 값을 그대로 복사하지 않고, registry 경로를 `$ref`나 주석으로 명시 |
| test assertions | registry를 fixture로 로드하여 검증. 하드코딩된 기대값은 registry에서 파생 |
| examples (`.md`) | reference를 인용. 예시 값이 enum에 없으면 audit에서 탐지 |

> **핵심**: consumer가 값을 직접 정의하는 순간 drift가 시작된다. 항상 canonical owner를 단일 출처로 삼는다.
