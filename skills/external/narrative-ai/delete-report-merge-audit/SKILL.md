---
name: delete-report-merge-audit
description: Use when auditing whether delete flows and report/stat reflection are safe to merge in this repo, especially for delete confirmation, next-card behavior, detox_logs, user_stats, and ReportManager updates. Triggers on requests like "delete/report merge audit", "리포트 반영 확인", "삭제 후 다음 카드", and "stats/report path review".
---

# Delete Report Merge Audit

Use this skill to audit the delete path and report/stat reflection path.

## When to use

Use it when:
- delete behavior changed
- report calculation changed
- stats logging changed
- a branch claims delete/report is fixed

## Default audit

1. Trace delete trigger to native delete call.
2. Check follow-up mutation recording and refresh.
3. Check report/stats sources and expected UI reflection.
4. Separate logical closure from runtime evidence.

## Repo-specific focus

- This repo treats `delete -> next card -> report` as a primary proof path.
- Separate UI logic from storage/stat reflection.
- A branch should not be called merge-ready if delete is coherent but report reflection is still unproven.

## Known repeated issues

- Code can look closed while `report` reflection is still only logically inferred, not runtime-proven.
- `delete` may succeed, but `next card` or report navigation can still be flaky in the live app.
- It is easy to confuse UI transition success with actual `detox_logs` or `user_stats` correctness.
- The fastest recovery is often to prove `delete/report` as its own tail instead of restarting the full flow.

## Files to read when needed

- `references/delete-report-checks.md`
  - Read when checking the full delete/report path and runtime proof requirements.
- `troubleshooting/delete-report-proof-gaps.md`
  - Read when delete/report keeps being "almost proven" and you need the repeated gap patterns and recovery moves.
- `../shared/merge-audit-output-contract.md`
  - **Read before producing output.** Defines the `MergeAuditSlice` schema this skill must follow.

## Sibling handoff rules

| When you find this | Handoff to |
|---|---|
| Broader runtime path (carousel, precious/result) also changed | `runtime-core-merge-audit` |
| Native mutation handling changed | `native-ios-merge-audit` |
| PR has noise mixed with delete/report code | `artifact-noise-merge-audit` |

## Output checklist (MergeAuditSlice)

Return a `MergeAuditSlice` per the [shared contract](../shared/merge-audit-output-contract.md) with **scope: `delete-report`**.
