# Noise Reduction Patterns

## Valuable code buried under logs and artifacts

### Symptom

- Runtime or CI fixes are present
- `test_log`, screenshots, temp media, or local helpers dominate the PR

### Recovery

1. Produce a keep list and remove list.
2. Split product code from evidence or archive material.

## Archive material should survive, but not in `main`

### Symptom

- Old experiment logs or reports still matter historically
- They should not be merged

### Recovery

1. Preserve them in a local archive path first.
2. Delete the archive branch/worktree after preservation if it has no remaining product value.

## Local machine residue

### Symptom

- `.xcuserstate`, local lock files, simulator images, or auth helpers appear in diff

### Recovery

1. Treat them as merge noise by default.
2. Only keep them if the user explicitly wants repo-level automation changes.
