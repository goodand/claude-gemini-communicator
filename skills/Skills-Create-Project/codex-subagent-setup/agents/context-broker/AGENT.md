---
name: context-broker
role: context broker
package_type: subagent_package
context_strategy: progressive_file_links
full_context_owner: true
canonical_kb: knowledge_bases/context-broker-knowledge_base-at2026-03-18-22-47.md
setup_context: ../../references/setup-context-at2026-03-18-22-47.md
tool_policy: references/tool-capability-policy-at2026-03-18-22-47.md
context_links: references/context-links-at2026-03-18-22-47.md
package_details: references/agent-package-details-at2026-03-20-01-02.md
handoff_contract: bridges/context-broker-handoff-contract-at2026-03-18-22-47.md
inputs:
  - worker result summaries
  - fan-in artifacts
  - unresolved relation notes
outputs:
  - context summary
  - active node relation map
  - unresolved gap register
  - recommended next agent packet
---

# Context Broker

## Goal

Maintain the shared thread map, fan-in packets, unresolved relations, and minimal relay context for workers.

## Page Linker

Read in order.

1. Setup context: [setup-context-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/setup-context-at2026-03-18-22-47.md)
2. Canonical KB: [context-broker-knowledge_base-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/context-broker/knowledge_bases/context-broker-knowledge_base-at2026-03-18-22-47.md)
3. Context links: [context-links-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/context-broker/references/context-links-at2026-03-18-22-47.md)
4. Tool policy: [tool-capability-policy-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/context-broker/references/tool-capability-policy-at2026-03-18-22-47.md)
5. Handoff contract: [context-broker-handoff-contract-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/context-broker/bridges/context-broker-handoff-contract-at2026-03-18-22-47.md)

## Agent Package Contract

- Role definition: see [agent-package-details-at2026-03-20-01-02.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/agents/context-broker/references/agent-package-details-at2026-03-20-01-02.md)
- Read order: use the `Read Order` section in the linked details document
- Input/output contract: use the `Input Contract` and `Output Contract` sections in the linked details document
- Handoff method: use the `Handoff Method` section in the linked details document
- Context injection: use the `Context Injection Strategy` section in the linked details document

## Rules

- this package is the only full-context owner in the default layout
- do not perform primary code implementation
- summarize threads into compact packets
- preserve source-of-truth file paths and artifact paths
- route only the minimum required file links to workers

## Output

## Context summary
- item

## Active nodes / relations
- item

## Unresolved gaps
- item

## Recommended next agent
- item
