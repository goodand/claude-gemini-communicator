# Cross-Repo Product Review Knowledge Base

## Proven Pattern

- source pattern: external/downstream product repo review
- repeated flow: expert review → Codex bounded fix → expert re-verification → residual checklist → repeated-pattern capture
- proven convergence sample: 15 findings → 3 residual → 2 residual → direct expert closure

## Stable Invariants

1. product intent lock is mandatory
2. findings must be severity-ranked and file-anchored
3. Codex fix closure requires current code-state reread
4. residual 1-2 items favor direct expert closure
5. async/API surface changes require specialized follow-up review

## Promoted Inputs

- repeated task: `TASK_cross_repo_product_review_and_codex_handoff.md`
- absorbed issue: `ISSUE_partial_structural_fix_same_class_different_fields.md`

## Reuse Target

- any downstream surface repo that needs milestone quality review before integration
- any repo where expert review and Codex fix operate as separate roles
