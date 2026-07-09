# Alternate Closure Routes

Use this reference when one parser/helper backend fails on a bounded image, but the image may still be promotable through an alternate normalized structure route.

## Goal

Avoid excluding an image too early just because the first parser helper failed.

Typical example:

- Apple Vision helper fails on one image
- Paddle normalized output still exists
- a single-source merged candidate can still support:
  - parser-enriched context package
  - reviewed isolated component context package
  - bounded `4-mode` comparison inclusion

## Preferred Order

1. Check whether the preferred helper failure is backend-specific or image-wide.
2. Confirm another normalized structure artifact already exists.
3. If dual-parser comparison is unavailable, allow single-source fallback through the existing merged-candidate builder.
4. Keep promotion state explicit:
   - parser-enriched reruns remain `comparison_only_pending_context_review` unless review closes
   - reviewed component reruns may become `comparison_ready_reviewed_branch` only if the reviewed-crop evidence is strong enough
5. Do not widen beyond the bounded image until the alternate route is documented.

## Do

- preserve original provenance
- write canonical manifests under workspace-owned paths
- use existing builders instead of handwritten transformation code
- record which backend failed and which backend supplied the actual closure route

## Do Not

- mark the image excluded on the first failed backend alone
- promote the fallback route to default baseline automatically
- treat single-source fallback as equivalent to a reviewed dual-parser decision

## Current Proven Pattern

- Apple helper failure on `image8.png`
- Paddle normalized structure used as the alternate closure route
- single-source merged candidate enabled parser-enriched and reviewed-component bounded reruns
