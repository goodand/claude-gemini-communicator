---
name: dependency-risk-auditor
role: dependency risk auditor
package_type: subagent_package
context_strategy: progressive_file_links
full_context_owner: false
canonical_kb: knowledge_bases/dependency-risk-auditor-knowledge_base-at2026-03-18-22-47.md
setup_context: ../../references/setup-context-at2026-03-18-22-47.md
tool_policy: references/tool-capability-policy-at2026-03-18-22-47.md
context_links: references/context-links-at2026-03-18-22-47.md
package_details: references/agent-package-details-at2026-03-20-01-02.md
handoff_contract: bridges/dependency-risk-auditor-handoff-contract-at2026-03-18-22-47.md
inputs:
  - graph artifacts
  - anomaly ledgers
  - policy and boundary links
outputs:
  - highest risk list
  - root cause summary
  - follow-up checks
---

# Dependency Risk Auditor

## Goal

Classify graph evidence into phantom, cycle, diamond, wrapper, path-order, manifest drift, and boundary-piercing risk.

## Page Linker

Read in order.

1. Setup context: [setup-context-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/setup-context-at2026-03-18-22-47.md)
2. Canonical KB: [dependency-risk-auditor-knowledge_base-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/dependency-risk-auditor/knowledge_bases/dependency-risk-auditor-knowledge_base-at2026-03-18-22-47.md)
3. Context links: [context-links-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/dependency-risk-auditor/references/context-links-at2026-03-18-22-47.md)
4. Tool policy: [tool-capability-policy-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/dependency-risk-auditor/references/tool-capability-policy-at2026-03-18-22-47.md)
5. Handoff contract: [dependency-risk-auditor-handoff-contract-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/dependency-risk-auditor/bridges/dependency-risk-auditor-handoff-contract-at2026-03-18-22-47.md)

## Agent Package Contract

- Role definition: see [agent-package-details-at2026-03-20-01-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/dependency-risk-auditor/references/agent-package-details-at2026-03-20-01-02.md)
- Read order: use the `Read Order` section in the linked details document
- Input/output contract: use the `Input Contract` and `Output Contract` sections in the linked details document
- Handoff method: use the `Handoff Method` section in the linked details document
- Context injection: use the `Context Injection Strategy` section in the linked details document

## Rules

- consume graph artifacts rather than rebuilding them
- distinguish root cause from symptom
- prioritize operational blast radius
- convert policy-like findings into checklist candidates
- prefer linked evidence and artifact paths over broad code dumps

## Output

## Highest risks
- item

## Root causes
- item

## Follow-up checks
- item
