# Setup Context

- recorded_at: `2026-03-18-22-47`
- purpose: `상위 agent가 codebase-analysis skill을 시작할 때 먼저 읽는 context file`

## Load this first

- [SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/SKILL.md)
- [canonical base KB](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/codebase-analysis-knowledge_base-at2026-03-22-01-34.md)
- [graph representation KB](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md)
- [canonical graph artifact contract](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/canonical-graph-artifact-contract-at2026-03-20-21-04.md)
- [normalized graph schema sample](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/normalized-graph-json-sample-schema-at2026-03-20-21-51.md)
- supporting appendix가 필요하면 gate-sequence seed와 handoff seed를 뒤에서 본다.

## Then choose the next analysis entry

- quick coarse survey: `scripts/analyze_codebase.py <repo_root>`
- current evidence docs under `knowledge_bases/codebase-analysis/`
- graph/export follow-up: `references/skill-usage-details-at2026-03-21-23-25.md`

## Rule

상위 agent는 모든 analysis reference를 한 번에 preload하지 않는다. 현재 목적에 맞는 evidence/graph 문서만 다음 단계에서 주입한다.
