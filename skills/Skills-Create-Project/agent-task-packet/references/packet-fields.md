# Packet Fields Reference

`v0.1` core field set과 `v0.2` extended profile 후보 필드를 구분한다. core는 모든 packet의 필수/선택 기반이고, extended는 core를 깨지 않고 richer metadata를 추가하는 opt-in profile이다.

## Core 필수 필드 (v0.1)

| 필드 | 타입 | 설명 |
|------|------|------|
| `packet_version` | string | core schema 버전 — 항상 `"0.1"`. standard/extended 구분은 `packet_profile`로 한다 |
| `task_id` | string | 비어있지 않은 고유 식별자 (예: "TASK-0001") |
| `title` | string | 태스크 제목 |
| `goal` | string | 구체적 목표 (최소 10자) |
| `why` | string | 이 작업이 필요한 이유 |
| `allowed_paths` | string[] | 수정 허용 경로 (1개 이상, repo root 상대경로) |
| `context_files` | string[] | 참고용 읽기 전용 파일 |
| `priority` | enum | `critical`, `high`, `medium`, `low` |
| `constraints` | object | 제약 조건 (아래 참조) |
| `done_definition` | string[] | 완료 조건 (1개 이상, 기계 검증 가능) |
| `required_checks` | object[] | 검증 항목 (type, value, required) |
| `deliverables` | object[] | 산출물 (path, type, required) |
| `revision` | integer | 개정 번호 (1부터 시작, 수정 시 증가) |
| `created_at` | string | ISO-8601 생성 시각 |
| `created_by` | string | 작성자 (사람/Claude/시스템) |
| `updated_at` | string | ISO-8601 최종 수정 시각 |

## Core 선택 필드 (v0.1)

| 필드 | 타입 | 설명 |
|------|------|------|
| `forbidden_paths` | string[] | 절대 수정 금지 경로 |
| `depends_on` | string[] | 선행 task_id 목록 |
| `parallel_group` | string | 병렬 실행 그룹명 |
| `non_goals` | object[] | 비목표 (case, description) — canonical 형식은 object[] |
| `handoff_notes` | string | 추가 전달 사항 |
| `branch_hint` | string | 브랜치명 힌트 — **hint only**, 실제 allocation은 dispatch |
| `worktree_hint` | string | worktree 경로 힌트 — **hint only**, 실제 allocation은 dispatch |
| `launch_hint` | string | 실행 명령 힌트 — **hint only**, 실제 ownership은 runtime |
| `trace_id` | string | 추적 ID |
| `parent_task_id` | string | 상위 태스크 ID |
| `timeout_minutes` | integer\|null | 작업 제한 시간 (분) — 없으면 무제한. **운영 안전 필드**: timeout 없는 worker는 무한 실행 위험 |
| `stop_conditions` | string[] | 작업 중단 조건 — worker가 범위를 넘었을 때 스스로 멈추는 기준. **운영 안전 필드** |

## Extended Profile 후보 필드 (v0.2 candidate)

extended profile은 core를 깨지 않고 richer metadata를 추가하는 opt-in 계층이다. `packet_profile`은 항상 명시한다 (`"standard"` 또는 `"extended"`). 하위 호환: 필드가 없는 기존 packet은 standard로 간주한다.

| 필드 | 타입 | 설명 |
|------|------|------|
| `packet_profile` | enum | `"standard"` \| `"extended"` — 항상 명시. 하위 호환: 없으면 standard |
| `repo_root` | string | 저장소 루트 경로 |
| `source_of_truth` | string | canonical 설계 문서 경로 |
| `env_requirements` | object | 환경 요구사항 (Python 버전, 필요 도구 등) |
| `failure_guide` | string | 실패 시 대응 안내 |
| `report_format` | string | 보고서 포맷 지정 |

**규칙:**
- extended field가 있어도 core field의 의미/형식은 변하지 않는다
- extended profile도 runtime/session/process ownership을 가져가지 않는다
- consumer는 extended field를 무시해도 정상 동작해야 한다

