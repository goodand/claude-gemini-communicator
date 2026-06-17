# Codebase-Analysis Spec

- recorded_at: `2026-03-23-03-14`
- purpose: `codebase-analysis`의 기능 요구, 입력/출력, 스키마, 완료 기준을 구현 전 단계에서 고정하기 위한 spec 문서
- source_of_truth:
  - `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`
  - `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
- supporting_appendix:
  - `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`
  - `references/dependency-slice-planner-handoff-contract-seed-at2026-03-22-00-54.md`
  - `references/canonical-graph-artifact-contract-at2026-03-20-21-04.md`
  - `references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md`
- implementation_support_refs:
  - `references/setup-context-at2026-03-18-22-47.md`
  - `references/skill-usage-details-at2026-03-21-23-25.md`
  - `scripts/test_analyze_codebase.py`
  - `references/smoke/SMOKE_export_canonical_graph_2026-03-21-12-49.md`

## Scope Rule

- `Functional Spec`, core `Schema Spec`, core `Orchestration Spec`는 canonical KB와 appendix를 우선 근거로 둔다.
- tool interface와 development playbook appendix는 implementation support refs까지 포함한 구현 지원 계층으로 읽는다.
- implementation support 계층은 canonical core와 충돌하지 않아야 하며, canonical core를 대체하지 않는다.
- related pages:
  - 운영 경계와 workspace rule: [codebase-analysis-development-playbook-at2026-03-23-03-36.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md)
  - bounded implementation task: [codebase-analysis-implementation-request-at2026-03-23-10-49.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md)
  - grounding source alignment: [kb-grounding-checklist-at2026-03-23-02-17.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/kb-grounding-checklist-at2026-03-23-02-17.md)
  - doc-code pair view: [doc-code-consistency-checklist-at2026-03-23-02-44.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/doc-code-consistency-checklist-at2026-03-23-02-44.md)

## Functional Spec

### Core Function

- 이 skill은 codebase에서 `graph evidence`를 수집하고 정리한다.
- analysis 본체는 `dependency evidence`, `class structure evidence`, `runtime overlay`를 evidence layer로 받아 `graph core`와 `sidecar evidence`를 구성한다.
- canonical source of truth는 `normalized_graph.json + nodes.jsonl + edges.jsonl`이다.
- export/view outputs는 canonical graph artifact를 입력으로 받아 후행 생성되는 결과물로 유지한다.

### Functional Requirements

- codebase의 active tree 또는 top-level structure는 coarse survey 입력으로 수용한다.
- v0 `graph core`는 file-first canonical graph로 유지하고 재현 가능한 구조 사실만 포함한다.
- dependency evidence는 v0 core에서 `IMPORTS` 중심 relation family로 정규화하고, `DEPENDS_ON`, `READS_MANIFEST`는 representable relation family로 유지한다.
- class structure evidence는 v0 core의 1급 node/edge로 채택하지 않고, file 수준 구조 사실은 graph-side structure로 유지하며 세부 symbol 구조는 future symbol graph core의 우선 수용 대상으로 남긴다.
- wrapper/path mutation/run signal은 graph-side relation candidate로 유지한다.
- runtime 관측은 static relation을 대체하지 않고 confidence 보강 또는 보류 판단 레이어로 반영한다.
- graph core에는 weak signal을 넣지 않고, `unresolved`, `risk`, `warning`, `ownership_exception`, `weak_signal` evidence kind는 sidecar evidence로 분기한다.
- graph core 편입 조건은 `file-first anchor + 재현 가능한 구조 사실 + directioned relation or stable graph field`를 만족하는 경우로 고정한다.
- 위 조건을 만족하지 않는 검토형 판단, 경고, ownership 예외, unresolved 정보는 sidecar evidence로 분기한다.

### Input

- `codebase`
- `active tree` 또는 `top-level structure`
- dependency evidence family
- class structure evidence family
- runtime overlay family

### Output

- primary output family
  - `normalized_graph.json`
  - `nodes.jsonl`
  - `edges.jsonl`
  - canonical artifact family는 `graph_kind=merged_graph`를 포함한 codebase graph 내부 layer 통합 표현을 산출할 수 있다.
- provenance sidecar output family
  - `graph_meta.json`
- sidecar evidence family
- export/view output family
  - Graphviz, Neo4j, Cytoscape, Gephi용 후행 산출물

### Exception Handling

- graph core에 넣기 어려운 저연결 정보는 sidecar evidence로 라우팅한다.
- anomaly 정보(`cycle`, `diamond`, `phantom`)는 단순 note가 아니라 후속 판단에 재사용 가능한 anomaly evidence로 남긴다.

### State Transition Contracts

- `coarse survey` output은 evidence collection의 직접 입력으로 사용되는 transient in-memory result 또는 local transient artifact로 해석한다.
- `dependency evidence`, `class structure evidence`, `runtime overlay`는 `graph evidence layer`로 수렴 가능해야 한다.
- `graph evidence layer`는 `graph core`와 `sidecar evidence` 분기 입력으로 사용 가능해야 한다.
- canonical graph artifact는 export/view outputs의 직접 입력으로 사용 가능해야 한다.

### Constraints

- source of truth는 visualization format이 아니라 canonical graph artifact다.
- codebase graph와 analysis/orchestration graph는 논리 계층을 분리한다.
- `merged_graph`는 codebase graph 내부 layer 통합 표현이며 analysis/orchestration graph와 병합하지 않는다.
- relation은 schema/storage에서 방향성을 유지하고 query/view에서는 역방향 조회를 허용한다.
- `DEFINES`는 v0 core relation 최소 집합에 포함하지 않는다.
- optional slice stage는 이번 skill의 공식 범위와 평가 대상에 포함하지 않는다.
- slice, handoff, fan-in은 analysis 본체가 아니라 인접 skill 또는 appendix에서 다룬다.
- 구현 위치, 함수명, 내부 helper 구조는 이 spec의 고정 대상이 아니다.

## API Spec

### Boundary

- 이 문서의 API는 HTTP API보다 넓은 `interface contract`를 뜻한다.
- 포함 대상은 `agent-to-agent`, `script-to-script`, `tool-to-agent`, `artifact-to-artifact` 경계다.
- 안정적인 호출 경계는 implementation file path가 아니라 `input family -> output family` 기준으로 정의한다.

### Layer Interfaces

#### Coarse Survey -> Evidence Collection

- required input family:
  - `codebase`
  - `active tree`
  - `top-level structure`
- required output family:
  - dependency evidence collection inputs
  - class structure evidence collection inputs
  - runtime overlay collection inputs

#### Evidence Collection -> Graph Evidence

- required input family:
  - dependency evidence
  - class structure evidence
  - runtime overlay
- required output family:
  - graph evidence layer

#### Graph Evidence -> Graph Core / Sidecar

- required input family:
  - graph evidence layer
- required output family:
  - graph core
  - sidecar evidence

#### Canonical Artifact -> Export/View

- required input:
  - `normalized_graph.json`
  - `nodes.jsonl`
  - `edges.jsonl`
- required output family:
  - export/view artifacts

### Interface Contract Families

#### Handoff Payload Contract

- required input fields:
  - `tree_snapshot` (`object`): active tree 또는 top-level structure snapshot
  - `graph_summary` (`object`): canonical graph 요약과 주요 edge/category count
  - `risk_boundaries` (`array<object>`): path/region anchor와 risk reason을 담는 경계 목록
  - `size_thresholds` (`object`): `file_count`, `bytes`, optional `depth` 단위의 numeric threshold set
  - `entrypoint_hints` (`array<string>`): relative path 또는 path-anchored symbol locator 목록
  - `artifact_destination` (`string`): handoff 결과 artifact를 기록할 상대 경로 또는 bounded artifact root
- required output fields:
  - `proposed_slices` (`array<object>`): 제안된 slice record 목록
  - `why_safe` (`object`): slice 또는 region별 safety rationale map
  - `do_not_split_regions` (`array<string>`): split 금지 region id 또는 path anchor 목록
  - `parallel_safe_summary` (`object`): 병렬 실행 가능성 요약
  - `follow_up_probes` (`array<object>`): 추가 확인이 필요한 probe/request 목록

#### Tool Call / CLI Contract

- coarse survey CLI contract는 최소 입력으로 `repo_root` 또는 이에 대응하는 codebase root를 수용할 수 있어야 한다.
- graph/export follow-up contract는 canonical graph artifact family를 후속 입력으로 수용할 수 있어야 한다.
- tool call result envelope required fields:
  - `status`
  - `artifact_paths`
  - `warnings`
  - `errors`

#### JSON Output Contract

- canonical JSON output contract는 `normalized_graph.json`, `nodes.jsonl`, `edges.jsonl`를 중심으로 유지한다.
- `graph_meta.json`은 graph-level metadata와 provenance baseline을 담는 공식 provenance sidecar artifact로 유지한다.
- `merged_graph`는 canonical artifact family의 허용 `graph_kind`이며, codebase graph 내부의 분리된 layer를 보존한 통합 표현을 뜻한다.

## Schema Spec

### Canonical Graph Artifact Schema

#### Required Top-Level Fields

- `graph_id`
- `generated_at`
- `source_scope`
- `graph_kind`
- `schema_version`
- `nodes`
- `edges`

#### Node Schema

Required fields:
- `id`
- `kind`
- `name`

Optional fields:
- `path`
- `parent_id`
- `region`
- `source_tool`
- `confidence`
- `attrs`

#### Edge Schema

Required fields:
- `src`
- `dst`
- `rel`

Optional fields:
- `kind`
- `source_tool`
- `confidence`
- `evidence_path`
- `attrs`

#### Allowed Graph Kinds

- `codebase_graph`
- `analysis_graph`
- `merged_graph`

Graph kind interpretation:
- `analysis_graph`는 과정/오케스트레이션 계층 표현으로 유지한다.
- `merged_graph`는 analysis/orchestration graph와의 병합이 아니라 codebase graph 내부 layer의 통합 표현을 뜻한다.

### Relation Families

Stable relation families that this spec expects to remain representable:
- broad upper relation kinds
  - `IMPORTS`
  - `USES`
  - `CONTAINS`
  - `DEPENDS_ON`
- dependency relations
  - `IMPORTS`
  - `DEPENDS_ON`
  - `READS_MANIFEST`
- containment / declaration relations
  - `DECLARES`
- wrapper / execution relations
  - `WRAPS`
  - `MUTATES_PATH`
  - `RUNS`

V0 core edge minimum:
- `IMPORTS`

Deferred or future-facing relation areas:
- `DECLARES`는 graph-side representable relation로 유지하되 v0 core 최소 집합에는 포함하지 않는다.
- class hierarchy/detail symbol relation은 future symbol expansion 시 future symbol graph core의 우선 수용 대상으로 남긴다.

### Future Symbol Locator

- qualified name 단독 locator는 채택하지 않는다.
- class structure evidence의 세부 symbol 구조는 future symbol graph core에서 path-anchored locator를 기준으로 수용한다.
- future symbol locator는 path-anchored locator를 사용한다.
- 기본 형식은 `relative/file/path.py#Symbol.path`다.
- 필요 시 signature를 추가해 `relative/file/path.py#Symbol.path(signature)` 형식을 사용할 수 있다.
- 예:
  - `src/service/user.py#UserService.save`
  - `src/service/user.py#UserService.save(User)`

