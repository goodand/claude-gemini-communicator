# Smoke Command Capture — Async Migration Verify

- recorded_at: `2026-04-08T00:18:20+09:00`
- status: `valid`
- label: `async-migration-scan-dead-imports`
- expected_status: `valid`

## Command

```bash
python3 scripts/test_scan_dead_imports.py
```

## Result

- exit_code: `0`
- stderr: empty
- smoke passed through the dead-import scan regression test

## Interpretation

- representative migration-residue scanner test is runnable
- scanner baseline for bare + node-prefixed alias residue remains green
