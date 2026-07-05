# Parser Sidecar To Canonical Schema Promotion Knowledge Base

## Why This Skill Exists

Some parser MCPs return:

- human-readable markdown-like text
- nested JSON payloads embedded in text fields
- parser-native region structures that are not stable enough for downstream consumers

The project should not make later consumers parse those raw payloads repeatedly.

Instead, one bounded promotion step should convert raw parser sidecars into the project's canonical `Table -> Row -> Cell` shape.

## Current Proven Case

The current bounded PaddleOCR table branch already produced:

- one raw sidecar artifact
- one canonical normalized table artifact
- one read-only wrapper consumer smoke over the canonical artifact

That makes the promotion path a reusable workflow surface rather than a one-off notebook step.

The same promotion path is now also proven against a bounded Apple helper sidecar:

- one Apple helper raw sidecar artifact
- one Apple helper normalized canonical artifact
- one direct comparison artifact against the current Paddle normalized output

That means the skill is no longer tied to one parser family.
It now owns a canonical comparison surface where different parser families can be normalized first and compared second.

The current bounded flow now has one more step:

- one merged candidate manifest built from Apple structure plus dual-parser text evidence

That makes the skill useful not only for promotion, but also for preparing review-stage table artifacts.

## Canonical Promotion Pattern

1. keep the raw sidecar as evidence
2. recover image provenance from the raw artifact
3. recover slide provenance from the PPT extraction manifest
4. extract the first stable table payload
5. normalize into canonical `Table -> Row -> Cell`
6. treat the canonical JSON as the new read surface

## Why This Is A Skill

The promotion step is:

- narrow
- repeated
- easy to do inconsistently by hand
- required before wrapper consumers, worksheet export, or row-level RAG can safely read table data

So the right packaging is a thin skill wrapper over a shared normalization helper, not an ad hoc shell recipe.

## Structure And Text Split

The current dual-parser evidence supports a practical split:

- Apple helper for structure-first hints
- Paddle parser for active parser execution
- OCR or later repair logic for text correction

The current comparison on `image11.png` shows:

- structure compatibility across Apple and Paddle
- text drift concentrated in numeric formatting and one header conflict

So the reusable lesson is:

- normalize both parser outputs into the same canonical shape first
- compare structure and text separately
- do not let raw parser-native payloads decide merge policy directly
- build review-stage merged candidates from canonical artifacts, not from raw parser payloads
