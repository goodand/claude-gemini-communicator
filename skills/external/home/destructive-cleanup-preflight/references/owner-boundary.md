# Owner Boundary

## Owner Role

[Destructive Cleanup Preflight](../SKILL.md) is the owner-family entrypoint for cleanup safety before destructive deletion.

## Owned Here

- path classification
- protected-path review
- explicit delete-list gating
- cleanup safety boundary definition

## Not Owned Here

- post-incident recovery
- backup restore execution
- exact-content recovery from snapshots or session logs

Those recovery concerns route to [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md).
