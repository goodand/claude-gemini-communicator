# Troubleshooting

## `normalized_status=no_table_found`

Possible causes:

- the raw sidecar has no `<table>...</table>` payload
- the detailed nested JSON did not include `table_res_list`
- the parser output is text-only or layout-only for that image

Action:

- inspect the raw sidecar first
- do not fabricate canonical rows
- keep the branch at raw-sidecar evidence only until a better parser result exists

## Wrong Or Missing Provenance

Possible causes:

- `image_path` inside the raw sidecar is stale
- the adjacent PPT extraction `manifest.json` cannot be found

Action:

- rerun with explicit `--image-path`
- confirm the image sits under a known `pptx_jobs/<job>/media/` surface

## Downstream Consumer Still Reads Raw Output

Cause:

- wrapper or consumer drift after canonical normalization was introduced

Action:

- treat the canonical normalized JSON as the new source of truth
- patch the downstream wrapper, not the normalized artifact

## Multiple Tables In One Raw Artifact

Current boundary:

- this skill promotes only the first stable table payload

Action:

- keep the run bounded
- if a backend starts returning multiple tables reliably, extend the canonical schema and wrapper contract first

## Apple Helper Returns `unsupported_in_current_sdk`

Cause:

- the bounded Vision runner did not compile against the local SDK
- `RecognizeDocumentsRequest` symbols are missing or changed in the active Xcode toolchain

Action:

- do not treat this as a parser failure
- read the `probe` block in the helper JSON first
- keep `paddleocr-mcp` as the active parser path for current table parsing

## Apple Helper Returns `not_available_in_current_os`

Cause:

- the local SDK compiled the helper path, but the current host macOS is below the required runtime level

Action:

- keep the run bounded and record the helper payload as environment evidence
- do not force a fallback normalization from the helper payload
- continue using the active `paddleocr-mcp` path

## Apple Helper Returns `completed` With `table_count=0`

Cause:

- Vision successfully analyzed the image but did not detect a recoverable table surface
- the image may still contain text paragraphs without a stable table grid

Action:

- treat this as a valid helper outcome, not a crash
- compare against `paddleocr-mcp` before concluding the image is non-tabular
- keep the helper output as sidecar evidence only until canonical promotion explicitly consumes it

## Apple Helper Writes JSON But Promotion Returns `no_table_found`

Cause:

- the helper output changed shape and the promotion library no longer matches `documents[*].tables[*].cells[*]`
- the helper returned documents but no populated table cell list

Action:

- inspect `documents[*].tables[*].cells[*]` first
- if cells exist, patch the promotion library instead of bypassing canonical normalization
- if cells do not exist, keep the helper artifact as disagreement evidence only
