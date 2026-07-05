# Destructive Cleanup Preflight Knowledge Base

## Purpose

Capture reusable guardrails for cleanup tasks that might otherwise drift into destructive deletion of active or canonical content.

## Canonical Takeaways

- exact absolute paths must be frozen before destructive cleanup discussion
- mixed-content directories are not delete-ready by default
- active runtime and source-of-truth content require different treatment than caches
- pre-delete safety review and post-incident recovery are different skills
- newly confirmed failure modes should be promoted into the root repeated pattern KBs

## Related Skills

- prevention owner: [Destructive Cleanup Preflight](../SKILL.md)
- post-incident recovery owner: [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md)

## Proven Evidence

- 2026-04-05 cleanup scope drift around `vscode-markdown-review-surface/control` showed that directory-level assumptions were not safe enough.
- `.codex` and active runtime surfaces must not be treated as disposable cache by default.
