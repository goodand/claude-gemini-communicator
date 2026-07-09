# Recovery Preflight

- Confirm the exact current workspace root before reading or restoring any file.
- Confirm the missing subtree is user-approved recovery scope.
- If deletion has not happened yet, stop and route to [Destructive Cleanup Preflight](../../destructive-cleanup-preflight/SKILL.md).
- Confirm the backup date and the exact target subtree inside the snapshot.
- Confirm whether current files newer than the snapshot already exist and must survive.
- Grade evidence as `exact-content`, `structure-only`, or `name-only`.
- Default to missing-only restore unless the user explicitly authorizes overwrite.
- Exclude noise such as `.DS_Store` from recovery counts unless the user asks otherwise.
- If a new failure mode or workaround appears, append it to [Repeated Task Patterns](../../../control/project_agent_ops/resources/skill_candidates/repeated_tasks/KB_repeated_task_patterns.md) or [Repeated Issue Patterns](../../../control/project_agent_ops/resources/skill_candidates/repeated_issues/KB_repeated_issue_patterns.md) after recovery.
