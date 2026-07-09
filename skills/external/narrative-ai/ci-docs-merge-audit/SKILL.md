---
name: ci-docs-merge-audit
description: Use when auditing whether CI, docs, README, env templates, Maestro docs, and GitHub-readiness changes are safe and coherent to merge in this repo. Triggers on requests like "CI/docs merge audit", "README/Actions review", "private GitHub prep review", and "docs-only mergeable?".
---

# CI Docs Merge Audit

Use this skill for non-runtime merge readiness around CI and docs.

## Scope

Typical files:
- `.github/workflows/*`
- `README.md`
- `.env.example`
- `.gitignore`
- `package.json`
- `docs/*`
- `.maestro/*`
- `scripts/maestro/*`

## When to use

Use it when:
- a branch mainly changes CI/docs
- GitHub/private repo prep is being reviewed
- README and product definition must be realigned

## Default audit

1. Check whether docs match the current product definition.
2. Check whether workflows are actually merge-ready, not just locally present.
3. Check ignore/env/template safety.
4. Flag anything that is still local-only but presented as repo-ready.

## Repo-specific focus

- This repo often changes product framing faster than README and checklists catch up.
- Distinguish:
  - repo-ready tracked files
  - local-only auth/config helpers
  - local docs that should not be committed
- For smoke reporting, distinguish:
  - structural runtime failure
  - assertion/copy drift
  - remote latency/cold-start behavior
- Do not present a slow Render `/health` as hard failure if it eventually returns the expected healthy payload.

## Known repeated issues

- README and checklist drift behind the actual product direction.
- Untracked or local-only files are sometimes described as if they were already repo-ready.
- Maestro smoke can fail on hero copy drift while the screen itself is still correct.
- Render health checks can be slow enough to be misread as hard backend failure.

## Files to read when needed

- `references/ci-docs-checks.md`
  - Read when deciding whether CI/docs scope is truly merge-ready or still local-only.
- `troubleshooting/ci-docs-drift-patterns.md`
  - Read when the same CI/docs disagreements keep recurring and you need concrete classification and recovery rules.
- `../shared/merge-audit-output-contract.md`
  - **Read before producing output.** Defines the `MergeAuditSlice` schema this skill must follow.

## Sibling handoff rules

| When you find this | Handoff to |
|---|---|
| Runtime code mixed into docs PR | `runtime-core-merge-audit` |
| PR noise (test_log, xcuserstate) | `artifact-noise-merge-audit` |

## Output checklist (MergeAuditSlice)

Return a `MergeAuditSlice` per the [shared contract](../shared/merge-audit-output-contract.md) with **scope: `ci-docs`**.

Scope-specific overrides:
- **proof_status**: always `not-applicable` (CI/docs have no runtime proof requirement)
