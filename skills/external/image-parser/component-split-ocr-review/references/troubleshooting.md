# Troubleshooting

## `alpha_component_count` is `0` or `1`

The image may be opaque, effectively single-surface, or not actually separable by alpha.
This skill is review-oriented, so treat that result as evidence and stop rather than forcing semantic isolation here.

## Too Many Tiny Components

This often means fragment-heavy slide exports, antialiased text edges, or decorative shards.
Raise `--min-pixels` first.
If the count stays high, move to a reviewed selection flow rather than trusting the raw count.

## OCR Is Mostly Empty

That is expected for purely visual fragments.
Use the component table as the primary review surface and treat OCR as supporting evidence only.

## Wrapper Works but Full Run Fails with Missing Packages

Run the wrapper with:

```bash
"$IMAGESORCERY_PYTHON" -B \
  skills/component-split-ocr-review/scripts/build_component_split_ocr_report.py \
  --image-path <image>
```

The lightweight wrapper `--help` path should work under plain `python3`, but actual execution may need the vendored runtime.

## Result Looks Mechanically Correct but Semantically Wrong

That is not a bug in this skill by itself.
This skill only exposes alpha-separated evidence and per-component OCR.
Semantic object selection belongs in a reviewed downstream step.
