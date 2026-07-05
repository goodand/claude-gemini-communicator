---
name: artifact-noise-merge-audit
description: Use when auditing whether a branch or PR contains artifact noise, local-only files, experiment logs, test_log churn, xcuserstate files, or unrelated tooling changes that should be excluded before merge. Triggers on requests like "noise audit", "PR scope 줄여", "artifact cleanup before merge", and "이 브랜치 뭐 빼야 해?".
---

# Artifact Noise Merge Audit

Use this skill to classify what should be kept, removed, archived, or split before a merge. This skill does NOT judge product code correctness — it only judges PR scope hygiene.

## When to use

Use it when:
- a PR is too wide
- logs, screenshots, test output, local config, or worktree residue are mixed into a branch
- you need a classified file list before opening or merging a PR

Do not use it for:
- runtime logic review → `runtime-core-merge-audit`
- native plugin review → `native-ios-merge-audit`
- CI/docs coherence → `ci-docs-merge-audit`

## Default audit

1. Separate product code from experiment output.
2. Separate repo-worthy automation from local-only helper files.
3. Mark archive/reference material versus merge scope.
4. Classify every file into one of: **keep**, **archive**, **remove**, **split**.

## Classification rules (4-way)

| Classification | Meaning | Action |
|---|---|---|
| **keep** | Product code or repo-worthy automation that belongs in this PR | Merge as-is |
| **archive** | Valuable reference material (experiment notes, perf results) that should be preserved but not in `main` | Move to archive branch or local backup before merge |
| **remove** | Noise with no future value (build artifacts, temp files, stale locks) | Delete from branch |
| **split** | Useful code that is correct but unrelated to this PR's purpose | Move to a separate PR |

## Category-specific rules

### `test_log/**`
- Raw run directories → **remove** (reproducible from scripts)
- `summary.tsv` with unique experiment results → **archive**
- Measurement scripts (`run_perf_trace_measurements.sh`) → **keep** if referenced by SKILL.md, else **split**

### Screenshots and media
- Demo proof screenshots referenced by checklist → **keep**
- Ad-hoc debugging screenshots → **remove**
- Recording artifacts (`.mp4`, `.mov`) → **archive** if playable, **remove** if broken

### `.xcuserstate` and Xcode local state
- Always **remove**. No exceptions.

### Local helpers and config
- `.env`, `credentials.plist`, auth tokens → **remove** (security risk)
- Local-only shell scripts not referenced by any skill or CI → **split** or **remove**
- Skill helper scripts referenced by SKILL.md → **keep**

### Experiment-only scripts or notes
- Notes with conclusions that inform future work → **archive**
- One-off throwaway experiments → **remove**

## Known repeated issues

- Valuable product code gets buried under `test_log`, screenshots, and local tooling residue.
- Local skill/auth/config helpers look important on the current machine but should not ride along with product merges.
- A branch can be technically correct and still need splitting because the PR scope is too noisy.
- Archive/reference material should be preserved before deletion, but not merged into `main`.

## Sibling handoff rules

| When you find this | Handoff to |
|---|---|
| Product code that needs runtime review | `runtime-core-merge-audit` or `native-ios-merge-audit` |
| CI/docs that need coherence review | `ci-docs-merge-audit` |
| Noise is entangled with product code and you cannot classify without understanding runtime | `runtime-core-merge-audit` first, then re-run noise audit |

## Files to read when needed

- `references/noise-patterns.md`
  - Read when you need repo-specific keep/remove guidance and examples of previous noisy PRs.
- `troubleshooting/noise-reduction-patterns.md`
  - Read when you need concrete repeated keep/remove decisions and the usual cleanup path before merge.
- `../shared/merge-audit-output-contract.md`
  - **Read before producing output.** Defines the `MergeAuditSlice` schema this skill must follow.

## Output checklist (MergeAuditSlice)

Return a `MergeAuditSlice` per the [shared contract](../shared/merge-audit-output-contract.md) with **scope: `artifact-noise`**.

Scope-specific overrides:
- **proof_status**: always `not-applicable`
- **classification_map**: required (see contract for `keep`/`archive`/`remove`/`split` schema)
