# Runtime

## Purpose

Capture the practical command surface for building an Obsidian-friendly caption review.

## Canonical Script

- `scripts/build_obsidian_caption_review.py`

## Common Modes

### 1. Canonical Copied-Asset Review

This is the default and preferred mode. Use it when the review should remain portable inside a bounded review directory.

```bash
python3 skills/obsidian-caption-review-builder/scripts/build_obsidian_caption_review.py \
  --ledger-glob "control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_ppt*.json" \
  --output "control/project_domain/resources/reports/REVIEW_example-atYYYY-MM-DD-HH-MM.md" \
  --review-title "Phase 1 Caption Review"
```

If you need a stable explicit asset path, override it:

```bash
python3 skills/obsidian-caption-review-builder/scripts/build_obsidian_caption_review.py \
  --ledger-glob "control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_ppt*.json" \
  --output "control/project_domain/resources/reports/REVIEW_example-atYYYY-MM-DD-HH-MM.md" \
  --review-title "Phase 1 Caption Review" \
  --mode canonical-copy \
  --asset-dir "control/project_domain/resources/reports/review_assets/example"
```

### 2. Direct Relative Image Paths

Use only when the markdown file and original images stay in a stable relative layout.

```bash
python3 skills/obsidian-caption-review-builder/scripts/build_obsidian_caption_review.py \
  --ledger-glob "control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_ppt*.json" \
  --output "control/project_domain/resources/reports/REVIEW_example-atYYYY-MM-DD-HH-MM.md" \
  --review-title "Phase 1 Caption Review" \
  --mode direct
```

### 3. Vault-Prefixed Embed Paths

Compatibility mode only. Use when images are already mirrored into a vault path and the markdown should point there directly. Do not treat this as the canonical run surface.

```bash
python3 skills/obsidian-caption-review-builder/scripts/build_obsidian_caption_review.py \
  --ledger-glob "control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_caption_10w_*.json" \
  --output "control/project_domain/resources/reports/REVIEW_phase1_caption_10w_obsidian_caption_review-atYYYY-MM-DD-HH-MM.md" \
  --review-title "Phase 1 Caption 10w Review" \
  --mode prefixed \
  --source-root "control/project_domain/resources/pptx_jobs" \
  --embed-prefix "img/pptx_jobs"
```

## Output Expectation

The markdown review should include:

- dataset grouping
- image embed
- caption blockquote
- alt text blockquote
- filename candidate
- source ledger trace

## Notes

- Exclude smoke ledgers unless the review explicitly targets smoke output.
- Keep one review surface per bounded experiment or batch.
- Keep the canonical review artifact under `control/project_domain/resources/reports/`.
- The skill-local wrapper defaults to `--mode canonical-copy`.
- If the review becomes a decision artifact, promote only the decision result, not the full vault surface.

## Operator Handoff

If the resulting markdown should be reviewed or edited inside VS Code instead of Obsidian:

1. keep this skill responsible only for producing the markdown review surface
2. hand that markdown artifact to `skills/vscode-fabriqa-foam-workflow/`
3. treat `vscode-fabriqa-foam-workflow` as the downstream operator surface for `fabriqa`, `Text Editor`, and Foam-side navigation

Do not expand this skill into VS Code editor-mode orchestration. That boundary belongs to the downstream operator skill.
