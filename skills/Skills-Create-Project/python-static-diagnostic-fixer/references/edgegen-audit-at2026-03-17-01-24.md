# python-static-diagnostic-fixer audit summary

- generated_at: `2026-03-17T01:24:52+09:00`
- target: `edge-case-generator/scripts/edgegen.py`
- status: `ok`
- runtime_gate_ok: `True`
- finding_count: `1`

## Runtime Gate

- tool: `py_compile`
- message: py_compile passed

## Findings

- `unused_variable` / `RULE_TYPES`
  - line: `34`
  - evidence: assigned name `RULE_TYPES` is never loaded
  - recommendation: remove it or rename to `_` if intentionally unused
