# Troubleshooting

## Registration Exists but the MCP Still Is Not Usable

Do not stop at config registration.
Check:

- launcher path exists
- vendored runtime executable exists
- logs or caches are writable
- a real tool call succeeds

## Model-Backed MCP Boots but Inference Fails

This often means post-install steps, model downloads, or cache redirection are incomplete.
Run the smallest representative inference smoke before marking the MCP active.

## Sandboxed Execution Behaves Differently

Some local OCR or ML MCPs behave differently in sandboxed and unsandboxed runs.
Record that explicitly in the inventory instead of pretending the surface is uniformly verified.

## VS Code and Codex Drift Apart

When a repo-local MCP is added, compare all four surfaces together:

- `.codex/config.toml`
- `.vscode/mcp.json`
- `control/project_agent_ops/registry/tools/tool_inventory.json`
- actual launcher files under `scripts/mcp/`

## Inventory Says `boot_verified` but No Smoke Artifact Exists

Treat that as incomplete.
Canonical smoke evidence should exist before the MCP is described as fully active.

## Launcher Works Only with Environment Overrides

That is still acceptable, but the launcher should own the workaround.
Do not patch stable downstream scripts when the real fix belongs in `scripts/mcp/start-*.sh`.
