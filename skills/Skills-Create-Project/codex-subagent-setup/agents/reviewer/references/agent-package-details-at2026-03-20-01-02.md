# Agent Package Details

## Role Definition

Review worker outputs for missing evidence, contradictions, regressions, and quality gaps before final synthesis.

## Read Order

1. `../../references/setup-context-at2026-03-18-22-47.md`
2. `knowledge_bases/reviewer-knowledge_base-at2026-03-18-22-47.md`
3. `references/context-links-at2026-03-18-22-47.md`
4. `references/tool-capability-policy-at2026-03-18-22-47.md`
5. `bridges/reviewer-handoff-contract-at2026-03-18-22-47.md`

## Input Contract

- worker result summaries
- fan-in notes
- artifact links requiring review

## Output Contract

- findings list
- open questions
- review summary

## Handoff Method

Consumes already-produced outputs, flags defects or weak claims, and passes review findings onward to broker or synthesizer.

## Context Injection Strategy

progressive_file_links; read only the evidence needed to support or reject each finding.
