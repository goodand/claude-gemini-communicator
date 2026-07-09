# Doc-Code Consistency Checklist — codebase-analysis

> 목적: `codebase-analysis`의 KB-grounded 문항을 문서 evidence와 code target의 pair로 내려서 실제 codebase와의 정합성을 점검한다.
> primary source of truth: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
> supporting appendix: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`

## Evaluation Record Rule

- 각 문항은 `doc evidence`와 `code target`의 pair 기준으로 `pass` 또는 `fail`로 판정한다.
- `doc evidence`는 KB grounding checklist에서 가져온 문서 근거를 유지한다.
- 문항이 layer 책임을 다루면 `Expected input family`와 `Expected output family`를 쓴다.
- 문항이 더 구체적인 계약을 다루면 `Expected input`과 `Expected output`을 쓴다.
- `pass`일 때는 문서 근거와 실제 코드/출력 근거를 함께 남기고, `fail`일 때는 mismatch 유형과 수정 대상을 남긴다.

## A. Identity / Boundary

- 검증 대상: `SKILL.md`의 `When to use`/`Notes`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Canonical design takeaways`

- [ ] 이 skill의 핵심 목적이 `graph evidence` 수집과 정리로 고정돼 있다
  - Pass 기준: `graph evidence`가 SKILL 또는 canonical base KB에서 핵심 목적 또는 핵심 키워드로 명시된다.
  - Fail 징후: skill 목적이 orchestration, launch ownership, 특정 export 도구 중심으로 이동한다.
  - Doc evidence: `SKILL.md:16-20,33`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:17`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] dependency evidence, class structure evidence, runtime overlay가 graph evidence의 하위 evidence layer로 고정돼 있다
  - Pass 기준: dependency, class structure, runtime overlay가 graph evidence의 하위 layer로 명시된다.
  - Fail 징후: 하위 evidence layer 구분이 사라지거나 별도 orchestration layer와 혼합된다.
  - Doc evidence: `SKILL.md:17,33`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:18`
  - Expected input family:
  - Expected output family:
  - Pass/Fail:
  - Notes:
- [ ] 이 skill의 역할 경계가 analysis 본체로 명확히 유지된다
  - Pass 기준: slice, handoff, fan-in, orchestration runtime ownership이 외부 skill 경계로 빠지고 analysis 본체만 남는다.
  - Fail 징후: subagent lifecycle, launch ownership, orchestration setup이 이 skill 본문으로 다시 들어온다.
  - Doc evidence: `SKILL.md:34-37`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:19-20,53-59`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## B. Input / Output Contract

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 frontmatter/purpose/takeaways

- [ ] canonical base KB와 graph representation KB가 primary source of truth로 유지된다
  - Pass 기준: read order와 source-of-truth 설명이 canonical base KB와 graph representation KB를 우선 기준으로 고정한다.
  - Fail 징후: appendix seed나 export artifact가 primary source처럼 앞선다.
  - Doc evidence: `consistency-checklist-at2026-03-23-01-50.md:2-4`, `SKILL.md:24-25,37`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:28-30`
  - Expected input family:
  - Expected output family:
  - Pass/Fail:
  - Notes:
- [ ] `gate-sequence seed`가 `hybrid_kb` appendix로 위치하고, primary source of truth는 canonical KB에 고정된다
  - Pass 기준: gate-sequence seed의 `kb_profile`이 `hybrid_kb`이고 base KB에서 appendix branch로 위치한다.
  - Fail 징후: gate-sequence seed가 canonical KB를 대체하거나 primary source 역할로 승격된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:1-10`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:28-31`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] 이 checklist가 사용하는 KB 경로가 `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`로 명시돼 있다
  - Pass 기준: checklist 본문에 세 KB 경로가 verification target 또는 source-of-truth 문맥으로 직접 적혀 있다.
  - Fail 징후: KB 경로 중 하나라도 빠지거나 다른 파일로 바뀐다.
  - Doc evidence: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-23-01-50.md:43`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## C. Rule Mapping

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Canonical design takeaways`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 `Core Decision`, `Recommended Canonical Artifacts`, `Layer Separation Rule`

