# Parallel Preflight

- Confirm the input dataset rows are stable.
- Confirm the intended worker count matches the current session capability.
- Confirm the shard manifest exists or regenerate it before fanout.
- Confirm each worker packet owns one shard JSONL, one ledger JSON, and one `_responses/` directory.
- Confirm overlap checks are explicit in the phase manifest.
- Confirm the main agent remains the only owner of shared summaries and registries.
- Confirm the downstream auditor or commit manager is not triggered before worker completion evidence exists.
