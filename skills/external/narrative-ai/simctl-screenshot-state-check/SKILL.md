---
name: simctl-screenshot-state-check
description: Use when you need a fast truth check of the live iOS Simulator state for this repo, especially to confirm which simulator is booted, capture the current screen with simctl, compare stale handoff claims against reality, or inspect a UI checkpoint before continuing a demo/debug flow. This skill produces bounded screenshot evidence for downstream multimodal refinement or review, not final semantic interpretation.
---

# Simctl Screenshot State Check

Use this skill to verify the live simulator state before trusting a handoff, a subagent note, or a flaky UI assumption.

## When to use

Use it when:
- the current simulator screen must be checked before proceeding
- a handoff says one screen is open but that may be stale
- a demo flow failed and you need a fresh screenshot before retrying
- two simulators may be booted and you need to confirm the active one

Do not use it for:
- long demo recordings
- complete UX validation by itself
- backend-only debugging

## Default workflow

1. Confirm which simulator is booted. Prefer one booted device only.
2. Capture a fresh screenshot with `xcrun simctl io <udid> screenshot ...`.
3. Open the screenshot with `view_image`.
4. State the actual current screen in plain terms.
5. Only then continue with any recovery or next automation step.

## Repo-specific rules

- Prefer `iPhone 17` unless the user asked for another device.
- Use this before trusting stale subagent runtime notes.
- If the screen differs from the handoff, update the plan from the live screen, not from the stale note.
- Use this immediately when a Maestro assertion fails on copy text. First confirm whether the screen is correct before changing the flow or blaming runtime behavior.

## Output checklist

Return:
- booted device / UDID
- screenshot path
- actual visible screen
- one recommended next action
