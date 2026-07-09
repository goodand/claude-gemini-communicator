# Codebase-Analysis Development Playbook

- recorded_at: `2026-03-23-03-36`
- purpose: `codebase-analysis`의 tool interface appendix와 development playbook을 core spec 밖의 implementation support 문서로 분리하기 위한 appendix
- derived_from:
  - `references/codebase-analysis-spec-at2026-03-23-03-14.md`
- implementation_support_refs:
  - `references/setup-context-at2026-03-18-22-47.md`
  - `references/skill-usage-details-at2026-03-21-23-25.md`
  - `scripts/test_analyze_codebase.py`
  - `references/smoke/SMOKE_export_canonical_graph_2026-03-21-12-49.md`

## Tool Interface Appendix

### Scope

- 이 섹션은 `CLI`, `MCP`, `SKILL`, `Git`, `tmux` 사용 계약 중 `codebase-analysis`에 직접 필요한 interface만 다룬다.
- tool 사용 계약은 implementation 위치가 아니라 `입력`, `출력`, `경계` 기준으로 적는다.

### CLI Contract

- stable CLI entrypoint:
  - `scripts/analyze_codebase.py <repo_root>`
- CLI input contract:
  - `repo_root` 또는 이에 대응하는 codebase root
- CLI output contract:
  - coarse survey artifact family
  - 후속 graph/export layer가 소비할 analysis seed
- CLI boundary:
  - canonical graph artifact 전체 생성 책임은 현재 CLI 한 개에 고정하지 않는다.

### SKILL Contract

- adjacent analysis skill interface:
  - [dependency-slice-planner](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/dependency-slice-planner/SKILL.md)
  - [codebase-architecture-mapper](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/codebase-architecture-mapper/SKILL.md)
  - [depsolve-analyzer](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/SKILL.md)
  - [class-hierarchy-classifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/class-hierarchy-classifier/SKILL.md)
  - [runtime-flow-tracer-web-preview](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/runtime-flow-tracer-web-preview/SKILL.md)
  - [graph-structure-classifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/graph-structure-classifier/SKILL.md)
- adjacent verification skill interface:
  - [claim-verifier](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/claim-verifier/SKILL.md)
  - [doc-code-sync-checker](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/SKILL.md)
- orchestration-adjacent boundary:
  - [codex-subagent-setup](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/SKILL.md)
  - [codex-worktree-dispatch](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-worktree-dispatch/SKILL.md)
  - [codex-tmux-orchestrator](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-tmux-orchestrator/SKILL.md)
- SKILL boundary:
  - `slice`는 `dependency-slice-planner`가 담당한다.
  - `handoff`와 `fan-in`은 `codex-subagent-setup` 인접 경계에 둔다.
  - bounded packet setup은 `codex-subagent-setup`, worktree dispatch는 `codex-worktree-dispatch`, runtime launch/heartbeat는 `codex-tmux-orchestrator`가 담당한다.
  - `codebase-analysis`는 graph evidence analysis 본체를 담당한다.

### MCP Contract

- MCP는 보조 evidence acquisition 또는 보조 실행 경계로만 사용한다.
- canonical source-of-truth와 primary artifact contract는 local KB와 local artifact를 우선한다.
- MCP boundary:
  - MCP output이 canonical graph artifact를 직접 대체하지 않는다.
  - MCP는 evidence producer 또는 supporting input boundary로만 위치한다.

### Git Contract

- Git은 repository snapshot과 path state 확인용으로 사용한다.
- Git boundary:
  - Git metadata는 canonical graph artifact를 직접 구성하는 primary schema가 아니다.
  - Git/worktree orchestration ownership은 `codebase-analysis` 본체 범위에 포함하지 않는다.

### tmux Contract

- tmux는 장시간 실행이나 로그 추적 보조 수단으로 사용한다.
- tmux boundary:
  - tmux session lifecycle은 `codebase-analysis`의 canonical source-of-truth contract가 아니다.
  - tmux runtime ownership은 인접 orchestration layer에 둔다.

## Development Playbook

### Scope

- 이 섹션은 `codebase-analysis`를 구현하고 다듬을 때 필요한 운영안이다.
- 전 skill inventory 전체를 나열하지 않고, 현재 spec과 직접 연결된 workflow, tool, rule만 다룬다.

### Progress Management

