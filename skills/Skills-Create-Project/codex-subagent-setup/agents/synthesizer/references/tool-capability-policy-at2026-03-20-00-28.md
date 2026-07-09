# Tool Capability Policy

## Allowed

- read worker output artifacts
- compare summaries against underlying file evidence
- normalize naming and merge duplicates
- produce final markdown or json synthesis artifacts

## Avoid

- full repository-wide rediscovery when worker evidence already exists
- primary implementation edits
- destructive cleanup of worker artifacts

## Escalate only if needed

- when final synthesis depends on opening external logs or artifacts outside the default scope
- when contradiction resolution requires one missing primary artifact
