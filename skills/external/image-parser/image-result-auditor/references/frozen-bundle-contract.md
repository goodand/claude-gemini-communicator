# Frozen Bundle Contract

## Per-Image Bundle Minimum Fields

The consumer expects each per-image frozen bundle to expose:

- `bundle_path`
- `source_image_path`
- `comparison_ready`
- `recommended_current_default`
- `ready_arms`
- `blocked_arms`
- `arms`
- `per_arm_promotion`

## Aggregate Bundle Minimum Fields

When an aggregate bundle is used, it should expose:

- `bundle_name`
- `image_count`
- `bundle_paths_used`
- `images[]`

Each `images[]` entry must include:

- `bundle_path`
- `source_image_path`
- `comparison_ready`
- `recommended_current_default`

## Consumer Output Fields

The downstream consumer should preserve:

- `input_resolution.actual_input_mode`
- `input_resolution.resolved_per_image_bundle_paths`
- `image_count`
- `image_ids`
- `evaluations[]`
- `batch_summary.winner_frequency`
- `batch_summary.baseline_retained`

## Interpretation Rule

- `qualitative_winner_candidate` is a comparison result
- `recommended_current_default` remains the active default anchor
- promotion state must be read separately from winner frequency
