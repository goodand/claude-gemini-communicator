# Runtime

## Canonical Preparation Command

Use the shared shard materializer before large parallel caption runs:

```bash
python3 scripts/prepare_parallel_caption_experiment.py \
  --phase-name phase1_caption_10w \
  --workers 10
```

This produces:

- shard JSONL files under `control/project_domain/resources/manifests/<phase>_shards/`
- issued task packets under `control/project_agent_ops/resources/task_packets/issued/`
- one aggregate shard manifest JSON

## Canonical Dispatch Pattern

1. Read `control/project_agent_ops/registry/runtime/session_paths.json`.
2. Read `control/project_domain/resources/master_plans/MASTER_PLAN_presentation_image_pipeline.md`.
3. If the shard manifest already exists, dispatch only rows owned by that shard.
4. Pass stable IDs and owned paths into each worker packet.
5. Keep one shard JSONL, one worker ledger, and one `_responses/` directory per worker.
6. Aggregate only after all workers that belong to the current batch have finished.

## Worker-Owned Surfaces

Per worker, the owned surfaces should be:

- one shard JSONL
- one output ledger JSON
- one `_responses/` directory
- one issued task packet JSON

The dispatcher may read shared plans and registries, but it should not let workers write shared summaries or cross-worker ledgers.

## Canonical Evidence

Known bounded example:

- shard manifest: `control/project_domain/resources/manifests/phase1_caption_10w_shards/phase1_caption_10w_manifest.json`
- worker packets: `control/project_agent_ops/resources/task_packets/issued/TASK_PACKET_phase1_caption_10w_*.json`
- smoke evidence: `control/project_agent_ops/resources/smoke/SMOKETEST_openai_image_caption_validation-at2026-03-27.md`

## Readiness Rule

Do not fan out parallel workers until:

- shard overlap checks are green
- each worker has a unique ledger path
- the packet owns only its shard surfaces
- the main agent remains the only summary writer
