# Review Queue Contract

## Queue Buckets

The auditor should only emit these queue classes:

- `approval_candidates`
- `retry_candidates`
- `hold_candidates`

## Promotion Rule

An item can enter `approval_candidates` only when:

- caption or structured result exists
- evidence paths exist
- execution state and row state agree
- no rename or metadata conflict remains

## Retry Rule

An item belongs in `retry_candidates` when:

- the failure is recoverable
- evidence is incomplete but the row is still actionable
- the issue is execution-related rather than approval-related

## Hold Rule

An item belongs in `hold_candidates` when:

- conflicts exist
- provenance is ambiguous
- state and evidence disagree in a way that needs human review
