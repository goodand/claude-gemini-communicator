---
name: ios-demo-capture-loop
description: iOS Operation family의 orchestration owner. Full demo run을 오케스트레이션하고 proof bundle을 수집한다. 개별 작업(recording, screenshot, tail recovery, perf measurement)은 각 sibling specialist를 직접 사용하라. Collected proof bundles may be handed to multimodal interpretation skills for downstream refinement or review.
---

# iOS Demo Capture Loop

Use this skill for repeated iOS simulator demo recording and runtime proof collection in this repo.

## When to use

Use it when the user wants to:
- record a full demo video on iOS Simulator
- capture result, report, and mypage in one flow
- let the user handle only Google login while the agent does the rest
- reseed specific photos into the simulator with `simctl addmedia`
- collect screenshots, JUnit, and video artifacts for demo approval
- turn a runtime validation flow into a repeatable demo runbook

Do not use it for:
- code-only reviews with no simulator runtime
- backend-only debugging
- architecture analysis with no recording or evidence capture
- merge readiness judgment → use merge-audit family instead

## Delegation rules

This skill **orchestrates** the full demo flow but **delegates** atomic operations:

| Operation | Delegate to |
|---|---|
| Live screen truth check before or during a flow | `simctl-screenshot-state-check` |
| Recording start/stop/verify artifact health | `simctl-recording-finalization` |
| Tail retry from current screen (not full restart) | `ios-runtime-tail-recovery` |
| Launch KPI measurement with 5-run stats | `xcode-perf-experiment-loop` |

This skill retains: **full run orchestration** (prelogin → login handoff → postlogin → artifact summary) and **artifact collection** (mp4, screenshots, JUnit, checklist).

> Captured proof bundle의 semantic interpretation/refinement는 `multimodal-evidence-refinement-loop`, review surface normalization은 `image-text-cot-review`를 사용한다.

## Default workflow

1. Use one simulator only. Prefer `iPhone 17` unless the user asks otherwise.
2. Confirm the active UDID before any run. Avoid mixed evidence from multiple booted simulators.
3. If the demo depends on seeded photos, re-run `xcrun simctl addmedia` before the recording.
4. Ensure recording is alive via `simctl-recording-finalization` before starting the product flow.
5. Split the flow into:
   - prelogin
   - manual login handoff
   - postlogin tail
6. Let the user do Google login if credentials or OTP are involved. Resume only after the user says login is complete.
7. Prefer Maestro for deterministic UI steps. For quick checkpoints, delegate to `simctl-screenshot-state-check`.
8. For this repo, the high-value demo proof is:
   - home carousel first display
   - one delete flow
   - report reflection
   - one `소중해 -> 기억 분석하기 -> 결과`
   - home return / same-day refresh
   - mypage confirmation
9. If one long flow is flaky, keep the recording alive and retry only the unstable tail once.
10. Save all artifacts and report exact paths:
   - mp4
   - screenshots
   - junit/xml
   - checklist/report markdown
11. Do not commit temporary videos, `/tmp` flows, or local-only auth/media setup unless the user explicitly asks.

## Repo-specific rules

- Keep `main` as the demo baseline unless the user explicitly asks for another branch.
- `docs/demo-checklist.md` can stay local-only unless the user asks to commit it.
- `ios/App/App/credentials.plist` is local-only and should not be committed.
- Prefer existing wrappers:
  - `./scripts/maestro/maestro.sh`
  - `xcrun simctl`
  - `test_log/scripts/run_perf_trace_measurements.sh`

## Patch philosophy

- Update this workflow only from live smoke evidence, not from stale assumptions.
- Treat the minimum smoke surface for this repo as:
  - frontend build
  - iOS simulator build
  - backend `/health`
  - one Maestro smoke flow
- If Maestro fails only because a marketing/hero copy assertion drifted, classify it as a patch-level flow update, not as a product/runtime failure.
- Prefer stable structural anchors over brittle hero text when choosing demo or smoke assertions.
- Treat slow remote health checks as possible cold-start behavior before classifying the backend as down.

## Known failure patterns

- `소중해` button tap can be flaky on the carousel. Re-check the current card and retry with a more stable selector or point tap.
- A selected card can open input with a blank image area. In that case, treat the current card as unstable and reselect before recording the final result flow.
- Some daily curation cards are poor `소중해` demo targets. Placeholder-like or unstable cards can fail before `Meaning` or hang before the result screen. Prefer a visibly normal photo card before attempting the record/result path.
- Delete flow does not always auto-navigate to report. When needed, return to home first and then tap `리포트`.
- OAuth fallback can drift to `Site URL` if Supabase mobile redirect config is wrong. Verify mobile deep link settings before blaming the app flow.
- `simctl io recordVideo` output can be large but still unusable if the recording process is killed abruptly. Validate the artifact before sharing; if it has no readable video track, do not treat it as a usable demo file.
- A stale subagent/runtime note can be wrong about the current simulator state. Before acting on a handoff, re-check the live screen and active recording process.
- Render-hosted backend checks can take tens of seconds before returning healthy. Do not abort the whole smoke run just because `/health` is slow.
- A Maestro smoke failure on text like `비움으로 선명해지는 당신의 기록` can be a copy drift only. Re-check the actual screen and replace the assertion with a more stable anchor before escalating.

## Files to read when needed

- `references/workflow.md`
  - Read when preparing a fresh demo run, choosing the split between manual and automated steps, or deciding how to recover from a flaky tail.
- `troubleshooting/`
  - Read when the demo run is blocked by unstable cards, broken recordings, stale simulator state, flaky CTA taps, or split-tail recovery decisions.

## Output checklist

Every demo run summary should state:
- simulator name and UDID
- whether media was reseeded
- whether login was manual or automated
- exact flow order used
- output video path
- screenshot and junit paths
- which UX checkpoints were proven
- which checkpoints were split into separate tails, if any
