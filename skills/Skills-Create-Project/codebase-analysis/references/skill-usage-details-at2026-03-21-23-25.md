# Skill Usage Details

- recorded_at: `2026-03-21-23-25`
- purpose: `entrypoint를 얇게 유지하고, analysis 상세 사용 지침과 보조 링크를 분리하기 위한 detail page`

## Details

- canonical base KB: [codebase-analysis-knowledge_base-at2026-03-22-01-34.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md)
- final consistency checklist: [kb-grounding-checklist-at2026-03-23-02-17.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/kb-grounding-checklist-at2026-03-23-02-17.md) — canonical core grounding only
- canonical graph artifact contract: [canonical-graph-artifact-contract-at2026-03-20-21-04.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/canonical-graph-artifact-contract-at2026-03-20-21-04.md)
- normalized graph schema sample: [normalized-graph-json-sample-schema-at2026-03-20-21-51.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md)
- gate-sequence seed appendix: [codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/codebase-analysis-gate-sequence-kb-seed-from-dependency-slice-planner-at2026-03-22-00-54.md)
- doc-code consistency checklist seed: [doc-code-consistency-checklist-at2026-03-23-02-44.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forconsistency-evaluation/doc-code-consistency-checklist-at2026-03-23-02-44.md)
- spec bundle: [codebase-analysis-spec-at2026-03-23-03-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-spec-at2026-03-23-03-14.md)
- implementation support appendix: [codebase-analysis-development-playbook-at2026-03-23-03-36.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-development-playbook-at2026-03-23-03-36.md)
- orchestration bridge: [codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md)
- orchestration consumer spec: [codebase-analysis-orchestration-consumer-spec-at2026-03-23-13-08.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-orchestration-consumer-spec-at2026-03-23-13-08.md)
- slice-stage handoff seed: [dependency-slice-planner-handoff-contract-seed-at2026-03-22-00-54.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/dependency-slice-planner-handoff-contract-seed-at2026-03-22-00-54.md)
- export implementation checklist: [export-checklist-at2026-03-20-21-51.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/checklist-forimplementation/export-checklist-at2026-03-20-21-51.md)
- graph sample fixture: [README.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/fixtures/graph-sample-at2026-03-20-22-45/README.md)
- decision queue rule: [decision-queue-rule-at2026-03-21-19-20.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/decision-queue/decision-queue-rule-at2026-03-21-19-20.md)
- decision template: [decision-template-at2026-03-21-19-20.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/decision-queue/decision-template-at2026-03-21-19-20.md)

## Execution entrypoints

- quick coarse survey: `scripts/analyze_codebase.py <repo_root>`
- graph/export follow-up: `checklist-forimplementation/export-checklist-at2026-03-20-21-51.md`
- smoke/reference layer example: `references/smoke/SMOKE_export_canonical_graph_2026-03-21-12-49.md`

## Notes

- 현재 skill의 중심은 `graph evidence`이며, dependency evidence, class structure evidence, runtime overlay가 그 하위 evidence layer다.
- subagent setup/orchestration은 [codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/codebase-analysis-orchestration-bridge-at2026-03-23-12-31.md)를 기준으로 읽고, `codex-subagent-setup`, `codex-worktree-dispatch`, `codex-tmux-orchestrator`가 인접 orchestration 계층을 담당한다. `slice`는 `dependency-slice-planner`가 담당한다.
- handoff와 fan-in은 orchestration에서 가져온 연결 개념으로 두고, 이 skill의 본체는 graph evidence 수집과 정리에 둔다.
- risk 판단은 graph evidence 위에서 읽되, graph와 연결성이 낮은 note·ownership 예외·weak signal은 sidecar evidence file로 분리한다.
- 그래프 표현 전략은 canonical graph artifact(`normalized_graph.json + nodes.jsonl + edges.jsonl`)를 source of truth로 두고, Graphviz/Neo4j/Cytoscape/Gephi는 export 또는 view layer로 취급한다.
- 정합성 평가용 checklist는 skill 의도와 canonical KB의 교집합만 평가해야 하므로, orchestration 세부나 adapter 채택 규칙을 과하게 끌어오지 않는다.
- 결정이 필요한 사항은 `knowledge_bases/decision-queue/`에 기록만 하고 premature promotion은 피한다.
- 상세 예외와 실패 패턴은 `(→ references/troubleshooting.md)`에 기록한다.
