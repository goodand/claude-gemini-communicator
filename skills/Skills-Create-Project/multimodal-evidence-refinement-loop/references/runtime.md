# Runtime

## Purpose

Use this loop when multimodal understanding must improve over repeated passes instead of closing after one caption or one judgment.

## Canonical Layers

Keep these layers separate through the loop:

- `image_evidence`
- `text_judgment`
- `baseline_anchor`
- `machine_truth_manifest`

The image is evidence.
The text is a normalized judgment.
The baseline is a comparison anchor.
The manifest is machine truth.

## Canonical Loop State

The manifest should preserve at least these fields:

- `item_id`
- `pass_index`
- `image_evidence`
- `text_judgment`
- `baseline_anchor`
- `delta_from_baseline`
- `review_state`
- `pending_reasons`
- `next_refinement_focus`

## Canonical Flow

1. Bind one bounded item set and one explicit baseline anchor.
2. Record the current image reading as evidence, not as final policy.
3. Record the current text judgment as a normalized hypothesis.
4. Reinject the image with the current hypothesis and any bounded context needed for refinement.
5. Compare the new reading against the baseline and previous pass.
6. If closure is still incomplete, keep `review_state=pending` and carry forward the next focus.
7. If closure is sufficient, freeze the loop state and hand off to `image-text-cot-review` for review-surface/output normalization.

## Boundary Rule

This skill must not:

- collapse one-pass caption output into final machine truth
- replace the baseline anchor with the latest winner implicitly
- hide unresolved multimodal ambiguity behind missing state
- treat markdown reading order as the loop source of truth
