# dependency-slice-planner runtime_overlay validation

- generated_at: `2026-03-19T14:24:52+09:00`
- input_runtime_overlay: `dependency-slice-planner/references/runtime-overlay-invalid-sample-at2026-03-19-14-14.json`
- status: `invalid`
- error_count: `6`

## Errors

- unobserved_path_count must be non-negative int
- unobserved_paths must contain non-empty strings
- runtime_overlays[1].overlay_id must be non-empty str
- runtime_overlays[1].root_path must be non-empty str
- runtime_overlays[1].observed_runtime_edges must be list[str]
- runtime_overlays[1].reason must be non-empty str
