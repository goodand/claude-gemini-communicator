# Cross-Repo Product Review Knowledge Base

## Canonical Design Takeaways

1. Product intent lock precedes file reading.
2. Review findings stay severity-ranked and file-anchored.
3. Codex closure must be verified from current code-state, not prior session state.
4. Residual 1-2 item sets default to direct expert closure.
5. Async/API surface changes trigger specialist follow-up instead of silent absorption.

## Proven Pattern

- source pattern: external/downstream product repo review
- repeated flow: expert review → Codex bounded fix → expert re-verification → residual checklist → repeated-pattern capture
- proven convergence sample: 15 findings → 3 residual → 2 residual → direct expert closure

## Promoted Inputs

- repeated task: `TASK_cross_repo_product_review_and_codex_handoff.md`
- absorbed issue: `ISSUE_partial_structural_fix_same_class_different_fields.md`

## Reuse Target

- downstream surface repos that need milestone quality review before integration
- repos where expert review and Codex fix operate as separate roles