- [ ] graph core가 analysis 본체로 고정돼 있다
  - Pass 기준: graph core가 analysis 본체의 주된 모델링 대상이라고 드러난다.
  - Fail 징후: graph core보다 orchestration graph나 view artifact가 본체처럼 서술된다.
  - Doc evidence: `SKILL.md:12,17-20,33-35`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:17,21`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] graph와 연결성이 낮은 risk note, ownership 예외, weak signal이 sidecar evidence file에 안정적으로 배치된다
  - Pass 기준: 저연결 정보가 sidecar evidence file로 분기된다고 명시된다.
  - Fail 징후: weak signal, ownership 예외, long-form note가 graph core에 직접 섞인다.
  - Doc evidence: `SKILL.md:19,35`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:21`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] canonical graph artifact가 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
  - Pass 기준: source-of-truth artifact가 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정된다.
  - Fail 징후: DOT, Neo4j, Cytoscape 같은 특정 도구 포맷이 canonical artifact를 대체한다.
  - Doc evidence: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:22`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:18-25,221-224`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] Graphviz, Neo4j, Cytoscape, Gephi가 export/view layer로만 취급된다
  - Pass 기준: Graphviz, Neo4j, Cytoscape, Gephi가 canonical artifact 이후의 storage/query/view consumer로 위치한다.
  - Fail 징후: Neo4j처럼 storage/query 역할이 있는 도구를 export/view layer only로 축소한다.
  - Doc evidence:
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] codebase graph와 analysis/orchestration graph의 논리 계층이 명확히 정의된다
  - Pass 기준: codebase graph와 analysis/orchestration graph가 별도 node/relation 집합으로 정의된다.
  - Fail 징후: slice, agent, contradiction 같은 analysis node가 codebase graph와 한 계층으로 섞인다.
  - Doc evidence: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:149-196`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] dependency evidence가 `IMPORTS`, `DEPENDS_ON`, `READS_MANIFEST` 같은 graph relation으로 닫혀 있다
  - Pass 기준: dependency evidence가 codebase graph relation set에서 relation kind로 명시된다.
  - Fail 징후: dependency evidence가 prose note나 external export 설정으로만 남는다.
  - Doc evidence: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:167-176`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] class structure evidence가 `DECLARES`, containment, hierarchy-related relation으로 graph에 반영될 수 있게 닫혀 있다
  - Pass 기준: class structure evidence를 위한 `DECLARES`, containment, hierarchy relation family가 canonical relation set에 직접 나타난다.
  - Fail 징후: `DECLARES`와 containment는 있어도 hierarchy relation family가 canonical relation set에 직접 나타나지 않는다.
  - Doc evidence:
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] wrapper/path mutation 정보가 일반 note가 아니라 `WRAPS`, `MUTATES_PATH`, `RUNS` 같은 relation 후보로 정리돼 있다
  - Pass 기준: wrapper/path mutation/run signal이 codebase graph relation 후보 또는 overlay signal로 명시된다.
  - Fail 징후: wrapper/path mutation이 long-form note나 risk memo로만 남는다.
  - Doc evidence: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:167-176`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:95-98,232`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] entrypoint가 단순 파일 목록이 아니라 graph node/relation 관점에서 다뤄진다
  - Pass 기준: `Entrypoint`가 node kind로 나타나고 slice-stage 입력/산출에서도 entrypoint가 별도 필드로 유지된다.
  - Fail 징후: entrypoint가 단순 참고 파일 목록으로만 남고 graph 모델에 연결되지 않는다.
  - Doc evidence: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:163-176`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:54,78,187,201`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] graph core relation들이 `source_path`, `evidence_path`, `confidence` 같은 추적 필드를 가질 수 있게 설계돼 있다
  - Pass 기준: node/edge schema에 path, evidence_path, confidence 같은 추적 필드가 제안된다.
  - Fail 징후: canonical schema가 relation traceability 없이 src/dst만 남긴다.
  - Doc evidence: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:122-147`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] sidecar 배치 기준이 graph core와 구분하여 명시된다
  - Pass 기준: graph core에는 고연결 구조 증거를 두고 저연결 정보는 sidecar로 보낸다는 기준이 직접 적혀 있다.
  - Fail 징후: graph core와 sidecar의 분기 기준이 빠지거나 암묵적이다.
  - Doc evidence: `SKILL.md:19,35`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:21`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## D. Layer / Ownership

