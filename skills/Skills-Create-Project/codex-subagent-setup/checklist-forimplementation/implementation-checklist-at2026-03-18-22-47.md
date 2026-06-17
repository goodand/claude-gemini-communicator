# Implementation Checklist — codex-subagent-setup

1. Move flat `agents/*.md` into `agents/<role>/AGENT.md`
2. Add `knowledge_bases/`, `scripts/`, `references/`, and `bridges/` under every role package
3. Split role, tool policy, context links, and handoff contract into separate files
4. Add a top-level setup context file for the parent agent
5. Keep actual script automation out of scope until runtime friction proves it is needed
