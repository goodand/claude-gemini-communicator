# Native Checks

## High-risk native areas

- applied/pending daily curation cache
- mutation day-key tracking
- thumbnail fallback
- original image loading
- delete path
- summary hydration contract

## Required questions

- Can JS still depend on `assetId`, `dayKey`, `thumb`, `flags`, and summary fields?
- Can a card open input with a blank image?
- Can a fallback return an empty but non-crashing payload?
- Is delete still reflected in a predictable order for the UI?

## Demo-sensitive finding

If a change can make some cards unstable demo targets, call that out even if the app does not crash.