### Sidecar Evidence Schema

Sidecar evidence is a separate evidence family for low-connectivity information.

Required fields:
- `evidence_kind`
- `subject_anchor`
- `summary`
- `source_path`
- `evidence_path`
- `reason`
- `confidence`
Optional fields:
- `attrs`

Typical sidecar contents:
- `unresolved`
- `risk`
- `warning`
- `ownership_exception`
- `weak_signal`
- low-connectivity anomaly context

Sidecar rules:
- sidecar record는 반드시 `subject_anchor`를 가진다.
- `summary`는 한 줄 판단 문장으로 유지한다.
- `confidence`는 자유 텍스트가 아니라 정규화된 값으로 유지한다.
- 가능하면 수치형을 사용하고, 수치형이 아니면 제한된 범주형을 사용한다.
- `evidence_kind`가 `unresolved`, `risk`, `warning`, `ownership_exception`, `weak_signal` 중 하나면 sidecar evidence로 유지한다.
- stable file anchor와 재현 가능한 구조 relation으로 닫히는 사실만 graph core 편입 대상으로 유지한다.

### Graph Provenance Sidecar Schema

Stable artifact name:
- `graph_meta.json`

Required fields:
- `graph_id`
- `schema_version`
- `generated_at`
- `source_scope`
- `graph_kind`
- `artifact_paths`
- `trace_id`
- `artifact_location`

