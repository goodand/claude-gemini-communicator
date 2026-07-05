# Component Split OCR Review Knowledge Base

## Purpose

This skill exists to expose deterministic component-level evidence from one image before any semantic promotion happens.

## Repo-Specific Fit

- The repo already has shared deterministic logic in `scripts/alpha_component_lib.py`.
- Component splitting plus OCR has already been proven on bounded slide-export images.
- The right promotion target is a review surface, not an automatic isolation decision.

## Operating Principles

1. Prefer shared root scripts and libraries over duplicated skill-local logic.
2. Use the skill as a review stage, not as automatic semantic selection.
3. Keep outputs under `control/project_domain/archive/component_split_ocr/`.
4. Promote reviewed decisions later; do not treat raw component counts as semantic truth.

## Known Evidence

- Alpha-only batch classification found a limited subset of mechanical candidates.
- Some high-count cases were fragment-heavy and unsuitable for blind promotion.
- Component-level OCR is useful as supporting evidence, but many valid components naturally produce `no_text`.

## Boundary Reminder

This skill should stop at:

- component crops
- component table
- OCR evidence
- markdown/JSON review artifacts

It should not expand into:

- semantic ranking
- imagegen correction
- caption reruns
- batch triage orchestration
