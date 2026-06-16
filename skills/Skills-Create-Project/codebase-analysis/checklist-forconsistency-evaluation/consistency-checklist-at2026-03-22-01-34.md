# Consistency Checklist — codebase-analysis

> 목적: `codebase-analysis`가 graph evidence 중심 analysis skill로 유지되고, processed KB 기준으로 slice stage와 graph representation 관계가 일관되게 닫히는지 점검한다.
> source of truth: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`, `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`

## A. Identity

- [ ] 이 skill의 핵심 목적이 `graph evidence` 수집과 정리로 고정돼 있다
- [ ] dependency evidence, class structure evidence, runtime overlay가 graph evidence의 하위 layer로 고정돼 있다
- [ ] 이 skill이 orchestration/setup skill로 다시 퍼지지 않고 analysis 본체로 유지된다

## B. Boundary

- [ ] `slice`는 `dependency-slice-planner`가 담당하고, 이 skill은 slice stage 입력과 결과를 소비하는 것으로 경계가 고정돼 있다
- [ ] `handoff`와 `fan-in`은 `codex-subagent-setup` 소관으로 분리돼 있다
- [ ] direct code edits와 destructive action은 기본 비목표로 분리돼 있다
- [ ] graph와 연결성이 낮은 risk note, ownership 예외, weak signal은 sidecar evidence file로 분리한다고 명시돼 있다

## C. Source Of Truth Order

- [ ] source of truth 순서가 `canonical base KB -> graph representation KB -> consistency checklist -> implementation checklist -> scripts`로 고정돼 있다
- [ ] `gate-sequence seed`는 `hybrid_kb` appendix, `handoff seed`는 supporting reference이며 primary source of truth가 아님이 유지된다
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
- [ ] graph evidence가 비면 추측 대신 probe 또는 follow-up artifact로 되돌린다는 방향이 유지된다

## G. Output Contract

- [ ] canonical graph artifact contract가 유지된다
- [ ] slice stage를 쓴 경우 `slice_manifest.json`, `parallel_slices.json`, `analysis_only_slices.json` 또는 `write_safe_slices.json`, `do_not_split_regions.json`이 output family로 닫혀 있다
- [ ] export/view layer는 canonical artifact 이후 후행 단계로 유지된다
