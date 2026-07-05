 것# Table Branch Activation Slice Knowledge Base

## Why Bounded Activation Slices Exist

The presentation-image pipeline treats the table branch as conditional enrichment, not as a globally active default path.

That means a parser backend, a draft plan, or one isolated demo is not enough to treat the branch as runnable.
The branch becomes trustworthy only after one narrow artifact-backed slice proves that:

- candidate selection was explicit
- parser boot was real
- real-image parsing worked on bounded inputs
- raw parser output could be normalized into canonical `Table -> Row -> Cell`
- at least one downstream consumer could read the normalized artifact

The bounded slice exists to close that proof without widening immediately into batch rollout, worksheet export, or row-level RAG work.

## Repeated Pattern In This Repo

The repeated-task log already records `Bounded Table-Branch Activation Slice Closure` as a recurring manual pattern.

The logged manual handling is not just "run the parser once." It is the same evidence-first closure sequence:

- `triage -> boot smoke -> real parse smoke -> canonical normalization -> wrapper spec`
- then patch the phase plan and master plan so the next active path is explicit

That is the reason this belongs in a skill-sidecar knowledge base.
The repo is no longer describing a hypothetical table branch.
It has identified a reusable activation problem that can recur whenever a dormant branch must be promoted into a runnable one.

## Current Table-Branch Evidence

The current phase-0 activation plan shows that the first bounded table-branch slice has already been closed on real repo artifacts.

Completed evidence includes:

- triage selected `image11.png` as `use_full_image`
- `paddleocr-mcp` boot smoke succeeded
- `PP-StructureV3` real-image smoke succeeded on the same bounded image
- one canonical `Table -> Row -> Cell` normalization was written
- the read-only wrapper served a bounded downstream consumer smoke on that normalized table

The master plan now reflects the same state:

- the bounded table branch is recorded as completed through wrapper-consumer smoke
- the table branch remains enrichment-first and non-blocking for non-table images
- canonical structured artifacts are still the gate for advancing the branch

So the repo evidence already supports the core claim behind this skill:
branch activation is a bounded closure problem, not just a parser availability check.

## Why This Is A Skill Rather Than A One-Off Plan

One plan can describe one activation attempt.
A skill exists because the workspace now has a reusable boundary and a reusable justification.

The reusable boundary is:

- one dormant or candidate table branch
- one bounded candidate set
- one ordered evidence slice
- one downstream readiness check before broader promotion

The reusable justification is that neighboring steps are already split into separate skill surfaces:

- `transparent-component-triage`
- `vendored-mcp-onboarding`
- `parser-sidecar-to-canonical-schema-promotion`

What remained unowned was the slice that connects those surfaces into a single readiness proof.
This skill fills that gap.
It packages the logic for "when a table branch is allowed to count as active" without turning into the branch's full production rollout surface.

## Boundary Reminder

This skill should stop at proving one bounded activation slice and recording why the branch can be treated as runnable.

It should not expand into:

- broad parser rollout
- routine table parsing after activation
- worksheet export hardening
- row-level RAG activation
- replacing the canonical phase plan or master plan as the runtime truth source
