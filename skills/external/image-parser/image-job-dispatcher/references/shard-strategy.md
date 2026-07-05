# Shard Strategy

## Purpose

Shard preparation exists to keep parallel caption runs non-overlapping and auditable.

## Shard Invariants

- one input row appears in exactly one shard
- one worker owns exactly one ledger JSON
- one worker owns exactly one `_responses/` directory
- one issued task packet maps to one worker shard
- aggregation happens only after worker-owned writes are finished

## Current Shared Tooling

The current materializer is:

```bash
scripts/prepare_parallel_caption_experiment.py
```

It allocates workers, writes shard JSONL files, writes issued task packets, and emits a phase manifest with overlap checks.

## When To Reuse Existing Shards

Reuse an existing shard manifest only when:

- the phase name is unchanged
- the dataset rows are unchanged
- the owned ledger paths are unchanged
- you are resuming or re-running the same bounded batch

If any of those change, rematerialize the shards.
