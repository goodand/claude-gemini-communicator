# Async Migration Implementation Checklist

1. Run `scripts/scan_dead_imports.sh <target>`.
2. Run `scripts/scan_sync_async_duplication.sh <target>`.
3. Verify host-side concurrent save/load semantics and visible busy feedback.
4. Add or update malformed-input and missing-file tests.
5. Check for `existsSync -> readFileSync` style residue and replace with async try/catch.
6. Ensure errors include the file path.
7. If the migrated module owns contract validation, expand tests for changed cross-field semantics.
8. Escalation trigger: if step 7 is executed independently (no async migration context) 3+ times, promote `decision-contract-test-expansion` to a standalone skill.
