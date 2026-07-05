---
name: ios-runtime-tail-recovery
description: Use when a full iOS demo or runtime validation flow already progressed partway and only the unstable tail needs to be recovered, especially for delete-report tails, result-mypage tails, split-tail recovery, or re-entry from the current live screen instead of restarting the entire run. Triggers on requests like "tail만 다시", "여기서부터 이어서", "리포트부터 다시", "마이페이지까지 이어서", and "split tail recovery".
---

# iOS Runtime Tail Recovery

Use this skill when restarting the whole demo is wasteful and the remaining proof can be recovered from the current screen.

## When to use

Use it when:
- login/onboarding already succeeded
- recording is already running
- only delete/report or result/mypage proof is still missing
- a full flow failed on one unstable card and you want to salvage the rest

Do not use it for:
- first-time full demo setup
- simulator boot/setup from scratch
- branch/code review work

## Core idea

Split unstable full flows into smaller tails:
- `delete -> home/report`
- `result -> home -> mypage`

Only restart the whole demo if the failure happened before the useful runtime state was reached.

## Default workflow

1. Check the current live screen first.
2. Identify what proof is already captured.
3. Build the smallest tail that closes the missing proof.
4. Prefer explicit navigation over assumed auto-navigation.
5. Retry the unstable tail once.
6. If the selected card is unstable, reselect before retrying the result path.

## Repo-specific rules

- `리포트` should be tapped explicitly after delete if auto-navigation is unreliable.
- `소중해` can be card-dependent; if the input screen opens blank, abandon that card and reselect.
- Keep recordings alive while retrying tails if the existing recording is still valid.

## Known tails

- `home -> delete -> report`
- `home -> precious -> result -> home`
- `home -> mypage`
- `report -> home -> mypage`

## Output checklist

Return:
- current live screen
- already-proven screens
- chosen tail
- whether a second retry is justified

