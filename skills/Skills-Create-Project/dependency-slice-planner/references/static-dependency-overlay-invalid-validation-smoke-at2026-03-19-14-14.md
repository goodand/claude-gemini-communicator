# dependency-slice-planner static_dependency_overlay validation

- generated_at: `2026-03-19T14:18:41+09:00`
- input_overlay: `dependency-slice-planner/references/static-dependency-overlay-invalid-sample-at2026-03-19-14-14.json`
- status: `invalid`
- error_count: `7`

## Errors

- missing field: overlays[1].anomaly_ledger
- overlays[1].overlay_id must be non-empty str
- overlays[1].root_path must be non-empty str
- overlays[1].source_import_edges must be list[str]
- overlays[1].anomaly_ledger must be list[str]
- overlays[1].reason must be non-empty str
- overlay_count must match len(overlays)
