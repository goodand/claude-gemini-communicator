# Agent Package Details

## Role Definition

Merge worker outputs into one deduplicated final narrative with contradiction handling and residual gap reporting.

## Read Order

1. `../../references/setup-context-at2026-03-18-22-47.md`
2. `knowledge_bases/synthesizer-knowledge_base-at2026-03-20-00-28.md`
3. `references/context-links-at2026-03-20-00-28.md`
4. `references/tool-capability-policy-at2026-03-20-00-28.md`
5. `bridges/synthesizer-handoff-contract-at2026-03-20-00-28.md`

## Input Contract

- per-slice result summaries
- fan-in gap notes
- contradiction register
- unresolved evidence links

## Output Contract

- final synthesis report
- deduplicated finding map
- contradiction resolution notes
- residual gap register

## Handoff Method

Consumes worker summaries and fan-in artifacts, produces final merged output without reopening the full repository pass.

## Context Injection Strategy

progressive_file_links; merge from artifacts, not memory, and keep unresolved gaps separate from confirmed findings.
