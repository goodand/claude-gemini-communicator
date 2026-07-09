# Native Instability Patterns

## Applied/pending policy looks safe but demo cards are unstable

### Symptom

- Swift diff looks small
- Home cards or refresh behavior become unreliable in runtime

### Recovery

1. Audit `applied`, `pending`, and mutation-dayKey behavior together.
2. Do not review one helper in isolation.
3. Require live home/delete/precious evidence if policy changed.

## Thumbnail fallback silently regressed

### Symptom

- Build passes
- Input or carousel can still show weak or blank image states

### Recovery

1. Check `PhotoAssetManager.swift` and plugin fallback paths together.
2. Prefer branches that preserve degraded-but-visible UX over elegant but brittle refactors.

## Large tracing experiment is tempting but too wide

### Symptom

- A native experiment branch contains useful scripts and useful findings
- The branch also carries large refactors or debug scaffolding

### Recovery

1. Do not merge the whole branch.
2. Salvage only small tooling or evidence helpers if they stand alone.