> **왜 `timeout_minutes`와 `stop_conditions`가 core인가**: 이 두 필드는 "있으면 좋은 부가 정보"가 아니라 "없으면 운영 위험이 있는 안전 장치"다. timeout 없는 worker는 무한 실행, stop_conditions 없는 worker는 범위 초과를 방지할 수단이 없다. Extended가 아니라 core optional로 두어야 standard packet에서도 사용할 수 있다.

## 금지 필드 (packet에 절대 넣지 않는다)

runtime/session/process 상태는 dispatch와 runtime이 관리한다. packet은 immutable contract이므로 다음 필드를 포함하지 않는다.

`status`, `session_name`, `session_id`, `pid`, `heartbeat`,
`retry_count`, `last_heartbeat`, `current_status`, `log_path`,
`worktree_path`, `branch`, `locked_paths`, `assigned_agent`

## constraints 구조

```json
{
  "must_not_modify": ["src/config.py", "package.json"],
  "must_run_tests": true,
  "must_not_use_network": true,
  "notes": "자유 텍스트 제약사항"
}
```

### Tool permissions (extended profile — 구현 완료)

Tool calling orchestration에서 worker가 사용할 수 있는 도구를 제한하는 것은 핵심 안전 장치다. ToolSandbox Action Score 관점에서 tool 경계를 packet에 명시하면 agent의 tool selection precision이 높아진다.

| 필드 | 타입 | profile | 설명 |
|------|------|---------|------|
| `allowed_tools` | string[] | extended | 사용 허용 도구 목록 (화이트리스트) |
| `forbidden_tools` | string[] | extended | 사용 금지 도구 목록 (블랙리스트) |

**검증 규칙 (builder 구현 완료):**
- `allowed_tools`/`forbidden_tools`는 **extended profile에서만** 사용 가능 (standard → error)
- `allowed_tools`와 `forbidden_tools`를 동시에 지정하면 경고 + `allowed_tools`가 우선 (화이트리스트 우선)
- 둘 다 없으면 모든 도구 허용 (backward compatible)
- 이 필드들은 `constraints` 객체 안에 둔다 (별도 최상위 필드가 아님)

```json
{
  "must_not_modify": [],
  "must_run_tests": true,
  "must_not_use_network": true,
  "allowed_tools": ["Read", "Edit", "Write", "Bash", "Grep", "Glob"],
  "forbidden_tools": ["Agent"],
  "notes": ""
}
```

### must_not_modify ⊆ forbidden_paths (builder 검증 완료)

`constraints.must_not_modify`에 있는 경로는 반드시 `forbidden_paths`에도 포함되어야 한다.
위반 시 validator가 error를 반환한다. 이 규칙은 Action Milestone의 path constraint precision을 보장한다.

## non_goals 구조

비목표는 "중요하지 않은 것"이 아니라 **이번 태스크의 책임 경계를 확정하는 장치**다.

### Case 분류

| Case | 설명 | 예시 |
|------|------|------|
| `state` | 보장하지 않는 상태 경계 | "A 상태는 개선하지만, B 상태로의 전이까지 보장하지 않음" |
| `type` | 제외할 Error Type / 예외 케이스 | "네트워크 타임아웃 에러는 이번 스코프에서 제외" |
| `performance:null` | 성능 개선 목표 없음 | "성능 최적화는 이번 작업의 목표가 아님" |
| `performance:over` | 과최적화 금지 | "O(n²)을 O(n log n)으로 바꾸는 것은 over-engineering" |
| `performance:under` | 일정 수준 이하 성능 저하 허용 | "100ms → 150ms 정도의 지연 증가는 결함으로 보지 않음" |

### 비목표 설정 가이드

- 비목표는 실패한 상태가 아니다
- 비목표는 무시해도 되는 사소한 문제가 아니다
- Side-effect가 시스템에 악영향을 줄 수 있음을 **인지**하되, 이번 태스크에서 그 최적화까지 **책임지지 않을 때** 설정한다