Optional fields:
- `attrs`

## Artifact / State Schema Spec

### Scope

- 이 섹션은 DB schema보다 `orchestration 중간 산출물`과 `analysis artifact state`를 우선한다.
- 대상은 task object 전체가 아니라 `codebase-analysis`에 직접 필요한 artifact/state contract다.

### Stable Artifact / State Objects

#### Evidence Record

Required fields:
- `evidence_kind`
- `source_path`
- `evidence_path`
- `confidence`
Optional fields:
- `attrs`
- `trace_id`

#### Sidecar Metadata

Required fields:
- `evidence_kind`
- `reason`
- `source_path`
- `artifact_location`
Optional fields:
- `created_by`
- `schema_version`

#### Tool Call Result Envelope

Required fields:
- `status`
- `artifact_paths`
- `warnings`
- `errors`
Optional fields:
- `trace_id`
- `created_by`

#### Agent Handoff Payload

- field type contract는 `API Spec -> Interface Contract Families -> Handoff Payload Contract`를 따른다.
- 이 단계에서는 `risk_boundaries`, `size_thresholds`, `proposed_slices` 같은 object 계열 필드의 상위 타입만 고정한다.

Required fields:
- `tree_snapshot`
- `graph_summary`
- `risk_boundaries`
- `size_thresholds`
- `entrypoint_hints`
- `artifact_destination`
Optional fields:
- `trace_id`
- `created_by`

