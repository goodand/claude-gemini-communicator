# Consistency Checklist

## Metadata
- scope: `codex-subagent-setup`
- basis_kb: `knowledge_bases/codex-subagent-setup-3layer-production-kb-at2026-03-20-17-21.md`
- checklist_type: `consistency_evaluation`
- created_at: `2026-03-20-17-21`

## Layer 1. Procedure Consistency

- [ ] `Agent Flow` exists as a dedicated procedural artifact
- [ ] the flow is condition-based, not time-based
- [ ] every major agent step has an explicit entry condition
- [ ] every major agent step has an explicit output gate
- [ ] backtrack rules are documented
- [ ] fan-in is distinguished from final synthesis
- [ ] smoke checkpoints are defined at the phase or gate level
- [ ] procedure-layer documents do not absorb per-agent low-level details

## Layer 2. Agent / Execution Consistency

- [ ] every agent package has `AGENT.md`
- [ ] every agent package declares a `package_details` link
- [ ] every agent package explicitly states role definition
- [ ] every agent package explicitly states read order
- [ ] every agent package explicitly states input contract
- [ ] every agent package explicitly states output contract
- [ ] every agent package explicitly states handoff method
- [ ] every agent package explicitly states context injection strategy
- [ ] every agent package is assigned an agent class or is covered by a class policy
- [ ] persistent structural agents are kept narrow and task-whitelisted
- [ ] run-scoped interpretive agents are documented as write-artifact-then-terminate
- [ ] the synthesizer is documented as artifact-backed rather than full-context structural
- [ ] lint/static handling is defined as an execution-discipline rule, not only an implementation afterthought
- [ ] subagent lint/static enforcement has a preferred on/off strategy and a fallback strategy
- [ ] execution-layer docs do not silently replace procedure-layer flow docs

## Layer 3. Skill Usability Consistency

- [ ] `SKILL.md` states when to use the skill clearly
- [ ] `SKILL.md` read order is short, actionable, and sequenced
- [ ] `SKILL.md` points to `Agent Flow` and `Agent Class Policy`
- [ ] `SKILL.md` does not overload the entrypoint with long operational detail
- [ ] long operational detail is pushed into linked references or package details
- [ ] linker usage is distinct from bridge usage
- [ ] progressive context strategy is understandable from the skill entrypoint
- [ ] built-in agent package list is current
- [ ] the skill explicitly reflects the canonical production order: KB first, consistency first, implementation later
- [ ] the skill reuses existing meta-skill guidance instead of duplicating it inline

## Cross-Layer Integrity

- [ ] the 3-layer model is reflected consistently across KB, checklist, and `SKILL.md`
- [ ] no layer is missing from the current document set
- [ ] no document mixes all three layers without a clear boundary
- [ ] procedure failures can be mapped to a specific implementation follow-up later
- [ ] usability failures can be evaluated without rereading every agent package in full

## Review Outcome

- [ ] pass
- [ ] pass with follow-ups
- [ ] fail and return to KB or skill restructuring

## Failure Notes
- item