```json
{
  "case": "performance:over",
  "description": "DB 쿼리 최적화는 이번 인증 모듈 구현의 범위가 아님"
}
```

## done_definition과 required_checks의 관계

`done_definition`은 **인간 판독용 성공 기준**이다. "무엇이 달성되면 이 태스크가 끝난 것인가"를 자연어로 적는다.

`required_checks`는 **그 중 기계 검증 가능한 부분집합**이다. `done_definition`의 어떤 항목을 자동으로 검증하는 것이어야 한다.

| 질문 | done_definition | required_checks |
|---|---|---|
| 형식 | string[] (자연어) | object[] (type/value/required) |
| 대상 | 모든 완료 조건 | 기계 검증 가능한 조건만 |
| 관계 | 상위 집합 | 하위 집합 |
| 실행 | 사람이 판단 | builder/runner가 자동 실행 |

**규칙:**
- 모든 `required_checks`는 `done_definition`의 어떤 항목을 검증하는 것이어야 한다
- `done_definition`에만 있고 대응하는 `required_checks`가 없는 항목은 사람이 수동 확인해야 한다
- `required_checks`가 모두 통과해도 `done_definition`의 수동 확인 항목이 남아있을 수 있다

## required_checks 구조

```json
{
  "type": "command",
  "value": "python3 -m pytest tests/test_auth.py",
  "required": true,
  "done_index": 0
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `type` | enum | O | `command`, `file_exists`, `pattern_match` |
| `value` | string | O | 검증 대상 (명령, 경로, 패턴) |
| `required` | boolean | O | 필수 통과 여부 |
| `done_index` | integer | X | done_definition[i]와의 연결 (0-based) |

- 구조화 check의 `target`은 `value`에 대응하고, `operator`/`expected`/`evidence_path`는 신규 확장 필드다(동의어 아님). 상세는 `packet-dispatch-boundary-and-checks-at2026-06-15-20-22.md` 참고. validator는 보존만 한다.

## deliverables 구조

```json
{
  "path": "src/auth.py",
  "type": "source",
  "required": true,
  "done_index": 0
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `path` | string | O | 산출물 경로 |
| `type` | enum | O | `source`, `test`, `config`, `doc`, `script` |
| `required` | boolean | O | 필수 산출물 여부 |
| `done_index` | integer | X | done_definition[i]와의 연결 (0-based). Response milestone traceability |

## Response Milestone Traceability

ToolSandbox 3-Milestone AND(Action × State × Response)에서 **Response milestone**은
agent가 올바른 최종 결과를 생산했는지 판정한다. 하나라도 0이면 전체 = 0.

`done_definition`, `required_checks`, `deliverables` 간 구조적 연결이 없으면
agent는 "이 check가 어떤 완료 조건을 검증하는지" 기계적으로 판단할 수 없다.

### done_index 연결 규칙

```
done_definition[0]: "인증 모듈이 테스트를 통과한다"
       ↑ done_index=0
required_checks[0]: {"type":"command", "value":"pytest tests/test_auth.py", "done_index":0}
deliverables[0]:    {"path":"src/auth.py", "type":"source", "done_index":0}

done_definition[1]: "API 문서가 갱신된다"
       ↑ done_index=1
deliverables[1]:    {"path":"docs/api.md", "type":"doc", "done_index":1}
```

### 채택 규칙

done_index는 **optional**이다. 기존 packet은 변경 없이 동작한다.
done_index를 하나라도 쓰기 시작하면 validator가 부분 커버리지를 경고한다.

> 성과 측정 메트릭(response_coverage, turn_budget_score, resolve_readiness 등)은 [agent-tool-benchmark/references/packet-measurement-fields-at2026-03-25.md](../../agent-tool-benchmark/references/packet-measurement-fields-at2026-03-25.md)를 참조한다.
