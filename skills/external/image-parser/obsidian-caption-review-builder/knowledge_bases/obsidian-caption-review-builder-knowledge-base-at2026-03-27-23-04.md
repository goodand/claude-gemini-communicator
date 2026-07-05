---
name: obsidian-caption-review-builder-kb
kb_profile: canonical_design_kb
role: obsidian caption review surface production
ver: 1
created_at: 2026-03-27
updated_at: 2026-03-29
reference_acquisition_mode: local_repo_design
source_scope: obsidian-caption-review-builder skill
purpose: caption ledger를 Obsidian-friendly review markdown surface로 만드는 canonical producer boundary를 고정한다
---

# Obsidian Caption Review Builder Knowledge Base

## Purpose

Summarize the stable operating model for turning caption ledgers into an Obsidian-friendly human review surface.

## Core Problem

Caption ledgers are machine-friendly but slow for human judgement. A reviewer usually needs:

- the image itself
- the generated caption
- the generated alt text
- the filename candidate
- the ledger trace that produced the record

## Stable Design Decision

The skill should default to a portable review surface, not to whichever path mode happens to be easiest to type.

That leads to three explicit modes:

1. `canonical-copy`
- default mode
- safest for Obsidian rendering
- review markdown and copied assets stay inside one bounded review surface

2. `direct`
- use only when the source image layout is already stable relative to the markdown output
- lower overhead, but more fragile when documents move

3. `prefixed`
- compatibility mode
- use only when the vault already exposes a prefixed asset path such as `img/pptx_jobs`

## Canonical Output Rule

- full review surface belongs under `control/project_domain/resources/reports/`
- a review is not a decision record by default
- only explicit human conclusions should later be promoted into `control/user_decisions/`

## Review Content Minimum

Each completed record should show:

- dataset grouping
- image embed
- caption
- alt text
- filename candidate
- source ledger name

Non-completed records may appear without embeds and should be treated as review signals rather than rendering failures.

## Practical Lessons

- defaulting to copied assets reduces Obsidian path breakage
- mode names are easier for agents to use correctly than prose-only policy
- wrapper-level defaults matter because the root script remains intentionally generic
- troubleshooting should explicitly call out missing ledgers, broken embed paths, and wrong output bucket choices

## Promotion Notes

This skill is repo-specific. It does not only build markdown; it also enforces local filing policy for review surfaces.

## Related Skill Boundary

- `skills/obsidian-caption-review-builder/` is the producer surface that turns caption ledgers into a portable markdown review artifact.
- `skills/vscode-fabriqa-foam-workflow/` is the downstream operator surface that opens and manages that markdown review inside VS Code.

Recommended composition:

1. build the review markdown with `obsidian-caption-review-builder`
2. if the review should stay in VS Code, operate it with `vscode-fabriqa-foam-workflow`
