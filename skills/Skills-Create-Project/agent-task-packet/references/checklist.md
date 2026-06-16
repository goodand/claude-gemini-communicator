# agent-task-packet v0.2 Refactor Checklist

이 체크리스트는 v0.2 refactor의 완료 상태를 추적한다.
v0.1 구현 체크리스트는 역할을 다했으며, 이 문서가 대체한다.

## Boundary Rules

- [x] packet = immutable task contract. runtime/session/process field 금지.
- [x] dispatch = canonical mutable execution-prep state. packet 원문 중복 저장 금지.
- [x] runtime = launch/session/log ownership layer. packet read-only, dispatch 대체 금지.
- [x] `branch_hint`, `worktree_hint`, `launch_hint`는 hint only — 실제 ownership은 dispatch/runtime.
- [x] local progress/state가 필요해도 dispatch canonical state를 대체하지 않는다.

## Version & Profile Rules

- [x] `packet_version`은 항상 `"0.1"` (core schema version). breaking schema change 시에만 변경.
- [x] standard/extended 구분은 `packet_profile` 필드로만 한다. version을 올려서 구분하지 않는다.
- [x] `packet_profile`이 없거나 `"standard"`이면 v0.1 core. `"extended"`이면 추가 필드 opt-in.

## Field Classification

- [x] `timeout_minutes`, `stop_conditions`는 core optional (운영 안전 필드).
- [x] `repo_root`, `source_of_truth`, `env_requirements`, `failure_guide`, `report_format`은 extended profile 후보.
- [x] `packet_profile`은 extended profile 구분자.
- [x] `allowed_tools`, `forbidden_tools`는 constraints 내부 향후 후보 (proposal-only).

## done_definition vs required_checks

- [x] `done_definition`은 인간 판독용 성공 기준 (상위 집합).
- [x] `required_checks`는 기계 검증 가능한 부분집합.
- [x] 모든 `required_checks`는 `done_definition`의 어떤 항목을 검증하는 것이어야 한다.
- [x] `done_definition`은 `string[]` 유지. object-array 전환은 proposal-only.

## Phase Model

- [x] phase는 linear waterfall이 아니라 허용 전이 집합.
- [x] `implement ↔ fix ↔ review` 루프 명시.
- [x] 단순 태스크는 중간 phase skip 가능 (status=skip 기록).
- [x] `phase_history`에 같은 phase가 여러 번 나타날 수 있다.

## Builder / Validator (packet_builder.py)

- [x] `FORBIDDEN_FIELDS`에 dispatch 소유 필드 포함 (`worktree_path`, `branch`, `locked_paths` 등).
- [x] `EXTENDED_FIELDS`와 `OPTIONAL_FIELDS` 분리 — `timeout_minutes`, `stop_conditions`는 OPTIONAL.
- [x] `_detect_profile` — `packet_profile` 필드로만 판별. implicit field-presence detection 제거.
- [x] `validate_packet(data, profile=None)` — `packet_profile` 필드로 판별, 명시 profile override 가능.
- [x] standard profile strict boundary — extended 필드 존재 시 에러.
- [x] `make_scaffold(profile="standard"|"extended")` — profile별 scaffold 분기.
- [x] standard scaffold에 `timeout_minutes: null`, `stop_conditions: []` 기본값 포함.
- [x] CLI `--profile` 옵션 (`new`, `validate`).
- [x] `timeout_minutes`, `stop_conditions` 타입 검증은 profile 무관 상시 실행.
- [x] 알 수 없는 필드 경고 (error 아님).
- [x] v0.1 packet 파일 zero-regression 검증 완료.

## P0–P5 Progress

- [x] P0: Boundary Wording (5개 문서)
- [x] P1: Core vs Extended Profile Spec (3개 문서)
- [x] P2: Consumer Compatibility Lock (builder + tests)
- [x] P3: Builder / Validator Extension Path (builder + tests, 38 passed)
- [x] P4: Optional Task-Local Progress Companion
- [x] P5: Downstream Adoption Review

## Downstream Templates (P5 완료)

- [x] `task_state_*.json` → legacy alias stub으로 축소 (canonical은 `dispatch_state_*.json`)
- [x] extended dispatch template에서 `runtime`/`phase_history`/`artifacts` 제거 → orchestrator/progress 소유
- [x] `task_packet_extended_template.json`의 `packet_version`을 `"0.1"`로 수정 완료
- [x] `task_packet_template.json` validator 호환 (source_of_truth→string, failure_guide→string, report_format→string)
- [x] downstream template 역할 문구 "canonical mutable execution-prep state"로 통일
- [x] `worktree_hint`/`worktree_path` 예시를 `.worktrees/<task-slug>` 패턴으로 통일
- [x] `task_packet_standard_template.json`에 `timeout_minutes: null`, `stop_conditions: []` 추가
- [x] `task_template_reference.md`에 Local Support / Legacy Alias 섹션 추가
- [x] phase model(`phase_enum`, `phase_transitions`)을 `task_progress_state_template.json`으로 이관

## Orchestration Validators (scripts/)

- [x] `done_index` traceability (done_definition ↔ required_checks ↔ deliverables)
- [x] dispatch status 전이 validator (`validate_dispatch_transition`, `validate_dispatch`)
- [x] history 연속성 검증 (마지막 to == current status)
- [x] `allowed_tools`/`forbidden_tools` 검증 (extended profile)
- [x] `must_not_modify ⊆ forbidden_paths` cross-validation

## Eval Metrics (evals/)

성과 측정 함수는 `evals/packet_eval_metrics.py`로 분리.
상세: [agent-tool-benchmark/references/packet-measurement-fields-at2026-03-25.md](../../agent-tool-benchmark/references/packet-measurement-fields-at2026-03-25.md)

- [x] `response_coverage()`, `turn_budget_score()`, `safety_audit()`, `resolve_readiness()`
- [x] `packet_eval_template.json` (측정용 템플릿)

## Tests

- [x] scripts/ 오케스트레이션: 63개 passed
- [x] evals/ 성과 측정: 16개 passed
