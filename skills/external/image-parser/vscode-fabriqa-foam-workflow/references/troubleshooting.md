# Troubleshooting

## Error: `Cannot read properties of undefined (reading 'document')`

Likely cause:

- `Foam: Update Wikilink Definitions` was executed while `fabriqa` custom editor was the active tab

Fix:

1. reopen the note with `Text Editor`
2. click inside the real text editor tab
3. rerun `Foam: Update Wikilink Definitions`

## `[[` inserts `[[]]` but shows no note suggestions

Likely cause:

- `fabriqa` is active

Interpretation:

- bracket auto-pairing is working
- Foam wikilink completion is not attached to the custom editor surface

Fix:

- switch to `text` mode or reopen the file with `Text Editor`

## `Connections` shows history noise or wrong counts

Likely cause:

- `.history` files are being indexed

Fix:

Add exclusions in workspace settings:

```json
{
  "files.exclude": {
    "**/.history": true
  },
  "search.exclude": {
    "**/.history": true
  },
  "foam.files.exclude": [
    "**/.history/**/*"
  ]
}
```

Then:

1. reload the VS Code window
2. run `Foam: Update Graph`

## Workspace settings became malformed after switching modes

Symptom:

- `.vscode/settings.json` becomes syntactically broken
- or later mode switches fail with a JSON parse error

Likely cause:

- two processes wrote the same workspace settings concurrently

Fix:

- restore the last good workspace settings
- rerun the mode switch sequentially, not in parallel

Prevention:

- one workspace, one mode switch at a time

## Existing tab still opens in the old editor mode

Likely cause:

- the tab was already open before the association changed

Fix:

- close and reopen the file
- or use `Reopen Editor With...`

## `code` CLI cannot directly choose `Reopen Editor With...`

This is expected.
The skill uses settings-driven default editor selection instead.

## `code` prints a macOS codesign warning but still opens

Symptom:

- `code` prints a macOS `SecCodeCheckValidity` warning to stderr

Interpretation:

- treat it as a warning unless the command actually exits nonzero or fails to open the target

Fix:

- no workflow change is needed if the window and file still open successfully
