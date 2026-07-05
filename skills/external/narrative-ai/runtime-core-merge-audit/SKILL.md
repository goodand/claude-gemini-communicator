---
name: runtime-core-merge-audit
description: Use when auditing whether runtime-core JS changes are safe to merge in this repo, especially for main.js, HomeManager, PhotoService, bridge contracts, and user-visible flow changes around carousel speed or precious/result transitions. Triggers on requests like "runtime core merge 가능?", "핵심 동작 merge audit", "carousel path audit", and "main/HomeManager/PhotoService review before merge". Delete/report path → use delete-report-merge-audit instead.
---

# Runtime Core Merge Audit

Use this skill to judge whether runtime-core JS changes are mergeable.

## Scope

This skill covers **JS runtime paths only** (carousel, precious/result, bridge contracts):
- `main.js`
- `src/components/HomeManager.js`
- `src/services/PhotoService.js`

`ReportManager.js` is in scope only when its changes affect carousel or precious/result transitions. If delete → next-card → report is the primary concern, handoff to `delete-report-merge-audit`.

## When to use

Use it when:
- a branch changes the main user flow in JS (carousel, precious/result)
- carousel speed work touched runtime state
- precious actions were rewired in JS
- bridge contracts changed and JS behavior may drift

Do not use it for:
- **Native Swift plugin changes** → handoff to `native-ios-merge-audit`
- **PR noise / test_log churn** → handoff to `artifact-noise-merge-audit`
- **Delete/report path specifically** → handoff to `delete-report-merge-audit`
- backend-only changes
- docs/CI-only changes

## Default audit

1. Identify the user-visible flow that changed.
2. Check whether the branch preserves home -> precious -> result behavior and carousel transitions. (If delete/report is the primary concern, handoff to `delete-report-merge-audit` instead of auditing it here.)
3. Check for new best-effort async behavior that needs runtime proof.
4. Separate "code looks coherent" from "runtime evidence exists".

## Repo-specific focus

- Treat `main.js`, `HomeManager`, `PhotoService` as the JS runtime slice.
- `RecocolPhotos.ts` bridge calls are in scope only for the JS-side contract shape. Native-side policy belongs to `native-ios-merge-audit`.
- For this repo, `carousel speed` and `precious/result` transitions are this skill's primary user-facing paths. `delete recommendation` and `next-card` are owned by `delete-report-merge-audit`.
- Flag any change that silently turns a guaranteed path into a best-effort async path.

## Known repeated issues

- `recorded -> refresh` can look logically closed in code but still behave as a best-effort async path at runtime.
- A side-effect on `next card` or same-day suppression can hide in carousel changes — if found, handoff that concern to `delete-report-merge-audit`.
- Runtime-coherent code is often mixed with CI/docs or experiment residue, which hides the true merge risk.
- Copy drift or UI wording drift should not be mistaken for runtime-core breakage without a live screenshot.

## Sibling handoff rules

| When you find this | Handoff to |
|---|---|
| Native Swift policy changes in `RecocolPhotosPlugin.swift` / `PhotoAssetManager.swift` | `native-ios-merge-audit` |
| PR contains test_log, xcuserstate, experiment residue | `artifact-noise-merge-audit` |
| Delete/report/stats path is the primary concern | `delete-report-merge-audit` |
| CI/docs/README are the only changes | `ci-docs-merge-audit` |

## Files to read when needed

- `references/runtime-paths.md`
  - Read when you need the canonical runtime path map and repo-specific merge questions.
- `troubleshooting/repeated-runtime-risks.md`
  - Read when the same runtime merge doubts keep recurring and you need the previously observed issue-to-recovery patterns.
- `../shared/merge-audit-output-contract.md`
  - **Read before producing output.** Defines the `MergeAuditSlice` schema this skill must follow.

## Output checklist (MergeAuditSlice)

Return a `MergeAuditSlice` per the [shared contract](../shared/merge-audit-output-contract.md) with **scope: `runtime-core`**.
