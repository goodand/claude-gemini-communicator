# Consistency Checklist — codebase-analysis

> 목적: `codebase-analysis`가 graph evidence 중심 analysis skill로 유지되고, canonical base KB와 graph representation KB를 primary source of truth로, slice-stage appendix를 supporting appendix로 읽으면서 관계와 로직이 일관되게 닫히는지 점검한다.
> primary source of truth: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
> supporting appendix: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `graph evidence` 수집과 정리로 고정돼 있다
- [ ] dependency evidence, class structure evidence, runtime overlay가 graph evidence의 하위 evidence layer로 고정돼 있다
- [ ] 이 skill의 역할 경계가 analysis 본체로 명확히 유지된다

## B. Source Of Truth Boundaries

- [ ] canonical base KB와 graph representation KB가 primary source of truth로 유지된다
- [ ] `gate-sequence seed`가 `hybrid_kb` appendix로 위치하고, primary source of truth는 canonical KB에 고정된다
- [ ] 이 checklist가 사용하는 KB 경로가 `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`로 명시돼 있다

## C. Graph Evidence Model

- [ ] graph core가 analysis 본체로 고정돼 있다
- [ ] graph와 연결성이 낮은 risk note, ownership 예외, weak signal이 sidecar evidence file에 안정적으로 배치된다
- [ ] canonical graph artifact가 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
- [ ] Graphviz, Neo4j, Cytoscape, Gephi가 export/view layer로만 취급된다
- [ ] codebase graph와 analysis/orchestration graph의 논리 계층이 명확히 정의된다
- [ ] dependency evidence가 `IMPORTS`, `DEPENDS_ON`, `READS_MANIFEST` 같은 graph relation으로 닫혀 있다
- [ ] class structure evidence가 `DECLARES`, containment, hierarchy-related relation으로 graph에 반영될 수 있게 닫혀 있다
- [ ] wrapper/path mutation 정보가 일반 note가 아니라 `WRAPS`, `MUTATES_PATH`, `RUNS` 같은 relation 후보로 정리돼 있다
- [ ] entrypoint가 단순 파일 목록이 아니라 graph node/relation 관점에서 다뤄진다
- [ ] graph core relation들이 `source_path`, `evidence_path`, `confidence` 같은 추적 필드를 가질 수 있게 설계돼 있다
- [ ] sidecar 배치 기준이 graph core와 구분하여 명시된다

## D. Slice Stage Input Signals

- [ ] slice stage required input family가 `directory tree + file count + total bytes + file extension buckets + manifest locations + static dependency overlay`로 닫혀 있다
- [ ] slice stage strongly recommended input family에 `known entrypoints`, `wrapper/path-mutation register`, `shared hub summary`, `cross-region edge summary`, `cycle/diamond/phantom anomaly ledger`가 남아 있다
- [ ] `tree` 기반 coarse seed 이후 `static dependency overlay`를 포함한 refinement를 거쳐 final slice가 확정된다

## E. Slice Stage Refinement Logic

- [ ] coarse slice seed가 `tree/size/file count/depth` 기준으로 시작된다고 유지된다
- [ ] refinement가 seed 이후 `merge`와 `re-cut`을 둘 다 허용한다고 유지된다
- [ ] `cross-edge ratio`와 `dependency cut cost`에 따라 dependency-aware refinement가 tree-only split보다 우선 적용될 수 있다
- [ ] large shared hub는 protected region 또는 non-write-safe region으로 분류되고, wrapper/path-mutation crossing과 manifest crossing은 관련 경로를 포함한 boundary exception evidence로 남는다
- [ ] slice-stage scoring family에 `size_score`, `internal_cohesion_score`, `cross_edge_ratio`, `shared_hub_penalty`, `runtime_condition_penalty`, `ownership_conflict_penalty`가 남아 있다
- [ ] anomaly 정보(`cycle`, `diamond`, `phantom`)가 초반 slice 판단과 impact/risk 판단에 재사용 가능한 anomaly evidence로 남는다
- [ ] manifest/package crossing이 boundary exception이면서도 graph relation로 남고, 세부 내용보다 관련 경로 중심으로 보존된다

## F. Runtime Overlay And Stop Rules

- [ ] observed runtime edge는 confidence를 높이고, static-only edge는 `unobserved_path_register`에 명시적으로 기록된다
- [ ] runtime overlay가 confidence 보강 또는 보류 판단 레이어로 작동한다
- [ ] stop rules에 `single large hub file`, `ambiguous wrapper indirection`, `excessive cross-edge density`, `path-order/runtime-condition dependence`, `coordination cost > split value`가 남아 있다

## G. Output Contract

