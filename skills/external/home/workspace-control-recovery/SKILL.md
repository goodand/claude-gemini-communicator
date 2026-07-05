---
name: workspace-control-recovery
description: Post-incident recovery specialist for deleted or partially missing workspace documentation trees from Time Machine, external snapshots, and session evidence without overwriting newer current files. Use when `control/`, `kb`, `knowledge_base`, `knowledge_bases`, `team/`, or `user_decisions/` content already disappeared and you need a missing-only recovery path.
---

# Workspace Control Recovery

## Overview

Use this skill when a live workspace lost operational or documentation trees and recovery must combine backup snapshots with local evidence.
It specializes in snapshot target validation, evidence grading, missing-only merge restore, and post-restore verification.
If the task is still pre-delete classification or protected-path review before deletion, route to [Destructive Cleanup Preflight](../destructive-cleanup-preflight/SKILL.md) instead.

## Use This Skill When

- `control/`, `kb`, `knowledge_base`, `knowledge_bases`, `team/`, or `user_decisions/` content is missing or partially missing
- a Time Machine or external backup exists, but the exact target subtree must be verified before restore
- some files were recreated after the backup and must not be clobbered
- session logs or tool traces can supplement backup evidence
- the workspace is not safely recoverable from git alone

## Do Not Use This Skill When

- the task is still deciding what is safe to delete before any destructive action
  - route to [Destructive Cleanup Preflight](../destructive-cleanup-preflight/SKILL.md)
- the task is ordinary disk-usage inspection with no restore need yet
- the task is a donor-workspace comparison without current-workspace recovery intent

## Required Inputs

- one explicit current workspace root
- one explicit missing subtree or document family
- one candidate backup or evidence source
- current-file preservation rule when newer files already exist

## Required MCPs

- `filesystem`

## Optional MCPs

- `conport`

## Required Shell Tools

- `tmutil`
- `find`
- `sort`
- `comm`
- `rsync`
- `sqlite3`

## Ownership Rule

This skill is the recovery specialist that [Destructive Cleanup Preflight](../destructive-cleanup-preflight/SKILL.md) routes to when deletion damage or partial loss is already real.
It does not own pre-delete approval, cleanup scoping, or protected-path classification.

## Not Owned Here

- destructive cleanup
- whole-tree overwrite restore by default
- donor-workspace substitution without provenance checks
- invented content for files lacking exact-content evidence
- backup trust based on timestamp alone

## Workflow

1. Lock the exact current workspace root and missing subtree.
2. Validate the exact target subtree inside the backup snapshot before trusting the backup.
3. Grade every source as `exact-content`, `structure-only`, or `name-only`.
4. Measure backup-vs-current `missing` and `extra` relative-path sets.
5. Restore only backup-missing files with preserve-current semantics.
6. Recompute gaps and open representative restored files to confirm body recovery.
7. Append any newly confirmed repeated pattern to the root repeated KBs.

## References

- [references/runtime.md](references/runtime.md)
- [references/restore-contract.md](references/restore-contract.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/owner-boundary.md](references/owner-boundary.md)
- [references/related-skill-routing.md](references/related-skill-routing.md)
- [checklists/recovery-preflight.md](checklists/recovery-preflight.md)
- [checklists/post-restore-verification.md](checklists/post-restore-verification.md)
- [knowledge_bases/workspace-control-recovery-knowledge-base-at2026-04-06-08-06.md](knowledge_bases/workspace-control-recovery-knowledge-base-at2026-04-06-08-06.md)
- [evals/evals.json](evals/evals.json)
