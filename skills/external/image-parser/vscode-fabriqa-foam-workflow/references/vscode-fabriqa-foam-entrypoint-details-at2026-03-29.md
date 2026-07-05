# VS Code Fabriqa Foam Workflow — Entrypoint Details

- recorded_at: `2026-03-29`

## Goal

Open or retarget a markdown review workspace into the right operating mode for the immediate task.

## Mode Table

| Mode | Default editor association | Use for | Known limitation |
|------|----------------------------|---------|------------------|
| `fabriqa` | `fabriqa.markdownEditor` | same-page image-visible editing | `[[wikilink]]` autocomplete and some Foam commands do not reliably attach |
| `text` | `default` | `[[wikilink]]` authoring, Foam commands, raw markdown inspection | same-page visual feel is weaker than `fabriqa` |
| `clear` | remove override | return control to host/editor default | resulting surface depends on existing host settings |

## CLI Usage

```bash
# switch workspace into fabriqa mode
python3 skills/vscode-fabriqa-foam-workflow/scripts/switch_vscode_markdown_mode.py \
  --workspace /path/to/workspace \
  --mode fabriqa

# switch workspace into text mode
python3 skills/vscode-fabriqa-foam-workflow/scripts/switch_vscode_markdown_mode.py \
  --workspace /path/to/workspace \
  --mode text

# switch + open workspace and file together
bash skills/vscode-fabriqa-foam-workflow/scripts/open_vscode_markdown_surface.sh \
  --workspace /path/to/workspace \
  --file /path/to/workspace/note.md \
  --mode fabriqa \
  --reuse-window

# run the mode-switch tests
python3 skills/vscode-fabriqa-foam-workflow/scripts/test_switch_vscode_markdown_mode.py
```

## Validated Runtime Notes

- `fabriqa` same-page image rendering: validated
- Foam `Connections` / backlinks: validated
- rename sync after note rename: validated
- `[[wikilink]]` autocomplete: validated in `Text Editor`, not validated in `fabriqa`
- `Foam: Update Wikilink Definitions`: validated in `Text Editor`, fails when `fabriqa` is the active custom editor

## Operational Constraint

The `code` CLI can open files and folders, but it does not expose a direct `Reopen Editor With...` flag.
Therefore this skill automates the effective editor mode through workspace-level `workbench.editorAssociations`.

If a markdown tab is already open in the previous editor type, close and reopen it, or use `Reopen Editor With...`.

## Notes

- Do not mutate the same workspace `settings.json` from multiple processes at once.
- Exclude `.history` from Foam indexing if local history noise contaminates `Connections`.
- Treat this as a split workflow, not a single-surface Obsidian clone claim.
