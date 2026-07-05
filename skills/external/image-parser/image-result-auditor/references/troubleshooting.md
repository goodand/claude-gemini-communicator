# Troubleshooting

## Missing Evidence With Completed State

Symptoms:

- row says `completed`
- raw response or execution evidence is missing

Action:

- downgrade from approval-ready
- move to retry or hold depending on recoverability
- preserve the mismatch as an explicit audit finding

## Rename Conflict

Symptoms:

- two items propose the same filename
- metadata write targets are not unique

Action:

- move both rows to hold
- preserve conflict notes for human review
- do not auto-resolve by silently renaming one side

## Invalid Status Transition

Symptoms:

- row state and execution record state disagree
- terminal state appears without a valid running or failure path

Action:

- keep MCP-backed artifacts authoritative
- record the drift
- avoid promoting the row until state alignment exists

## Unsupported Media Or Terminal Upstream Failure

Symptoms:

- upstream worker already recorded `unsupported_media_type` or another terminal failure

Action:

- do not turn it into retry-ready unless the failure class is actually recoverable
- preserve the original failure reason in the review queue
