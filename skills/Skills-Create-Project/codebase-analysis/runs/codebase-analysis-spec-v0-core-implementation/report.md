# Implementation Report: codebase-analysis-spec-v0-core-implementation

## Test Results

- **Tests run**: 25
- **Tests passed**: 25
- **Tests failed**: 0

All 24 original tests continue to pass. 1 new test added as part of Fix 1 validation.

## Semantic Review

- **Semantic review checks**: 10/10 pass

## Review Findings Applied

### Fix 1 (High): CLI 필터가 canonical graph에 적용되지 않음

**Problem**: `main()` called `build_canonical_graph(root)` without passing
`--include-top-level`, `--exclude-top-level`, or `--exclude-dir-name` filter
arguments, so CLI filters silently had no effect on the canonical graph output.

**Fix applied** (`scripts/analyze_codebase.py`, line ~509):
`build_canonical_graph` is now called with `excludes`, `include_top_level_names`,
and `exclude_top_level_names` derived from the CLI arguments via the same
`merge_excluded_dir_names` / `merge_name_filter` helpers used by `build_summary`.

**Test added**: `test_cli_canonical_output_respects_include_filter` — runs the CLI
with `--include-top-level src --canonical-output <dir>` and asserts that `tests/`
file nodes do not appear in `normalized_graph.json` while `src/` nodes do.

---

### Fix 2 (Medium): `from pkg import mod` が `pkg/__init__.py` に誤 resolve される

**Problem**: `extract_imports` passed only `node.module` (e.g. `"src"`) to
`_resolve_module_to_file` for `ast.ImportFrom` nodes. A statement like
`from src import core` would resolve to `src/__init__.py` instead of the
intended `src/core.py`.

**Fix applied** (`scripts/analyze_codebase.py`, `extract_imports` function):
For each `alias` in `node.names`, the code now first attempts to resolve
`module_name + "." + alias.name` (e.g. `"src.core"`). If that resolves to a
file inside the repo, it is used. Only when that fails does the code fall back
to the original `module_name`-only resolution. Relative imports (`level > 0`)
are unchanged and still use the module-only path.

**Test strengthened**: `test_extract_imports_resolves_internal` now explicitly
asserts that the resolved `dst` value is `"file:src/core.py"`, not merely that
some edge exists.

---

### Fix 3 (Low): report.md 작성

This file.

## Done Definition Checklist

| Item | Status |
|------|--------|
| `build_canonical_graph` accepts filter parameters | PASS |
| CLI `--canonical-output` passes filters through | PASS |
| `from pkg import mod` resolves to `pkg/mod.py` when it exists | PASS |
| Fallback to `pkg/__init__.py` when `pkg/mod.py` absent | PASS |
| All original 24 tests continue to pass | PASS |
| 1 new CLI filter test added and passes | PASS |
| `test_extract_imports_resolves_internal` asserts specific `dst` | PASS |
| Coarse summary (`build_summary`) behaviour unchanged | PASS |
| Sidecar evidence routing unchanged | PASS |
| `report.md` present in run directory | PASS |
