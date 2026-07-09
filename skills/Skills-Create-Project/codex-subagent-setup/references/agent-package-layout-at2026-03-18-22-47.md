# Agent Package Layout

- recorded_at: `2026-03-18-22-47`
- purpose: `directory-per-agent 구조를 고정`

## Canonical layout

```text
agents/
  <role>/
    AGENT.md
    knowledge_bases/
    scripts/
    references/
    bridges/
```

## Why this layout

- `AGENT.md`: role definition entrypoint
- `knowledge_bases/`: role-specific design takeaways
- `references/`: context links, tool capability policy, local notes
- `bridges/`: handoff contract and packet shape
- `scripts/`: future automation slot; currently optional placeholder

## Policy

- flat `agents/*.md`는 쓰지 않는다
- runtime nickname은 file-backed role path를 대체하지 않는다
- tool/permission 정보는 별도 reference file에 둔다
