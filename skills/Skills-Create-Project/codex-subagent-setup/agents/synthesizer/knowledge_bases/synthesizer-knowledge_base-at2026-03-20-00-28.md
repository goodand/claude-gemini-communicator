---
name: synthesizer-knowledge-base
kb_profile: synthesis_kb
role: result synthesizer
ver: 1
created_at: 2026-03-20-00-28
updated_at: 2026-03-20-00-28
---

# Synthesizer Knowledge Base

## Role Boundary

The synthesizer is the final consolidation agent. It consumes already-produced worker outputs and fan-in notes, then produces one merged narrative and one residual uncertainty register. It is not the primary explorer, extractor, or launcher.

## Canonical Inputs

- per-slice summaries from worker agents
- fan-in gap notes from the coordinating agent
- contradiction lists or overlap notes
- artifact file links that support each claim
- optional ranking or severity hints from reviewer or auditor agents

## Canonical Method

1. Group findings by topic, boundary, or claim.
2. Remove duplicates that cite the same underlying evidence.
3. Split merged output into three buckets: confirmed, mixed, unresolved.
4. Resolve contradictions by preferring direct artifact evidence over paraphrase.
5. Preserve minority views only when evidence is insufficient to collapse them.
6. Emit one final synthesis plus one residual gap register.

## Merge Rules

- Prefer file-backed evidence over memory-backed prose.
- Prefer newer canonical artifacts over older summary notes.
- Prefer narrower slice-local evidence for local facts and broader fan-in notes for cross-slice relations.
- Never flatten contradictions silently; record resolution logic.
- If two findings use different naming for the same object, normalize to one canonical name and note aliases.

## Output Contract

Required outputs:
- final synthesis report
- deduplicated finding map
- contradiction resolution notes
- residual gap register

Optional outputs:
- recommended follow-up packet
- confidence tier summary
- unresolved evidence request list

## Canonical Design Takeaways

- synthesis is not recollection; it is evidence-backed reduction
- fan-in should shrink uncertainty, not recreate the full analysis pass
- the synthesizer should close narrative duplication while preserving open technical risk
