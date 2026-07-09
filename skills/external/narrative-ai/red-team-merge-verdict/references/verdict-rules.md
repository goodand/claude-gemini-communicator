# Verdict Rules

## Decision order

1. Is the code path coherent?
2. Is the runtime proof adequate?
3. Is the PR scope clean enough to merge as-is?

## Repo-specific guidance

- Coherent code + missing runtime proof = `merge-after-runtime-proof`
- Good code buried in noisy PR = `split-before-merge`
- Branch has no remaining product value = `archive-only`
- Clean code, adequate runtime proof, clean scope = `merge-now`
- For smoke evidence on this repo, treat the following as the minimum gate:
  - frontend build passes
  - iOS simulator build passes
  - backend `/health` returns healthy, even if slow
  - at least one Maestro smoke flow passes, or a copy-only failure is patched and re-run
- Copy/assertion drift alone should not be promoted to a structural no-merge verdict.

## Output style

Keep the verdict short:
- final verdict
- 1 to 3 blockers
- exact next action
