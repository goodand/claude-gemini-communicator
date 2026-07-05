# Record Contract

## Minimum Read Surface

The worker should resolve from canonical state:

- `job_id`
- `image_id`
- source image path
- current phase status
- prior caption state when present
- context package reference when present

## Minimum Write Surface

The worker should write back:

- terminal or in-progress phase state
- caption or failure reason
- raw evidence paths
- execution timing where available

## Completion Contract

The worker is considered done only when:

- the image row is updated
- evidence paths exist
- execution record state and row state agree

If these disagree, MCP-backed state and artifact presence win over prose summaries.
