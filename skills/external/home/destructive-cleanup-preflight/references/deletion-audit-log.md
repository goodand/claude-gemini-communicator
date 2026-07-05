# Deletion Audit Log

The delete-ready list decides *what* may be deleted. This document adds the
record of *what was actually deleted* — an append-only audit trail so any
deletion can later be explained or handed to recovery.

## Rule

- **No silent deletion.** Every destructive `rm` produces one audit record per path.
- Compute `size` and `sha256` **while the file still exists** (before `rm`) — they
  cannot be recovered afterward. Append the record at deletion time and set
  `committed` to whether the `rm` actually succeeded.
- Log location: `<project-root>/logs/cleanup_<YYYY-MM-DD-HH-MM>.jsonl`, where
  `<project-root>` is the root of the workspace being cleaned. If unclear, use `cwd`.
- The log itself is source-of-truth — never delete it in the same pass.

## Record (one JSON line per path)

```json
{"ts":"2026-06-21T15:30:00","path":"/abs/path","bucket":"cache","size":1024,"sha256":"<16hex>","reason":"regenerable build output","value_now_at":"none","regen":"make build","operator":"agent","committed":true}
```

| field | required | meaning |
|-------|----------|---------|
| `ts` | Y | ISO 8601 deletion time |
| `path` | Y | normalized absolute path |
| `bucket` | Y | safety bucket: `cache` / `generated-runtime` / `active-runtime` / `mixed-content` / `source-of-truth` |
| `size` | Y | bytes, captured before deletion |
| `sha256` | Y | first 16 hex — identifies *what* was removed, not just where |
| `reason` | Y | one-line deletion rationale |
| `value_now_at` | Y | durable location of the content's value, or `"none"` |
| `regen` | N | command to recreate, or `"not regenerable"` |
| `operator` | Y | who performed the deletion |
| `committed` | Y | whether the `rm` actually completed after the record was written |

## Why size + sha256

- A path alone does not identify *what* was removed (the same path may later hold
  different content).
- [Workspace Control Recovery](../../workspace-control-recovery/SKILL.md) needs the
  checksum to match a recovery candidate against what was deleted.

## When the value is not yet preserved

- Promote it to a durable home first, then record `value_now_at` before deletion.
- For promotion, use the `evidence-to-knowledge-promoter` skill
  (workspace-artifact-production-process family, in the Skills-Create-Project
  category). It lives in a different category, so no relative-path link is used here.

## Log retention

- The cleanup log file is excluded from deletion (`source-of-truth` bucket).
- Old logs may be archived, but keep them at least 30 days after the deletion.
