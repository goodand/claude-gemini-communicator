---
name: image-job-dispatcher
description: Dispatch one-image-per-worker jobs for the presentation image pipeline. Use when you need to register image jobs, fan out isolated Codex subagents, and keep MCP state as the source of truth.
---

# Image Job Dispatcher

## Overview

Use this skill when a batch of presentation images must be processed through isolated workers.
This skill owns dispatch only. It does not decide final approvals or commit rename and metadata changes.

## Use This Skill When

- A presentation export has already produced image files.
- Each image should run in its own worker context.
- Job state must be tracked through MCPs instead of chat text.
- The parent agent needs to resume safely after interruption.

## Inputs

- Image list or extracted image directory
- Stable `job_id`
- Stable `image_id` per file
- Registry location from `registry/session_paths.json`
- Optional shard manifest when a multi-worker batch has already been materialized

## Required MCPs

- `agent-task-manager`
- `conport`

## Optional MCPs

- `filesystem` for path inspection
- `cv-mcp` only when the dispatcher also performs a smoke check

## Workflow

1. Read the registry and pipeline spec.
2. If needed, materialize shard JSONL files and issued task packets before worker fanout.
3. Register the parent job and per-image records through MCP-backed state.
4. Dispatch one worker per image or per shard-owned row using stable identifiers only.
5. Treat MCP state and worker-owned artifacts as the completion signal.
6. Hand off only finished items to the auditor or commit manager.

## Dispatch Rules

- Use `job_id` and `image_id` as worker inputs.
- Keep image content and captions in the registry, not in worker prompts.
- Do not trust free-form worker text as the completion signal.
- A worker is complete only when MCP state and evidence say it is complete.
- Retry failed rows individually. Do not re-run the full batch without reason.
- For parallel runs, one shard JSONL, one worker ledger, and one `_responses/` directory belong to exactly one worker.
- Only the main agent may aggregate shared summaries after parallel workers finish.

## Handoff Targets

- Use `image-worker` for single-image processing.
- Use `image-result-auditor` after worker completion.
- Use `image-commit-manager` only after human approval is recorded.

## References

- `references/runtime.md`
- `references/troubleshooting.md`
- `references/shard-strategy.md`
- `references/task-packet-contract.md`
- `references/cohort-expansion-truth-sync.md`
- `checklists/parallel-preflight.md`
- `knowledge_bases/image-job-dispatcher-knowledge-base-at2026-03-28-10-55.md`
- `evals/evals.json`

## Extension Boundary

This skill may also guide the coordinator when a newly closed image must be folded back into an already-canonical experiment cohort.
That extension is limited to truth synchronization:

- rebuild aggregate bundle truth from finished per-image artifacts
- rebuild downstream consumer truth from the same canonical inputs
- patch closure and registry surfaces so shared state matches the widened cohort

It still does not own semantic judging, file commit, or baseline promotion.
