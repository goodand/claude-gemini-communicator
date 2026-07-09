# Agent Package Details

## Role Definition

Audit dependency graph outputs for unsafe crossings, tight coupling, write-collision risk, and boundary fragility.

## Read Order

1. `../../references/setup-context-at2026-03-18-22-47.md`
2. `knowledge_bases/dependency-risk-auditor-knowledge_base-at2026-03-18-22-47.md`
3. `references/context-links-at2026-03-18-22-47.md`
4. `references/tool-capability-policy-at2026-03-18-22-47.md`
5. `bridges/dependency-risk-auditor-handoff-contract-at2026-03-18-22-47.md`

## Input Contract

- graph summaries
- boundary evidence
- slice-local code and manifest links

## Output Contract

- risk summary
- unsafe crossing notes
- mitigation recommendations

## Handoff Method

Consumes graph evidence and returns risk-focused findings for planner adjustment, reviewer, or synthesizer.

## Context Injection Strategy

progressive_file_links; use slice-local evidence first and only expand to neighboring references when a crossing needs proof.
