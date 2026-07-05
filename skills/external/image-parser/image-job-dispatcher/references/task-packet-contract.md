# Task Packet Contract

Each dispatched worker packet should include:

- stable `task_id`
- stable `worker_id`
- stable `dataset_id`
- `allowed_paths`
- `locked_paths`
- `command`
- `expected_rows`
- `row_indexes`
- `done_definition`

## Ownership Rule

The packet must make the worker's write set explicit. At minimum:

- shard JSONL
- worker ledger JSON
- worker `_responses/` directory

Shared plans, registries, and summary reports may be readable context, but they are not worker-owned write surfaces.

## Current Canonical Example

Issued packet family:

```text
control/project_agent_ops/resources/task_packets/issued/TASK_PACKET_phase1_caption_10w_*.json
```

These packets are the canonical example for this skill's current parallel caption surface.
