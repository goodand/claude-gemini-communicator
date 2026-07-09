---
name: pptx-slide-screenshot-capture
description: Capture per-slide screenshots for PPTX cross-validation. Use when a presentation needs slide-level screenshots captured through a simulator-visible viewer surface, then reused as image inputs for caption validation.
---

# PPTX Slide Screenshot Capture

## Overview

Use this skill for the third validation path in the presentation image pipeline:

`PPTX -> slide viewer surface -> simctl screenshot -> image-to-API caption validation`

This skill is separate from raw PPTX media extraction.
Use it when slide-level visual appearance matters and the validation target should match what a viewer sees on screen.

## Use This Skill When

- A `.pptx` file is already available locally.
- Cross-validation needs slide screenshots, not only embedded media assets.
- `xcrun simctl` is available and a simulator can be used for capture.
- A simulator-visible surface exists for the slides.
  Examples:
  - browser-based slide viewer
  - image gallery made from exported slide images
  - app/web page that renders one slide at a time

## Do Not Use This Skill When

- Only embedded media extraction is needed.
- No simulator-visible slide surface exists yet.
- The task is metadata extraction from PPT internals rather than rendered slide validation.

## Required Inputs

- Source PPTX path
- Stable job directory under `control/project_domain/resources/cross_validation/<job_name>/`
- Target screenshot directory
- Simulator UDID
- Ordered slide list or capture loop plan

## Required Tools

- `xcrun simctl`
- `view_image` for spot checks after capture

## Optional Tools

- Viewer launcher or prebuilt slide surface
- OpenAI API caption flow in another session

## Depends On

- `pptx` for any PPTX-specific handling before capture
- `ios-demo-capture-loop` as an operational reference for simulator screenshot habits

## References

- `references/viewer-surface-requirements.md` for what must already exist before `simctl screenshot` is useful
- `references/troubleshooting.md` for known sandbox and simulator failure patterns

## Script

- `scripts/capture_simctl_slide_screenshots.py` captures the current simulator-visible slide sequence and writes `slide_screenshots_simctl_dataset.jsonl`

## Workflow

1. Read the job manifest under `control/project_domain/resources/cross_validation/<job_name>/cross_validation_manifest.json`.
2. Confirm the target screenshot directory:
   `control/project_domain/resources/cross_validation/<job_name>/slide_screenshots_simctl`
3. Choose one simulator only and record its UDID.
4. Prepare a simulator-visible slide surface before any capture.
5. Step through slides in order and capture each screen with:
   `python3 <path-to-skill>/scripts/capture_simctl_slide_screenshots.py --job-manifest <cross_validation_manifest> --udid <UDID> --slide-count <N> --manual-advance`
6. Spot-check sample captures with `view_image`.
7. Save a JSONL dataset that maps `slide_no`, `screenshot_path`, and `source_pptx`.
8. Hand the dataset to the caption-validation flow.

## Capture Rules

- Treat slide screenshots as a separate validation source from embedded media images.
- Keep one file per slide.
- Use stable names such as `slide-0001.png`.
- Do not mix screenshots from multiple simulators in one dataset.
- If the viewer surface changes resolution mid-run, restart the capture loop.
- If the on-screen slide is uncertain, do not continue. Reconfirm the active slide first.

## Outputs

- `slide_screenshots_simctl/slide-*.png`
- `slide_screenshots_simctl_dataset.jsonl`
- optional spot-check notes for failed or ambiguous slides

## Known Failure Pattern

- A sandboxed Python process may fail to call `xcrun simctl` reliably and raise a `CoreSimulatorService connection invalid` error.
  If that happens, rerun the helper unsandboxed rather than changing the capture logic first.

## Not Owned Here

- Raw PPTX media extraction
- Caption generation or caption approval
- EXIF/XMP/IPTC metadata write-back
- Viewer-surface creation for the slides
- Final presentation regeneration

## Handoff Notes

- For raw media comparison, use the extraction manifest under `control/project_domain/resources/pptx_jobs/<job_name>/manifest.json`.
- For direct image-worker processing, use extracted media files instead of slide screenshots.
- This skill owns screenshot capture only. It does not approve captions or commit metadata changes.
