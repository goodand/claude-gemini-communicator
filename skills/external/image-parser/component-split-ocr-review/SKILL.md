---
name: component-split-ocr-review
description: Export deterministic component-level OCR evidence for one transparent or semi-transparent image by splitting alpha-connected components, writing a component table, and running OCR on each component. Use when bounded component evidence must be exported before any downstream refinement or caption rerun.
---

# Component Split OCR Review

## Overview

Use this skill to turn one local image into a bounded review surface:

- alpha-connected component crops
- component summary table
- per-component OCR evidence
- markdown and JSON artifacts for human review

This skill wraps the shared component split/OCR builder. It does not own semantic object selection, imagegen repair, or caption regeneration.

## Use This Skill When

- one local image already exists
- the image is transparent or semi-transparent, or at least worth checking for alpha-separated parts
- a human needs to inspect component-level slices before deciding what to keep
- OCR on each separated component is useful evidence

## Do Not Use This Skill When

- the task is full-image caption generation
- semantic object isolation or model-assisted correction is the current task
- batch subset triage across many images is the current task
- final image approval or rename/metadata commit is the current task
- the underlying tool lifecycle is broken — route to `vendored-mcp-onboarding`

## Required Inputs

- one absolute or repo-relative `--image-path`
- optional `--output-root`
- optional `--alpha-threshold`
- optional `--min-pixels`
- optional `--padding`
- optional `--min-components-for-success`

## Script

- `scripts/build_component_split_ocr_report.py`

## References

- `knowledge_bases/component-split-ocr-review-knowledge-base-at2026-03-28-01-20.md`
- `references/runtime.md`
- `references/troubleshooting.md`

## Workflow

1. Confirm the target is one bounded local image.
2. Run the skill-local wrapper, not a handwritten ad hoc command.
3. Let the shared builder perform alpha split first.
4. Use the generated component table and per-component OCR as the review surface.
5. Treat the output as review evidence only until a human decides what components are meaningful.
6. Promote only reviewed components into later object-isolation or caption flows.

## Preferred Output Surface

- default output root: `control/project_domain/archive/component_split_ocr/`
- one bounded subdirectory per source dataset and image stem
- keep review artifacts in `project_domain/runs`, not `user_decisions`, until a decision is explicitly promoted

## Outputs

- `COMPONENT_SPLIT_OCR_REPORT.md`
- `COMPONENT_SPLIT_OCR_REPORT.json`
- `alpha_components/*.png`
- `component_ocr/*_OCR_RESULT.json`

## Known Good Fit

- transparent PNGs with disconnected visual parts
- slide-export images where alpha-separated icons or panels need inspection
- weak semantic isolation cases where deterministic component evidence is needed first

## Not Owned Here

- semantic object selection
- imagegen correction
- full-image caption rerun
- batch triage across directories
- final approval or commit
- component evidence를 multimodal loop state로 재주입하거나 refinement할 때 → `multimodal-evidence-refinement-loop`
- review surface 정규화 및 manifest split이 필요할 때 → `image-text-cot-review`
- tool lifecycle integrity (launcher, registration, inventory, setup state)
