# Semantic Judge Waiver

## When It Applies

Emit a waiver when the comparison or auto-eval lane is mechanically ready but the repo does not expose a first-party semantic judge harness for the same scope.

## What The Waiver Must Preserve

- the bundle paths actually consumed
- the input mode used by the consumer
- the image ids included in the lane
- the current qualitative winner candidates
- explicit confirmation that the default baseline remains unchanged

## What The Waiver Must Not Imply

- that a semantic judge actually ran
- that the comparison winner replaces the baseline
- that pending-review comparison arms are now default-ready

## Promotion-State Rule

Keep these interpretations intact:

- `default_ready_anchor`: active default path
- `comparison_ready_reviewed_branch`: comparison-ready only
- `comparison_only_pending_context_review`: comparison-only until review closes
