# Viewer Surface Requirements

Use this note before running `pptx-slide-screenshot-capture`.

## Required Preconditions

- The PPTX already exists locally.
- One simulator and one UDID are chosen for the full run.
- A simulator-visible surface can show exactly one target slide at a time.

## Acceptable Viewer Surfaces

- Browser-based slide viewer
- App screen that renders one slide or one exported slide image at a time
- Local gallery or simple viewer built from exported slide images

## Minimum Capture Conditions

- Stable resolution for the full run
- Predictable slide order
- One output file per slide
- Low or no transient UI overlays during capture

## Not Solved Here

- Exporting PPTX slides to images
- Building the viewer surface itself
- Caption generation from the captured screenshots
- Human review of captions
