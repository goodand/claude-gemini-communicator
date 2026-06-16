# Legacy-Safe Handoff Clause

worker/subagent packet에 그대로 넣는 보존 우선 규칙.

## Canonical Clause

```text
Preservation rules are mandatory.

- Do not delete, move, rename, or overwrite content unless you first preserve the prior content in a legacy/ or timestamped backup location.
- Do not touch any existing legacy/ directory unless the user explicitly asks for legacy maintenance.
- If you think a file must be replaced, create a preserved copy first and report the exact backup path.
- No cleanup, no removal, and no destructive edits by default.
- If lifecycle work is unavoidable, hand off to artifact-lifecycle-manager rules before applying the change.
```

## When to attach

- file replacement
- rename or move
- cleanup or deduplication
- archive split
- risky generated artifact rewrite

## Why

- `allowed_paths`만으로는 보존 우선 원칙이 강제되지 않는다
- `do not touch legacy/`만으로는 overwrite 이전 backup 의무가 생기지 않는다
- worker가 범위를 잘 지켜도 destructive change를 먼저 하면 복구가 어려워진다

## Related

- [artifact-lifecycle-manager](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/artifact-lifecycle-manager/SKILL.md)
