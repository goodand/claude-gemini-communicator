# Troubleshooting

## No clear issue label

Symptom:

- the source image exists, but the correction path is still ambiguous

Fix:

- choose the visible failure mode first
- if the main problem is multiple bundled objects or wrong target selection, use `merged_objects`, `split_decision_needed`, or `wrong_target_selected`
- if the main problem is visual damage in the current cutout, use `missing_object_part` or `edge_artifact`

## Source image missing

Symptom:

- the packet script fails before writing output

Fix:

- confirm the absolute path to `--source-image`
- do not use this skill before PPT extraction or screenshot capture has produced a real local image

## Current result is optional, but route is still vague

Symptom:

- there is no `--current-result`, and the packet is too generic

Fix:

- provide `--target-description`
- give at least one precise issue label
- if the current output does not exist yet, bias toward `imagesorcery-first` for target selection and split decisions

## Wrong route chosen

Symptom:

- the packet recommends `imagegen-first`, but the problem is really a deterministic boundary problem

Fix:

- use `merged_objects`, `split_decision_needed`, `wrong_target_selected`, or `text_grounding_needed`
- those labels should bias the route back toward `imagesorcery-first`

## Too much prompt prose

Symptom:

- the correction packet contains a long prompt but still does not clarify the next tool call

Fix:

- keep the packet bounded
- always preserve:
  - route
  - issue list
  - target description
  - recommended next tool surface
- treat the prompt as a supplement, not the source of truth

## Worker fails with `ModuleNotFoundError: fastmcp`

Symptom:

- the packet exists, but the worker fails before contacting ImageSorcery

Fix:

- run the worker with the vendored ImageSorcery interpreter:
  - `vendor/mcp/imagesorcery-mcp/.venv/bin/python`
  - or `vendor/mcp/imagesorcery-mcp/venv/bin/python`
- do not assume the repo root `.venv` contains `fastmcp`

## Worker cannot start the ImageSorcery launcher

Symptom:

- the worker fails with `PermissionError` while opening `scripts/mcp/start-imagesorcery-mcp.sh`

Fix:

- invoke the launcher through `bash` instead of assuming the shell script itself is executable
- the current worker already does this automatically; if the error reappears, check whether the launcher path drifted

## Alpha split finds only one component

Symptom:

- the source is a transparent PNG, but the worker still reports one large component

Fix:

- confirm that the objects are actually disconnected in the alpha channel, not just visually separated by color
- lower `--alpha-threshold` only if the foreground uses very faint alpha
- reduce `--min-pixels` if the dropped objects are very small
- if the image is really one connected alpha surface, let ImageSorcery fallback handle the next step

## Alpha split produces too many tiny fragments

Symptom:

- the worker exports many meaningless specks instead of usable object crops

Fix:

- increase `--min-pixels`
- if tiny fragments are normal for the asset, keep alpha split only as an inspection aid and rely on ImageSorcery or later review for the actual target choice

## ImageSorcery fallback returns zero matches

Symptom:

- the worker reached ImageSorcery, but `find` or `detect` returned no usable crops

Fix:

- if `target_description` is too specific, simplify it before retrying
- if the target is not a standard object category, remove `target_description` and let `detect` return generic detections
- if the real next step is visual cleanup rather than object discovery, use the generated imagegen request instead of retrying the same detection path

## `find` works, but geometry is unavailable

Symptom:

- `find` succeeds only when `return_geometry=False`, or the geometry request fails upstream

Fix:

- treat `find` as a text-guided bbox selector in this workspace
- use `detect` when segmentation masks are required
- if bbox isolation is still not good enough, rely on the generated imagegen request for the cleanup pass

## imagegen request exists, but no final edit was executed

Symptom:

- the worker finished, but there is only an `IMAGEGEN_REQUEST.md/json` artifact

Fix:

- this is expected
- the worker prepares a bounded request because built-in `imagegen` is not directly callable from a plain local Python script
- use the generated request artifact as the next-step handoff for an agent or skill that can execute the edit

## OCR Should Really Come Next

Symptom:

- the correction packet is being used when the real blocker is unreadable text

Fix:

- if the object boundary is already acceptable and the question is only about text, switch to `macos-ocr-evidence`
- use this skill only when isolation quality itself is the problem
