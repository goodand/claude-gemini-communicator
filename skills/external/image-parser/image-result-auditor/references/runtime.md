# Runtime

## Canonical Inputs

The auditor should read:

- completed or terminal image rows
- related execution records
- evaluation decision artifacts when present

It should not infer queue state from chat summaries alone.

## Canonical Flow

1. Load finished image rows and related execution records.
2. Flag missing caption, missing evidence, invalid state transitions, and rename or metadata conflicts.
3. Split rows into:
   - approval candidates
   - retry candidates
   - hold or manual review
4. Emit a human-review-friendly queue surface.

## Canonical Evidence Surfaces

Representative bounded examples live under:

- `control/project_agent_ops/registry/jobs/image_caption_jobs/*_execution_records.jsonl`
- `control/project_agent_ops/registry/jobs/image_caption_jobs/*_evaluation_decisions.jsonl`
- `control/project_agent_ops/registry/jobs/image_caption_jobs/*.json`

Known bounded examples include:

- `control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_ppt1_w1_execution_records.jsonl`
- `control/project_agent_ops/registry/jobs/image_caption_jobs/phase1_ppt1_w1_evaluation_decisions.jsonl`

## Decision Rule

The auditor should prefer:

- approval-ready only when evidence and state agree
- retry when execution failed or evidence is incomplete but still recoverable
- hold when there is a naming conflict, ambiguous provenance, or approval-blocking inconsistency

## Boundary Rule

The auditor must not:

- apply file mutations
- invent evidence paths
- upgrade an item to approval-ready when evidence is absent
