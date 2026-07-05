---
name: openai-image-caption-validation
description: Run the local OpenAI caption runner on extracted images or a prepared dataset JSONL to produce bounded caption evidence for downstream refinement or review, usually as a smoke test first and then as a resumable batch, not final machine-truth closure.
---

# OpenAI Image Caption Validation

## Overview

Use this skill to run the local OpenAI caption path on image assets.
This skill owns the caption run only. It does not approve captions or commit rename and metadata changes.

## Use This Skill When

- extracted images already exist locally
- a dataset JSONL already points at image paths
- OpenAI caption output is needed for cross-validation
- a resumable ledger should be written after each image

## Do Not Use This Skill When

- images still need to be extracted from PPTX
- slide screenshots still need to be captured
- caption review or document mapping decisions are the current task
- the underlying tool launcher, registration, inventory, or setup state is broken — route to `vendored-mcp-onboarding`

## Required Inputs

- one of:
  - `--image`
  - `--dataset-jsonl`
  - `--input-dir`
- optional manifest for richer source context
- output ledger path

## Script

- `scripts/caption_images_openai.py`

## References

- `references/troubleshooting.md`

## Workflow

1. Start with a one-image smoke test.
2. Verify the ledger record, raw response, and candidate filename.
3. Only then run the wider batch.
4. Resume with `--retry-failed` when the ledger already exists.

## Preferred Cross-Validation Input

- `control/project_domain/resources/cross_validation/<job>/openai_api/media_extract_dataset.jsonl`

## Outputs

- JSON ledger under `control/project_agent_ops/registry/jobs/image_caption_jobs/` or a caller-specified path
- sibling sidecars:
  - `<job_stem>_execution_records.jsonl`
  - `<job_stem>_evaluation_decisions.jsonl`
- per-image raw response JSON under a sibling `_responses/` directory

## Known Failure Pattern

- Network-restricted or sandboxed runs may fail before the API request completes.
  If the local smoke test cannot reach OpenAI, rerun the runner outside the sandbox before changing the prompt or parser.

## Not Owned Here

- PPTX extraction
- simulator screenshot capture
- caption approval
- metadata write-back
- final presentation regeneration
- reinjection, refinement, baseline comparison → `multimodal-evidence-refinement-loop`
- normalized review artifact, manifest split → `image-text-cot-review`
- tool lifecycle integrity (launcher, registration, inventory, setup state)
