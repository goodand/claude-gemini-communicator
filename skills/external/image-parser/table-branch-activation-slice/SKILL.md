---
name: table-branch-activation-slice
description: Close a dormant or candidate table-parser branch through one evidence-first bounded activation slice. Use when the project must prove a parser path with ordered artifacts such as triage, boot smoke, real-image parse, canonical normalization, and downstream wrapper consumption before any wider rollout.
---

# Table Branch Activation Slice

## Overview

Use this skill to close one bounded table-branch activation slice without widening directly into batch rollout.

This skill owns the activation protocol:

- bounded candidate selection
- parser boot verification
- bounded real-image parse evidence
- canonical normalization
- wrapper-consumer confirmation

It does not own broad parser rollout, worksheet export, or row-level RAG activation.

## Use This Skill When

- a parser backend is available but not yet trusted as an active branch
- one bounded table-bearing image set must prove the branch
- the project needs evidence in a fixed order before downstream promotion
- the current task is branch activation, not broad production usage

## Do Not Use This Skill When

- the parser branch is already active and only routine parsing is needed
- the task is single-step MCP boot smoke only
- the task is canonical normalization only
- the task is downstream wrapper usage only
- the task is batch-wide table rollout

## Required Inputs

- one active branch plan
- one bounded candidate image set
- one chosen parser backend
- canonical artifact paths for:
  - triage
  - smoke
  - normalization
  - wrapper-consumer evidence

## References

- `references/runtime.md`
- `references/troubleshooting.md`
- `knowledge_bases/table-branch-activation-slice-knowledge-base-at2026-03-28-02-20.md`
- `evals/evals.json`
- `control/project_domain/resources/experiment_plans/PLAN_phase0_table_branch_activation-at2026-03-27-23-57.md`

## Workflow

1. Treat the branch as inactive until bounded evidence exists.
2. Keep the activation slice ordered and narrow.
3. Use reviewed or bounded gates before parser fanout.
4. Normalize parser output into canonical schema before downstream consumers.
5. Confirm at least one bounded consumer can read the canonical output.
6. Promote the branch only after the ordered slice is complete and documented.

## Preferred Output Surface

- plans: `control/project_domain/resources/experiment_plans/`
- manifests: `control/project_domain/resources/manifests/`
- reports: `control/project_domain/resources/reports/`
- smoke evidence: `control/project_agent_ops/resources/smoke/`

## Outputs

- activation runtime guidance
- activation troubleshooting guidance
- activation rationale KB
- activation eval matrix

## Not Owned Here

- parser implementation itself
- broad parser rollout
- worksheet export
- row-level RAG indexing
- downstream table explanation features
