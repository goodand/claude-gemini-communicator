# Repeated Runtime Risks

## Best-effort async drift

### Symptom

- The code path looks complete in review
- Runtime still depends on a fire-and-forget refresh or background update

### Repeated case in this repo

- `recorded -> refresh` looked logically closed, but still needed runtime proof before merge.

### Recovery

1. Mark the path as coherent-but-unproven.
2. Ask for the smallest runtime proof, not a full re-audit.
3. Use `merge-after-runtime-proof` unless proof already exists.

## Runtime path mixed with noise

### Symptom

- Real runtime fixes exist
- PR is too wide to merge safely as-is

### Recovery

1. Keep the runtime slice.
2. Remove CI/docs residue, logs, and local artifacts.
3. Re-open as a slim PR.

## Copy drift mistaken for flow regression

### Symptom

- A smoke assertion fails on hero text
- The visible screen may still be correct

### Recovery

1. Re-check the live screen with a screenshot.
2. Separate copy/assertion drift from actual runtime breakage.
3. Patch the flow/assertion if the screen is structurally correct.
