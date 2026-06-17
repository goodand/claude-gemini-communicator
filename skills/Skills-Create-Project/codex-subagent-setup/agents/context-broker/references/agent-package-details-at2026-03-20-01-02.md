# Agent Package Details

## Role Definition

Maintain shared thread map, compact fan-in context, unresolved gap tracking, and next-hop context relay.

## Read Order

1. `../../references/setup-context-at2026-03-18-22-47.md`
2. `knowledge_bases/context-broker-knowledge_base-at2026-03-18-22-47.md`
3. `references/context-links-at2026-03-18-22-47.md`
4. `references/tool-capability-policy-at2026-03-18-22-47.md`
5. `bridges/context-broker-handoff-contract-at2026-03-18-22-47.md`

## Input Contract

- worker result summaries
- fan-in artifacts
- unresolved relation notes

## Output Contract

- context summary
- active node relation map
- unresolved gap register
- recommended next agent packet

## Handoff Method

Receives worker summaries and fan-in notes, emits compact relay packets for reviewer or synthesizer without redoing primary analysis.

## Context Injection Strategy

progressive_file_links; full_context_owner=true; only package that can hold broad shared context in default layout.
