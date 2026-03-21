# Handoff and Context Pattern

- recorded_at: `2026-03-18-22-27`
- source_scope: `local_codebase_only`

## Core rule

Do not give every worker full context by default.

## Recommended flow

1. main orchestrator launches worker subagents
2. worker results are normalized into a fan-in packet
3. a context broker maintains the shared relation map
4. only unresolved gaps trigger deeper follow-up
5. `fork_context=true` is concentrated in the broker when possible

## Role separation

- `role`: actual responsibility
- `nickname`: runtime alias only
- `agent_type`: execution type (`default`, `explorer`, `worker`)

## Dependency-oriented recommendation

- `depsolve-analyzer` remains the main dependency skill
- `dependency-graph-analyst`, `dependency-risk-auditor`, and `dependency-slice-planner` are worker-level roles
- `context-broker` is the only role that should own full-thread relay by default