- progress는 `KB grounding -> spec -> doc-code consistency -> implementation checklist -> script/test/smoke` 순서로 관리한다.
- 결정이 남아 있는 내용은 premature promotion 대신 decision queue에 기록한다.
- implementation 전에는 source of truth와 appendix를 먼저 고정한다.
- 관련 page:
  - grounding 기준: [kb-grounding-checklist-at2026-03-23-02-17.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/kb-grounding-checklist-at2026-03-23-02-17.md)
  - doc-code pair 기준: [doc-code-consistency-checklist-at2026-03-23-02-44.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/doc-code-consistency-checklist-at2026-03-23-02-44.md)
  - fixed contract: [codebase-analysis-spec-at2026-03-23-03-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md)
  - bounded implementation task: [codebase-analysis-implementation-request-at2026-03-23-10-49.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md)

### Workflow

1. `SKILL.md`와 canonical KB를 먼저 읽는다.
2. canonical graph artifact contract와 schema sample을 확인한다.
3. [kb-grounding-checklist-at2026-03-23-02-17.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/kb-grounding-checklist-at2026-03-23-02-17.md)로 문항의 KB 연결을 먼저 고정한다.
4. [doc-code-consistency-checklist-at2026-03-23-02-44.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/doc-code-consistency-checklist-at2026-03-23-02-44.md)로 `Doc evidence -> Expected input/output` pair를 정리한다.
5. [codebase-analysis-spec-at2026-03-23-03-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md)의 `Acceptance Criteria`를 구현 전 고정 기준으로 삼고, bounded task가 필요하면 [codebase-analysis-implementation-request-at2026-03-23-10-49.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md)로 내려간다.
6. test와 smoke로 계약을 확인한다.

### TDD 방식

