---
name: simctl-recording-finalization
description: Use when recording iOS Simulator video with simctl and you must prevent or diagnose broken movie artifacts, especially to start recording safely, stop it without corrupting the file, verify the artifact after capture, or explain why a large file is still unplayable. Triggers on requests like "녹화 finalize", "영상이 안 열려", "simctl recordVideo", "깨진 mp4", and "video track 0".
---

# Simctl Recording Finalization

Use this skill to avoid and diagnose broken simulator video recordings.

## When to use

Use it when:
- starting a new `simctl io recordVideo` capture
- stopping a recording cleanly
- checking whether a recorded file is actually playable
- QuickTime says the file is incompatible

Do not use it for:
- generic screenshot capture
- demo flow logic by itself
- media library seeding

## Default workflow

1. Start recording before the runtime flow begins.
2. Note the recorder process and output path.
3. Stop recording gracefully when possible.
4. Wait for the recorder process to exit.
5. Verify the artifact before sharing.

## Verification rule

Do not trust:
- file existence
- file size
- file extension

Trust only a playable artifact or a confirmed readable video track.

## Repo-specific findings

- We observed `.mp4` / `.mov` files that existed and were large but had:
  - `duration = 0`
  - `videoTracks = 0`
- In those cases, the recording artifact was broken and should not be shared.

## Recovery

If the artifact is broken:
1. Preserve it only as a failed artifact reference.
2. Do not keep trying to open the same file.
3. Re-record or fall back to a screenshot/JUnit evidence bundle.

## Output checklist

Return:
- recording output path
- whether stop was graceful
- whether the file is playable
- if broken, the likely cause and next recovery action

