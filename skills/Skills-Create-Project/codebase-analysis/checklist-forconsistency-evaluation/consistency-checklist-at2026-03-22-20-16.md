# Consistency Checklist — codebase-analysis

> 목적: `codebase-analysis`가 graph evidence 중심 analysis skill로 유지되고, canonical base KB와 graph representation KB를 primary source of truth로, slice-stage appendix를 supporting appendix로 읽으면서 관계와 로직이 일관되게 닫히는지 점검한다.
> primary source of truth: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
> supporting appendix: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `graph evidence` 수집과 정리로 고정돼 있다
- [ ] dependency evidence, class structure evidence, runtime overlay가 graph evidence의 하위 evidence layer로 고정돼 있다
- [ ] 이 skill이 orchestration/setup 본체나 final launch/runtime ownership으로 다시 퍼지지 않고 analysis 본체로 유지된다

## B. Source Of Truth Boundaries

- [ ] canonical base KB와 graph representation KB가 primary source of truth로 유지된다
- [ ] `gate-sequence seed`는 `hybrid_kb` appendix로 남고 primary source of truth를 대체하지 않는다
- [ ] accumulated analysis evidence docs는 supporting evidence이며 canonical KB가 아님이 유지된다

## C. Graph Evidence Model

- [ ] graph core가 analysis 본체로 고정돼 있다
- [ ] graph와 연결성이 낮은 risk note, ownership 예외, weak signal은 sidecar evidence file로 분리한다고 유지된다
- [ ] canonical graph artifact가 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
- [ ] Graphviz, Neo4j, Cytoscape, Gephi가 export/view layer로만 취급된다
- [ ] codebase graph와 analysis/orchestration graph가 논리적으로 분리된다는 원칙이 유지된다
- [ ] dependency evidence가 `IMPORTS`, `DEPENDS_ON`, `READS_MANIFEST` 같은 graph relation으로 닫혀 있다
- [ ] class structure evidence가 `DECLARES`, containment, hierarchy-related relation으로 graph에 반영될 수 있게 닫혀 있다
- [ ] wrapper/path mutation 정보가 일반 note가 아니라 `WRAPS`, `MUTATES_PATH`, `RUNS` 같은 relation 후보로 정리돼 있다
- [ ] entrypoint가 단순 파일 목록이 아니라 graph node/relation 관점에서 다뤄진다
- [ ] graph core relation들이 `source_path`, `evidence_path`, `confidence` 같은 추적 필드를 가질 수 있게 설계돼 있다
- [ ] sidecar로 빠진 정보가 왜 graph core에 못 들어가는지 기준이 분명하다

## D. Slice Stage Input Signals

- [ ] slice stage required input family가 `directory tree + file count + total bytes + file extension buckets + manifest locations + static dependency overlay`로 닫혀 있다
- [ ] slice stage strongly recommended input family에 `known entrypoints`, `wrapper/path-mutation register`, `shared hub summary`, `cross-region edge summary`, `cycle/diamond/phantom anomaly ledger`가 남아 있다
- [ ] `tree`만으로 시작할 수는 있어도 `static dependency overlay` 없이 final slice를 확정하지 않는다고 유지된다

## E. Slice Stage Refinement Logic

- [ ] coarse slice seed가 `tree/size/file count/depth` 기준으로 시작된다고 유지된다
- [ ] refinement가 seed 이후 `merge`와 `re-cut`을 둘 다 허용한다고 유지된다
- [ ] `cross-edge ratio`가 높거나 `dependency cut cost`가 더 나쁘면 tree-only split을 포기할 수 있다고 유지된다
- [ ] large shared hub는 write-safe split 금지 대상이고, wrapper/path-mutation crossing은 위험 표시, manifest crossing은 boundary exception으로 처리된다고 유지된다
- [ ] slice-stage scoring family에 `size_score`, `internal_cohesion_score`, `cross_edge_ratio`, `shared_hub_penalty`, `runtime_condition_penalty`, `ownership_conflict_penalty`가 남아 있다
- [ ] anomaly 정보(`cycle`, `diamond`, `phantom`)가 초반 slice 판단과 impact/risk 판단에 재사용 가능한 anomaly evidence로 남는다
- [ ] manifest/package crossing이 boundary exception이면서도 graph relation로 남고, 세부 내용보다 관련 경로 중심으로 보존된다

## F. Runtime Overlay And Stop Rules

- [ ] observed runtime edge는 confidence를 높이고, static-only edge는 `unobserved_path_register`로 분리한다고 유지된다
- [ ] 누락 관계를 runtime/probe follow-up으로 다시 확인하는 방향이 남아 있고, 정적 근거 없는 추측으로 닫지 않는다고 유지된다
- [ ] runtime overlay가 static relation을 덮어쓰는 것이 아니라 confidence 보강 또는 보류 판단 레이어로 붙는다
- [ ] stop rules에 `single large hub file`, `ambiguous wrapper indirection`, `excessive cross-edge density`, `path-order/runtime-condition dependence`, `coordination cost > split value`가 남아 있다

## G. Output Contract

- [ ] primary source-of-truth output family는 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
- [ ] slice stage를 쓴 경우 global outputs에 `inventory_snapshot.json`, `slice_seed_candidates.json`, `static_dependency_overlay.json`, `slice_refinement_report.md`가 포함된다
- [ ] optional slice-stage outputs로 `runtime_overlay.json`과 `unobserved_path_register.json`을 허용한다고 유지된다
- [ ] final slice outputs가 `parallel_slices.json` + (`write_safe_slices.json` 또는 `analysis_only_slices.json`) + `do_not_split_regions.json`으로 닫혀 있다
- [ ] export/view outputs는 후행 산출물이며 canonical graph artifact를 대체하지 않는다

## H. Input And Output Families

- [ ] 최종 analysis input family가 `active tree/top-level structure + dependency evidence + class structure evidence + runtime overlay`로 닫혀 있다
- [ ] 최종 analysis output family가 `graph core + sidecar evidence + optional slice-stage outputs + export/view outputs`로 구분돼 있다
- [ ] optional slice-stage outputs는 appendix-derived outputs로 남고 primary graph outputs와 혼동되지 않는다

## I. Layer-To-Layer Transition

- [ ] `coarse survey`와 `active tree/top-level structure` 결과가 dependency evidence, class structure evidence, runtime overlay 수집의 초기 입력으로 이어진다고 유지된다
- [ ] dependency evidence, class structure evidence, runtime overlay가 누적되어 graph evidence layer를 이루고, 그 graph evidence가 graph core/sidecar split 또는 optional slice stage의 상위 입력으로 이어진다고 유지된다
- [ ] slice stage를 쓰는 경우 `inventory_snapshot.json`과 `slice_seed_candidates.json`이 static dependency overlay와 refinement의 중간 입력/출력 artifact로 유지된다
- [ ] `static_dependency_overlay.json`이 refinement 단계의 직접 입력으로 이어지고, refinement 결과가 runtime overlay와 stop rules 판단의 입력으로 이어진다고 유지된다
- [ ] `runtime_overlay.json`과 `unobserved_path_register.json`은 final slice proposal 이전의 transition artifact로 남고, 필요 시 probe follow-up의 근거로 재사용된다고 유지된다
- [ ] graph core/sidecar split 이후 canonical graph artifact가 export/view layer의 직접 입력으로 이어지며, export/view layer output이 역으로 source of truth를 덮지 않는다고 유지된다
