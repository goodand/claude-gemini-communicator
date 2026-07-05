# Troubleshooting

## CoreSimulatorService connection invalid

Symptom:

- helper script fails while calling `xcrun simctl io <UDID> screenshot ...`
- error mentions `CoreSimulatorService connection invalid`

Observed cause in this workspace:

- direct shell `xcrun simctl io ... screenshot` worked
- the same call inside a sandboxed Python subprocess failed

Action:

1. Re-run the helper outside the sandbox.
2. Do not change capture logic until the permission boundary is ruled out.

## Home Screen Captured Instead Of Slide Viewer

Symptom:

- screenshot exists, but only the simulator home screen or Safari chrome is visible

Action:

1. Confirm the simulator is fully booted.
2. Re-open the target URL or viewer surface after boot completion.
3. Only then trigger the capture helper.

## Mixed Screenshot Sources

Symptom:

- screenshots in one dataset come from different simulators or different resolutions

Action:

1. Use one simulator and one UDID per run.
2. Restart the run if resolution or orientation changes mid-capture.
