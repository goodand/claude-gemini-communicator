# Runtime — async-migration-verify

## Input Contract

- target file or repo root
- description of the sync→async change
- validation command or existing test surface

## Verification Target

- file I/O migration
- loader/saver host call sites
- sync reader compatibility residue
- scanner evidence for dead imports and duplication

## Acceptance Rule

- all six checkpoints are reviewed
- unresolved items are explicitly marked as residual risk, not silently ignored
- if migration touched product UX, blocked-user feedback must be visible
