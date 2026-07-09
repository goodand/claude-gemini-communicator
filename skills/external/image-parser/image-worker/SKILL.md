---
name: image-worker
description: Process exactly one image in isolation. Use when a single image needs caption generation, status updates, and candidate rename preparation through MCP-backed state.
---

# Image Worker

## Overview

Use this skill for exactly one image record at a time.
It owns single-image execution only. Dispatch, cross-worker aggregation, and final approval remain outside this skill.

## Use This Skill When

- The dispatcher already issued a bounded packet with `job_id` and `image_id`.
- The image should be processed without cross-image context bleed.
- MCP-backed state and evidence must remain the source of truth for completion.

## Required MCPs

- `agent-task-manager`
- `conport`
- `cv-mcp`

## Optional MCPs

- `filesystem`
- `exiftool`

## Not Owned Here

- Parallel shard planning
- Cross-worker summaries
- Human approval decisions
- File rename or metadata commit

## References

- `references/runtime.md`
- `references/troubleshooting.md`
- `references/record-contract.md`
- `checklists/worker-preflight.md`
- `knowledge_bases/image-worker-knowledge-base-at2026-03-28-11-20.md`
- `evals/evals.json`
