# Consistency Checklist — codex-subagent-setup

- [ ] `agents/` directory exists
- [ ] each agent file defines goal, rules, and output shape
- [ ] SKILL.md distinguishes role / nickname / agent_type
- [ ] SKILL.md treats `context-broker` as the preferred owner of full context
- [ ] dependency worker roles are documented as subagents, not top-level skills
- [ ] references include local MCP setup facts
- [ ] references include troubleshooting.md
- [ ] knowledge base declares `internal_codebase_only`
