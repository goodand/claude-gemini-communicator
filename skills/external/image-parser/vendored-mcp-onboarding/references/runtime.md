# Runtime

## Canonical Operating Pattern

For this workspace, a vendored MCP is considered properly onboarded only after all of these surfaces agree:

1. vendor source exists under `vendor/mcp/`
2. isolated runtime exists inside the vendored surface
3. thin launcher exists under `scripts/mcp/`
4. `.codex/config.toml` registration exists
5. `.vscode/mcp.json` registration exists when VS Code use matters
6. `tool_inventory.json` reflects the current state
7. canonical smoke evidence exists under `control/project_agent_ops/resources/smoke/`

## Recommended Order

### Python MCP

1. vendor upstream into `vendor/mcp/<name>/`
2. create dedicated venv inside the vendored tree
3. install package into that venv
4. create thin launcher under `scripts/mcp/`
5. redirect logs and writable caches if needed
6. register in config files
7. update inventory
8. run light smoke
9. run heavy smoke if model-backed

### Node or TypeScript MCP

1. vendor upstream into `vendor/mcp/<name>/`
2. run package install inside the vendored tree
3. compile if the workspace wrapper expects built output
4. create thin launcher under `scripts/mcp/`
5. register in config files
6. update inventory
7. run light smoke
8. run representative tool smoke

## Review Rule

Do not treat `registered = true` as enough.

For model-backed or community MCPs, the minimum trustworthy state is:

- launcher verified
- at least one real tool invocation verified
- canonical smoke artifact written

## Existing Workspace Examples

- `imagesorcery-mcp`
- `macos-ocr-mcp`
- `paddleocr-mcp`
- `tigaweb-image-edit-sample-mcp`