### Version / Provenance

- canonical graph artifact는 `schema_version`을 유지한다.
- provenance baseline 필드는 `trace_id`, `artifact_location`으로 고정한다.
- `trace_id`는 같은 실행/검증 흐름에서 여러 artifact를 묶어 추적하는 상관 식별자다.
- `artifact_location`은 evidence나 metadata가 참조하는 산출물의 경로 또는 위치 포인터다.
- `created_by`는 agent 전용이 아니라 script, tool, agent를 포함하는 producer 식별자다.
- `created_by`는 현재 baseline에 포함하지 않고 optional 또는 future extension으로 유지한다.
- sidecar evidence와 handoff payload는 `trace_id`, `artifact_location`을 provenance baseline field로 수용할 수 있고, `created_by`는 optional field로 둘 수 있다.

## Fixed Vs Flexible

### Fixed Before Implementation

- canonical source of truth는 `normalized_graph.json`, `nodes.jsonl`, `edges.jsonl`로 고정한다.
- `graph_meta.json`은 공식 provenance sidecar artifact로 고정한다.
- provenance baseline field는 `trace_id + artifact_location`으로 고정한다.
- `graph evidence -> graph core / sidecar evidence` 분기 구조는 고정한다.
- codebase graph와 analysis/orchestration graph의 논리 계층 분리는 고정한다.
- Node/Edge/Sidecar/Handoff의 required fields는 구현 전 고정한다.
- `Acceptance Criteria`의 required 항목은 구현 전 고정한다.

### Flexible During Implementation

- 구현 파일 경로, 함수명, helper 구조는 유연하게 둔다.
- export/view 도구 선택은 canonical artifact 이후 단계에서 유연하게 둔다.
- `created_by` 같은 추가 provenance field의 채택 여부는 구현 단계에서 결정할 수 있다.

## Implementation Support Appendix

- tool interface와 development playbook은 `references/codebase-analysis-development-playbook-at2026-03-23-03-36.md`로 분리한다.
- bounded worker/sub-agent handoff contract는 [agent-task-packet/SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/SKILL.md)를 implementation support reference로 사용한다.
- 이 appendix는 implementation support 계층이며 canonical core를 대체하지 않는다.

