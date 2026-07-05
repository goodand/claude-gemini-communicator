# Runtime

## Canonical Inputs

The worker accepts only:

- `job_id`
- `image_id`

All other image details should be resolved from MCP-backed state or canonical artifacts. Do not stuff captions, OCR text, or image bytes into the worker prompt when the registry already owns them.

## Canonical Flow

1. Resolve the image row from registry-backed state using `job_id` and `image_id`.
2. Confirm the row belongs to the current worker-owned ledger family.
3. Mark the task as running through the control plane.
4. Run caption generation or refinement for that one image only.
5. Write structured outputs and raw evidence paths back to the registry.
6. Mark the phase state with evidence-backed completion or failure.

## Evidence Rule

Completion requires both:

- MCP-backed state updated to the expected phase terminal state
- evidence paths that point to real generated artifacts such as raw responses or execution records

Free-form worker prose is never the completion signal.

## Canonical Evidence Surfaces

Known bounded examples live under:

- `control/project_agent_ops/registry/jobs/image_caption_jobs/*.json`
- `control/project_agent_ops/registry/jobs/image_caption_jobs/*_responses/`
- `control/project_agent_ops/registry/jobs/image_caption_jobs/*_execution_records.jsonl`
- `control/project_agent_ops/registry/jobs/image_caption_jobs/*_evaluation_decisions.jsonl`

Representative rows include:

- `control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_ppt1_w1.json`
- `control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_ppt1_w1_execution_records.jsonl`

## Boundary Rule

This skill must not:

- read or mutate rows owned by another worker shard
- aggregate batch-wide summaries
- mark review approval
- commit filename or metadata mutations