- 검증 대상: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Canonical Input Signals`

- [ ] slice stage required input family가 `directory tree + file count + total bytes + file extension buckets + manifest locations + static dependency overlay`로 닫혀 있다
  - Pass 기준: required input family가 해당 여섯 신호로 닫혀 있다.
  - Fail 징후: static dependency overlay가 빠지거나 required set이 다른 구조로 흔들린다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:45-52`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] slice stage strongly recommended input family에 `known entrypoints`, `wrapper/path-mutation register`, `shared hub summary`, `cross-region edge summary`, `cycle/diamond/phantom anomaly ledger`가 남아 있다
  - Pass 기준: strongly recommended input family가 entrypoint, wrapper/path-mutation, hub, cross-region, anomaly ledger를 포함한다.
  - Fail 징후: anomaly ledger나 wrapper/path-mutation register가 입력 family에서 사라진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:53-58`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] `tree` 기반 coarse seed 이후 `static dependency overlay`를 포함한 refinement를 거쳐 final slice가 확정된다
  - Pass 기준: tree-based coarse seed가 refinement 전 단계로 위치하고 static dependency overlay가 final slice 전제 조건으로 남는다.
  - Fail 징후: tree-only partition이 final slice 결정으로 승격된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:66-67,83-117`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## E. Slice Stage Refinement Logic

- 검증 대상: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Recommended Slice Stage Sequence` 중 `Coarse slice seed`, `Static dependency graph overlay`, `Refinement`와 `Canonical Design Takeaways`

- [ ] coarse slice seed가 `tree/size/file count/depth` 기준으로 시작된다고 유지된다
  - Pass 기준: coarse slice seed 단계가 tree, size, file count, depth 기준으로 시작한다.
  - Fail 징후: 초기 seed가 dependency overlay나 runtime signal 없이 바로 graph-aware split로 시작한다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:83-88`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] refinement가 seed 이후 `merge`와 `re-cut`을 둘 다 허용한다고 유지된다
  - Pass 기준: refinement 단계가 seed 이후 `merge`와 `re-cut`을 함께 허용한다.
  - Fail 징후: refinement가 split only 또는 merge only 정책으로 축소된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:107-117`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] `cross-edge ratio`와 `dependency cut cost`에 따라 dependency-aware refinement가 tree-only split보다 우선 적용될 수 있다
  - Pass 기준: cross-edge ratio와 dependency cut cost가 tree boundary보다 우선하는 refinement 조건으로 남아 있다.
  - Fail 징후: directory boundary가 dependency crossing cost와 무관하게 유지된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:111-117,229-230`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] large shared hub는 protected region 또는 non-write-safe region으로 분류되고, wrapper/path-mutation crossing과 manifest crossing은 관련 경로를 포함한 boundary exception evidence로 남는다
  - Pass 기준: shared hub protection과 crossing exception이 path-bearing boundary evidence shape로 직접 닫혀 있다.
  - Fail 징후: source KB가 risk 표시나 boundary exception 등록까지만 말하고 경로 포함 evidence shape를 직접 닫지 않는다.
  - Doc evidence:
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] slice-stage scoring family에 `size_score`, `internal_cohesion_score`, `cross_edge_ratio`, `shared_hub_penalty`, `runtime_condition_penalty`, `ownership_conflict_penalty`가 남아 있다
  - Pass 기준: 여섯 scoring 신호가 slice-stage scoring family로 직접 나열된다.
  - Fail 징후: scoring family가 일부만 남거나 다른 규칙으로 대체된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:119-125`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] anomaly 정보(`cycle`, `diamond`, `phantom`)가 초반 slice 판단과 impact/risk 판단에 재사용 가능한 anomaly evidence로 남는다
  - Pass 기준: anomaly ledger와 overlay/takeaway가 cycle, diamond, phantom을 graph-side evidence로 유지한다.
  - Fail 징후: anomaly 정보가 한 번 보는 note로만 남고 overlay나 takeaways에서 사라진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:57-58,100-102,232`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] manifest/package crossing이 boundary exception이면서도 graph relation로 남고, 세부 내용보다 관련 경로 중심으로 보존된다
  - Pass 기준: manifest/package crossing이 boundary exception이면서 path-centered graph relation 또는 evidence shape로 직접 닫혀 있다.
  - Fail 징후: source KB가 manifest crossing을 signal 또는 boundary exception으로만 말하고 final graph relation shape를 직접 닫지 않는다.
  - Doc evidence:
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## F. Runtime Overlay And Stop Rules

