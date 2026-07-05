# Owner Boundary — vendored-mcp-onboarding

## What "Owner" Means in This Context

`vendored-mcp-onboarding` is the workspace MCP lifecycle owner-family entrypoint.

Owner here means: when a workspace MCP's registration, launcher, runtime, inventory record, or setup documentation is wrong or stale, this skill is the canonical place to route that problem.

It does not mean: this skill is responsible for everything that uses or depends on an MCP.

---

## Owner Verbs

These actions belong to the owner layer. Route them here.

| Verb | Description |
|---|---|
| Vendored MCP onboarding | First-time adoption of a new MCP under `vendor/mcp/` with launcher, config, inventory, smoke |
| Launcher / config alignment | Ensuring `scripts/mcp/`, `.codex/config.toml`, and `.vscode/mcp.json` stay consistent |
| Inventory update | Writing or correcting activation state in `tool_inventory.json` |
| Setup-doc alignment | Keeping `REFERENCE_mcp_setup.md` consistent with actual MCP state |
| Bounded smoke evidence maintenance | Running or re-verifying boot/activation smoke to confirm a tool is live |
| Activation state management | Marking a tool registered, launcher-wired, boot-verified, heavy-smoke-verified, or active |
| Drift detection | Finding and reconciling gaps between launcher, config, inventory, and setup docs |

---

## Not Owned Here

These actions belong to consumer specialists or pipeline skills. Do not route them to this skill.

| Not Owned | Canonical Owner |
|---|---|
| OCR evidence gathering from images | `macos-ocr-evidence` |
| Caption generation or validation | `openai-image-caption-validation` |
| Component review or split decisions | `component-split-ocr-review` |
| Downstream experiment execution | respective pipeline/workflow skill |
| Object isolation logic | `object-isolation-correction` or pipeline skill |
| Consumer-side business logic that depends on an MCP | respective consumer specialist |
| Designing or modifying the MCP implementation itself | out of scope for all current skills |

---

## Boundary Principle

> If the task is about **whether an MCP is correctly installed, registered, and active in the workspace**, it routes to `vendored-mcp-onboarding`.
>
> If the task is about **what to do with an MCP's output in a pipeline or experiment**, it routes to the relevant consumer specialist.

A consumer specialist may depend on an MCP being correctly installed, but that dependency does not make the consumer specialist a tool owner.

---

## Canonical Owner Outputs

Any skill or task that needs to update these two files must route through the owner layer:

- `control/project_agent_ops/registry/tools/tool_inventory.json`
- `control/project_agent_ops/resources/tools_inventory/REFERENCE_mcp_setup.md`

Consumer specialists read from these files. They do not write to them.
