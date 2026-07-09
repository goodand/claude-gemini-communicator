---
name: transparent-component-triage
description: Triage a bounded batch of PPT-extracted images to find the small subset that is mechanically sufficient for alpha-only component splitting. Use when conservative preprocessing is required and only review-gated deterministic candidates should advance beyond the full-image baseline.
---

# Transparent Component Triage

## Overview

Use this skill to run a conservative batch pass over PPT-extracted media and answer one narrow question:

- which files are already good enough for deterministic alpha-only splitting
- which files should stay on the full-image baseline

This skill wraps the existing alpha-only batch classifier and keeps the result as a review-gated candidate subset, not an automatic promotion surface.

## Use This Skill When

- the source set is a bounded PPT media batch under `control/project_domain/resources/pptx_jobs/`
- automatic object isolation is still considered unsafe
- a deterministic prefilter is needed before any reviewed component selection
- the goal is to separate `alpha_split_sufficient` from the rest

## Do Not Use This Skill When

- the task is one-image component review
- semantic object selection is the current task
- imagegen correction is the current task
- full-image caption rerun is the current task
- the source set is not a bounded PPT media extraction surface

## Required Inputs

- optional `--input-root`
- optional `--output-root`
- optional `--manifest-jsonl`
- optional `--summary-json`
- optional `--report-md`
- optional `--limit`

## Script

- `scripts/classify_alpha_split_batch.py`

## References

- `knowledge_bases/transparent-component-triage-knowledge-base-at2026-03-28-01-20.md`
- `references/runtime.md`
- `references/troubleshooting.md`

## Workflow

1. Confirm the batch is a conservative preprocessing candidate set.
2. Run the skill-local wrapper, not a handwritten worker loop.
3. Let the shared classifier call the correction worker in alpha-only mode.
4. Read the markdown report and summary JSON before using any subset downstream.
5. Treat `alpha_split_sufficient` as review-gated only.
6. Keep every other file on the full-image baseline unless a later reviewed gate says otherwise.

## Preferred Output Surface

- report: `control/project_domain/resources/reports/`
- summary: `control/project_domain/resources/manifests/`
- manifest JSONL: `control/project_domain/resources/manifests/`
- per-image worker outputs: `control/project_domain/archive/object_isolation/alpha_split_batch/`

## Outputs

- one markdown report
- one summary JSON
- one manifest JSONL
- per-image worker result directories

## Known Good Fit

- transparent PNG-heavy PPT extract batches
- phase0 preprocessing where the default baseline must remain conservative
- cases where deterministic alpha-connectivity is useful as a review prefilter only

## Not Owned Here

- semantic object selection
- component-level OCR review of a single image
- imagegen correction
- object-level caption reruns
- automatic downstream promotion without review
