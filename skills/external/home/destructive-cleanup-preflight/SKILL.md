---
name: destructive-cleanup-preflight
description: Canonical owner-family entrypoint for destructive cleanup scope classification, protected-path review, and exact target approval before cache cleanup, archive reduction, runtime pruning, or space-recovery deletion. Use when deletion might touch active workspaces, `control/`, `.codex`, generated runtime, or ambiguous large directories.
---

# Destructive Cleanup Preflight — Workspace Destructive-Cleanup Owner-Family Entrypoint

## Overview

This skill is the canonical owner-family entrypoint for destructive cleanup safety before files are deleted.
It owns path classification, protected-path review, exact target approval, and cleanup boundary definition.
If deletion damage already happened and files must be restored, route to [Workspace Control Recovery](../workspace-control-recovery/SKILL.md).

## Use This Skill When

- a user wants to free disk space and deletion is on the table
- candidate paths are large but their role is ambiguous
- cleanup may touch `control/`, `.codex`, active workspaces, generated runtime, or mixed-content directories
- cache, generated runtime, active runtime, and source-of-truth content must be separated before deletion
- an exact approved delete list must be prepared before any destructive action

## Do Not Use This Skill When

- files already disappeared and the task is now restoration
  - route to [Workspace Control Recovery](../workspace-control-recovery/SKILL.md)
- the request is only to inspect size with no deletion planning
- package-specific uninstall semantics dominate the task more than path safety review

## Required Inputs

- one explicit workspace root or home-root context
- one explicit set of candidate paths
- whether active runtimes or agent sessions may still depend on those paths
- whether a backup fallback exists and matters for deletion risk

## Owner Verbs

This skill owns the following verbs:

- cleanup preflight
- destructive-scope classification
- protected-path review
- explicit delete-list approval gating

## Not Owned Here

- post-incident restore work
- donor-workspace recovery
- destructive deletion without a reviewed exact path list
- silent downgrade from ambiguous path to safe-to-delete assumption

## Canonical Owner Outputs

- reviewed candidate-path classification
- protected-path block list
- explicit delete-ready path list
- explicit do-not-delete path list

Any deletion plan that could affect active workspaces or canonical docs should route through this skill first.

## Workflow

1. Enumerate candidate paths and normalize them to exact absolute paths.
2. Classify each path as cache, generated runtime, active runtime, mixed-content, or source-of-truth.
3. Mark protected paths explicitly before discussing deletion.
4. Check whether active sessions, current workspaces, or runtime surfaces still depend on the candidate paths.
5. Decide whether backup dependence raises the safety bar for deletion.
6. Produce an explicit delete-ready list and an explicit blocked list.
7. Only after approval should destructive deletion proceed.
8. While executing the approved deletion, append a per-path audit record to `<project-root>/logs/cleanup_<timestamp>.jsonl` — capture `size`/`sha256` before each `rm`; no silent deletion. See [references/deletion-audit-log.md](references/deletion-audit-log.md).
9. If deletion already caused loss, route immediately to [Workspace Control Recovery](../workspace-control-recovery/SKILL.md).

## References

- [references/runtime.md](references/runtime.md)
- [references/troubleshooting.md](references/troubleshooting.md)
- [references/owner-boundary.md](references/owner-boundary.md)
- [references/related-skill-routing.md](references/related-skill-routing.md)
- [references/deletion-audit-log.md](references/deletion-audit-log.md) — deletion audit log spec (per-file JSONL)
- [checklists/pre-delete-classification.md](checklists/pre-delete-classification.md)
- [checklists/protected-path-review.md](checklists/protected-path-review.md)
- [knowledge_bases/destructive-cleanup-preflight-knowledge-base-at2026-04-06-08-15.md](knowledge_bases/destructive-cleanup-preflight-knowledge-base-at2026-04-06-08-15.md)
- [evals/evals.json](evals/evals.json)
