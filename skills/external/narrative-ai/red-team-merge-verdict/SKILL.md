---
name: red-team-merge-verdict
description: Use when multiple code and audit findings need to be collapsed into one final merge decision for this repo, especially to decide merge now, split before merge, archive only, or merge after runtime validation. Triggers on requests like "최종 merge verdict", "red-team 판단", "지금 merge해도 돼?", and "audit 종합 결론".
---

# Red Team Merge Verdict

Use this skill to produce the final merge decision after other audits are done. This is the **terminal** skill in the merge-audit family — it consumes `MergeAuditSlice` outputs from sibling audit skills.

## When to use

Use it when:
- **multi-scope PR**: 2+ scopes changed and multiple `MergeAuditSlice` inputs need collapsing
- **ambiguous single-scope**: 1 slice exists but its verdict is uncertain and a formal decision is needed
- the team needs one clear merge/no-merge decision

Do not use it for:
- **first-pass audit** of any scope — run the appropriate audit skill first
- **clean single-scope PR**: when one audit skill already returned a clear `merge-ready` or `block` verdict, that slice IS the final answer — no red-team needed
- **root-cause debugging** → `troubleshooting-cot-2`

## Input requirements

Slice rules are scope-aware — see [shared contract](../shared/merge-audit-output-contract.md) for full field definitions.

### Scope-aware minimum slices
- **Single-scope PR** (e.g., ci-docs only, native-ios only): 1 relevant slice is sufficient to issue a verdict.
- **Multi-scope PR** (e.g., runtime + native): all relevant scope slices required (2+).
- **Noisy PR**: relevant scope slice + `artifact-noise` slice required when any slice reports `noisy-blocks-merge`.
- **Runtime proof gap**: if the critical path is only `logically-closed`, auto-downgrade to `merge-after-runtime-proof` is allowed without additional slices.

### Expected slice sources
| Scope | Source Skill | When Required |
|---|---|---|
| `runtime-core` | `runtime-core-merge-audit` | When JS runtime paths changed |
| `native-ios` | `native-ios-merge-audit` | When Swift plugin code changed |
| `delete-report` | `delete-report-merge-audit` | When delete/report/stats path changed |
| `ci-docs` | `ci-docs-merge-audit` | When CI/docs/README changed |
| `artifact-noise` | `artifact-noise-merge-audit` | When PR scope is wide or mixed |

### Missing scope handling
If a relevant scope was **not audited**, the verdict must:
1. Note the gap explicitly
2. Not assume the missing scope passes
3. Recommend running the missing audit before finalizing, OR downgrade to `merge-after-runtime-proof`

## Allowed verdicts

- `merge-now` — all slices are `merge-ready`, no gaps
- `merge-after-runtime-proof` — code is coherent, runtime proof is the only gap
- `split-before-merge` — useful code exists but PR scope must be narrowed
- `archive-only` — no product merge value, preserve as reference only

## Default process

1. Read all input `MergeAuditSlice` outputs. Verify each has the required fields (scope, proof_status, noise_status, blockers, evidence_paths, next_action, verdict).
2. Trust prior audit slices; do not re-open every code path unless slices conflict.
3. Separate product risk from PR hygiene risk.
4. Apply conflict resolution: if two slices disagree, the more conservative verdict wins.
5. Apply noise escalation: any slice with `noisy-blocks-merge` forces at least `split-before-merge`.
6. Apply proof hierarchy: `logically-closed` is weaker than `proven`. If the critical path is only `logically-closed`, prefer `merge-after-runtime-proof`.

## Repo-specific focus

- Prefer the smallest true verdict over a long recap.
- Runtime proof gaps matter more than stylistic concerns for this repo.
- If the branch has value but the PR is too wide, prefer `split-before-merge` rather than `archive-only`.

## Known repeated issues

- Good code often arrives with too much noise, so the real verdict is `split-before-merge`, not `reject`.
- Missing runtime proof is repeatedly the last blocker after code and CI already look good.
- Copy drift and slow remote health can inflate the severity of a branch if not classified correctly.
- Re-opening every audit slice from scratch wastes time when the existing slice verdicts already align.

## Files to read when needed

- `references/merge-audit-output-contract.md`
  - **Read first.** Defines the `MergeAuditSlice` and `MergeVerdict` schemas.
- `references/verdict-rules.md`
  - Read when collapsing multiple audit slices into one final merge call.
- `troubleshooting/verdict-escalation-patterns.md`
  - Read when repeated merge debates need a compressed issue-to-resolution pattern instead of a full re-audit.

## Output checklist (MergeVerdict)

Return a `MergeVerdict` per the [shared contract](../shared/merge-audit-output-contract.md#mergeverdictproduced-only-by-red-team-merge-verdict).
