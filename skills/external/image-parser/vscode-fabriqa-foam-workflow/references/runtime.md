# Runtime

## Core Decision

Use two editor modes, not one:

- `fabriqa` for review and inline visual editing
- `Text Editor` for wikilinks and Foam commands

## Why

Validated locally:

- `fabriqa` shows embedded images in the same markdown page
- Foam `Connections` works for backlinks and forward links
- rename sync works
- Foam wikilink features depend on `window.activeTextEditor.document`
- `fabriqa` is a custom editor and may leave `activeTextEditor` undefined for some Foam commands

## Workspace Setting Used

The mode switcher writes to workspace `.vscode/settings.json` and updates:

```json
{
  "workbench.editorAssociations": {
    "*.md": "fabriqa.markdownEditor"
  }
}
```

or:

```json
{
  "workbench.editorAssociations": {
    "*.md": "default"
  }
}
```

If a host VS Code build ignores the association for already-open tabs, close and reopen the target file.

## Recommended Operation

- review image-heavy markdown in `fabriqa`
- switch to `text` before running:
  - `Foam: Update Wikilink Definitions`
  - heavy `[[wikilink]]` authoring
  - Foam diagnostics that depend on the active text editor

## Practical Mode Rule

- visual review question -> `fabriqa`
- backlink or graph navigation question -> `Foam` side panel
- link-authoring or Foam command question -> `Text Editor`

Keep the mental model simple:

- `fabriqa` shows
- `Text Editor` authors
- `Foam` navigates

## Launch Strategy

The bundled shell wrapper:

1. updates workspace mode
2. opens the workspace in VS Code
3. optionally opens a target markdown file

It uses a VS Code CLI surface such as `${VSCODE_BIN:-code}`.
It does not simulate `Reopen Editor With...`.

Required editor surface should be treated as host preflight, not as a repo guarantee:

- `fabriqa.markdownEditor`
- Foam extension commands

## Operational Caution

- Do not run multiple mode-switch writes against the same workspace `settings.json` in parallel.
- Change mode first, then open VS Code.
- If a markdown tab is already open, close and reopen it before assuming the new association took effect.
