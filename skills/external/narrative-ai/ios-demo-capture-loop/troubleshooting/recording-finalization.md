# Recording Finalization

## Symptom

- A `.mp4` or `.mov` file exists and may even be large
- QuickTime Player says the file is incompatible
- Local inspection shows:
  - `duration = 0`
  - `videoTracks = 0`

## Most Likely Cause

The `simctl io recordVideo` process did not finalize the movie correctly.

In practice, this usually means the recording process was stopped too abruptly or the workflow moved on before the recording process had fully exited.

## Repo Rule

- Do not trust file size alone.
- After recording, verify the artifact before sharing.
- Prefer graceful stop and wait for the recorder process to exit cleanly.

## Recovery

1. Do not keep trying to open the broken file.
2. Preserve the path only as a failed artifact reference.
3. Use screenshots + JUnit + a fresh rerecord if a client-share artifact is still needed.
4. If a rerecord is required, keep the recording process lifecycle isolated from the Maestro flow lifecycle.

## Notes from This Repo

- `simctl io help` states that recording is finalized only after stop and in-flight frame processing complete.
- We observed broken artifacts that looked like QuickTime movies but had no readable video track.