- 검증 대상: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Runtime overlay`, `Stop rules`

- [ ] observed runtime edge는 confidence를 높이고, static-only edge는 `unobserved_path_register`에 명시적으로 기록된다
  - Pass 기준: observed runtime edge의 confidence 상승과 static-only edge의 register 기록 규칙이 함께 남아 있다.
  - Fail 징후: observed/runtime distinction이 사라지거나 unobserved register가 빠진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:135-142`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] runtime overlay가 confidence 보강 또는 보류 판단 레이어로 작동한다
  - Pass 기준: runtime overlay의 목적이 static relation의 활성 여부 확인과 confidence 조정으로 적혀 있다.
  - Fail 징후: runtime overlay가 static graph를 대체하는 primary source처럼 서술된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:130-137`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] stop rules에 `single large hub file`, `ambiguous wrapper indirection`, `excessive cross-edge density`, `path-order/runtime-condition dependence`, `coordination cost > split value`가 남아 있다
  - Pass 기준: stop rules 항목이 다섯 가지로 직접 나열된다.
  - Fail 징후: wrapper indirection, path-order/runtime condition, coordination cost 규칙이 빠진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:144-150`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## G. Output Contract

- 검증 대상: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 `Core Decision`/`Recommended Canonical Artifacts`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 `Canonical Output Contract`

- [ ] primary source-of-truth output family는 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
  - Pass 기준: primary output family가 canonical artifact triple로 직접 고정된다.
  - Fail 징후: slice outputs나 DOT/Neo4j artifact가 primary source-of-truth output으로 승격된다.
  - Doc evidence: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:20-25,221-224`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] slice stage를 쓴 경우 global outputs에 `inventory_snapshot.json`, `slice_seed_candidates.json`, `static_dependency_overlay.json`, `slice_refinement_report.md`가 포함된다
  - Pass 기준: global outputs에 inventory, slice seed, static overlay, refinement report가 함께 포함된다.
  - Fail 징후: refinement report나 static dependency overlay가 global outputs에서 빠진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:162-166`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] optional slice-stage outputs로 `runtime_overlay.json`과 `unobserved_path_register.json`을 허용한다고 유지된다
  - Pass 기준: runtime overlay와 unobserved path register가 optional outputs로 직접 남아 있다.
  - Fail 징후: optional outputs가 필수 출력으로 승격되거나 output family에서 빠진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:167-168`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] final slice outputs가 `parallel_slices.json` + (`write_safe_slices.json` 또는 `analysis_only_slices.json`) + `do_not_split_regions.json`으로 닫혀 있다
  - Pass 기준: final slice outputs가 `parallel_slices.json`, write-safe or analysis-only slices, do-not-split regions로 닫혀 있다.
  - Fail 징후: final outputs에서 slice classification 파일이나 do-not-split regions가 빠진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:152-156,169-172`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] export/view outputs는 canonical graph artifact를 입력으로 받아 후행 생성되는 결과물이다
  - Pass 기준: canonical artifact가 먼저 생성되고 export/view는 그 이후 단계로 배치된다.
  - Fail 징후: export/view artifact가 canonical artifact보다 먼저 생성되거나 source of truth처럼 취급된다.
  - Doc evidence: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:25,71-77`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## H. Input And Output Families

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Gate sequence relation`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 artifact 정의, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 input/output family

- [ ] 최종 analysis input family가 `active tree/top-level structure + dependency evidence + class structure evidence + runtime overlay`로 닫혀 있다
  - Pass 기준: active tree/top-level 구조와 dependency/class/runtime evidence family가 analysis 입력 축으로 함께 나타난다.
  - Fail 징후: active tree나 runtime overlay가 analysis 입력 family에서 빠진다.
  - Doc evidence: `SKILL.md:16-18`, `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:36-38`
  - Expected input family:
  - Expected output family:
  - Pass/Fail:
  - Notes:
