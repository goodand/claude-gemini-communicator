# Consistency Checklist — codex-subagent-setup

- [ ] every built-in role uses `agents/<role>/AGENT.md`
- [ ] every built-in role has `knowledge_bases/`, `scripts/`, `references/`, and `bridges/`
- [ ] every built-in role has a `tool-capability-policy` file
- [ ] every built-in role has a `context-links` file
- [ ] every built-in role has a handoff contract under `bridges/`
- [ ] top-level setup context is separate from per-agent context
- [ ] SKILL.md points to the directory-per-agent structure
- [ ] `context-broker` is documented as the preferred full-context owner
