---
name: macos-ocr-evidence
description: Extract bounded OCR evidence from local image files with macos-ocr-mcp, using macOCR only as a fallback reference when MCP coverage is insufficient. Use when downstream refinement or review needs visible-text evidence, not final semantic decisions.
---

# macOS OCR Evidence

## Overview

Use this skill to extract OCR text evidence from local image files in the presentation image pipeline.
The preferred path is `macos-ocr-mcp` with `ocr_image(file_path)`.

Use it when a caption, object-isolation result, or content classification decision depends on visible text inside an image.

For table-like images, this skill may reference a local Apple Vision document-structure helper script as a secondary surface.
That helper is not treated as a standalone MCP and is owned by the table-structure promotion skill, not by this OCR skill.

## Use This Skill When

- a local PNG or JPG needs OCR evidence
- a PPT-extracted image or isolated cutout needs text confirmation
- a chart, UI screenshot, or table-like image should be grounded with OCR output
- the current task is evidence gathering before review or evaluation
- a table-like image needs Apple Vision structure hints before cell-level re-OCR or parser comparison

## Do Not Use This Skill When

- the current task is object isolation itself
- image files do not exist locally yet
- full PDF document parsing is needed instead of image OCR
- caption approval or metadata write-back is the current task
- canonical `Table -> Row -> Cell` normalization is the current task
- the underlying tool lifecycle is broken — route to `vendored-mcp-onboarding`

## Preferred Tool Surface

- `macos-ocr-mcp.ocr_image(file_path)`

## Fallback Surface

- first fallback:
  - local Swift Vision fallback triggered from the vendored `macos-ocr-mcp` wrapper
- secondary helper path for table-like images:
  - local Apple Vision document-structure helper script used only as a structure-hint surface
- reference-only tertiary fallback:
  - `macOCR` CLI for interactive region OCR or future `--input <file>` comparison runs

## Required Inputs

- absolute path to a local image file
- related image or run identifier if the OCR result should be persisted
- output report target when OCR evidence becomes part of a review artifact

## References

- `references/runtime.md`

## Workflow

1. Prefer `macos-ocr-mcp` on one image first.
2. If the run is sandboxed and OCR comes back empty or throws a Vision-side error, rerun unsandboxed before concluding there is no usable text.
3. Confirm whether annotations are non-empty.
4. Summarize the useful OCR text in the run artifact instead of pasting every raw box into a canonical resource doc.
5. If the image is table-like and row or column structure matters, gather Apple Vision structure hints through the helper script before concluding that OCR-only evidence is sufficient.
6. Treat Apple Vision structure output as a helper sidecar, not as a final canonical table artifact.
7. Use `macOCR` only as a reference or future comparison path unless the local CLI has been explicitly activated in this workspace.
8. Store OCR evidence under the active run artifact unless it becomes reusable knowledge.

## Outputs

- OCR annotations from `macos-ocr-mcp`
- optional Apple Vision structure-hint sidecar for table-like images
- optional run report or review note under the current experiment
- optional evidence snippets attached to caption review or evaluation output

## Not Owned Here

- object isolation preprocessing
- caption generation
- caption approval
- metadata write-back
- full-document OCR parsing
- canonical table-schema promotion
- tool lifecycle integrity (launcher, registration, inventory, setup state)
