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
codex-subagent-setup/
├── SKILL.md
├── agents/
│   ├── <role>/
│   │   ├── AGENT.md
│   │   ├── knowledge_bases/
│   │   ├── references/
│   │   ├── bridges/
│   │   └── scripts/
├── references/
├── knowledge_bases/
├── checklist-forconsistency-evaluation/
├── checklist-forimplementation/
└── evals/
```

## Naming rule

- directory name = stable role name
- `AGENT.md` = canonical role guide
- runtime nickname is optional and should not replace the file-backed role name
