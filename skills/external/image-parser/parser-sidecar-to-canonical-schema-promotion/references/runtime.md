# Runtime

## Canonical Command

```bash
python3 skills/parser-sidecar-to-canonical-schema-promotion/scripts/promote_parser_sidecar_to_canonical_schema.py \
  --raw-sidecar-json control/project_domain/resources/manifests/phase0_paddleocr_table_parse_raw_at2026_03_28.json
```

## Apple Helper Location

The Apple Vision document-structure helper is owned by this skill and lives here:

```bash
skills/parser-sidecar-to-canonical-schema-promotion/scripts/macos_table_structure_helper.swift
```

Current bounded command shape:

```bash
"${SWIFT_EXEC:-xcrun swift}" "${APPLE_VISION_HELPER:-skills/parser-sidecar-to-canonical-schema-promotion/scripts/macos_table_structure_helper.swift}" \
  --input "$SOURCE_IMAGE" \
  --output "$HELPER_SIDECAR_JSON"
```

Current status:

- location fixed
- CLI contract fixed
- helper ownership fixed under the table-structure promotion skill
- explicit local SDK compile probe wired
- explicit local OS availability probe wired
- live `RecognizeDocumentsRequest` extraction has been locally validated on a recent macOS/Xcode stack
- helper can emit real `documents[*].tables[*].cells[*]` sidecar JSON when the local Vision stack recognizes a table
- helper can also complete with `status=completed` and `table_count=0` when the image is readable but Vision does not detect a table
- current promotion wrapper now ingests helper-sidecar output through the same `--raw-sidecar-json` entry point used for bounded Paddle sidecars

## Input Notes

- `--raw-sidecar-json` is required.
- `--image-path` is optional and only needed when the raw sidecar has missing or stale provenance.
- `--normalized-output-json` defaults under `control/project_domain/resources/manifests/`.
- `--output-json` defaults under `control/project_agent_ops/resources/smoke/artifacts/`.

For smoke or contract testing, prefer explicit output paths so an already-promoted canonical manifest is not overwritten accidentally.
The current promotion CLI accepts helper-sidecar JSON through the same `--raw-sidecar-json` flag.
The Apple helper always emits JSON to stdout and also writes the same payload to `--output` when provided.

Example helper-to-canonical flow:

```bash
"${SWIFT_EXEC:-xcrun swift}" "${APPLE_VISION_HELPER:-skills/parser-sidecar-to-canonical-schema-promotion/scripts/macos_table_structure_helper.swift}" \
  --input "$SOURCE_IMAGE" \
  --output "${TMPDIR:-/tmp}/apple_helper_sidecar.json"

python3 skills/parser-sidecar-to-canonical-schema-promotion/scripts/promote_parser_sidecar_to_canonical_schema.py \
  --raw-sidecar-json "${TMPDIR:-/tmp}/apple_helper_sidecar.json"
```

Example dual-parser comparison flow:

```bash
python3 scripts/run_table_parser_comparison.py \
  --apple-normalized-json control/project_domain/resources/manifests/phase0_apple_document_structure_normalized_at2026_03_28.json \
  --paddle-normalized-json control/project_domain/resources/manifests/phase0_paddleocr_table_parse_normalized_at2026_03_28.json \
  --output-json control/project_domain/resources/manifests/phase0_table_parser_comparison_at2026_03_28.json
```

Example merged candidate flow:

```bash
python3 scripts/run_table_merge_candidate_builder.py \
  --apple-normalized-json control/project_domain/resources/manifests/phase0_apple_document_structure_normalized_at2026_03_28.json \
  --paddle-normalized-json control/project_domain/resources/manifests/phase0_paddleocr_table_parse_normalized_at2026_03_28.json \
  --comparison-json control/project_domain/resources/manifests/phase0_table_parser_comparison_at2026_03_28.json \
  --output-json control/project_domain/resources/manifests/phase0_table_merge_candidate_at2026_03_28.json
```

## Default Promotion Behavior

- recover the source image path from `raw_sidecar.image_path`
- recover `slide_usages` from the adjacent PPT extraction `manifest.json`
- extract the first stable table payload from the raw parser sidecar
- write canonical `Table -> Row -> Cell` JSON

## Output Shape

Expected promotion result JSON fields:

- `experiment`
- `raw_sidecar_json`
- `image_path`
- `manifest_path`
- `normalized_status`
- `normalized_output_json`
- `document_id`
- `page`
- `table_id`
- `row_count`
- `cell_count`
- `parser_backend`

Expected Apple helper JSON fields:

- `status`
- `backend`
- `helper_role`
- `ownership_skill`
- `input_path`
- `output_path`
- `message`
- `probe`
- `summary` on success
- `documents` on success

## Interpretation

- `normalized_status=completed` means one canonical table record was written.
- `normalized_status=no_table_found` means the raw sidecar did not contain a recoverable table payload.
- Downstream consumers should read the normalized JSON, not the raw sidecar, once promotion succeeds.
- Apple helper output is still helper-sidecar only until the promotion path consumes it.
- Apple helper `status=unsupported_in_current_sdk` means the local wrapper could not compile the bounded Vision runner and returned probe details instead.
- Apple helper `status=not_available_in_current_os` means the SDK probe compiled but the current host OS is below the minimum runtime required for `RecognizeDocumentsRequest`.
- dual-parser comparison should happen on canonical normalized outputs only, not on raw Paddle sidecars or raw Apple helper payloads
- merged candidate building should happen on the comparison manifest plus the two canonical normalized tables, not on raw sidecars
- hosted or Linux runners should treat the Apple helper as optional and provide an explicit non-mac fallback instead of assuming `xcrun swift` exists
