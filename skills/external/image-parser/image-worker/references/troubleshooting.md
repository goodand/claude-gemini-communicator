# Troubleshooting

## Missing MCP State

Symptoms:

- `job_id` exists in the packet, but the row for `image_id` cannot be resolved
- status transitions cannot be written back

Action:

- fail loudly
- write the missing-state reason into the control plane
- do not fabricate fallback image rows in worker-local state

## Cross-Image Context Bleed

Symptoms:

- prompt includes unrelated image summaries
- worker tries to batch-process multiple rows

Action:

- stop and reduce the run back to one `job_id` + one `image_id`
- keep context package data image-scoped only

## Evidence Missing At Completion

Symptoms:

- worker prose says complete
- raw response JSON or execution record path is missing

Action:

- treat the run as incomplete
- record the failure in MCP-backed state
- do not promote the item to review-ready

## Unsupported Media Type

Symptoms:

- `.emf` or another unsupported type surfaces in the row

Action:

- preserve the upstream reason
- mark the terminal state with evidence-backed failure
- do not retry as if it were an LLM quality problem
