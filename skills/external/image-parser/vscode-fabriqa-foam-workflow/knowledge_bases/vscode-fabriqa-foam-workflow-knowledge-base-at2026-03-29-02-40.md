---
name: vscode-fabriqa-foam-workflow-kb
kb_profile: canonical_design_kb
role: vscode markdown review workspace operation
ver: 1
created_at: 2026-03-29
updated_at: 2026-03-29
reference_acquisition_mode: local_validation
source_scope: vscode-fabriqa-foam-workflow skill
purpose: VS Code에서 fabriqa, Text Editor, Foam을 분업형으로 운영하는 canonical operator boundary를 고정한다
---

# VS Code Fabriqa Foam Workflow Knowledge Base

## Purpose

Summarize the stable operating model for using VS Code as a markdown review workspace with:

- `fabriqa` for same-page image-visible editing
- `Foam` for backlinks and graph navigation
- `Text Editor` for wikilink authoring and Foam commands that require an active text editor

## Core Problem

One editor surface does not satisfy every requirement.

The workspace needs all of the following:

- embedded images visible in the same markdown page
- continued text editing in the same document
- backlinks and graph navigation
- reliable `[[wikilink]]` authoring
- reliable execution of Foam commands that read `window.activeTextEditor.document`

## Stable Design Decision

Use a split workflow, not a single-surface claim.

1. `fabriqa`
- visual review surface
- same-page image rendering
- best for editing while looking at embeds

2. `Text Editor`
- authoring surface for `[[wikilink]]`
- safe surface for `Foam: Update Wikilink Definitions`
- safer for any Foam feature that expects a real active text editor

3. `Foam`
- side-shell for `Connections`, backlinks, and graph-like navigation

## Validated Behavior

- embedded image render in `fabriqa`: pass
- Foam `Connections` counts and filtering: pass
- rename sync after note rename: pass
- `[[wikilink]]` autocomplete in `Text Editor`: pass
- `Foam: Update Wikilink Definitions` in `Text Editor`: pass
- `[[wikilink]]` autocomplete in `fabriqa`: fail
- `Foam: Update Wikilink Definitions` while `fabriqa` is active: fail

## Practical Lessons

- `fabriqa` is useful because it restores the Obsidian-like same-page review feel inside VS Code.
- Foam remains valuable, but mainly as navigation and references shell rather than the primary editing surface.
- `code` CLI cannot directly perform `Reopen Editor With...`, so workspace-level `workbench.editorAssociations` is the practical automation lever.
- editor association changes do not reliably retarget already-open tabs; close/reopen or `Reopen Editor With...` may still be required.
- do not mutate the same workspace `settings.json` concurrently from multiple processes; sequential writes are safer.
- exclude `.history` from Foam indexing when local history noise contaminates `Connections`.

## Promotion Notes

This skill is repo-specific.
It is not a generic VS Code extension guide.
Its purpose is to operationalize the validated `VS Code + fabriqa + Foam` review pattern for this workspace.

## Related Skill Boundary

- `skills/obsidian-caption-review-builder/` is the producer surface that turns caption ledgers into a markdown review artifact.
- `skills/vscode-fabriqa-foam-workflow/` is the operator surface that opens and manages an already-existing markdown review inside VS Code.

Recommended composition:

1. build the review markdown with `obsidian-caption-review-builder`
2. open and operate that markdown with `vscode-fabriqa-foam-workflow`