## Policy / Guardrail Spec

### Scope

- 이 섹션은 전체 worktree 운영 규칙이 아니라 `codebase-analysis` spec을 유지하기 위한 최소 guardrail만 다룬다.

### Guardrails

- canonical source of truth를 export/view artifact가 대체하지 않는다.
- codebase graph와 analysis/orchestration graph를 같은 논리 계층으로 합치지 않는다.
- graph core에 넣기 어려운 저연결 정보는 sidecar evidence로 분기한다.
- static relation을 runtime overlay가 직접 덮어쓰지 않고 confidence 보강 또는 보류 판단 레이어로 유지한다.
- spec은 구현 위치, helper 함수명, 내부 세부 구조를 고정하지 않는다.

## Orchestration Spec

### Scope

- 이 섹션은 multi-agent 운영 일반론이 아니라 `codebase-analysis`의 stable stage set과 artifact handoff contract를 다룬다.
- 이 섹션은 구현 순서나 실행 스케줄을 고정하지 않고, stage vocabulary와 stage 간 contract만 고정한다.

### Stable Stage Set

1. coarse survey
2. dependency/class/runtime evidence collection
3. graph evidence formation
4. graph core / sidecar split
5. canonical graph artifact generation
6. export/view derivation

### Stage Contracts

- `coarse survey`
  - input: `codebase`, `active tree`, `top-level structure`
  - output: evidence collection inputs
- `evidence collection`
  - input: dependency/class/runtime source signals
  - output: dependency evidence, class structure evidence, runtime overlay
- `graph evidence formation`
  - input: dependency evidence, class structure evidence, runtime overlay
  - output: graph evidence layer
- `graph core / sidecar split`
  - input: graph evidence layer
  - output: graph core, sidecar evidence
- `canonical graph artifact generation`
  - input: graph core
  - output: `normalized_graph.json`, `nodes.jsonl`, `edges.jsonl`
- `export/view derivation`
  - input: canonical graph artifact
  - output: export/view artifacts

### Conditional Contracts

- runtime evidence가 불완전한 경우 sidecar evidence가 보류 판단과 anomaly context를 보존하고, canonical graph artifact contract는 계속 유지될 수 있다.

## Acceptance Criteria

- related pages:
  - TDD and workspace procedure: [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L95](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L95), [codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md#L207)
  - implementation done-definition/checks: [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L123](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L123), [codebase-analysis-implementation-request-at2026-03-23-10-49.md#L138](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-implementation-request-at2026-03-23-10-49.md#L138)

### Required

- `codebase-analysis`의 핵심 목적이 `graph evidence` 수집과 정리로 유지된다.
- primary source of truth가 canonical base KB와 graph representation KB에 고정된다.
- canonical output set이 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 유지된다.
- `graph_meta.json`이 공식 provenance sidecar artifact로 유지된다.
- provenance baseline field가 `trace_id + artifact_location`으로 유지된다.
- `merged_graph`가 codebase graph 내부 layer의 통합 표현으로 허용된다.
- graph evidence layer가 dependency evidence, class structure evidence, runtime overlay를 입력으로 받아 형성된다.
- graph core와 sidecar evidence의 분기 기준이 명시된다.
- codebase graph와 analysis/orchestration graph의 논리 계층이 분리된다.
- export/view outputs는 canonical graph artifact를 입력으로 받아 후행 생성되는 결과물로 남는다.
- Node Schema required fields `id`, `kind`, `name`가 유지된다.
- Edge Schema required fields `src`, `dst`, `rel`이 유지된다.
- Sidecar Evidence required fields `evidence_kind`, `subject_anchor`, `summary`, `source_path`, `evidence_path`, `reason`, `confidence`가 유지된다.

### Optional

- `created_by`를 provenance extension field로 둘 수 있다.

### Non-Goals

- optional slice stage는 이번 skill의 공식 범위와 평가 대상에 포함하지 않는다.
- 변동성 큰 구현 위치, 함수명, helper 구조는 acceptance 기준으로 고정하지 않는다.
- export/view 도구 종류는 acceptance 기준의 필수 항목으로 고정하지 않는다.
