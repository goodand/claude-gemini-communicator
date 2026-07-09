# Runtime

## Canonical Command

```bash
python3 skills/transparent-component-triage/scripts/classify_alpha_split_batch.py
```

## Recommended Runtime

If the underlying worker needs the ImageSorcery dependency set, point `IMAGESORCERY_PYTHON` at any compatible interpreter.
Resolve the actual interpreter path outside this runtime note so the skill stays portable across local, Docker, and hosted runners.

Then run:

```bash
"$IMAGESORCERY_PYTHON" -B \
  skills/transparent-component-triage/scripts/classify_alpha_split_batch.py
```

## Useful Narrow Smoke

```bash
"$IMAGESORCERY_PYTHON" -B \
  skills/transparent-component-triage/scripts/classify_alpha_split_batch.py \
  --limit 3
```

## Input Notes

- `--input-root` defaults to `control/project_domain/resources/pptx_jobs/`
- `--limit` is useful for smoke runs only
- tuning knobs like `--alpha-threshold`, `--min-pixels`, and `--min-components-for-success` are passthrough classifier settings

## Output Interpretation

- `alpha_split_sufficient` means mechanically sufficient for alpha-only splitting
- it does **not** mean semantically safe for automatic downstream promotion
- `single_component_only` means keep the file on the full-image baseline
- use the report and summary as triage evidence, not as a final approval record
