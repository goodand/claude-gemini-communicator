---
name: obsidian-caption-review-builder
description: Render an Obsidian-friendly markdown review surface from caption ledgers and local image assets. Use when generated caption records must be exported into a human-readable review view with embedded images, without defining machine-truth semantics or refinement state.
---

# Obsidian Caption Review Builder

## Overview

Use this skill to package caption run results into an Obsidian-friendly review surface.

The primary output is a markdown review file with local image embeds so a human can quickly judge:

- caption quality
- alt text quality
- filename candidate quality
- obvious truncation or grounding drift

This skill wraps the local review-builder script. It does not generate captions by itself.
The skill-local wrapper is policy-aware and defaults to the canonical copied-asset mode.

## Use This Skill When

- caption ledgers already exist locally
- a human needs a visual review surface before approval or rerun
- image embeds should work in Obsidian Live Preview or Reading View
- the default review surface should be portable inside a bounded review asset directory

## Do Not Use This Skill When

- caption generation itself is the current task
- images still need to be extracted from PPTX
- OCR evidence or object isolation is the current task
- final approval decisions need to be written into ADR or closed-question records directly

## Required Inputs

- one explicit ledger glob or one bounded ledger set
- one output markdown path
- one explicit review mode:
  - `canonical-copy`
    - default mode
    - portable review surface
    - auto-creates `review_assets/<output-stem>/` unless `--asset-dir` is given
  - `direct`
    - only when the source layout is already stable and bounded
    - do not pass `--asset-dir`, `--source-root`, or `--embed-prefix`
  - `prefixed`
    - compatibility mode only
    - requires both `--source-root` and `--embed-prefix`

## Script

- `scripts/build_obsidian_caption_review.py`
- `scripts/test_build_obsidian_caption_review.py`

## References

- [knowledge_bases/obsidian-caption-review-builder-knowledge-base-at2026-03-27-23-04.md](knowledge_bases/obsidian-caption-review-builder-knowledge-base-at2026-03-27-23-04.md)
- [references/runtime.md](references/runtime.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/cross_skill_dependencies.yaml](references/cross_skill_dependencies.yaml)

## Workflow

1. Confirm the input ledgers are the exact run surface you want to review.
2. Default to `--mode canonical-copy`.
3. Only use `--mode direct` when the source layout is already stable and local.
4. Treat `--mode prefixed` as a compatibility mode, not the canonical run surface.
5. Generate the markdown review file.
6. Confirm a few sample image embeds resolve correctly.
7. Use the generated review in Obsidian for human judgement.
8. If the same markdown review should instead be operated inside VS Code, hand the generated review surface to `skills/vscode-fabriqa-foam-workflow/`.
9. Keep the review artifact under `control/project_domain/resources/reports/` unless an explicit decision result is promoted elsewhere.

## Preferred Output Surface

- run review under `control/project_domain/resources/reports/`
- copied review assets under `control/project_domain/resources/reports/review_assets/<output-stem>/`
- do not write the canonical review surface directly under `control/user_decisions/`

## Outputs

- one markdown review file
- copied image assets in canonical mode
- no copied assets in `direct` or `prefixed` mode

## Known Good Fit

- phase-1 caption batch review
- shard-level caption inspection before rerun
- human comparison between raw caption output and visible image content
- upstream producer surface for `skills/vscode-fabriqa-foam-workflow/` when the final review should happen inside VS Code instead of Obsidian

## Not Owned Here

- caption generation
- OCR extraction
- object isolation
- metadata write-back
- final approval or rename commit
- VS Code editor-mode switching or Foam/fabriqa workspace operation
- iterative reinjection, refinement loop state → `multimodal-evidence-refinement-loop`
- machine-truth manifest normalization, comparison outcome split → `image-text-cot-review`
