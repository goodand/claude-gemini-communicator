# Pre-Delete Classification

- Normalize every candidate to an exact absolute path.
- Confirm whether the request is deletion planning or actual restore.
- Classify each path as cache, generated runtime, active runtime, mixed-content, or source-of-truth.
- If a path mixes user docs with generated runtime, keep it out of the delete-ready list.
- If a path belongs to an active workspace, keep it out of the delete-ready list until explicit dependency review is complete.
- If deletion already happened and recovery is needed, route to [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md).
