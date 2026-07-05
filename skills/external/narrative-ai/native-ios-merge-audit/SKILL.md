---
name: native-ios-merge-audit
description: Use when auditing iOS native plugin changes for merge safety in this repo, especially around RecocolPhotosPlugin, PhotoAssetManager, daily curation cache, thumbnail fallback, photo summary hydration, delete, and native mutation handling. Triggers on requests like "native merge audit", "RecocolPhotosPlugin review", "iOS plugin merge 가능?", and "daily curation swift path check".
---

# Native iOS Merge Audit

Use this skill to judge whether native iOS plugin changes are safe to merge.

## Scope

Typical files:
- `ios/App/App/Plugins/RecocolPhotosPlugin/RecocolPhotosPlugin.swift`
- `ios/App/App/Plugins/RecocolPhotosPlugin/RecocolPhotosPlugin.m`
- `ios/App/App/Plugins/RecocolPhotosPlugin/PhotoAssetManager.swift`

## When to use

Use it when:
- daily curation policy changed in Swift
- thumbnail fallback changed
- native delete or summary methods changed
- bridge contracts depend on native responses

Do not use it for:
- **JS-only runtime changes** → handoff to `runtime-core-merge-audit`
- **Delete/report path specifically** → handoff to `delete-report-merge-audit`
- **PR noise / test_log churn** → handoff to `artifact-noise-merge-audit`
- **CI/docs/README only** → handoff to `ci-docs-merge-audit`

## Default audit

1. Check cache/applied/pending/mutation behavior.
2. Check thumbnail and image-loading fallback behavior.
3. Check native contract shape against JS expectations.
4. Flag card or asset states that can become unstable demo targets.

## Repo-specific focus

- `RecocolPhotosPlugin.swift` is the policy center for daily curation.
- `PhotoAssetManager.swift` is the critical point for thumbnail/original image preparation.
- Prefer contract safety over refactor elegance. Small native changes can destabilize JS flows.

## Known repeated issues

- `applied/pending/mutation` policy can be coherent in Swift but still create unstable demo cards or stale home refresh.
- Thumbnail fallback is easy to regress silently; a branch may still compile while producing blank or weak demo targets.
- Rejected preheat or large tracing experiments can look attractive but still be wrong for product merge scope.
- Native changes often have wider runtime impact than the diff size suggests.

## Files to read when needed

- `references/native-checks.md`
  - Read when checking native cache rules, image loading, and JS bridge expectations.
- `troubleshooting/native-instability-patterns.md`
  - Read when native cache/image behavior keeps raising the same merge doubts and you need concrete issue-to-recovery guidance.
- `../shared/merge-audit-output-contract.md`
  - **Read before producing output.** Defines the `MergeAuditSlice` schema this skill must follow.

## Sibling handoff rules

| When you find this | Handoff to |
|---|---|
| JS-side bridge behavior drifted from native contract | `runtime-core-merge-audit` |
| PR has test_log or xcuserstate noise | `artifact-noise-merge-audit` |
| Delete/report path is the primary concern | `delete-report-merge-audit` |

## Output checklist (MergeAuditSlice)

Return a `MergeAuditSlice` per the [shared contract](../shared/merge-audit-output-contract.md) with **scope: `native-ios`**.
