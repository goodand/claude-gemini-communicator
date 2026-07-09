# Recovery

## Broken recording symptoms

- QuickTime says the file is incompatible
- local inspection shows zero duration
- local inspection shows zero video tracks

## Likely cause

The `simctl io recordVideo` file was not finalized correctly before use.

## Immediate next action

- stop retrying the broken file
- produce a new recording
- or share screenshots/JUnit if rerecording is not possible immediately

## Share gate

Only share a recording if:
- it opens in a player
- or local inspection confirms a readable video track and non-zero duration
