# Worker Preflight

- Confirm the packet contains exactly one `job_id` and one `image_id`.
- Confirm the image row resolves from canonical state.
- Confirm the worker owns exactly one ledger family.
- Confirm required MCPs are available before starting generation.
- Confirm raw evidence will be written to a worker-owned path.
- Confirm the worker will not write approvals, shared summaries, or commit mutations.
