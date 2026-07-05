# CI Docs Drift Patterns

## Product definition changed before docs changed

### Symptom

- Code now represents a different product emphasis
- README or checklist still describes the old framing

### Recovery

1. Update README, package framing, and checklists together.
2. Do not treat this as runtime failure.

## Local-only file presented as repo-ready

### Symptom

- `.env`, local auth plist, or helper config looks central in local testing
- It is not meant to be committed

### Recovery

1. Mark it explicitly as local-only.
2. Keep `.env.example` and ignore rules aligned.

## Slow Render health misread as outage

### Symptom

- `/health` hangs for a while
- It later returns a healthy payload

### Recovery

1. Record the latency.
2. Classify it as pass-with-latency, not hard failure.

## Maestro copy drift misread as product failure

### Symptom

- Smoke flow fails on a marketing text assertion

### Recovery

1. Check the live screen.
2. Patch the assertion to a stable anchor if the screen is right.
