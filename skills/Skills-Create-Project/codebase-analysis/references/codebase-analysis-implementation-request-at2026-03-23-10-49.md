# Codebase-Analysis Implementation Request

- recorded_at: `2026-03-23-10-49`
- packet_version: `0.1`
- task_id: `codebase-analysis-spec-v0-core-implementation`
- priority: `high`
- created_by: `Codex`

## Goal

`codebase-analysis`의 v0 core spec을 실제 script/test 수준으로 구현한다.

구현 목표는 다음에 한정한다.
- file-first canonical graph 생성
- canonical artifact triple 생성
  - `normalized_graph.json`
  - `nodes.jsonl`
  - `edges.jsonl`
- provenance sidecar 생성
  - `graph_meta.json`
- graph core / sidecar evidence 분기
- `merged_graph`를 codebase graph 내부 layer 통합 표현으로 수용

## Why

현재 문서 계층은 충분히 고정됐다.
- core spec
- KB grounding checklist
- doc-code consistency checklist
- development playbook

이제 다른 agent가 구현으로 내려가도 되는 상태다. 다만 범위가 퍼지지 않도록 v0 core만 bounded task로 고정해야 한다.

## Allowed Paths

- `scripts/analyze_codebase.py`
- `scripts/test_analyze_codebase.py`

## Run Artifact Paths

- `runs/codebase-analysis-spec-v0-core-implementation/plan.md`
- `runs/codebase-analysis-spec-v0-core-implementation/doc.md`
- `runs/codebase-analysis-spec-v0-core-implementation/report.md`
- `runs/codebase-analysis-spec-v0-core-implementation/log.json`

## Context Files

- `references/codebase-analysis-spec-at2026-03-23-03-14.md`
- `references/codebase-analysis-development-playbook-at2026-03-23-03-36.md`
- `checklist-forconsistency-evaluation/kb-grounding-checklist-at2026-03-23-02-17.md`
- `checklist-forconsistency-evaluation/doc-code-consistency-checklist-at2026-03-23-02-44.md`
- `references/canonical-graph-artifact-contract-at2026-03-20-21-04.md`
- `references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md`

## Related Pages

