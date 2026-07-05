# Recovery Boundary

## Specialist Role

[Workspace Control Recovery](../SKILL.md) is the post-incident recovery specialist for missing workspace documentation trees after loss has already happened.

## Owned Here

- snapshot target-path validation
- evidence grading
- missing-only merge restore
- preserve-current verification

## Not Owned Here

- pre-delete cleanup approval
- cache/runtime/source-of-truth classification before deletion
- destructive path review before `rm`

Those pre-delete owner concerns route to [Destructive Cleanup Preflight](../../destructive-cleanup-preflight/SKILL.md).
