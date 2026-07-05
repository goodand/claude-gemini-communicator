# Runtime

## Core Workflow

1. Lock the exact candidate path set.
2. Separate cleanup planning from restore work.
3. Classify each path into safety buckets.
4. Mark protected paths before discussing deletion.
5. Produce explicit delete-ready and blocked lists.
6. Delete nothing until the reviewed path list is approved.

## Safety Buckets

- `cache`
- `generated-runtime`
- `active-runtime`
- `mixed-content`
- `source-of-truth`

## Related Skills

- If deletion has already caused loss, route to [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md).
- If the task remains pre-delete safety review, stay here.

## Root Pattern Logs

- [Repeated Task Patterns](../../../control/project_agent_ops/resources/skill_candidates/repeated_tasks/KB_repeated_task_patterns.md)
- [Repeated Issue Patterns](../../../control/project_agent_ops/resources/skill_candidates/repeated_issues/KB_repeated_issue_patterns.md)
