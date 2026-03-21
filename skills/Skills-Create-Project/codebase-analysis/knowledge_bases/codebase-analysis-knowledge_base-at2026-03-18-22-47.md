---
name: codebase-analysis-knowledge-base
kb_profile: canonical_design_kb
role: codebase analysis baseline design
ver: 1
created_at: 2026-03-18-22-47
updated_at: 2026-03-20-21-51
reference_acquisition_mode: internal_codebase_only
source_scope: local_workspace_and_local_repo_only
purpose: codebase-analysis를 directory-per-agent package로 운영하기 위한 local KB
---

# codebase-analysis Knowledge Base

## Role Boundary

This KB is the baseline canonical design source for `codebase-analysis` itself: package layout, role separation, progressive context rules, and built-in subagent composition.

It is not the graph-representation-specific KB. Graph storage/query/view strategy belongs to [codebase-graph-representation-kb-at2026-03-20-21-04.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/knowledge_bases/codebase-graph-representation-kb-at2026-03-20-21-04.md).

## Canonical design takeaways

1. runtime-created subagent and file-backed agent package are different layers
2. each role should have its own package directory, not a flat markdown file
3. tool capability policy, context links, and handoff contract must be separated
4. top-level setup context and per-agent context should not be mixed
5. progressive context injection should pass links, not full raw context, to workers
6. `depsolve-analyzer` remains the main dependency skill; dependency subagents stay below it

## Local references used

- `skills/super-skill-creator/agents/analyzer.md`
- `skills/super-skill-creator/agents/grader.md`
- `skills/super-skill-creator/agents/comparator.md`
- `skills/depsolve-analyzer/SKILL.md`
- `skills/depsolve-analyzer/references/MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md`
- local Codex MCP setup state for `codex-subagent`

## Recommended built-in roles

- reviewer
- context-broker
- dependency-graph-analyst
- dependency-risk-auditor
- dependency-slice-planner
