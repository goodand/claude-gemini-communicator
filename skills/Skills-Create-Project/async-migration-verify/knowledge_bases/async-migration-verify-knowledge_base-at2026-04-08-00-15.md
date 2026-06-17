# Async Migration Verify Knowledge Base

## Canonical Design Takeaways

1. Dead imports often survive functional migrations.
2. Sync/async duplication creates new drift points.
3. Concurrency guard without UX feedback is still a user-facing bug.
4. Malformed-input and missing-file tests must be added explicitly.
5. TOCTOU cleanup should replace pre-check + read patterns with try/catch.
6. File path should appear in migration error messages.

## Proven Pattern

- source pattern: sync file I/O changed to async host/persistence flow
- proven sample: `decision-session-artifacts.js` migration with 6 checkpoints all exercised

## Absorbed Inputs

- repeated task: `TASK_async_migration_verification.md`
- absorbed issue: `ISSUE_concurrency_guard_without_ux_feedback.md`
- absorbed issue: `ISSUE_dead_import_after_api_migration.md`
- absorbed issue: `ISSUE_sync_async_logic_duplication_drift_point.md`
- absorbed issue: `ISSUE_guard_filter_set_missing_alias_forms.md`
- absorbed task lane: `TASK_decision_contract_cross_field_test_expansion.md`
  - escalation trigger: if contract-test expansion runs independently (no async migration context) 3+ times, promote to standalone skill
