# Consistency Checklist — codebase-analysis

> 목적: `codebase-analysis`가 graph evidence 중심 analysis skill로 유지되고, canonical base KB와 graph representation KB를 primary source of truth로, slice-stage appendix를 supporting appendix로 읽으면서 관계와 로직이 일관되게 닫히는지 점검한다.
> primary source of truth: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
> supporting appendix: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`

## Evaluation Record Rule

- 각 문항은 자유 해석이 아니라 지정된 파일, 섹션, 필드 기준으로 `pass` 또는 `fail`로 판정한다.
- `pass`일 때만 인용 근거를 남기고, 인용 근거는 재검토 가능한 파일 경로와 줄번호 형태로 남긴다.
- `fail`은 수정 대상으로만 남기고, 인용 근거 강제는 두지 않는다.

## A. Identity

- 검증 대상: `SKILL.md`의 `When to use`/`Notes`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Canonical design takeaways`

- [ ] 이 skill의 핵심 목적이 `graph evidence` 수집과 정리로 고정돼 있다
- [ ] dependency evidence, class structure evidence, runtime overlay가 graph evidence의 하위 evidence layer로 고정돼 있다
- [ ] 이 skill의 역할 경계가 analysis 본체로 명확히 유지된다

## B. Source Of Truth Boundaries

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 frontmatter/purpose/takeaways

- [ ] canonical base KB와 graph representation KB가 primary source of truth로 유지된다
- [ ] `gate-sequence seed`가 `hybrid_kb` appendix로 위치하고, primary source of truth는 canonical KB에 고정된다
- [ ] 이 checklist가 사용하는 KB 경로가 `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`로 명시돼 있다

## C. Graph Evidence Model

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Canonical design takeaways`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 `Core Decision`, `Recommended Canonical Artifacts`, `Layer Separation Rule`

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

- 검증 대상: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Canonical Input Signals`

- [ ] slice stage required input family가 `directory tree + file count + total bytes + file extension buckets + manifest locations + static dependency overlay`로 닫혀 있다
- [ ] slice stage strongly recommended input family에 `known entrypoints`, `wrapper/path-mutation register`, `shared hub summary`, `cross-region edge summary`, `cycle/diamond/phantom anomaly ledger`가 남아 있다
- [ ] `tree` 기반 coarse seed 이후 `static dependency overlay`를 포함한 refinement를 거쳐 final slice가 확정된다

## E. Slice Stage Refinement Logic

- 검증 대상: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Recommended Slice Stage Sequence` 중 `Coarse slice seed`, `Static dependency graph overlay`, `Refinement`와 `Canonical Design Takeaways`

- [ ] coarse slice seed가 `tree/size/file count/depth` 기준으로 시작된다고 유지된다
- [ ] refinement가 seed 이후 `merge`와 `re-cut`을 둘 다 허용한다고 유지된다
- [ ] `cross-edge ratio`와 `dependency cut cost`에 따라 dependency-aware refinement가 tree-only split보다 우선 적용될 수 있다
- [ ] large shared hub는 protected region 또는 non-write-safe region으로 분류되고, wrapper/path-mutation crossing과 manifest crossing은 관련 경로를 포함한 boundary exception evidence로 남는다
- [ ] slice-stage scoring family에 `size_score`, `internal_cohesion_score`, `cross_edge_ratio`, `shared_hub_penalty`, `runtime_condition_penalty`, `ownership_conflict_penalty`가 남아 있다
- [ ] anomaly 정보(`cycle`, `diamond`, `phantom`)가 초반 slice 판단과 impact/risk 판단에 재사용 가능한 anomaly evidence로 남는다
- [ ] manifest/package crossing이 boundary exception이면서도 graph relation로 남고, 세부 내용보다 관련 경로 중심으로 보존된다

## F. Runtime Overlay And Stop Rules

- 검증 대상: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Runtime overlay`, `Stop rules`

- [ ] observed runtime edge는 confidence를 높이고, static-only edge는 `unobserved_path_register`에 명시적으로 기록된다
- [ ] runtime overlay가 confidence 보강 또는 보류 판단 레이어로 작동한다
- [ ] stop rules에 `single large hub file`, `ambiguous wrapper indirection`, `excessive cross-edge density`, `path-order/runtime-condition dependence`, `coordination cost > split value`가 남아 있다

## G. Output Contract

- 검증 대상: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 `Core Decision`/`Recommended Canonical Artifacts`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Canonical Output Contract`

- [ ] primary source-of-truth output family는 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
- [ ] slice stage를 쓴 경우 global outputs에 `inventory_snapshot.json`, `slice_seed_candidates.json`, `static_dependency_overlay.json`, `slice_refinement_report.md`가 포함된다
- [ ] optional slice-stage outputs로 `runtime_overlay.json`과 `unobserved_path_register.json`을 허용한다고 유지된다
- [ ] final slice outputs가 `parallel_slices.json` + (`write_safe_slices.json` 또는 `analysis_only_slices.json`) + `do_not_split_regions.json`으로 닫혀 있다
- [ ] export/view outputs는 canonical graph artifact를 입력으로 받아 후행 생성되는 결과물이다

## H. Input And Output Families

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Gate sequence relation`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 artifact 정의, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 input/output family

- [ ] 최종 analysis input family가 `active tree/top-level structure + dependency evidence + class structure evidence + runtime overlay`로 닫혀 있다
- [ ] 최종 analysis output family가 `graph core + sidecar evidence + optional slice-stage outputs + export/view outputs`로 구분돼 있다
- [ ] optional slice-stage outputs의 appendix-derived 지위가 primary graph outputs와 구분하여 표시된다

## I. Layer-To-Layer Transition

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Gate sequence relation`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 phase sequence, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 `Recommended build sequence`

- [ ] `coarse survey`와 `active tree/top-level structure` 결과가 dependency evidence, class structure evidence, runtime overlay 수집의 초기 입력으로 이어진다고 유지된다
- [ ] dependency evidence, class structure evidence, runtime overlay가 누적되어 graph evidence layer를 이루고, 그 graph evidence가 graph core/sidecar split 또는 optional slice stage의 상위 입력으로 이어진다고 유지된다
- [ ] slice stage를 쓰는 경우 `inventory_snapshot.json`과 `slice_seed_candidates.json`이 static dependency overlay와 refinement의 중간 입력/출력 artifact로 유지된다
- [ ] `static_dependency_overlay.json`이 refinement 단계의 직접 입력으로 이어지고, refinement 결과가 runtime overlay와 stop rules 판단의 입력으로 이어진다고 유지된다
- [ ] `runtime_overlay.json`과 `unobserved_path_register.json`은 final slice proposal 이전의 transition artifact로 남는다
- [ ] graph core/sidecar split 이후 canonical graph artifact가 export/view layer의 직접 입력으로 이어진다
