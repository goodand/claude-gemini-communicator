# Tool Owner Family Map

## Purpose

This map defines which skills belong to the owner layer and which belong to the consumer layer for workspace MCP lifecycle work.

Use it when a task could be confused for either ownership or consumption, or when a reviewer asks "which skill owns MCP X?"

---

## Owner Layer

| Skill | Role | Canonical Outputs |
|---|---|---|
| `vendored-mcp-onboarding` | **Owner-family entrypoint** — vendored third-party MCP lifecycle integrity | `tool_inventory.json`, `REFERENCE_mcp_setup.md` |

**Primary charter**: the `vendor → launcher → config → inventory → smoke` path for vendored third-party MCPs under `vendor/mcp/`. Currently vendored: `imagesorcery-mcp`, `macos-ocr-mcp`, `paddleocr-mcp`, `tigaweb-image-edit-sample-mcp`.

Non-vendored workspace tools (e.g., `filesystem`, `exiftool`, `agent-task-manager`, `conport`) and system skills (e.g., `imagegen`) route lifecycle questions here by convention until a separate owner surface is established. They are not in the primary charter.

There is currently one owner-family skill. Additional owner skills should only be created when recurring evidence shows a stable workload split (see strategy reference for details).

---

## Consumer Layer

These skills consume MCPs or adjacent tool surfaces but do not own inventory, registration, or activation state.

The examples below are illustrative, not exhaustive. Any skill that consumes an MCP or adjacent tool surface as input without managing its installation, launcher, or inventory record is a consumer specialist.

| Skill | Primary Lifecycle Surface | Supporting Tool Surface | Lifecycle Routing Status | What It Does Not Own |
|---|---|---|---|---|
| `macos-ocr-evidence` | `macos-ocr-mcp` | — | `canonical` | MCP inventory, launcher, or activation state |
| `component-split-ocr-review` | `macos-ocr-mcp` | `scripts/build_component_split_ocr_report.py` | `canonical` | MCP registration, config, or setup docs |
| `openai-image-caption-validation` | — | `scripts/caption_images_openai.py` | `consumer-only` | tool lifecycle, launcher wiring, inventory |
| `object-isolation-correction` | `imagesorcery-mcp` | `imagegen` (system skill — see note) | `canonical` | MCP registration or inventory writes |
| `image-job-dispatcher` | `agent-task-manager`, `conport` | — | `temporarily routed adjacent` | launcher config or activation state |
| `image-commit-manager` | `filesystem` MCP, `exiftool` MCP | — | `temporarily routed adjacent` | MCP lifecycle, launcher wiring, or inventory writes |

**Lifecycle Routing Status legend** — describes the ownership status of the *Primary Lifecycle Surface* for each row, not the skill itself:
- `canonical` — Primary Lifecycle Surface is a vendored third-party MCP under `vendor/mcp/`; lifecycle canonically owned by `vendored-mcp-onboarding`
- `temporarily routed adjacent` — Primary MCP Surface is a global or non-vendored tool; lifecycle routes here by convention, not by primary charter
- `consumer-only` — no vendored MCP dependency; MCP lifecycle is not relevant for this row

**Note on `object-isolation-correction` Supporting Surface:** `imagegen` is a Codex system skill, not a vendored MCP. It is tracked in `tool_inventory.json` under `workspace_skills.system_skill_notes`. Its lifecycle does not route through the `vendor → launcher → config → inventory → smoke` path. Listed here for surface fidelity, not as a vendored lifecycle concern.

**Open issue (`BACKLOG_setup_ref_system_skill_cross_link`):** cross-link from `REFERENCE_mcp_setup.md` to `tool_inventory.json` `system_skill_notes` for `imagegen` and other system skills remains backlog. The inventory has the record; the setup reference does not yet point to it. Until this is closed, treat `REFERENCE_mcp_setup.md` as incomplete for system skill coverage.

