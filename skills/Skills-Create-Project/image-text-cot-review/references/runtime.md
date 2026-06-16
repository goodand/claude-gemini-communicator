# Runtime

## Purpose

Use this surface when outputs from `multimodal-evidence-refinement-loop` must preserve:

- image evidence
- text judgment
- machine-truth state
- human reading order

without collapsing them into one prose blob.

## Canonical Output Split

Keep two outputs:

- `human_review_markdown`
- `machine_truth_manifest`

The markdown is for reading.
The manifest is the source of truth.

## Canonical Manifest Fields

The manifest should keep these fields separate:

- `item_id`
- `image_evidence`
- `text_judgment`
- `comparison_outcome`
- `policy_decision`
- `review_state`
- `pending_reasons`
- `qualitative_winner_candidate`
- `recommended_current_default`

## Canonical Flow

1. Bind one bounded output item set from the upstream loop.
2. Record image evidence and text judgment separately.
3. Normalize both into one machine-truth manifest keyed by `item_id`.
4. Derive the markdown review surface from the same manifest.
5. If semantic closure is incomplete, emit `review_state=pending` with explicit `pending_reasons`.
6. If a winner exists, keep it as comparison output only until a later promotion gate changes the default.

## Boundary Rule

This skill must not:

- own the reinjection/refinement loop itself
- treat markdown reading order as machine truth
- collapse `comparison_outcome` and `policy_decision` into one field
- replace the current default baseline just because a qualitative winner exists
- hide unresolved multimodal ambiguity behind an implicit or missing state
