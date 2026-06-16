# Tool Capability Policy — Dependency Slice Planner

## Allowed

- tree/size heuristics
- dependency-aware refinement
- slice proposal drafting
- graph artifact reading
- markdown/JSON artifact synthesis

## Preferred skills / tools

- `depsolve-analyzer`
- `agent-task-packet`
- read-only graph artifacts from workspace

## Disallowed by default

- final risk taxonomy ownership
- broad full-context ownership
- direct code edits
- destructive commands

## Enforcement note

- This is a document-first capability contract.
- If runtime automation is added later, lower this file into JSON or CLI policy artifacts instead of expanding AGENT.md.
