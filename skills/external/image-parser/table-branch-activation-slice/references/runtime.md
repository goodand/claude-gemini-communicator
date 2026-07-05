# Runtime

## Canonical Operating Pattern

Treat the table branch as inactive until one bounded activation slice is complete in this exact order:

1. A reviewed triage selection decides one of `use_full_image`, `use_reviewed_crop`, `not_a_table_candidate`, or `needs_manual_audit` per source image and writes `control/project_domain/resources/manifests/phase0_table_triage_selection.jsonl`.
2. `paddleocr-mcp` full boot smoke writes `control/project_agent_ops/resources/smoke/SMOKETEST_paddleocr_mcp_boot-atYYYY-MM-DD-HH-MM.md`.
3. `PP-StructureV3` real-image smoke runs only on `1` to `2` triage-approved surfaces and, in the current bounded example, writes:
   - `control/project_domain/resources/manifests/phase0_paddleocr_table_parse_smoke_at2026_03_28.json`
   - `control/project_domain/resources/manifests/phase0_paddleocr_table_parse_raw_at2026_03_28.json`
   - `control/project_domain/resources/reports/REPORT_phase0_table_parser_smoke-at2026-03-28-01-19.md`
4. Canonical normalization maps raw parser output into the project `Table -> Row -> Cell` schema and, in the current bounded example, writes `control/project_domain/resources/manifests/phase0_paddleocr_table_parse_normalized_at2026_03_28.json`.
5. The read-only wrapper surface comes only after normalization, exposes `get_tables(document_id)`, `get_table_rows(table_id)`, and `get_cells(table_id)`, and is implemented by:
   - `control/project_domain/resources/specs/contracts/table_branch_wrapper_surface.contract.json`
   - `scripts/table_branch_wrapper_lib.py`
   - `scripts/test_table_branch_wrapper_lib.py`
6. Bounded downstream consumer smoke proves wrapper consumption over normalized output and writes:
   - `control/project_domain/resources/manifests/phase0_table_wrapper_consumer_smoke_atYYYY_MM_DD.json`
   - `control/project_domain/resources/reports/REPORT_phase0_table_wrapper_consumer_smoke-atYYYY-MM-DD-HH-MM.md`

## Activation Rules

- Step 0 is mandatory because automatic crop fanout can be mechanically valid while still semantically wrong.
- Prefer the full image unless triage explicitly selects a reviewed crop.
- Keep parser smoke bounded to `1` to `2` real PPT-extracted table images.
- The wrapper surface is read-only and must read normalized manifests, not raw parser responses.
- Do not run wrapper implementation or downstream consumer smoke ahead of normalization success.

## Canonical Artifact Families

- selection manifest: `control/project_domain/resources/manifests/phase0_table_triage_selection.jsonl`
- current bounded parser smoke artifacts: `control/project_domain/resources/manifests/phase0_paddleocr_table_parse_smoke_at2026_03_28.json`, `control/project_domain/resources/manifests/phase0_paddleocr_table_parse_raw_at2026_03_28.json`
- current bounded normalized artifact: `control/project_domain/resources/manifests/phase0_paddleocr_table_parse_normalized_at2026_03_28.json`
- bounded consumer manifest: `control/project_domain/resources/manifests/phase0_table_wrapper_consumer_smoke_atYYYY_MM_DD.json`
- parser and consumer reports: `control/project_domain/resources/reports/REPORT_phase0_table_parser_smoke-atYYYY-MM-DD-HH-MM.md`, `control/project_domain/resources/reports/REPORT_phase0_table_wrapper_consumer_smoke-atYYYY-MM-DD-HH-MM.md`
- boot smoke evidence: `control/project_agent_ops/resources/smoke/SMOKETEST_paddleocr_mcp_boot-atYYYY-MM-DD-HH-MM.md`
- wrapper contract and implementation: `control/project_domain/resources/specs/contracts/table_branch_wrapper_surface.contract.json`, `scripts/table_branch_wrapper_lib.py`, `scripts/test_table_branch_wrapper_lib.py`

## Stop Boundary

This runtime sidecar stops at one bounded consumer-ready slice.

It does not define batch rollout, worksheet export, or row-level RAG activation. If normalization fails, the branch remains inactive even if boot smoke or wrapper code already exists.
