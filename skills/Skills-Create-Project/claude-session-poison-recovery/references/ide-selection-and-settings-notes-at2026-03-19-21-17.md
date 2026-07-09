# IDE Selection and Settings Notes

## What is verified

- repeated `Selected N lines from ... in Visual Studio Code` is a strong local signal that the editor selection is being injected into request context
- closing the offending editor tab can unblock the poisoned request loop even when the on-disk markdown file itself is UTF-8 clean
- official GitHub issue evidence confirms that Claude Code's VS Code integration can pass selection context and that this feature can regress; see [official-github-corroboration-at2026-03-19-21-34.md](official-github-corroboration-at2026-03-19-21-34.md)

## What is not globally safe to assume

- an exact settings key such as `includeIdeSelection` is not officially verified here and must be confirmed in the actual runtime before relying on it
- local package search can fail to find the key if the running app version differs from the inspected CLI install
- the exact banner string `Selected N lines from ... in Visual Studio Code` is a strong local signal, not an official string contract

## Hard safety rule

Never do this:

```bash
echo '{"includeIdeSelection": "never"}' >> ~/.claude/settings.json
```

Reason:
- this appends a second JSON object and corrupts `settings.json`

## Safe pattern if a key is verified for your runtime

```bash
python3 - <<'PY'
from pathlib import Path
import json
p = Path.home() / '.claude' / 'settings.json'
text = p.read_text(encoding='utf-8') if p.exists() else '{}'
data = json.loads(text) if text.strip() else {}
verified_key = 'replace-with-runtime-verified-key'
data[verified_key] = 'replace-with-runtime-verified-value'
p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
PY
```

Use this only after you verify that the exact key/value pair is supported by the actual app/runtime you are using.
