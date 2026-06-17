# Packet Examples

## TOC

### Standard Packet (v0.1 Core)

1. [최소 패킷](#1-최소-패킷)
2. [파일 수정 태스크](#2-파일-수정-태스크)
3. [분석 전용 태스크](#3-분석-전용-태스크)
4. [의존성 있는 태스크](#4-의존성-있는-태스크)
5. [비목표 포함 태스크](#5-비목표-포함-태스크)

### Extended Packet (v0.2 Profile)

6. [Extended Profile 태스크](#6-extended-profile-태스크)

---

# Standard Packet Examples (v0.1 Core)

아래 예시는 모두 `packet_version: "0.1"` core field만 사용한다. `packet_profile: "standard"`를 명시한다.

## 1. 최소 패킷

가장 단순한 유효 패킷. goal과 allowed_paths만 의미 있게 채움.

```json
{
  "packet_version": "0.1",
  "task_id": "TASK-0001",
  "title": "README 오타 수정",
  "goal": "README.md의 설치 가이드 섹션에서 오타를 수정한다",
  "why": "사용자가 설치 단계에서 혼란을 겪고 있음",
  "allowed_paths": ["README.md"],
  "forbidden_paths": [],
  "context_files": [],
  "depends_on": [],
  "parallel_group": null,
  "priority": "low",
  "constraints": {
    "must_not_modify": [],
    "must_run_tests": false,
    "must_not_use_network": true,
    "notes": ""
  },
  "non_goals": [],
  "done_definition": ["README.md의 오타가 수정됨"],
  "required_checks": [
    {"type": "file_exists", "value": "README.md", "required": true}
  ],
  "deliverables": [
    {"path": "README.md", "type": "doc", "required": true}
  ],
  "handoff_notes": "",
  "branch_hint": "feat/codex-task-0001",
  "worktree_hint": ".worktrees/task-0001",
  "launch_hint": null,
  "trace_id": null,
  "parent_task_id": null,
  "revision": 1,
  "created_at": "2026-03-15T01:00:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T01:00:00+09:00"
}
```

> **왜 packet에 있는가**: goal, allowed_paths, done_definition은 **작업 계약**이므로 packet에 속한다. branch_hint는 dispatch에 대한 힌트일 뿐 — 최종 결정은 dispatch가 한다.

---

## 2. 파일 수정 태스크

여러 파일을 수정하고 테스트까지 요구하는 패킷.

```json
{
  "packet_version": "0.1",
  "task_id": "TASK-0010",
  "title": "인증 모듈 구현",
  "goal": "JWT 기반 인증 미들웨어를 구현하고 테스트를 작성한다",
  "why": "현재 인증 없이 API가 노출되어 있음",
  "allowed_paths": ["src/auth/", "tests/test_auth.py", "src/middleware/"],
  "forbidden_paths": ["src/config.py", "package.json"],
  "context_files": ["src/app.py", "docs/auth-spec.md"],
  "depends_on": [],
  "parallel_group": "auth-group",
  "priority": "high",
  "constraints": {
    "must_not_modify": ["src/config.py"],
    "must_run_tests": true,
    "must_not_use_network": true,
    "notes": "외부 패키지 추가 금지, 표준 라이브러리만 사용"
  },
  "non_goals": [],
  "done_definition": [
    "src/auth/jwt_middleware.py가 존재한다",
    "tests/test_auth.py가 존재하고 모든 테스트가 통과한다",
    "기존 테스트가 깨지지 않는다"
  ],
  "required_checks": [
    {"type": "command", "value": "python3 -m pytest tests/test_auth.py", "required": true, "done_index": 1},
    {"type": "command", "value": "python3 -m pytest tests/ --tb=short", "required": true, "done_index": 2}
  ],
  "deliverables": [
    {"path": "src/auth/jwt_middleware.py", "type": "source", "required": true, "done_index": 0},
    {"path": "tests/test_auth.py", "type": "test", "required": true, "done_index": 1}
  ],
  "revision": 1,
  "created_at": "2026-03-15T01:00:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T01:00:00+09:00"
}
```

---

## 3. 분석 전용 태스크

코드 수정 없이 분석 보고서만 산출하는 패킷.

```json
{
  "packet_version": "0.1",
  "task_id": "TASK-0020",
  "title": "의존성 순환 분석",
  "goal": "src/ 하위 모듈 간 import 순환을 탐지하고 보고서를 작성한다",
  "why": "최근 import error가 간헐적으로 발생하고 있음",
  "allowed_paths": [".codex/reports/"],
  "context_files": ["src/"],
  "priority": "medium",
  "constraints": {
    "must_not_modify": ["src/"],
    "must_run_tests": false,
    "must_not_use_network": false,
    "notes": "코드 수정 없음, 분석 보고서만 산출"
  },
  "done_definition": [
    ".codex/reports/dep-cycle-report.md가 존재한다",
    "보고서에 순환 경로가 명시되어 있다"
  ],
  "required_checks": [
    {"type": "file_exists", "value": ".codex/reports/dep-cycle-report.md", "required": true}
  ],
  "deliverables": [
    {"path": ".codex/reports/dep-cycle-report.md", "type": "doc", "required": true}
  ],
  "revision": 1,
  "created_at": "2026-03-15T01:00:00+09:00",
  "created_by": "user",
  "updated_at": "2026-03-15T01:00:00+09:00"
}
```

---

## 4. 의존성 있는 태스크

TASK-0010 (인증 모듈) 완료 후에만 실행 가능.

```json
{
  "packet_version": "0.1",
  "task_id": "TASK-0011",
  "title": "인증 미들웨어 라우트 연결",
  "goal": "TASK-0010에서 만든 JWT 미들웨어를 모든 API 라우트에 적용한다",
  "why": "미들웨어 구현 후 실제 적용이 필요함",
  "allowed_paths": ["src/routes/", "tests/test_routes.py"],
  "context_files": ["src/auth/jwt_middleware.py", "src/app.py"],
  "depends_on": ["TASK-0010"],
  "parallel_group": "auth-group",
  "priority": "high",
  "constraints": {
    "must_run_tests": true,
    "must_not_use_network": true
  },
  "done_definition": [
    "모든 API 라우트에 인증 미들웨어가 적용됨",
    "기존 라우트 테스트가 통과함"
  ],
  "required_checks": [
    {"type": "command", "value": "python3 -m pytest tests/", "required": true}
  ],
  "deliverables": [
    {"path": "src/routes/", "type": "source", "required": true},
    {"path": "tests/test_routes.py", "type": "test", "required": true}
  ],
  "revision": 1,
  "created_at": "2026-03-15T01:00:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-15T01:00:00+09:00"
}
```

> **왜 depends_on이 packet에 있는가**: 작업 순서는 **설계 결정**이므로 계약서에 속한다. dispatch는 이 의존성을 읽고 실행 순서를 조율할 뿐이다.

---

## 5. 비목표 포함 태스크

non_goals로 책임 경계를 명확히 하는 패킷.

```json
{
  "packet_version": "0.1",
  "task_id": "TASK-0030",
  "title": "로그인 에러 핸들링 개선",
  "goal": "로그인 실패 시 사용자에게 명확한 에러 메시지를 보여준다",
  "why": "현재 500 에러만 노출되어 사용자 경험이 나쁨",
  "allowed_paths": ["src/auth/login.py", "src/auth/errors.py", "tests/test_login_errors.py"],
  "context_files": ["src/auth/jwt_middleware.py"],
  "priority": "medium",
  "constraints": {
    "must_run_tests": true,
    "must_not_use_network": true
  },
  "non_goals": [
    {
      "case": "state",
      "description": "로그인 성공 후 세션 관리 로직은 개선하지 않는다. 에러 상태만 다룬다."
    },
    {
      "case": "type",
      "description": "네트워크 타임아웃으로 인한 로그인 실패는 이번 스코프에서 제외한다."
    },
    {
      "case": "performance:null",
      "description": "로그인 응답 속도 최적화는 이번 태스크의 목표가 아니다."
    }
  ],
  "done_definition": [
    "잘못된 비밀번호 시 401 + 'Invalid credentials' 메시지 반환",
    "존재하지 않는 사용자 시 404 + 'User not found' 메시지 반환",
    "모든 에러 응답에 error_code 필드 포함"
  ],
  "required_checks": [
    {"type": "command", "value": "python3 -m pytest tests/test_login_errors.py -v", "required": true}
  ],
  "deliverables": [
    {"path": "src/auth/errors.py", "type": "source", "required": true},
    {"path": "tests/test_login_errors.py", "type": "test", "required": true}
  ],
  "revision": 1,
  "created_at": "2026-03-15T01:00:00+09:00",
  "created_by": "user",
  "updated_at": "2026-03-15T01:00:00+09:00"
}
```

---

# Extended Packet Examples (v0.2 Profile)

아래 예시는 `packet_profile: "extended"`를 포함하며, core field 위에 richer metadata를 추가한다. consumer는 extended field를 무시해도 정상 동작해야 한다.

## 6. Extended Profile 태스크

core field에 `repo_root`, `source_of_truth`, `env_requirements`, `stop_conditions`, `timeout_minutes`를 추가한 패킷.

```json
{
  "packet_version": "0.1",
  "packet_profile": "extended",
  "task_id": "TASK-0040",
  "title": "codebase-analysis v0 core 구현",
  "goal": "analyze_codebase.py의 layer-1 AST 수집과 layer-2 cross-ref 로직을 구현하고 테스트를 통과시킨다",
  "why": "codebase-analysis skill의 첫 동작 가능한 버전이 필요함",
  "allowed_paths": ["skills/Skills-Create-Project/codebase-analysis/scripts/", "skills/Skills-Create-Project/codebase-analysis/runs/"],
  "forbidden_paths": ["skills/Skills-Create-Project/codebase-analysis/SKILL.md"],
  "context_files": ["skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md"],
  "depends_on": [],
  "parallel_group": null,
  "priority": "high",
  "constraints": {
    "must_not_modify": ["skills/Skills-Create-Project/codebase-analysis/SKILL.md"],
    "must_run_tests": true,
    "must_not_use_network": true,
    "notes": "Python 표준 라이브러리 + ast 모듈만 사용"
  },
  "non_goals": [
    {
      "case": "state",
      "description": "layer-3 graph 시각화는 이번 스코프에서 제외한다"
    }
  ],
  "done_definition": [
    "python3 -m pytest test_analyze_codebase.py 가 통과한다",
    "runs/ 하위에 분석 결과 JSON이 생성된다"
  ],
  "required_checks": [
    {"type": "command", "value": "python3 -m pytest skills/Skills-Create-Project/codebase-analysis/scripts/test_analyze_codebase.py", "required": true}
  ],
  "deliverables": [
    {"path": "skills/Skills-Create-Project/codebase-analysis/scripts/analyze_codebase.py", "type": "source", "required": true}
  ],
  "handoff_notes": "spec 문서의 layer-1, layer-2 섹션을 참조할 것",
  "branch_hint": "feat/codex-task-0040",
  "worktree_hint": ".worktrees/task-0040",
  "launch_hint": null,
  "trace_id": null,
  "parent_task_id": null,
  "repo_root": ".",
  "source_of_truth": "skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md",
  "env_requirements": {
    "python": ">=3.9",
    "tools": ["ast"]
  },
  "stop_conditions": ["spec 문서에 명시되지 않은 layer-3 이상 기능 구현 시도"],
  "timeout_minutes": 60,
  "revision": 1,
  "created_at": "2026-03-24T12:00:00+09:00",
  "created_by": "claude",
  "updated_at": "2026-03-24T12:00:00+09:00"
}
```

> **Standard vs Extended**: `packet_profile`은 항상 명시한다 (`"standard"` 또는 `"extended"`). 하위 호환: 없으면 standard. `"extended"`이면 추가 필드를 opt-in으로 수용하되, consumer는 이 필드를 무시해도 core 기능에 영향이 없어야 한다. extended field가 runtime/session/process ownership을 가져가면 안 된다.
