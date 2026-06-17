# Codex Handoff Prompt Template

Use this template after the expert review has already classified findings.

```md
You are fixing bounded product-review findings in <repo>.

Product intent:
- <1-2 lines>

Non-goals:
- <explicit exclusions>

Findings to fix:
1. <severity> <file:line> <problem> <expected correction>
2. <severity> <file:line> <problem> <expected correction>

Requirements:
- preserve existing product boundaries
- do not broaden scope
- rerun relevant validation
- report residual risks separately from completed fixes
```
