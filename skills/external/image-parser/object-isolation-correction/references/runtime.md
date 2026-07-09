# Runtime

## Purpose

Capture the practical command surface for building an object-isolation correction packet and then running the bounded worker.

## Canonical Script

- `scripts/prepare_object_isolation_correction_packet.py`
- `scripts/run_object_isolation_correction_worker.py`

## Canonical Interpreter For The Worker

Use a Python runtime that already contains the ImageSorcery-side dependencies such as `fastmcp`, `Pillow`, and `numpy`.
Set `IMAGESORCERY_PYTHON` to a compatible interpreter in your environment.
If you rely on the repo-local vendored runtime, resolve that path in your shell or launcher instead of hardcoding it into the packet contract.

Then run:

```bash
"$IMAGESORCERY_PYTHON" \
  skills/object-isolation-correction/scripts/run_object_isolation_correction_worker.py \
  --packet-json "$PACKET_JSON" \
  --output-dir "$RUN_DIR"
```

## Common Modes

### 1. Boundary Or Split Problem

Use this when the image bundles multiple objects, the wrong target was selected, or the deterministic boundary is still the first thing to fix.

```bash
python3 skills/object-isolation-correction/scripts/prepare_object_isolation_correction_packet.py \
  --source-image "$SOURCE_IMAGE" \
  --current-result "$CURRENT_RESULT" \
  --issue merged_objects \
  --issue split_decision_needed \
  --target-description "the table only" \
  --output-md "control/project_domain/resources/reports/CORRECTION_object_isolation_example.md"
```

Expected route:

- `imagesorcery-first`

### 2. Visual Damage Or Missing Part

Use this when the current cutout is visually broken and deterministic re-cropping is unlikely to be enough.

```bash
python3 skills/object-isolation-correction/scripts/prepare_object_isolation_correction_packet.py \
  --source-image "$SOURCE_IMAGE" \
  --current-result "$CURRENT_RESULT" \
  --issue missing_object_part \
  --issue edge_artifact \
  --target-description "the product only" \
  --output-md "control/project_domain/resources/reports/CORRECTION_object_isolation_example.md"
```

Expected route:

- `imagegen-first`

### 3. Hybrid Repair

Use this when the main problem is still boundary cleanup, but a model-assisted polish may be needed after deterministic masking.

```bash
python3 skills/object-isolation-correction/scripts/prepare_object_isolation_correction_packet.py \
  --source-image "$SOURCE_IMAGE" \
  --current-result "$CURRENT_RESULT" \
  --issue background_residue \
  --issue transparent_cutout_needed \
  --target-description "the main icon only" \
  --output-md "control/project_domain/resources/reports/CORRECTION_object_isolation_example.md" \
  --output-json "control/project_domain/resources/manifests/object_isolation_correction_example.json"
```

Expected route:

- `hybrid`

## Issue Vocabulary

- `background_residue`
- `missing_object_part`
- `merged_objects`
- `wrong_target_selected`
- `overcrop`
- `undercrop`
- `transparent_cutout_needed`
- `split_decision_needed`
- `text_grounding_needed`
- `edge_artifact`

## Notes

- The packet script does not edit the image. It creates the correction packet that should drive the next retry.
- The worker tries alpha connected-components first when the source already has a useful alpha channel.
- `imagesorcery-first` usually means `find` or `detect` first, followed by `fill` and `crop`.
- `imagegen-first` usually means a multimodal edit request should be prepared first.
- `hybrid` means deterministic masking/cropping first, then model-assisted cleanup if the result still looks wrong.

## Worker Example: Transparent PNG With Separated Objects

Use this when the image already has transparency and the main question is whether alpha split alone is enough.

```bash
"$IMAGESORCERY_PYTHON" \
  skills/object-isolation-correction/scripts/run_object_isolation_correction_worker.py \
  --packet-json "$PACKET_JSON" \
  --output-dir "$RUN_DIR"
```

Expected behavior:

- attempt alpha connected-components first
- if two or more meaningful components are found, export component crops and skip ImageSorcery fallback
- if alpha split is insufficient, fall back to ImageSorcery

## Worker Example: Force ImageSorcery Fallback

Use this when alpha split is not expected to help, or the current image has no useful alpha channel.

```bash
"$IMAGESORCERY_PYTHON" \
  skills/object-isolation-correction/scripts/run_object_isolation_correction_worker.py \
  --packet-json "$PACKET_JSON" \
  --output-dir "$RUN_DIR" \
  --skip-alpha-split
```

Expected behavior:

- skip alpha split
- call `find` when `target_description` exists
- otherwise call `detect`
- write isolated crops and a bounded imagegen request when the route is `hybrid` or `imagegen-first`
