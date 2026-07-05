# Troubleshooting

## Network Or Sandbox Failure

Symptom:

- the local runner cannot reach the OpenAI Responses API
- the run fails before any record completes

Action:

1. Confirm the API key is available through environment or `.env`.
2. Re-run outside the sandbox if the failure is due to restricted network access.
3. Keep the smoke test to one image before scaling out.

## Dataset JSONL Path Failure

Symptom:

- `--dataset-jsonl` is provided but images are not found

Action:

1. Confirm each row has `image_path`.
2. Confirm the referenced file still exists locally.
3. Fix the dataset JSONL rather than overriding paths manually in the prompt.
