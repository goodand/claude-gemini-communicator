# Post-Restore Verification

- Recompute backup-vs-current relative path diff for the restored subtree.
- Verify backup-based missing count is zero or explain every remaining gap.
- Verify newer current files remained present after the restore.
- Open representative restored files and confirm body content, not just path existence.
- Report recovered counts, preserved extra counts, excluded noise, and unresolved gaps.
- If session-log or donor evidence was used, confirm workspace provenance for every promoted file.
