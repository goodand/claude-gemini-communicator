# Related Skill Routing

## Choose [Destructive Cleanup Preflight](../../destructive-cleanup-preflight/SKILL.md) When

- the user wants to free space safely
- candidate paths need classification before deletion
- active runtime, generated runtime, caches, and source-of-truth docs must be separated
- deletion scope needs explicit approval first

## Choose [Workspace Control Recovery](../SKILL.md) When

- files already disappeared
- a backup snapshot or session evidence must be used
- newer current files must be preserved while missing files are restored

## Sequential Route

1. Start with [Destructive Cleanup Preflight](../../destructive-cleanup-preflight/SKILL.md) before destructive deletion.
2. If deletion damage already occurred, continue with [Workspace Control Recovery](../SKILL.md).
