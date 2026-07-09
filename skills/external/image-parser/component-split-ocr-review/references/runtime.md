# Runtime

## Canonical Command

```bash
python3 skills/component-split-ocr-review/scripts/build_component_split_ocr_report.py \
  --image-path control/project_domain/resources/pptx_jobs/02_1/media/image11.png
```

## Recommended Runtime

If the default interpreter is missing image-processing dependencies, set `IMAGESORCERY_PYTHON` to any compatible runtime that already has the ImageSorcery-side packages available.
Keep the concrete interpreter resolution in the shell or launcher layer rather than this document.

Then run:

```bash
"$IMAGESORCERY_PYTHON" -B \
  skills/component-split-ocr-review/scripts/build_component_split_ocr_report.py \
  --image-path control/project_domain/resources/pptx_jobs/02_1/media/image11.png
```

## Input Notes

- `--image-path` is required.
- `--output-root` defaults to `control/project_domain/archive/component_split_ocr/`.
- `--alpha-threshold`, `--min-pixels`, `--padding`, and `--min-components-for-success` are passthrough tuning knobs for difficult images.

## Output Shape

The wrapper forwards to the shared builder and prints the generated package JSON.

Expected artifact set under the bounded output directory:

- `COMPONENT_SPLIT_OCR_REPORT.md`
- `COMPONENT_SPLIT_OCR_REPORT.json`
- `alpha_components/*.png`
- `component_ocr/*_OCR_RESULT.json`

## Interpretation

- `alpha_component_count > 1` means the image had mechanically separable alpha-connected regions.
- This does **not** mean every component is semantically meaningful.
- `ocr_status=no_text` is normal for icons, decorative fragments, or empty crops.
- Review the markdown surface before using any component downstream.
