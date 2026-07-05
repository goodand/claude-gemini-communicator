---
name: vscode-fabriqa-foam-workflow
description: Operate an existing markdown review surface in VS Code with fabriqa for same-page image editing and Foam for backlinks and graph navigation, without redefining machine-truth semantics.
---

# VS Code Fabriqa Foam Workflow

## Overview

Use this skill when a human or agent needs a VS Code-native markdown review surface that behaves as follows:

- `fabriqa` for same-page image-visible editing
- `Foam` for backlinks, connections, and graph navigation
- `Text Editor` for wikilink authoring and Foam commands that require an active text editor

This skill bundles a workspace mode switcher and a launch helper.
It does not try to automate VS Code GUI state beyond what `code` CLI and workspace settings can reliably control.

## Use This Skill When

- markdown review should stay in VS Code instead of Obsidian
- image embeds must stay visible while editing
- Foam backlinks and connections should stay available in the side bar
- the workflow must switch between `fabriqa` review mode and `Text Editor` authoring mode
- an agent should set the workspace default markdown editor before launching VS Code
- a markdown review surface already exists and now needs to be operated inside VS Code

## Do Not Use This Skill When

- the task is to generate the review markdown itself from ledgers or experiment outputs
- the task is to produce an Obsidian-native portable review vault
- the task is to install VS Code extensions for the first time
- the task requires guaranteed GUI automation of `Reopen Editor With...`

## Required Inputs

- one explicit workspace path
- optional target markdown file path
- one explicit mode:
  - `fabriqa`
    - same-page visual editing
    - best for embedded-image review
  - `text`
    - wikilink authoring
    - Foam commands that require `window.activeTextEditor.document`
  - `clear`
    - removes the workspace override and lets the host default decide

## Validated Behavior

- same-page embedded image render in `fabriqa`: pass
- Foam `Connections` / backlinks: pass
- rename sync after note rename: pass
- `[[wikilink]]` autocomplete in `Text Editor`: pass
- `Foam: Update Wikilink Definitions` in `Text Editor`: pass
- `[[wikilink]]` autocomplete in `fabriqa`: fail
- `Foam: Update Wikilink Definitions` while `fabriqa` is the active editor: fail

Treat this as a split workflow, not a fully unified Obsidian clone.

## Required Extensions

- `fabriqaai.fabriqa-markdown-editor`
- `foam.foam-vscode`
- `bierner.markdown-mermaid`

## Mode Model

- `fabriqa`
  - default markdown editor becomes `fabriqa.markdownEditor`
  - use for image-visible review and same-page editing
- `text`
  - default markdown editor becomes `default`
  - use for `[[wikilink]]` authoring and Foam commands that require `window.activeTextEditor.document`
- `clear`
  - removes the workspace-level markdown association override

## Scripts

- `scripts/switch_vscode_markdown_mode.py`
- `scripts/open_vscode_markdown_surface.sh`
- `scripts/test_switch_vscode_markdown_mode.py`

## Workflow

1. Decide the task surface first.
2. If no markdown review surface exists yet, create it first with `skills/obsidian-caption-review-builder/` or another producer.
3. If the current task is image review or inline markdown editing with visible embeds, use `fabriqa` mode.
4. If the current task is wikilink authoring, link-definition updates, or Foam diagnostics, use `text` mode.
5. Run the mode switcher before opening or reopening the target markdown file.
6. Launch VS Code through the bundled shell wrapper when you want the mode change and open action together.
7. If a markdown tab was already open in the previous editor type, close and reopen it, or use `Reopen Editor With...`.

## Outputs

- workspace-level markdown editor association under `.vscode/settings.json`
- optional VS Code window launch through `code`
- no generated markdown review artifact by itself

## Important Constraint

VS Code CLI can open files, folders, windows, and profiles, but it does not expose a direct `Reopen Editor With...` CLI argument in `code --help`.
Therefore this skill controls the effective open mode through workspace settings and then opens the file with `code`.

## Known Good Commands

```bash
python3 skills/vscode-fabriqa-foam-workflow/scripts/switch_vscode_markdown_mode.py \
  --workspace /path/to/workspace \
  --mode fabriqa

bash skills/vscode-fabriqa-foam-workflow/scripts/open_vscode_markdown_surface.sh \
  --workspace /path/to/workspace \
  --file /path/to/workspace/note.md \
  --mode text \
  --reuse-window
```

## Not Owned Here

- installing VS Code itself
- installing extensions
- hard-forcing existing already-open tabs to change editor type without user interaction
- AppleScript-driven GUI automation

## Known Good Fit

- reviewing image-heavy markdown already present in the repo
- switching between visual markdown inspection and link-authoring inside one workspace
- keeping Foam `Connections` and graph navigation available while using `fabriqa` selectively
- workspace-local operational guidance for agents that should open markdown in the right mode first
- downstream operator surface for markdown reviews produced by `skills/obsidian-caption-review-builder/`

## References

- [references/runtime.md](references/runtime.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/vscode-fabriqa-foam-entrypoint-details-at2026-03-29.md](references/vscode-fabriqa-foam-entrypoint-details-at2026-03-29.md)
- [references/cross_skill_dependencies.yaml](references/cross_skill_dependencies.yaml)
- [knowledge_bases/vscode-fabriqa-foam-workflow-knowledge-base-at2026-03-29-02-40.md](knowledge_bases/vscode-fabriqa-foam-workflow-knowledge-base-at2026-03-29-02-40.md)
- [evals/evals.json](evals/evals.json)
