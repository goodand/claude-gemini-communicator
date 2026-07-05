# Workspace Control Recovery Knowledge Base

## Purpose

Capture reusable recovery heuristics for deleted or partially missing workspace doc trees.

## Canonical Takeaways

- Snapshot timestamp alone is not sufficient; verify the exact target subtree.
- Recovery evidence must be graded before file content is claimed restored.
- Missing-only merge restore is safer than whole-tree overwrite when current files may be newer than the backup.
- Backup and current relative-path diff should be measured before and after restore.
- Proven recovery patterns should be promoted into the root repeated Task and Issue KBs.

## Proven Session Evidence

- `vscode-markdown-review-surface/control` recovery on 2026-04-06 required validating the dated Time Machine subtree before restore.
- The authoritative backup-vs-current gap was `MISSING_COUNT 2862` before merge.
- Missing-only restore preserved `17` newer current files while refilling backup-missing files.
- Representative restored files had to be opened directly to confirm body recovery.

## Operational Heuristics

- Prefer backup snapshots over donor workspaces when both exist.
- Prefer exact-content session evidence over filename-only traces.
- Preserve current files unless the user explicitly asks for overwrite.
- Append newly confirmed patterns to:
  - `/Users/jaehyuntak/control/project_agent_ops/resources/skill_candidates/repeated_tasks/KB_repeated_task_patterns.md`
  - `/Users/jaehyuntak/control/project_agent_ops/resources/skill_candidates/repeated_issues/KB_repeated_issue_patterns.md`