- [ ] primary source-of-truth output family는 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
- [ ] slice stage를 쓴 경우 global outputs에 `inventory_snapshot.json`, `slice_seed_candidates.json`, `static_dependency_overlay.json`, `slice_refinement_report.md`가 포함된다
- [ ] optional slice-stage outputs로 `runtime_overlay.json`과 `unobserved_path_register.json`을 허용한다고 유지된다
- [ ] final slice outputs가 `parallel_slices.json` + (`write_safe_slices.json` 또는 `analysis_only_slices.json`) + `do_not_split_regions.json`으로 닫혀 있다
- [ ] export/view outputs는 canonical graph artifact를 입력으로 받아 후행 생성되는 결과물이다

## H. Input And Output Families

- [ ] 최종 analysis input family가 `active tree/top-level structure + dependency evidence + class structure evidence + runtime overlay`로 닫혀 있다
- [ ] 최종 analysis output family가 `graph core + sidecar evidence + optional slice-stage outputs + export/view outputs`로 구분돼 있다
- [ ] optional slice-stage outputs의 appendix-derived 지위가 primary graph outputs와 구분하여 표시된다

## I. Layer-To-Layer Transition

- [ ] `coarse survey`와 `active tree/top-level structure` 결과가 dependency evidence, class structure evidence, runtime overlay 수집의 초기 입력으로 이어진다고 유지된다
- [ ] dependency evidence, class structure evidence, runtime overlay가 누적되어 graph evidence layer를 이루고, 그 graph evidence가 graph core/sidecar split 또는 optional slice stage의 상위 입력으로 이어진다고 유지된다
- [ ] slice stage를 쓰는 경우 `inventory_snapshot.json`과 `slice_seed_candidates.json`이 static dependency overlay와 refinement의 중간 입력/출력 artifact로 유지된다
- [ ] `static_dependency_overlay.json`이 refinement 단계의 직접 입력으로 이어지고, refinement 결과가 runtime overlay와 stop rules 판단의 입력으로 이어진다고 유지된다
- [ ] `runtime_overlay.json`과 `unobserved_path_register.json`은 final slice proposal 이전의 transition artifact로 남는다
- [ ] graph core/sidecar split 이후 canonical graph artifact가 export/view layer의 직접 입력으로 이어진다

## J. Graph Core Minimal Schema

- [ ] graph core의 기본 분석 단위가 우선 `file`로 고정되고, 추후 symbol 단위 확장이 가능한 방향으로 설계된다
- [ ] 초기 graph core의 최소 node kind가 `file`로 닫혀 있다
- [ ] 초기 core edge는 `imports`를 중심 relation으로 두고, `defines`는 후속 확장 대상으로 유보된다
- [ ] node `id`가 path 기반 안정 식별자를 우선 사용한다
- [ ] relation이 schema 수준에서 방향성을 가지며, query/view 단계에서 역방향 조회 가능성이 분리되어 이해된다
- [ ] graph core에는 재현 가능한 구조 사실만 편입된다
- [ ] 동일 의미 관계를 과도하게 하나의 edge kind로 압축하지 않고, relation kind 확장 가능성을 열어 둔다
- [ ] 초기에 `uses`, `contains`, `depends_on` 같은 broad relation 상위 kind를 둘 수 있는 확장 방향이 명시된다
- [ ] 넓은 relation kind를 사용하더라도 relation 의미가 path-anchored 구조 증거와 연결되도록 유지된다

## K. Sidecar Evidence Schema

- [ ] weak signal이 기본적으로 sidecar evidence schema로 배치되고, core 승격은 예외 경로로 이해된다
- [ ] unresolved 상태의 정보가 sidecar evidence schema에 정규화된 검토 단위로 남는다
- [ ] risk, warning, ownership exception이 sidecar kind로 수용된다
- [ ] 각 sidecar record가 특정 subject(node 또는 path)에 anchor된다
- [ ] confidence가 자유 텍스트가 아니라 정규화된 값으로 기록된다
- [ ] summary가 장문 메모보다 한 줄 판단 문장 중심으로 유지된다
- [ ] provenance 또는 evidence 참조가 sidecar evidence schema의 공통 개념으로 포함된다

## L. Canonical Artifact Record Discipline

- [ ] `normalized_graph.json`은 graph-level 규약과 설명을 담고, node/edge 실레코드와 역할이 구분된다
- [ ] `nodes.jsonl`과 `edges.jsonl`의 각 레코드가 독립 검증 가능한 최소 필수 필드를 가진다
- [ ] core와 sidecar 모두에서 provenance/evidence 참조를 공통 개념으로 유지한다
- [ ] 초기 schema는 optional field를 과도하게 늘리기보다 적은 mandatory field를 먼저 고정한다
- [ ] 초기 설계 우선순위가 표현력 최대화에 놓이고, 정합성 최대화는 후속 refinement 단계로 남는다

## M. Future Symbol Extension Direction

- [ ] future symbol locator가 기본적으로 path-anchored symbol locator 방향을 따른다
- [ ] future symbol locator가 `relative file path + symbol path`를 기본 형식으로 사용한다
- [ ] 이름 충돌이나 overload 구분이 필요할 때 symbol locator가 인자, 타입, 형태 정보를 더해 정확도를 높일 수 있게 설계된다
