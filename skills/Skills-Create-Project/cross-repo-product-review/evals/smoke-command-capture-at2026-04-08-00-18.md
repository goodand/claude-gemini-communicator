# Smoke Command Capture — Cross-Repo Product Review

- recorded_at: `2026-04-08T00:18:20+09:00`
- status: `valid`
- label: `cross-repo-review-file-classifier`
- expected_status: `valid`

## Command

```bash
python3 scripts/review_file_classifier.py package.json src/extension.js src/decision/webview-client.js src/test/suite/smoke.test.js
```

## Result

- exit_code: `0`
- stderr: empty
- stdout contained canonical role buckets:
  - `package.json -> host_entry`
  - `src/extension.js -> host_entry`
  - `src/decision/webview-client.js -> webview_render`
  - `src/test/suite/smoke.test.js -> tests`

## Interpretation

- canonical role classification CLI works on representative review paths
- this is the primary runnable smoke for the reusable script owned by the skill
