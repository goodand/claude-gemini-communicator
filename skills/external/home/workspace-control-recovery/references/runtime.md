# Runtime

## Core Workflow

1. Fix the workspace root and the exact missing subtree.
2. Find the authoritative backup snapshot path, then inspect the target subtree inside that snapshot.
3. Build relative-path inventories for snapshot and current trees.
4. Measure `missing` and `extra` sets before any restore.
5. Restore only snapshot-missing files with missing-only semantics.
6. Recompute diffs and open representative files to confirm real content recovery.
7. Append any newly confirmed repeated Task or Issue pattern to the root KBs.

## Related Skills

- Pre-delete safety and path classification route to [Destructive Cleanup Preflight](../../destructive-cleanup-preflight/SKILL.md).
- This skill stays responsible once loss is already real and recovery must preserve newer current files.

## Evidence Discipline

- `exact-content`: direct file body from snapshot, session log, or other authoritative source
- `structure-only`: proven directory shape or file presence without body
- `name-only`: filename or path mention only

Do not promote `structure-only` or `name-only` evidence into exact recovery without explicit labeling.

## Snapshot Validation Notes

- Do not trust a recent backup timestamp by itself.
- Validate the exact subtree under the actual snapshot root.
- If the visible mounted volume path looks incomplete, inspect the dated snapshot path directly before concluding the content is absent.

## Merge Rule

- Default restore mode is preserve-current.
- Prefer `rsync --ignore-existing` or equivalent missing-only behavior when the current tree may contain newer files.
- Re-measure `extra` after restore so newer current artifacts are accounted for explicitly.

## Root Pattern Logs

- [Repeated Task Patterns](../../../control/project_agent_ops/resources/skill_candidates/repeated_tasks/KB_repeated_task_patterns.md)
- [Repeated Issue Patterns](../../../control/project_agent_ops/resources/skill_candidates/repeated_issues/KB_repeated_issue_patterns.md)