Consumer specialists may depend on MCPs being active. If an MCP they depend on is not active or correctly registered, that problem routes to `vendored-mcp-onboarding`, not to the consumer skill.

---

## Routing Decision Tree

```
Task involves a tool lifecycle surface?
│
├── Is the surface a vendored MCP under vendor/mcp/ AND the task touches launcher, config, inventory, or smoke?
│       └── → vendored-mcp-onboarding  (primary charter, Lifecycle Routing Status: canonical)
│
├── Is the surface a non-vendored adjacent tool or system skill (filesystem, exiftool, agent-task-manager, conport, imagegen)?
│       └── → vendored-mcp-onboarding  (temporarily routed adjacent, not primary charter)
│
└── Is the task about using a tool's output in a workflow? (Lifecycle Routing Status: consumer-only)
        ├── OCR text evidence?
        │       └── → macos-ocr-evidence
        ├── Caption generation or validation?
        │       └── → openai-image-caption-validation
        ├── Component split or review?
        │       └── → component-split-ocr-review
        └── Other pipeline / experiment logic?
                └── → respective pipeline skill
```

---

## Policy

- Consumer specialists do not write to `tool_inventory.json` or `REFERENCE_mcp_setup.md`.
- If a consumer specialist finds that an MCP is broken, it surfaces the finding but does not reconcile inventory. Reconciliation goes to the owner skill.
- Creating new owner skills should wait for repeated evidence of a stable split in workload. Until then, one owner entrypoint is preferable to premature fragmentation.

---

## Owner vs Specialist Self-Check

Use these verb and noun tests before assigning a skill to the owner family or the consumer layer.

### Verb signal

| If the skill's core verbs are… | Likely role |
|---|---|
| orchestrate, route, reconcile, maintain, normalize, dispatch, audit, verify, align | owner candidate |
| run, extract, export, build, render, apply, generate, validate | specialist candidate |

Verb alone is not sufficient. A skill with `reconcile` in its description is still a specialist if it reconciles within a single pipeline stage, not across the canonical output surfaces.

### Noun boundary test

An owner candidate must answer yes to both:

1. Does the skill write to or gatekeep at least one canonical output (`tool_inventory.json` or `REFERENCE_mcp_setup.md`)?
2. Is the noun scope — the thing being owned — a **vendored third-party MCP** under `vendor/mcp/`?

If the noun is a global tool (`filesystem`, `exiftool`), a non-vendored service (`agent-task-manager`, `conport`), or a system skill (`imagegen`, `taskmaster`), the skill routes here by convention but is **not** in the primary owner charter.

### Quick pre-routing check

Apply in order — stop at the first match:

1. **Is the primary surface a vendored MCP under `vendor/mcp/`?**
   - Yes → `canonical`. Proceed here only if the task also touches launcher, config, inventory, setup, or smoke.
   - If the task only uses the MCP's output, continue to step 3.
2. **Is the primary surface a non-vendored adjacent tool or system skill** (e.g., `filesystem`, `exiftool`, `agent-task-manager`, `conport`, `imagegen`)**?**
   - Yes → `temporarily routed adjacent`, but **only if the task also touches launcher, config, inventory, setup, or smoke for that surface**. Route here by convention, not primary charter.
   - If the task only uses that surface's output, continue to step 3.
3. **If the task only uses tool output and does not touch any lifecycle surface:**
   - Task is `consumer-only`. Route to the relevant consumer specialist, not here.

### Drift prevention — check before finalizing any change to this document set

1. **YAML trigger verbs changed?** — if yes, verify that the body, family map, and Routing Decision Tree still match the narrowed verb
2. **Noun boundary widened beyond vendored third-party MCP?** — if yes, add the surface as `temporarily routed adjacent` in the family map, not as `canonical`
3. **Routing tree still matches the family-map legend?** — verify that every `Lifecycle Routing Status` value in the consumer table has a corresponding branch or label in the decision tree
