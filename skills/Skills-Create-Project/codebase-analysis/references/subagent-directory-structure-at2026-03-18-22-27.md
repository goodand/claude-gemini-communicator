# Subagent Directory Structure

- recorded_at: `2026-03-18-22-27`
- source_scope: `local_codebase_only`
- reference_pattern: `claude-gemini-communicator/skills/super-skill-creator/agents/*.md`

## Why this structure

Claude-side reference already uses a simple file-backed agent guide layout:

- `agents/analyzer.md`
- `agents/grader.md`
- `agents/comparator.md`

This skill mirrors that pattern for Codex subagents.

## Recommended structure

```text
codebase-analysis/
├── SKILL.md
├── agents/
│   ├── reviewer.md
│   ├── context-broker.md
│   ├── dependency-graph-analyst.md
│   ├── dependency-risk-auditor.md
│   └── dependency-slice-planner.md
├── references/
├── knowledge_bases/
├── checklist-forconsistency-evaluation/
├── checklist-forimplementation/
└── evals/
```

## Naming rule

- filename = stable role name
- file body = short operational guide
- runtime nickname is optional and should not replace the file-backed role name
