# MCP Inventory Sync Checklist

## Purpose

One-pass checklist for verifying that a workspace MCP's launcher, config, inventory, setup reference, and smoke evidence are all aligned.

Run this checklist:
- after a new MCP is onboarded
- when an existing MCP's activation state may have drifted
- before marking any MCP `active` in `tool_inventory.json`
- when a consumer skill reports unexpected behavior from an MCP

---

## MCP Name: _______________

## Date: _______________

## Primary Lifecycle Surface: _______________

## Supporting Tool Surface(s): _______________ *(write `—` if none; used by Section 8 system-skill gate)*

---

## Section 1 — Vendor Runtime

- [ ] Vendor source exists at `vendor/mcp/<name>/`
- [ ] Runtime isolation is confirmed (dedicated venv, uv project, or node_modules under vendor path)
- [ ] No dependencies installed into main workspace runtime

---

## Section 2 — Launcher

- [ ] Launcher exists at `scripts/mcp/<name>` (or `scripts/mcp/<name>.sh`)
- [ ] Launcher is executable
- [ ] Launcher correctly points to the vendored runtime, not main workspace runtime

---

## Section 3 — Config Registration

- [ ] `.codex/config.toml` has an entry for this MCP
- [ ] `.vscode/mcp.json` has an entry (if VS Code MCP use is intended)
- [ ] Config entry names match what is recorded in `tool_inventory.json`
- [ ] Adjacent skill doc audit: any consumer skills that reference this MCP in their SKILL.md (`Do Not Use This Skill When` or `Not Owned Here`) still reflect the current launcher, config, and inventory state — cross-check `.codex/config.toml`, `.vscode/mcp.json`, `tool_inventory.json`, `REFERENCE_mcp_setup.md`, and the relevant `skills/*/SKILL.md` files together

---

## Section 4 — Inventory Record

- [ ] `control/project_agent_ops/registry/tools/tool_inventory.json` has a record for this MCP
- [ ] Activation level accurately reflects the current state (select exactly one):
  - Current level: `_______` ← fill in one of: `registered` / `launcher-wired` / `boot-verified` / `heavy-smoke-verified` / `active`
    - `registered` — config only, runtime/launcher not confirmed
    - `launcher-wired` — launcher + runtime exist, not smoke-tested
    - `boot-verified` — light smoke passed
    - `heavy-smoke-verified` — one real call confirmed
    - `active` — all seven surfaces aligned, smoke evidence exists
- [ ] No stale or outdated paths in the inventory record

---

## Section 5 — Setup Reference

- [ ] `control/project_agent_ops/resources/tools_inventory/REFERENCE_mcp_setup.md` documents this MCP
- [ ] Setup reference reflects current launcher path and vendor location
- [ ] Setup reference reflects current activation level

---

## Section 6 — Smoke Evidence

- [ ] Smoke evidence file exists in `control/project_agent_ops/resources/smoke/`
- [ ] Light smoke evidence: tool executable, help/tool-list surface works
- [ ] Heavy smoke evidence (for model-backed MCPs): one real inference or representative call recorded
- [ ] Evidence is dated; re-run if more than 30 days old and state is unknown

---

## Section 7 — Drift Summary

List any gaps found above:

| Surface | Gap Found | Action Taken |
|---|---|---|
| Vendor runtime | | |
| Launcher | | |
| Codex config | | |
| VS Code config | | |
| Inventory record | | |
| Setup reference | | |
| Smoke evidence | | |
| Adjacent skill docs (`skills/*/SKILL.md`) | | |

---

## Section 8 — Final Gate

- [ ] All gaps in Section 7 are resolved or explicitly deferred with a reason
- [ ] `tool_inventory.json` updated to reflect current state
- [ ] `REFERENCE_mcp_setup.md` updated to reflect current state
- [ ] If activation level changed: reason is recorded in the inventory record
- [ ] **System skill coverage check** *(skip if Supporting Tool Surface contains no system skills)*: if the primary lifecycle surface or its adjacent workflow depends on a system skill (e.g., `imagegen`), confirm whether `REFERENCE_mcp_setup.md` cross-links `tool_inventory.json` `workspace_skills.system_skill_notes` — if not, record as partial coverage in the Notes section and defer as backlog item `BACKLOG_setup_ref_system_skill_cross_link`

**Result (select exactly one):**

Final activation level recorded: `_______` ← fill in one of: `registered` / `launcher-wired` / `boot-verified` / `heavy-smoke-verified` / `active`

Requires follow-up: yes / no — if yes, describe: _______________

---

## Notes

_Record any observations, deferred items, or edge cases here._

---

## Routing Reminder

- If gaps were found because a consumer skill reported a problem: confirm fix with consumer skill owner after inventory is updated.
- Consumer specialists do not update `tool_inventory.json` or `REFERENCE_mcp_setup.md`. All writes go through `vendored-mcp-onboarding`.
