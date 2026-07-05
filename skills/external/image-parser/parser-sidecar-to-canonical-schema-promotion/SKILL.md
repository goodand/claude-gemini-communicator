---
name: parser-sidecar-to-canonical-schema-promotion
description: Promote a bounded parser raw sidecar artifact into the canonical Table -> Row -> Cell schema. Use when a parser MCP returned markdown plus nested JSON sidecars and the project must normalize that output before any downstream wrapper, worksheet, or RAG consumer reads it.
---

# Parser Sidecar To Canonical Schema Promotion

## Overview

Use this skill to convert one bounded raw parser sidecar into the project's canonical normalized table shape:

- raw parser sidecar JSON
- recovered PPT provenance
- canonical `Table -> Row -> Cell` JSON
- machine-readable promotion result artifact

This skill exists so downstream consumers do not read parser-native payloads directly once a canonical record is available.
It also owns the canonical Apple Vision helper-sidecar location. That helper now performs an explicit SDK and OS probe, emits live `RecognizeDocumentsRequest` document and table structure JSON when available, and returns structured unsupported JSON when the local environment cannot run that path.

## Use This Skill When

- one raw parser sidecar JSON already exists
- the parser returned markdown plus nested detailed JSON in `content[*].text`
- the next consumer expects `Table -> Row -> Cell`
- provenance from the source image and slide manifest must be preserved
- you need live Apple Vision document or table structure hints as helper-sidecar evidence before canonical promotion logic consumes them

## Do Not Use This Skill When

- the current task is booting or smoking the parser MCP itself
- the current task is downstream read-only wrapper consumption
- the current task is worksheet export, row-level RAG, or caption rerun
- no bounded raw parser artifact exists yet

## Required Inputs

- one `--raw-sidecar-json`
- optional `--normalized-output-json`
- optional `--output-json`
- optional `--image-path` override
- optional `--table-id`
- optional `--parser-backend`

## Script

- `scripts/promote_parser_sidecar_to_canonical_schema.py`
- `scripts/macos_table_structure_helper.swift`
- `scripts/run_table_parser_comparison.py`
- `scripts/run_table_merge_candidate_builder.py`

## References

- `knowledge_bases/parser-sidecar-to-canonical-schema-promotion-knowledge-base-at2026-03-28-02-05.md`
- `references/alternate_closure_routes.md`
- `references/runtime.md`
- `references/troubleshooting.md`

## Workflow

1. Confirm a bounded raw parser sidecar already exists.
2. If Apple Vision table skeleton hints are needed, run the skill-local helper script from this skill's `scripts/` directory.
3. Let the helper perform its own SDK and OS probe; treat `unsupported_in_current_sdk` and `not_available_in_current_os` as bounded helper outcomes rather than parser crashes.
4. If the preferred helper backend fails, check whether an alternate normalized parser surface or single-source fallback can still close the bounded route before excluding the image.
5. Run the skill-local wrapper, not a handwritten normalization snippet.
6. Recover source image provenance from the raw sidecar or an explicit override.
7. Promote only the first stable table payload into canonical `Table -> Row -> Cell`.
8. Write both the canonical normalized JSON and the promotion result JSON.
9. Treat the normalized output as the new source of truth for downstream wrapper consumers.

## Preferred Output Surface

- canonical normalized output: `control/project_domain/resources/manifests/`
- machine-readable promotion result: `control/project_agent_ops/resources/smoke/artifacts/`

## Outputs

- one canonical normalized JSON
- one promotion result JSON
- optional Apple helper sidecar JSON with either live Vision document and table structure output or an explicit unsupported status
- optional parser comparison manifest between normalized Apple and Paddle outputs
- optional merged candidate manifest for review-stage downstream use

## Known Good Fit

- bounded PaddleOCR `PP-StructureV3` sidecar artifacts
- parser backends that place detailed table payloads into nested text JSON
- early table-branch activation where normalization must happen before wrappers or consumers
- Apple Vision helper-sidecar runs that need document or table structure hints before canonical normalization consumes them
- bounded dual-parser comparison before designing a review-stage merged candidate
- structure-first plus text-repair candidate building before any wider auto-merge policy
- bounded single-source fallback closure when one helper backend fails but another normalized parser surface still supports parser-enriched or reviewed-component downstream use

## Ownership Rule

- Apple Vision document-structure helper ownership belongs here, not in generic OCR-only skills.
- The helper script should live under this skill's `scripts/` directory and produce helper-sidecar output only; it must not perform canonical normalization itself.
- Generic OCR skills may call or reference the helper, but they do not own its implementation path.

## Not Owned Here

- parser execution or MCP boot smoke
- read-only table wrapper consumption
- worksheet export
- row-level RAG indexing
- mutation of the source image