- fixed acceptance contract:
  - [codebase-analysis-spec-at2026-03-23-03-14.md#L457](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md#L457)
- TDD and run boundary:
  - [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L95](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L95)
  - [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207)
  - [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L248](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L248)
- grounding and doc-code views:
  - [kb-grounding-checklist-at2026-03-23-02-17.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/kb-grounding-checklist-at2026-03-23-02-17.md)
  - [doc-code-consistency-checklist-at2026-03-23-02-44.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/doc-code-consistency-checklist-at2026-03-23-02-44.md)

## Constraints

- core spec을 우선 기준으로 구현한다.
- patch 철학을 유지한다.
- 구현 범위는 v0 core에 한정한다.
- optional slice stage는 구현하지 않는다.
- class structure evidence는 v0 core의 1급 node/edge로 승격하지 않는다.
- `DEFINES`를 v0 core 최소 relation 집합에 넣지 않는다.
- `merged_graph`는 analysis/orchestration graph와의 병합으로 구현하지 않는다.
- 문서 수정은 이번 task의 목표가 아니다.
- 허용 경로 밖 수정은 하지 않는다.

## Non-Goals

- slice-stage artifact 구현
- orchestration graph 구현
- multi-agent runtime 관리 구현
- export/view tool integration 구현
- future symbol graph core 구현
- class hierarchy/detail symbol relation의 full expansion 구현
- playbook, checklist, KB 구조 재정리

## Implementation Scope

### Required Scope

- 입력:
  - `repo_root`
  - `active tree` 또는 `top-level structure`
- 출력:
  - `normalized_graph.json`
  - `nodes.jsonl`
  - `edges.jsonl`
  - `graph_meta.json`
- core relation 최소 집합:
  - `IMPORTS`
- representable but not required core-minimum:
  - `DEPENDS_ON`
  - `READS_MANIFEST`
  - `WRAPS`
  - `MUTATES_PATH`
  - `RUNS`
- sidecar evidence kind:
  - `unresolved`
  - `risk`
  - `warning`
  - `ownership_exception`
  - `weak_signal`

### Required Interpretation

- graph core 편입 조건:
  - `file-first anchor`
  - `재현 가능한 구조 사실`
  - `directioned relation or stable graph field`
- sidecar 분기 조건:
  - 위 조건을 만족하지 않는 검토형 판단
  - 경고
  - ownership 예외
  - unresolved 정보
- provenance baseline:
  - `trace_id`
  - `artifact_location`
- `created_by`:
  - optional, not baseline
- `merged_graph`:
  - codebase graph 내부 layer 통합 표현

## Done Definition

- `scripts/analyze_codebase.py`가 기존 coarse summary만이 아니라 canonical artifact triple과 `graph_meta.json` 생성을 지원한다.
- 생성된 canonical artifacts가 spec의 required top-level/schema field를 만족한다.
- `graph_meta.json`이 최소 required fields를 포함한다.
- sidecar evidence가 required fields를 가진 별도 artifact family로 생성되거나, sidecar artifact가 비어 있더라도 spec상 sidecar routing path가 코드에 존재한다.
- `merged_graph`가 허용 `graph_kind`로 처리된다.
- `nodes.jsonl`의 각 record가 최소 required node fields `id`, `kind`, `name`을 만족한다.
- `edges.jsonl`의 각 record가 최소 required edge fields `src`, `dst`, `rel`을 만족한다.
- sidecar evidence artifact가 생성되는 경우 각 record가 required sidecar fields `evidence_kind`, `subject_anchor`, `summary`, `source_path`, `evidence_path`, `reason`, `confidence`를 만족한다.
- `graph_meta.json.artifact_paths`가 canonical artifact triple 경로를 가리킨다.
- `merged_graph`가 허용될 때 analysis/orchestration graph와의 병합이 아니라 codebase graph 내부 layer 통합 표현으로 처리된다.
- optional slice-stage 관련 구현 분기가 추가되지 않는다.
- 기존 테스트는 유지되고, 새/수정 테스트가 canonical artifact contract를 검증한다.

## Required Checks

- `python3 scripts/test_analyze_codebase.py`
- fixture 또는 bounded worktree repo를 대상으로 `scripts/analyze_codebase.py`를 실행해 `normalized_graph.json`, `nodes.jsonl`, `edges.jsonl`, `graph_meta.json`이 생성되는지 확인
- `graph_meta.json`에 다음 required fields가 있는지 확인
  - `graph_id`
  - `schema_version`
  - `generated_at`
  - `source_scope`
  - `graph_kind`
  - `artifact_paths`
  - `trace_id`
  - `artifact_location`
- `nodes.jsonl` / `edges.jsonl`이 newline-delimited JSON인지 확인
- `nodes.jsonl`의 sample records가 `id`, `kind`, `name`을 포함하는지 확인
- `edges.jsonl`의 sample records가 `src`, `dst`, `rel`을 포함하는지 확인
- sidecar evidence artifact가 생성되는 경우 sample records가 `evidence_kind`, `subject_anchor`, `summary`, `source_path`, `evidence_path`, `reason`, `confidence`를 포함하는지 확인
- `graph_meta.json.artifact_paths`가 `normalized_graph.json`, `nodes.jsonl`, `edges.jsonl`를 가리키는지 확인
- v0 core relation 최소 집합이 `IMPORTS` 중심으로 유지되는지 확인
- `merged_graph`를 사용하는 경우 codebase graph 내부 layer 통합 표현으로만 처리되고 analysis/orchestration graph merge를 만들지 않는지 확인

## Deliverables

- `scripts/analyze_codebase.py`
- `scripts/test_analyze_codebase.py`
- `runs/codebase-analysis-spec-v0-core-implementation/plan.md`
- `runs/codebase-analysis-spec-v0-core-implementation/doc.md`
- `runs/codebase-analysis-spec-v0-core-implementation/report.md`
- `runs/codebase-analysis-spec-v0-core-implementation/log.json`

## Severity Classification

### P0 Hard Fail — 발생 즉시 작업 중단

1. allowed paths 밖 수정
2. merged_graph를 외부 graph 또는 analysis/orchestration graph와 병합
3. sidecar evidence를 graph core에 섞기
4. export/view output을 canonical source-of-truth로 대체
5. 기존 테스트 깨뜨리기

### P1 Strong Fail — 원칙적 fail

6. coarse summary 기능 제거
7. slice-stage 구현 추가
8. DEFINES를 v0 core 최소 집합에 추가
9. class hierarchy/detail symbol relation을 v0 core node/edge로 승격

## Validation Tiers

### Tier 1. Lightweight Warning (기계적 탐지)

| ID | 조건 | 메시지 |
|---|---|---|
| A | run artifact가 `runs/<task-id>/` 밖에 생성됨 | run artifact must be stored under `runs/<task-id>/` |
| B | `log.md` 또는 `log.txt` 생성, `log.json` 없음 | log must be stored as `log.json` |
| C | `plan.md` / `doc.md` / `report.md` / `log.json` 누락 | missing required run artifact |
| D | git diff 기준 allowed paths 밖 변경 | changed file is outside allowed paths |
| E | 실행 후 canonical artifact 미생성 | missing canonical artifact |
| F | artifact 이름/확장자 위반 | unexpected canonical artifact name |

### Tier 2. Heuristic Warning (semantic review에 위임)

| ID | 조건 | 메시지 |
|---|---|---|
| A | `DEFINES` relation 문자열 추가 | DEFINES relation detected; v0 core minimum must remain IMPORTS-centered |
| B | `INHERITS`/`IMPLEMENTS`/`class_hierarchy`/`parent_class` 추가 | class hierarchy relation detected; verify not promoted into v0 core |
| C | `slice_seed`/`parallel_slices`/`runtime_overlay.json` 등 추가 | slice-stage branch detected; current scope excludes optional slice stage |
| D | `analysis_graph`와 `merged_graph`를 같은 흐름에서 병합 | merged_graph touches analysis_graph path; semantic review required |

### Tier 3. Hard Gate (최종 fail 처리)

- allowed paths 밖 수정 → fail
- 기존 테스트 실패 → fail
- canonical artifact 미생성 → fail
- `graph_meta.json` required field 누락 → fail
- `nodes.jsonl` / `edges.jsonl` required field 누락 → fail

### 검증 흐름

1. 구현 완료 후 Tier 3 hard gate 먼저 확인
2. Tier 1 lightweight warning 확인
3. Tier 2 heuristic warning 확인 → semantic review task에 인계

## Handoff Notes

- 문서가 아니라 코드 구현 task다.
- spec과 playbook은 context-only다. 구현을 위해 다시 구조를 바꾸지 않는다.
- ambiguity가 생기면 더 넓게 구현하지 말고 v0 core 쪽으로 보수적으로 해석한다.
- `plan/doc/report`는 markdown으로 남기고 `log`는 `json`으로 남긴다.
- run artifact는 `scripts/`가 아니라 `runs/codebase-analysis-spec-v0-core-implementation/` 아래에 저장한다.
