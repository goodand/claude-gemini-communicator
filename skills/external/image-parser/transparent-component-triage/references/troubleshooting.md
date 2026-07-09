# Troubleshooting

## Almost Everything Is `single_component_only`

That is not necessarily a failure.
The batch may simply not contain many alpha-separated files.
This skill is conservative by design and should preserve the full-image baseline when separation is weak.

## `alpha_split_sufficient` Count Looks Too High

Inspect the report before trusting it.
Fragment-heavy slides can mechanically produce multiple components without yielding meaningful semantic objects.

## The Wrapper Help Works but Execution Fails

Run the wrapper through the vendored runtime:

```bash
"$IMAGESORCERY_PYTHON" -B \
  skills/transparent-component-triage/scripts/classify_alpha_split_batch.py
```

The classifier delegates to the object-isolation worker, which may require the same vendored environment.

## Per-Image Outputs Exist but the Batch Report Is Misleading

Read the summary JSON and a few per-image worker reports together.
The skill is meant to build a candidate subset, not replace reviewed interpretation.

## You Want to Inspect One File More Closely

Switch to the single-image review skill:

- `skills/component-split-ocr-review`

Do not stretch this batch triage skill into a one-image semantic reviewer.
