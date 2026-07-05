---
name: object-isolation-correction
description: Wrap object-isolation correction as a repo-specific workflow. Use when a local image already exists, the current isolation result is imperfect, and the next step is to choose between ImageSorcery-first, imagegen-first, or a hybrid correction path with a bounded correction packet and worker run.
---

# Object Isolation Correction

## Overview

Use this skill when an object-isolation result needs repair, not when isolation is still undefined.
This skill does not perform the final multimodal edit by itself.
It standardizes the correction route first, then allows a bounded worker run that tries alpha split, ImageSorcery fallback, and an imagegen request artifact.

## Use This Skill When

- a local source image already exists
- a current isolation result or crop candidate already exists, or the failure mode is visible
- the next step is to choose `imagesorcery`, `imagegen`, or `hybrid`
- a bounded correction packet should be written before retrying the edit

## Do Not Use This Skill When

- images still need to be extracted from PPTX
- caption generation is the current task
- OCR-only evidence is the current task
- final metadata write-back or rename commit is the current task

## Required Inputs

- one absolute `--source-image`
- optional `--current-result`
- one or more `--issue`
- one `--output-md`
- optional `--output-json`

## Script

- `scripts/prepare_object_isolation_correction_packet.py`
- `scripts/run_object_isolation_correction_worker.py`

## References

- `knowledge_bases/object-isolation-correction-knowledge-base-at2026-03-27-23-10.md`
- `references/runtime.md`
- `references/troubleshooting.md`

## Workflow

1. Confirm the source image and current failure mode.
2. Build a correction packet before editing anything.
3. Run the worker in a bounded output directory.
4. Try alpha connected-components first when the source is already a transparent PNG with separated objects.
5. Default to `imagesorcery-first` for boundary, split, or target-selection problems once alpha split is insufficient.
6. Prefer `imagegen-first` for repair-like problems where the current cutout is visually damaged.
7. Use `hybrid` when deterministic masking is still useful but a model-assisted cleanup may be needed after it.
8. Keep the original image path stable and write corrected outputs to a bounded run surface.
9. Review the correction result before promoting it into a caption or OCR rerun.

## Outputs

- one markdown correction packet
- optional JSON sidecar with the same route and prompt data
- one worker report
- one worker result JSON
- alpha component crops when alpha split is sufficient
- ImageSorcery fallback crops when alpha split is insufficient
- bounded imagegen request artifacts when the route still needs model-assisted cleanup

## Not Owned Here

- PPTX extraction
- caption generation
- OCR extraction by itself
- final approval and commit
- direct built-in `imagegen` execution inside a plain local Python script