- [ ] 최종 analysis output family가 `graph core + sidecar evidence + optional slice-stage outputs + export/view outputs`로 구분돼 있다
  - Pass 기준: graph core, sidecar evidence, optional slice-stage outputs, export/view outputs가 별도 output family로 읽힌다.
  - Fail 징후: sidecar나 optional slice outputs가 graph core 또는 export/view와 섞여 하나의 output처럼 서술된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:21-24,40`, `SKILL.md:19-20,35`
  - Expected input family:
  - Expected output family:
  - Pass/Fail:
  - Notes:
- [ ] optional slice-stage outputs의 appendix-derived 지위가 primary graph outputs와 구분하여 표시된다
  - Pass 기준: optional slice-stage outputs가 appendix branch의 파생 산출물이고 primary graph outputs와 다른 층위로 읽힌다.
  - Fail 징후: optional slice-stage outputs가 canonical graph artifact와 같은 primary source output처럼 보인다.
  - Doc evidence: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:28-31,34-40`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:20-25`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:

## I. Layer-To-Layer Transition

- 검증 대상: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`의 `Gate sequence relation`, `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`의 phase sequence, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`의 `Recommended build sequence`

- [ ] `coarse survey`와 `active tree/top-level structure` 결과가 dependency evidence, class structure evidence, runtime overlay 수집의 초기 입력으로 이어진다고 유지된다
  - Pass 기준: coarse survey와 active tree 단계가 evidence collection의 앞단으로 배치된다.
  - Fail 징후: evidence collection이 coarse survey/active tree와 무관하게 독립 시작 단계로 서술된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:36-38`, `SKILL.md:16-18`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] dependency evidence, class structure evidence, runtime overlay가 누적되어 graph evidence layer를 이루고, 그 graph evidence가 graph core/sidecar split 또는 optional slice stage의 상위 입력으로 이어진다고 유지된다
  - Pass 기준: 세 evidence layer가 graph evidence로 모이고 이후 graph core/sidecar 또는 slice-stage 입력으로 이어진다.
  - Fail 징후: evidence layer가 graph evidence로 수렴하지 않거나 slice-stage와 끊긴다.
  - Doc evidence: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:17-24,37-38`
  - Expected input family:
  - Expected output family:
  - Pass/Fail:
  - Notes:
- [ ] slice stage를 쓰는 경우 `inventory_snapshot.json`과 `slice_seed_candidates.json`이 static dependency overlay와 refinement의 중간 입력/출력 artifact로 유지된다
  - Pass 기준: inventory snapshot과 slice seed candidates가 overlay/refinement 이전의 중간 artifact로 유지된다.
  - Fail 징후: inventory나 seed artifact 없이 곧바로 refinement 또는 final slice로 건너뛴다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:80-91,163-165`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] `static_dependency_overlay.json`이 refinement 단계의 직접 입력으로 이어지고, refinement 결과가 runtime overlay와 stop rules 판단의 입력으로 이어진다고 유지된다
  - Pass 기준: static dependency overlay 다음에 refinement가 오고, refinement 뒤에 runtime overlay와 stop rules가 온다.
  - Fail 징후: static dependency overlay가 refinement와 분리되거나 runtime overlay/stop rules가 refinement 앞에 온다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:93-150`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] `runtime_overlay.json`과 `unobserved_path_register.json`은 final slice proposal 이전의 transition artifact로 남는다
  - Pass 기준: runtime overlay artifacts가 final slice proposal 전에 생성되는 transition artifact로 위치한다.
  - Fail 징후: runtime overlay artifacts가 final slice proposal 이후 산출물로 밀리거나 빠진다.
  - Doc evidence: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md:140-156,167-172`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
- [ ] graph core/sidecar split 이후 canonical graph artifact가 export/view layer의 직접 입력으로 이어진다
  - Pass 기준: graph artifact가 canonical neutral form으로 남고 export/view layer가 그 뒤 단계로 배치된다.
  - Fail 징후: export/view layer가 canonical graph artifact와 분리된 별도 source처럼 서술된다.
  - Doc evidence: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md:40`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md:25,71-77`
  - Expected input:
  - Expected output:
  - Pass/Fail:
  - Notes:
