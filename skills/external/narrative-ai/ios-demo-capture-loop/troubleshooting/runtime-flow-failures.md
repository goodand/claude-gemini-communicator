# Runtime Flow Failures

## Unstable `소중해` path

### Symptom

- `소중해` button is visible but Maestro cannot find or tap it reliably
- Point tap works sometimes, text selector works sometimes

### Cause Pattern

The carousel CTA hitbox is unstable across cards and states.

### Recovery

1. Re-check the current card with a screenshot.
2. If needed, use a point tap.
3. If the current card still fails, reselect a different card before retrying.

## Blank image on input screen

### Symptom

- Input screen opens
- Image area is blank
- `기억을 분석하는 중...` may hang afterward

### Cause Pattern

The selected card is not a stable demo target. The UI reached input, but the selected image payload was not prepared in a reliable way for that card.

### Recovery

1. Treat the current card as unstable.
2. Return home.
3. Move to another visible card.
4. Retry the record/result path.

## Result hang vs backend failure

### Symptom

- UI stays on `기억을 분석하는 중...`

### How to Separate the Cause

- Check backend `/health`
- If needed, call the backend narrative endpoint directly with a known image

### Repo Finding

In this repo, we confirmed cases where backend was healthy and narrative generation succeeded directly, while the UI flow still hung. That points to the selected card / image preparation path rather than the backend itself.

## Smoke assertion drift

### Symptom

- Maestro smoke fails on a text assertion
- The expected hero copy is not visible
- The app may still be on the correct screen

### Cause Pattern

The product screen is structurally correct, but the copy changed. This is a flow/assertion maintenance issue, not necessarily a runtime regression.

### Recovery

1. Capture a fresh simulator screenshot.
2. Confirm whether the app is on the intended screen.
3. Replace the brittle copy assertion with a more stable anchor if available.
4. Only escalate as a runtime failure if the screen itself is wrong.

## Slow backend `/health`

### Symptom

- Remote `/health` hangs for tens of seconds before returning

### Cause Pattern

Render cold-start or remote wake-up latency. This is slow, but not automatically equivalent to backend failure.

### Recovery

1. Allow a longer wait window before classifying the backend as down.
2. If `/health` eventually returns `200` and the expected JSON, record it as pass-with-latency.
3. Keep frontend/iOS smoke moving if the rest of the environment is healthy.

## Stale runtime state

### Symptom

- A handoff or subagent says the app is on one screen
- Live simulator is actually on another screen

### Recovery

Always re-check:
- active recording process
- current simulator screenshot
- current app screen

before continuing a stale handoff.

## Split-tail strategy

If one single full demo becomes unstable:

1. Prove delete/report separately
2. Prove result/mypage separately
3. Rejoin only when a stable card and stable recording path are available
