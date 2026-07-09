---
name: codex-subagent-setup-3layer-production-kb
kb_profile: canonical_design_kb
role: codex-subagent-setup production governance
ver: 1
created_at: 2026-03-20-17-21
updated_at: 2026-03-20-17-21
---

# codex-subagent-setup 3-Layer Production KB

## Purpose

Define a reusable 3-layer production model for `codex-subagent-setup` work so that scope splitting, consistency evaluation, implementation follow-up, and usability review do not drift into one mixed pass.

## Canonical 3-Layer Model

### Layer 1. Procedure Layer

Purpose:
- control the large procedural steps
- define artifact gates and backtrack rules
- keep the orchestration condition-based rather than time-based

Primary objects:
- `Agent Flow`
- top-level phase checklist
- artifact gate definitions
- smoke checkpoints

Representative questions:
- is the next step allowed yet?
- which artifact must exist before the next agent runs?
- when must execution return to a previous step?

### Layer 2. Agent Or Execution Layer

Purpose:
- validate each agent package or wrapper as an operational unit
- keep agent role, task boundaries, and runtime discipline explicit

Primary objects:
- `AGENT.md`
- `package_details`
- handoff bridges
- wrapper rules
- lint/static guard procedures

Representative questions:
- does each agent package declare role, read order, input/output contract, handoff method, and context injection strategy?
- is the agent class declared and respected?
- does subagent execution enforce the intended runtime discipline?

### Layer 3. Skill Usability Layer

Purpose:
- evaluate whether the `SKILL.md` entrypoint is actually usable by an operator or lead agent
- prevent overgrown or ambiguous skill entrypoints

Primary objects:
- `SKILL.md`
- read order quality
- linker vs bridge clarity
- context load discipline
- production process references

Representative questions:
- can a reader determine the next action from `SKILL.md` alone?
- are the referenced documents minimal and sequenced correctly?
- does the skill separate overview, contract, and detail cleanly?
- does the skill reuse existing meta-skills instead of re-explaining everything inline?

## Scope Split Rules

### Procedure-layer scope

Include:
- top-level flow
- artifact gate definitions
- backtrack rules
- phase-level smoke gates

Exclude:
- detailed per-agent IO field descriptions
- wrapper implementation details
- large usability commentary blocks

### Agent or execution-layer scope

Include:
- per-agent class
- per-agent role and whitelist
- package details fields
- lint/static handling trigger points
- wrapper on/off discipline

Exclude:
- full skill usability review
- broad orchestration narrative already covered by procedure layer

### Skill usability-layer scope

Include:
- entrypoint clarity
- read order quality
- detail split quality
- linker/bridge fit
- progressive context usability

Exclude:
- low-level wrapper implementation
- per-agent graph or risk findings

## Canonical Build Order

1. Build or update the KB first.
2. Build consistency evaluation checklists from the KB.
3. Run consistency review before implementation planning.
4. Only then create implementation checklists, wrappers, or code changes.

## Production Order For This Skill

1. lock the 3-layer KB
2. create procedure-layer consistency checks
3. create agent/execution-layer consistency checks
4. create skill-usability consistency checks
5. review failures and only then open implementation work

## Linter / Static Handling Principle

For this skill family, lint/static handling belongs to the production process itself, not only to later implementation notes.

Required interpretation:
- script or wrapper production must define runtime gate first
- lint/static handling must be documented as an operational rule
- warning-based enforcement is allowed as a runtime discipline mechanism for subagents
- runtime-only toggle is preferred; lead-agent on/off is fallback

## Canonical Design Takeaways

- consistency evaluation should happen before implementation planning
- scope split should follow the 3-layer model, not file type alone
- agent package quality and skill usability must be reviewed separately
- long details belong in linked documents, not in `SKILL.md` entrypoints
