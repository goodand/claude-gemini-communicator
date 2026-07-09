---
name: vendored-mcp-onboarding
description: Canonical owner-family entrypoint for workspace vendored third-party MCP lifecycle integrity. Use when a third-party MCP must be vendored under vendor/mcp, launched through a thin wrapper, registered in Codex and VS Code config, recorded in inventory, and verified through bounded smoke evidence before being treated as active. Also use when ongoing launcher/config/inventory/setup-doc alignment for a vendored MCP needs to be verified or restored.
---

# Vendored MCP Onboarding — Vendored Third-Party MCP Owner-Family Entrypoint

## Overview

This skill is the canonical owner-family entrypoint for workspace vendored third-party MCP lifecycle integrity.

It covers two distinct but related concerns:

**First-time onboarding** — adopting a new MCP into this workspace through the standard local pattern:

- vendor the upstream source
- isolate its runtime
- add a thin launcher
- register it in local config
- record it in inventory and registry
- verify it through bounded smoke evidence

**Ongoing owner responsibilities** — after onboarding completes, this skill retains ownership of:

- verifying that already-vendored MCPs still boot correctly
- detecting and resolving drift between launcher, config, inventory, and setup docs
- updating activation state when smoke evidence changes
- keeping `tool_inventory.json` and `REFERENCE_mcp_setup.md` consistent with actual workspace state

This skill does not own the MCP's product semantics, downstream experiment logic, or consumer-side business logic after onboarding is complete.
For consumer specialist skills that depend on MCPs, see `references/tool-owner-family-map.md`.

## Use This Skill When

- a new third-party MCP should live under `vendor/mcp/`
- the MCP should stay isolated from the main workspace runtime
- `.codex/config.toml` must be aligned with the MCP's launcher and vendor state
- `.vscode/mcp.json` must be aligned when VS Code MCP use is intended
- the vendored MCP inventory and canonical smoke evidence need to be brought to a trustworthy state
- launcher, config, inventory, and setup references have drifted and need to be reconciled
- the activation state of an existing MCP needs to be re-verified without a full re-onboard
- a reviewer asks which skill owns vendored third-party MCP lifecycle integrity — the answer is this skill

## Do Not Use This Skill When

- the change is consumer-local only and does not touch launcher, config registration, inventory, setup docs, or smoke evidence
  - if any of those owner outputs are affected, route here regardless of how small the change is
- the MCP is remote-only and not vendored into the workspace
- the task is using an already-registered MCP for a downstream experiment (see consumer specialists)
- the task is creating a new workflow skill rather than adopting or maintaining a new MCP runtime
- the task is gathering OCR evidence, generating captions, or reviewing image components

## Required Inputs

### For new onboarding

- upstream source location or repo URL
- target vendor directory under `vendor/mcp/`
- chosen runtime isolation strategy
  - dedicated venv
  - uv-managed vendor project
  - node/npm vendor runtime
- target launcher path under `scripts/mcp/`
- intended registration names for:
  - `.codex/config.toml`
  - `.vscode/mcp.json`
  - `tool_inventory.json`

### For ongoing owner tasks

- name of the MCP to verify or reconcile
- current known state (if any) from `tool_inventory.json`
- checklist to run: `checklists/mcp_inventory_sync_checklist.md`

## Owner Verbs

This skill owns the following verbs:

- vendored MCP onboarding (new adoption)
- launcher / config / inventory / setup-doc alignment verification
- bounded smoke evidence gathering to determine activation state
- activation state update in `tool_inventory.json` and `REFERENCE_mcp_setup.md`

## Not Owned Here

- designing the MCP itself
- changing stable workspace business logic that consumes the MCP
- workflow skill creation unrelated to MCP lifecycle
- downstream experiment execution after onboarding is complete
- OCR evidence gathering (owned by `macos-ocr-evidence`)
- caption generation or validation (owned by `openai-image-caption-validation`)
- component review decisions (owned by `component-split-ocr-review`)
- consumer-side business logic for any MCP-consuming pipeline skill

## References

- `knowledge_bases/vendored-mcp-onboarding-knowledge-base-at2026-03-28-01-30.md`
- `references/runtime.md`
- `references/troubleshooting.md`
- `references/owner-boundary.md` — defines what "owner" means and what this skill owns vs. not
- `references/tool-owner-family-map.md` — maps owner vs. consumer skills for workspace MCPs
- `references/inventory-setup-sync.md` — canonical sync targets and alignment protocol
- `checklists/mcp_inventory_sync_checklist.md` — one-pass drift detection checklist
- `control/project_agent_ops/resources/skill_candidates/repeated_tasks/TASK_vendored_python_mcp_bootstrap.md`
- `control/project_agent_ops/resources/skill_candidates/repeated_tasks/TASK_model_backed_mcp_activation_and_smoke.md`

## Canonical Owner Outputs

- `control/project_agent_ops/registry/tools/tool_inventory.json` — authoritative activation state for all workspace MCPs
- `control/project_agent_ops/resources/tools_inventory/REFERENCE_mcp_setup.md` — authoritative setup reference

Any task that should update these two files routes through this skill, not through consumer specialists.

## Workflow

1. Vendor the upstream MCP under `vendor/mcp/`.
2. Isolate its runtime inside the vendored surface, not the main workspace runtime.
3. Create a thin launcher under `scripts/mcp/`.
4. Redirect writable logs and caches into workspace-owned paths when needed.
5. Register the MCP in `.codex/config.toml`.
6. Register the MCP in `.vscode/mcp.json` when VS Code MCP use matters.
7. Update `control/project_agent_ops/registry/tools/tool_inventory.json`.
8. Update `control/project_agent_ops/registry/runtime/session_paths.json` if canonical paths or smoke artifacts are part of the onboarding.
9. Run light smoke first:
   - executable or runtime exists
   - help, boot, or tool-list surface works
10. Run heavy smoke second for model-backed MCPs:
    - one real inference or representative tool call
11. Only mark the MCP active after canonical smoke evidence exists.
12. For ongoing maintenance: run `checklists/mcp_inventory_sync_checklist.md` to detect drift before reporting or reconciling.

## Preferred Output Surface

- launcher: `scripts/mcp/`
- vendor source: `vendor/mcp/<name>/`
- canonical inventory: `control/project_agent_ops/registry/tools/tool_inventory.json`
- canonical smoke evidence: `control/project_agent_ops/resources/smoke/`
- canonical setup reference: `control/project_agent_ops/resources/tools_inventory/REFERENCE_mcp_setup.md`

## Outputs

- vendored MCP source
- isolated runtime under the vendored surface
- thin launcher under `scripts/mcp/`
- config entries in `.codex/config.toml` and optionally `.vscode/mcp.json`
- inventory and session-registry updates
- bounded smoke evidence

## Known Good Fit

- Python MCPs that need dedicated venvs
- model-backed MCPs with cache redirection and post-install steps
- TypeScript MCPs that need vendored node_modules and a compiled entrypoint
- ongoing inventory/setup drift detection and reconciliation for already-onboarded MCPs
