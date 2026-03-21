# codebase-analysis Knowledge Base

- created_at: `2026-03-18-22-27`
- reference_acquisition_mode: `internal_codebase_only`
- source_scope: `local_workspace_and_local_repo_only`
- purpose: `codebase-analysis를 file-backed role guide로 운영하기 위한 local KB`

## Canonical design takeaways

1. runtime-created subagents and file-backed subagent guides are different layers
2. role, nickname, and agent_type must stay separate
3. broad Codex subagent execution is practical, but role guides and task packets must constrain it
4. dependency analysis should keep `depsolve-analyzer` as the main skill; subagents stay as role workers
5. context fan-in should be centralized; do not spray full context to every worker

## Local references used

- `skills/super-skill-creator/agents/analyzer.md`
- `skills/super-skill-creator/agents/grader.md`
- `skills/super-skill-creator/agents/comparator.md`
- `skills/depsolve-analyzer/SKILL.md`
- `skills/depsolve-analyzer/references/MECE_SUBAGENT_FANIN_FOR_DEPGRAPH_2026-03-18-21-22.md`
- local Codex MCP setup state already configured for `codex-subagent`

## Recommended built-in roles

- reviewer
- context-broker
- dependency-graph-analyst
- dependency-risk-auditor
- dependency-slice-planner

## Not part of this skill

- direct code execution scripts
- worktree dispatch ownership
- tmux runtime ownership
- dependency graph implementation itself

## Why this is a skill

This skill standardizes the reusable subagent layer so runtime-created agents are not ad-hoc every time.
