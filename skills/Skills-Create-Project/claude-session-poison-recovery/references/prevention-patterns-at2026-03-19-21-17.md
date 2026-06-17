# Prevention Patterns

## 1. Batch output isolation

Use:

```bash
bash scripts/safe_batch_run.sh logs/run_latest.log -- python3 some_eval.py
```

Default behavior:
- full stdout/stderr goes only to the log file
- terminal receives summary only

## 2. Stream sanitize

Use `scripts/sanitize_stream.py` when long output may contain:
- ANSI CSI sequences
- carriage returns
- NUL bytes
- invalid UTF-8 fragments

## 3. Model/API input sanitize

Use `sanitize_utils.py` before `json.dumps(...)` for payloads that can contain long tool output, editor text, or other uncontrolled strings.

## 4. Artifact write sanitize

Use `safe_json_write(...)` or `safe_json_dumps(...)` before writing JSON/JSONL artifacts that may later be read back into chat context.

## 5. Sniffer only when needed

`claude_sniffer.py` is a diagnostic tool. Use it to capture the next bad request, not as the first step for every failure.
