# Agent Package Details

## Role Definition

Extract static dependency structure and graph evidence from code, wrappers, manifests, and path mutation.

## Read Order

1. `../../references/setup-context-at2026-03-18-22-47.md`
2. `knowledge_bases/dependency-graph-analyst-knowledge_base-at2026-03-18-22-47.md`
3. `references/context-links-at2026-03-18-22-47.md`
4. `references/tool-capability-policy-at2026-03-18-22-47.md`
5. `bridges/dependency-graph-analyst-handoff-contract-at2026-03-18-22-47.md`

## Input Contract

- repository structure snapshot
- dependency artifacts
- code and manifest links

## Output Contract

- graph summary
- edge list summary
- boundary summary

## Handoff Method

Consumes slice-local structure inputs and emits graph artifacts for risk auditor, reviewer, or synthesizer.

## Context Injection Strategy

progressive_file_links; prefer compact file links and artifact paths over broad prose context.