- script 변경 전에는 가능한 한 문서 계약과 checklist 문항을 먼저 고정한다.
- Python script 변경 시에는 [test_analyze_codebase.py](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/scripts/test_analyze_codebase.py)를 우선 실행 가능한 최소 단위 테스트 기준으로 둔다.
- 새 output contract를 추가하면 test도 같은 계약을 직접 확인하도록 확장한다.
- TDD 전에 먼저 읽을 page:
  - 완료 기준: [codebase-analysis-spec-at2026-03-23-03-14.md#L457](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md#L457)
  - 구현 범위와 검사: [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L123](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L123), [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L138](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L138)
  - 작업 경계: [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207), [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L248](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L248)

#### Before TDD

- [codebase-analysis-spec-at2026-03-23-03-14.md#L457](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md#L457)의 `Acceptance Criteria`를 다시 확인한다.
- [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L48](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L48)의 `Constraints`, [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L59](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L59)의 `Non-Goals`, [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L123](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L123)의 `Done Definition`, [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L138](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L138)의 `Required Checks`를 다시 확인한다.
- [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207)의 `Implementation Workspace Contract`와 [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L248](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L248)의 `Worktree 활용하여 작업 공간의 분리`를 기준으로 workspace root와 `runs/<task-id>/` 경로를 먼저 고정한다.
- worktree baseline이 stale이거나 `allowed_paths` 안의 파일이 worktree에 없으면, 허용된 파일만 baseline sync하고 그 사실을 `runs/<task-id>/doc.md`와 `runs/<task-id>/log.json`에 남긴다.
- 구현 전에는 `Done Definition`과 `Required Checks`를 테스트 항목으로 먼저 내리고, 실패하는 테스트를 만든 뒤 코드 구현으로 내려간다.

### Smoke Test

- canonical graph/export 계열 smoke는 [SMOKE_export_canonical_graph_2026-03-21-12-49.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/smoke/SMOKE_export_canonical_graph_2026-03-21-12-49.md)를 기준 예시로 삼는다.
- smoke는 canonical artifact 경로와 split-only 경로를 구분해서 기록한다.
- smoke 결과는 export/view가 canonical source-of-truth를 대체하지 않는지 확인하는 데 사용한다.

### Smoke Target Scope Contract

- 한 번의 smoke run은 정확히 하나의 `repo_root`만 대상으로 잡는다.
- smoke 대상 codebase root는 아래 둘 중 하나로 제한한다.
  - `references/fixtures/` 아래의 fixture workspace root
  - repo root `.worktrees/` 아래의 bounded worktree root
- smoke 범위는 `repo_root` 전체 또는 그 안의 하나의 `active tree`로 닫는다.
- main workspace와 worktree를 동시에 하나의 smoke 범위로 합치지 않는다.
- 외부 repo를 smoke 대상으로 삼을 때는 clone 이후 fixture 또는 worktree로 편입한 뒤 실행한다.
- 임의 외부 repo root를 smoke 대상으로 직접 지정하지 않는다.
- smoke report에는 `repo_root`, `active tree` 여부, canonical artifact 경로, split-only artifact 경로를 함께 기록한다.
- smoke report의 영구 산출물은 `references/smoke/` 아래에만 남긴다.
- smoke 실행은 `knowledge_bases/`, `checklist-forconsistency-evaluation/`, `checklist-forimplementation/`, `SKILL.md`, canonical spec 본문을 직접 수정하지 않는다.
- smoke 결과에서 canonical 문서를 갱신할 필요가 생기면 먼저 report를 남기고, 이후 patch 단계에서 별도로 반영한다.

### 필요한 실행환경 및 자료

- local skill corpus
- local repo snapshot
- canonical base KB
- graph representation KB
- canonical graph artifact contract
- normalized graph schema sample
- graph sample fixture

### 주요 Tool 설명서

- setup context: [setup-context-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/setup-context-at2026-03-18-22-47.md)
- detail page: [skill-usage-details-at2026-03-21-23-25.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/skill-usage-details-at2026-03-21-23-25.md)
- canonical graph artifact contract: [canonical-graph-artifact-contract-at2026-03-20-21-04.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/canonical-graph-artifact-contract-at2026-03-20-21-04.md)
- normalized graph schema sample: [normalized-graph-json-sample-schema-at2026-03-20-21-51.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md)
- orchestration consumer spec: [codebase-analysis-orchestration-consumer-spec-at2026-03-23-13-08.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-orchestration-consumer-spec-at2026-03-23-13-08.md)

### CLI 도구

- `rg`: split point, stale link, rule text, file path 검색
- `sed`, `cat`, `nl`: 줄 단위 읽기와 patch 전 확인
- `diff`, `git diff`: 변경 범위 비교
- `python scripts/analyze_codebase.py <repo_root>`: quick coarse survey entrypoint

### SKILL

- 직접 연결된 analysis / verification skill만 사용한다.
- analysis-adjacent:
  - `dependency-slice-planner`
  - `codebase-architecture-mapper`
  - `depsolve-analyzer`
  - `class-hierarchy-classifier`
  - `runtime-flow-tracer-web-preview`
  - `graph-structure-classifier`
- verification-adjacent:
  - `claim-verifier`
  - `doc-code-sync-checker`
- worker handoff support:
  - `agent-task-packet`
- orchestration-adjacent:
  - `codex-subagent-setup`
  - `codex-worktree-dispatch`
  - `codex-tmux-orchestrator`

### Task Packet Contract

- worker 또는 sub-agent에 bounded implementation task를 넘길 때는 `agent-task-packet`을 사용한다.
- `codebase-analysis` 문맥에서 우선 사용하는 packet 필드는 `goal`, `allowed_paths`, `context_files`, `constraints`, `done_definition`, `required_checks`, `deliverables`다.
- 병렬 작업이나 책임 경계 고정이 필요할 때는 `forbidden_paths`, `depends_on`, `parallel_group`, `non_goals`, `trace_id`를 선택 필드로 사용한다.
- packet은 불변 작업 계약서로 취급하고, runtime 상태(`status`, `session_id`, `pid`, `heartbeat`)는 넣지 않는다.
- `codebase-analysis`에서 packet은 구현 위치를 고정하는 문서가 아니라 worker scope, 비목표, 완료 조건을 bounded form으로 전달하는 문서다.
- orchestration 연결 규칙은 [codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md)를 따른다.
- reusable consumer-side launch/input/ownership contract는 [codebase-analysis-orchestration-consumer-spec-at2026-03-23-13-08.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-orchestration-consumer-spec-at2026-03-23-13-08.md)를 따른다.

### MCP 도구

- MCP는 보조 evidence acquisition 또는 보조 실행 경계로만 사용한다.
- canonical source-of-truth와 primary artifact contract는 local KB와 local artifact를 우선한다.

### Git, Worktree, tmux 관리

- Git은 repository snapshot과 path state 확인용으로 사용한다.
- worktree는 필요 시 작업 공간 분리 수단으로 사용하되, `codebase-analysis`의 canonical contract에는 포함하지 않는다.
- tmux는 장시간 실행이나 로그 추적 보조 수단으로 사용하되, runtime ownership 자체는 이 skill 범위에 두지 않는다.

### 기억해야 하는 것

- `graph evidence`가 이 skill의 핵심이다.
- canonical source of truth는 visualization export가 아니라 canonical graph artifact다.
- graph core와 sidecar evidence를 섞지 않는다.
- optional slice stage는 현재 공식 구현 범위 밖이며, appendix-derived reference로만 남긴다.
- 구현 세부 위치보다 layer와 책임을 먼저 고정한다.

### Task

- KB grounding
- spec 보강
- doc-code consistency 정리
- implementation checklist 작성
- script/test/smoke 반영

### Env

- 현재 workspace root:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis`
- repo root:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator`
- 실행 환경은 local repo + local skill corpus를 기준으로 잡는다.

### Implementation Workspace Contract

- 한 번의 구현 작업은 정확히 하나의 code-writing workspace root만 사용한다.
- code-writing workspace root는 아래 둘 중 하나로 제한한다.
  - repo root working copy
  - repo root `.worktrees/` 아래의 bounded worktree root
- 병렬 구현, worker/sub-agent 구현, bounded task 구현은 `.worktrees/codebase-analysis-*` 하위 worktree를 우선 사용한다.
- 단일 작업자가 로컬로 작은 범위를 수정할 때만 repo root working copy를 사용할 수 있다.
- 하나의 구현 작업이 repo root working copy와 worktree root를 동시에 수정 대상으로 잡지 않는다.
- 실제 코드 수정 경로는 선택된 workspace root 내부에서 `agent-task-packet`의 `allowed_paths` 또는 그에 준하는 bounded path contract로 닫는다.

### 가상환경 위치

- 가상환경 경로는 이 appendix에서 고정하지 않는다.
- interpreter contract는 현재 workspace에서 script와 test를 실행할 수 있는 Python 환경이라는 조건만 유지한다.

### Workspace 주요 디렉토리 경로

- repo root:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator`
- skill entrypoint:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/SKILL.md`
- worktree base:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/.worktrees`
- knowledge bases:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases`
- consistency checklists:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation`
- implementation checklist:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forimplementation`
- references:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references`
- runs:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/runs`
- smoke reports:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/smoke`
- smoke fixtures:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/fixtures`
- scripts:
  - `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/scripts`

### Worktree 활용하여 작업 공간의 분리

- worktree는 필요할 때 bounded implementation 작업 분리 수단으로만 사용한다.
- KB, spec, checklist 정리 단계에서는 worktree를 필수 전제로 두지 않는다.
- worktree를 쓰는 경우 base path는 repo root의 `.worktrees/`로 고정한다.
- `codebase-analysis`용 worktree 이름은 `codebase-analysis-<task-or-slice>` 패턴으로 둔다.
- worker packet이나 dispatch hint가 worktree를 가리킬 때는 `.worktrees/codebase-analysis-*` 하위 경로만 사용한다.
- main workspace와 별도 worktree를 섞어 같은 파일을 동시 수정하지 않는다.
- 구현/실험 산출물은 `scripts/`가 아니라 `runs/<task-id>/` 아래에 남긴다.
- `runs/<task-id>/`의 기본 파일은 `plan.md`, `doc.md`, `report.md`, `log.json`으로 고정한다.

### Rule

#### 작명 규칙

- timestamped markdown artifact naming을 유지한다.
- canonical, appendix, seed, smoke, checklist 구분이 파일명에 드러나야 한다.
- `runs/` 산출물은 task-id 단위 디렉토리로 분리한다.
- `log`는 `md`가 아니라 `json`으로 남긴다.

#### linter 규칙

- Markdown 문서는 patch 방식으로 수정한다.
- split point를 먼저 찾고, 필요한 section만 수정한다.
- 한 문항은 하나의 검증 단위만 가진다.
- `scripts/`에는 실행 코드만 두고, `plan/doc/report/log` 같은 run artifact는 넣지 않는다.

### Policy

#### 실행 우선

- source of truth 고정과 문서 계약 정리를 구현보다 먼저 한다.

#### 결정 보류

- KB나 spec으로 아직 닫히지 않은 결정은 checklist나 code에 섞지 않고 decision queue로 보낸다.

#### 로그 수집

- test, smoke, export 결과는 후속 판단이 가능하도록 artifact 형태로 남긴다.

#### 기존 파일 보존

- 기존 문서는 copy-first 후 patch 방식으로 수정한다.
- 기존 canonical KB와 checklist는 전체 재작성 대신 split/append/join 순서로 다룬다.
