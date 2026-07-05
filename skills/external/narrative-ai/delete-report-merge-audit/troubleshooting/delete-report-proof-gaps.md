# Delete Report Proof Gaps

## Delete works, report still unproven

### Symptom

- Delete flow is coherent in code
- Report or stats reflection has not been proven in runtime

### Recovery

1. Do not call the branch merge-ready yet.
2. Run a focused `delete -> report` proof instead of a full demo.

## Next card appears, stats may still be wrong

### Symptom

- UX looks correct after delete
- Underlying `detox_logs` or `user_stats` may still be wrong or partial

### Recovery

1. Separate UI success from stat-storage success.
2. Ask for evidence of both, not just one.

## Auto-navigation assumption causes false failure

### Symptom

- Reviewer expects report to open automatically
- The product actually requires explicit navigation

### Recovery

1. Use explicit `리포트` navigation in proof flows.
2. Judge correctness on reflected data, not on assumed navigation style.
