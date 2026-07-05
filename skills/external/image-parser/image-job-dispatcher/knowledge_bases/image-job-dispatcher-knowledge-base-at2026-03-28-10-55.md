# Image Job Dispatcher Knowledge Base

## Why This Skill Exists

Parallel caption runs are easy to do unsafely by hand.

The repeated failure modes were:

- overlapping worker ledgers
- packet scope drift
- trusting worker prose instead of MCP-backed state
- claiming high fanout when the live session still used an older thread cap

So the dispatcher is not just a fanout note. It is a control-plane skill.

## Current Proven Pattern

The current proven pattern is:

1. materialize shard JSONL files
2. issue one packet per worker with explicit owned paths
3. let workers write only worker-owned artifacts
4. aggregate only from ledgers and MCP state

## Boundary

This skill stops at dispatch and aggregation readiness.

It does not own:

- actual per-image caption generation
- review judgment
- approval
- commit of rename or metadata changes
