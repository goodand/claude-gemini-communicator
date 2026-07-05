# Object Isolation Correction Knowledge Base

## Purpose

Summarize the stable decision model for correcting imperfect object-isolation results in this workspace.

## Core Problem

Object isolation errors are not all the same. The repair route depends on whether the problem is:

- boundary selection
- split decision
- wrong target choice
- or visual damage after the boundary has already been chosen

## Stable Route Model

### Route A: `imagesorcery-first`

Use this when the main problem is deterministic:

- multiple bundled objects
- wrong target selected
- undercrop or overcrop
- a better mask, polygon, or crop should be found before any generative cleanup

This route is usually:

- `detect` or `find`
- then `fill` and/or `crop`

### Route B: `imagegen-first`

Use this when the main problem is repair-like:

- missing object parts
- bad edges
- current cutout is visibly broken even though the target is already known

This route is useful when a multimodal model can repair the current result faster than another round of strict masking.

### Route C: `hybrid`

Use this when deterministic masking is still useful but the expected final output will probably need model-assisted cleanup.

Typical cases:

- boundary is mostly right but background residue remains
- transparent cutout is needed and the edges will likely need polish
- the user wants a clean presentational asset, not only a raw mask

## Why A Packet Matters

The correction packet is the boundary object between:

- raw error observation
- tool choice
- edit prompt
- review

Without the packet, the retry path tends to drift into ad hoc prompting.

## Stable Output Fields

A useful correction packet should contain:

- source image
- current result if present
- issue labels
- target description
- chosen route
- reasoning for the chosen route
- recommended next tools
- optional imagegen correction prompt

## Repo-Specific Boundary

This skill is not a generic image-edit skill.
It is a repo-specific decision layer that prepares the next retry for:

- `imagesorcery-mcp`
- `imagegen`
- or a hybrid of both

## Practical Lesson

Deterministic masking and GPT-style correction should not compete at the same layer.
The skill should choose the route first, then the edit should happen on the chosen surface.
