# Consistency Checklist — codebase-analysis

> 목적: `codebase-analysis`가 graph evidence 중심 analysis skill로 유지되고, canonical base KB, graph representation KB, supporting hybrid appendix 기준으로 관계가 일관되게 닫히는지 점검한다.
> source of truth: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
> supporting appendix: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `graph evidence` 수집과 정리로 고정돼 있다
- [ ] dependency evidence, class structure evidence, runtime overlay가 graph evidence의 하위 layer로 고정돼 있다
- [ ] 이 skill이 orchestration/setup skill로 다시 퍼지지 않고 analysis 본체로 유지된다

## B. Boundary

- [ ] `slice`는 `dependency-slice-planner`가 담당하고, 이 skill은 slice stage 입력과 결과를 소비하는 것으로 경계가 고정돼 있다
- [ ] `handoff`와 `fan-in`은 `codex-subagent-setup` 소관으로 분리돼 있다
- [ ] graph와 연결성이 낮은 risk note, ownership 예외, weak signal은 sidecar evidence file로 분리한다고 명시돼 있다

## C. Source Of Truth Boundaries

- [ ] canonical base KB와 graph representation KB가 primary source of truth로 유지된다
- [ ] `gate-sequence seed`는 `hybrid_kb` appendix로 남고 primary source of truth를 대체하지 않는다
- [ ] `knowledge_bases/codebase-analysis/` 아래 evidence docs는 accumulated evidence이고 canonical KB가 아님이 유지된다

## D. Evidence Layers

- [ ] graph core가 analysis 본체로 고정돼 있다
- [ ] dependency evidence, class structure evidence, runtime overlay가 evidence layer로 분리돼 있다
- [ ] canonical graph artifact가 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
- [ ] Graphviz, Neo4j, Cytoscape, Gephi가 export/view layer로만 취급된다

## E. Slice Stage Relation

- [ ] slice stage가 `inventory -> coarse slice seed -> static dependency overlay -> refinement -> runtime overlay -> stop rules -> final slice proposal` 순서를 따른다고 닫혀 있다
- [ ] `tree`만으로 시작할 수는 있어도 `static dependency overlay` 없이 final slice를 확정하지 않는다고 유지된다
- [ ] refinement가 `merge`와 `re-cut`을 모두 허용한다고 유지된다

## F. Graph Core Vs Sidecar

- [ ] 연결성이 높은 구조 증거만 graph core에 남긴다고 유지된다
- [ ] 저연결 risk note, ownership 예외, weak signal은 sidecar evidence file로 분리한다고 유지된다
- [ ] slice stage가 필요한 경우 누락 관계를 appendix gate로 되돌리는 방향이 유지된다

## G. Output Contract

- [ ] canonical source-of-truth output family는 `normalized_graph.json + nodes.jsonl + edges.jsonl`로 고정돼 있다
- [ ] slice stage를 쓴 경우 `slice_manifest.json`, `parallel_slices.json`, `analysis_only_slices.json` 또는 `write_safe_slices.json`, `do_not_split_regions.json`이 output family로 닫혀 있다
- [ ] export/view output family는 후행 산출물이며 canonical artifact를 대체하지 않는다

## H. Input And Output Families

- [ ] 최종 analysis input family가 `top-level structure/active tree + dependency evidence + class structure evidence + runtime overlay`로 닫혀 있다
- [ ] slice stage input family는 baseline input이 아니라 appendix input으로 분리돼 있다
- [ ] 최종 output family가 `graph core + sidecar evidence + optional slice-stage outputs + export/view outputs`로 구분돼 있다

## I. Layer Sequence

- [ ] 큰 순서가 `coarse survey -> graph evidence layers -> optional slice stage -> graph core/sidecar split -> export/view layer`로 닫혀 있다
- [ ] dependency evidence, class structure evidence, runtime overlay가 evidence layer로 묶여 있다
- [ ] graph core와 sidecar evidence가 혼합되지 않고 역할이 분리돼 있다
- [ ] export/view layer가 graph core나 sidecar evidence보다 먼저 source of truth처럼 읽히지 않는다
