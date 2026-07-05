# Workflow

## Standard run order

1. Confirm only one simulator is booted.
2. Reseed media if the demo depends on specific sample photos.
3. Start `simctl io ... recordVideo`.
4. Run prelogin flow if needed.
5. Pause for manual Google login.
6. Resume with postlogin flow:
   - home
   - delete
   - report
   - precious
   - result
   - home
   - mypage
7. Stop recording cleanly.
8. Verify the video file exists and is non-empty.
9. Save screenshots and junit under `build/maestro-results`.
10. Summarize evidence in a short markdown note if the run is approval-facing.

## Recovery rules

- If a full flow fails before login, restart the run.
- If a full flow fails after login, keep the recording alive and retry only the tail once.
- If result generation hangs, separate backend health verification from UI state verification before retrying.
- If `기억을 분석하는 중...` persists, check whether the selected card opened with a blank image area. If so, reselect a different card before blaming backend generation.
- If report and mypage are already proven, do not rerun them unnecessarily unless the user wants one single continuous video.
- If the current home card set changes into unstable or placeholder-like images, do not force the same full flow again. Split the proof into:
  - delete/report tail
  - result/mypage tail
  and only rejoin them if a stable card is available.
- After every recording, verify the file is actually playable. A large file size alone is not enough.
- Prefer graceful recording stop when possible. If the recording artifact is corrupted, fall back to a screenshot-based evidence bundle or re-record rather than sharing a broken video.

## Evidence paths

- Video: usually `/tmp/*.mp4`
- Screenshots: `build/maestro-results/screenshots/`
- JUnit: `build/maestro-results/*.xml`
- Demo notes: `docs/demo-checklist.md` or `test_log/*.md`
