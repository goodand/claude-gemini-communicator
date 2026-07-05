# Verdict Escalation Patterns

## Good code, noisy PR

### Symptom

- Technical audits look positive
- PR is still too wide

### Resolution

Use `split-before-merge`, not `archive-only`.

## Good code, missing runtime proof

### Symptom

- Build and code review pass
- The last unanswered question is runtime behavior

### Resolution

Use `merge-after-runtime-proof`.

## Copy drift inflates severity

### Symptom

- Smoke fails on text or hero copy
- Structural screen is still correct

### Resolution

Do not escalate to a structural no-merge call.
Patch the assertion or classify it as copy drift.

## Branch has no remaining product value

### Symptom

- Useful ideas are already merged elsewhere
- The remaining branch is only reference or archive

### Resolution

Use `archive-only`.
