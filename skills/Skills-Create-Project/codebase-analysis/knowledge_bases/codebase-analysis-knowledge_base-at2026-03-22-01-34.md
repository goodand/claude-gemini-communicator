---
name: codebase-analysis-knowledge-base
kb_profile: canonical_design_kb
role: codebase analysis canonical base design
ver: 1
created_at: 2026-03-22-01-34
updated_at: 2026-03-22-01-34
reference_acquisition_mode: local_skill_corpus_and_local_repo_only
source_scope: Skills-Create-Project/codebase-analysis + adjacent analysis skills
purpose: codebase-analysis를 graph evidence 중심의 analysis skill로 운영하기 위한 canonical KB
---

# codebase-analysis Knowledge Base

## Canonical design takeaways

1. `graph evidence`가 이 skill의 핵심 키워드다.
2. dependency evidence, class structure evidence, runtime overlay는 graph evidence의 하위 evidence layer다.
3. `slice`는 `dependency-slice-planner`가 담당하고, `codebase-analysis`는 slice stage의 입력과 결과를 소비한다.
4. `handoff`와 `fan-in`은 `codex-subagent-setup`에서 가져온 orchestration 개념으로 두고, 이 skill의 본체는 analysis 본체에 둔다.
5. graph core에는 연결성이 높은 구조 증거를 두고, 저연결 risk note, ownership 예외, weak signal은 sidecar evidence file로 분리한다.
6. canonical graph artifact는 `normalized_graph.json + nodes.jsonl + edges.jsonl`이며 Graphviz, Neo4j, Cytoscape, Gephi는 export/view layer다.
7. 정합성 평가용 checklist는 skill 의도와 canonical KB의 교집합만 평가해야 한다.
8. slice stage는 `inventory -> coarse slice seed -> static dependency overlay -> refinement -> runtime overlay -> stop rules -> final slice proposal` 순서를 따른다.

## KB branches under Skills-Create-Project

- canonical base KB: `knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md`
- graph representation branch: `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
- slice-stage appendix seed: `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`
- slice-stage handoff seed: `references/dependency-slice-planner-handoff-contract-seed-at2026-03-22-00-54.md`
- accumulated analysis evidence: `knowledge_bases/codebase-analysis/`

## Gate sequence relation

1. coarse survey와 active tree 파악으로 분석 범위를 좁힌다.
2. dependency evidence, class structure evidence, runtime overlay를 graph evidence로 모은다.
3. slice stage가 필요한 경우 `dependency-slice-planner` 계열 규칙으로 inventory, coarse seed, static overlay, refinement, runtime overlay를 순차 적용한다.
4. slice stage 결과는 `slice_manifest.json`, `parallel_slices.json`, `analysis_only_slices.json` 또는 `write_safe_slices.json`, `do_not_split_regions.json`으로 정리한다.
5. graph artifact는 canonical neutral form으로 남기고 export/view layer는 후행 단계로 둔다.

## Local references used

- `knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md`
- `knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md`
- `references/dependency-slice-planner-handoff-contract-seed-at2026-03-22-00-54.md`
- `skills/dependency-slice-planner/SKILL.md`
- `skills/codebase-architecture-mapper/SKILL.md`
- `skills/depsolve-analyzer/SKILL.md`
- `skills/class-hierarchy-classifier`
- `skills/runtime-flow-tracer-web-preview`

## Not part of this skill

- final fan-out launch ownership
- tmux or worktree runtime ownership
- subagent lifecycle orchestration
- parser or adapter adoption boundary decision
- graph 외 저연결 정보의 long-form orchestration note

## Why this is a skill

This skill standardizes graph evidence collection, normalization, and evidence branching so codebase analysis does not collapse into one tool, one graph view, or one orchestration layer too early.
