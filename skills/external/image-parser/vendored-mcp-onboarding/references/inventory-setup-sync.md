# Inventory and Setup Sync Reference

## Purpose

Defines the canonical sync targets for workspace MCP state and the protocol for verifying or restoring alignment between them.

Use this reference when:
- a new MCP has been onboarded and all surfaces need to be confirmed consistent
- an existing MCP's activation state may have drifted
- a reviewer asks "is this MCP actually active in the workspace?"

---

## Canonical Sync Targets

These seven surfaces must agree about every MCP's state. Any gap between them is a drift condition.

| Surface | Path | Role |
|---|---|---|
| Launcher | `scripts/mcp/<name>.sh` or equivalent | Executable entry point for the MCP |
| Vendor runtime | `vendor/mcp/<name>/` | Isolated source and runtime |
| Codex config | `.codex/config.toml` | MCP registration for Codex tooling |
| VS Code config | `.vscode/mcp.json` | MCP registration for VS Code MCP use |
| Tool inventory | `control/project_agent_ops/registry/tools/tool_inventory.json` | Authoritative activation state |
| Setup reference | `control/project_agent_ops/resources/tools_inventory/REFERENCE_mcp_setup.md` | Human-readable setup and status reference |
| Smoke evidence | `control/project_agent_ops/resources/smoke/` | Bounded evidence that activation was verified |

---

## Activation State Levels

A tool's record in `tool_inventory.json` should reflect one of these levels:

| Level | Meaning |
|---|---|
| `registered` | Config entry exists but launcher and runtime not yet confirmed |
| `launcher-wired` | Launcher and vendor runtime exist; not yet smoke-tested |
| `boot-verified` | Light smoke passed — tool executable, help/tool-list surface works |
| `heavy-smoke-verified` | One real inference or representative call confirmed |
| `active` | All surfaces aligned, smoke evidence exists; ready for workspace use |

Only mark a tool `active` when all seven sync targets are consistent and smoke evidence exists.

---

## Sync Protocol

Run this when confirming MCP state, not just after first onboarding.

1. Check that the launcher exists at `scripts/mcp/<name>`.
2. Check that the vendor runtime exists at `vendor/mcp/<name>/`.
3. Check that `.codex/config.toml` has an entry for this MCP.
4. Check that `.vscode/mcp.json` has an entry if VS Code MCP use is intended.
5. Check that `tool_inventory.json` has a record with the correct activation level.
6. Check that `REFERENCE_mcp_setup.md` documents this MCP with the current state.
7. Check that bounded smoke evidence exists in `control/project_agent_ops/resources/smoke/`.

If any surface is missing or inconsistent, reconcile and update `tool_inventory.json` and `REFERENCE_mcp_setup.md` together.

For a quick one-pass run, use `checklists/mcp_inventory_sync_checklist.md`.

---

## Drift Conditions and Responses

| Drift Condition | Response |
|---|---|
| Launcher missing but config exists | Create launcher or demote status to `registered` in inventory |
| Vendor runtime missing | Re-vendor or mark inactive |
| Config entry missing for working tool | Add config entry, do not change inventory status until confirmed |
| Inventory shows `active` but no smoke evidence | Re-run smoke; do not downgrade until confirmed broken |
| Setup reference describes old path | Update `REFERENCE_mcp_setup.md` to match current launcher and vendor path |
| Consumer skill reports MCP not responding | Route to owner skill for diagnosis; consumer does not mutate inventory |

---

## Who May Write to These Files

| File | Who Writes | Who Reads |
|---|---|---|
| `tool_inventory.json` | `vendored-mcp-onboarding` (owner skill) | consumer specialists, pipeline skills |
| `REFERENCE_mcp_setup.md` | `vendored-mcp-onboarding` (owner skill) | consumer specialists, pipeline skills |
| `scripts/mcp/` | `vendored-mcp-onboarding` (owner skill) | launchers invoked at runtime |
| `.codex/config.toml` | `vendored-mcp-onboarding` during onboarding | Codex tooling |
| `.vscode/mcp.json` | `vendored-mcp-onboarding` during onboarding | VS Code MCP integration |
| `control/project_agent_ops/resources/smoke/` | `vendored-mcp-onboarding` (owner skill) | auditors, downstream checks |
