# Comparison Consumer Runtime

## Purpose

Use this surface when completed caption arms or frozen eval bundles must be compared without regenerating the underlying ledgers.

## Accepted Input Modes

The consumer may close on either:

- one aggregate small-batch bundle
- multiple per-image frozen bundles

When both are available, prefer the freshest truth-source. If aggregate freshness is uncertain, consume the per-image bundle list directly.

## Canonical Flow

1. Resolve the input into a per-image bundle path list.
2. Verify the resolved image set before scoring or reporting.
3. Build comparison or auto-eval outputs without mutating upstream bundles.
4. Preserve:
   - actual input mode
   - resolved per-image bundle paths
   - image ids
   - comparison winner candidates
   - baseline retention status
5. If no semantic judge harness exists, emit a waiver instead of implying semantic execution.

## Thin Wrappers

- `scripts/run_caption_arm_comparison.py`
- `scripts/run_four_mode_small_batch_auto_eval.py`

These wrappers should remain thin and reuse the shared root scripts under `repo/scripts/`.

## Output Expectations

The consumer should emit:

- comparison JSON and markdown report when comparing arms
- auto-eval JSON and markdown report when scoring a small batch
- semantic judge waiver markdown when no repo-local judge exists

## Guardrails

- do not regenerate arms
- do not rewrite context packages
- do not treat a qualitative winner as a default-baseline replacement
- keep `comparison_only_pending_context_review` as comparison-only until later promotion closes
