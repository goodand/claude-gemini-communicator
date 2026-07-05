# Related Skill Routing

## Start With [Destructive Cleanup Preflight](../SKILL.md) When

- the user is asking what can be removed safely
- you need a protected-path list before deletion
- the directory role is ambiguous

## Route To [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md) When

- deletion already happened
- a backup snapshot must be validated
- missing-only merge restore is required

## Sequential Relationship

1. [Destructive Cleanup Preflight](../SKILL.md) owns prevention.
2. [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md) owns post-incident repair.
