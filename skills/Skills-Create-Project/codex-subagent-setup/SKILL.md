---
name: codex-subagent-setup
description: >-
  worktree-parallel family의 subagent-setup specialist. Use this skill when
  reusable Codex subagent packages, setup context, agent flow, class policy,
  and handoff structure must be prepared for later orchestration or parallel
  execution. broader multi-agent orchestration은 worktree-parallel을 사용하라.
---

# codex-subagent-setup

Codex subagent package 구조와 setup/orchestration 문서를 정리하는 skill.

## When to use

- subagent package를 새로 만들거나 기존 package를 재정리할 때
- setup context, agent flow, class policy, handoff 구조를 분리하고 싶을 때
- reusable orchestration layer를 codebase analysis와 분리하고 싶을 때
- 각 agent의 `AGENT.md`, `context-links`, `tool policy`, `bridges`를 정합하게 유지하고 싶을 때

## Read order

1. `references/setup-context-at2026-03-18-22-47.md`
2. `knowledge_bases/codex-subagent-setup-knowledge_base-at2026-03-18-22-47.md`
3. `knowledge_bases/codex-subagent-setup-3layer-production-kb-at2026-03-20-17-21.md`
4. `references/agent-package-layout-at2026-03-18-22-47.md`
5. `references/progressive-context-routing-at2026-03-18-22-47.md`
6. `references/agent-flow-at2026-03-20-01-14.md`
7. `references/agent-class-policy-at2026-03-20-01-14.md`
8. `references/skill-usage-details-at2026-03-21-23-25.md`
9. agent 선택 후 `agents/<role>/AGENT.md`
10. 같은 agent의 `references/context-links-*.md`, `references/tool-capability-policy-*.md`, `bridges/<role>-handoff-contract-*.md`

## Notes

- entrypoint는 얇게 유지하고, package 목록/예외/운영 노트는 `references/skill-usage-details-at2026-03-21-23-25.md`로 내린다.
- analysis 전용 graph/export/schema 문서는 `codebase-analysis`에 두고, 이 skill은 setup/orchestration layer만 다룬다.
- 해결된 실패 패턴과 운영 예외는 `references/troubleshooting.md`에 누적한다.
