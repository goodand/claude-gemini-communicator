# Subagent Preservation Rule

subagent에게 구현을 맡길 때는 범위 제한과 별도로 보존 우선 규칙을 handoff contract에 명시한다.

## Rule

1. 삭제, 이름변경, 이동, overwrite는 기본 금지다.
2. 기존 내용을 바꿔야 하면 먼저 `legacy/` 또는 timestamped backup으로 보존한다.
3. 기존 `legacy/` 디렉토리는 read-only archive로 취급한다.
4. lifecycle 작업이 필요하면 직접 처리하지 말고 [artifact-lifecycle-manager](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/artifact-lifecycle-manager/SKILL.md) 규칙으로 넘긴다.
5. subagent done-definition에는 아래 둘이 함께 들어가야 한다.
   - backup path report
   - destructive edit 금지 또는 preservation-first 확인

## Minimal Handoff Addendum

```text
Preservation-first rule:
- no delete/move/rename/overwrite without backup first
- legacy/ is read-only archive
- if replacement is unavoidable, report the exact backup path
- lifecycle work must follow artifact-lifecycle-manager
```

## Apply To

- bounded subagent delegation
- multi-worker worktree dispatch
- packet-based worker execution

## Related

- [agent-task-packet](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/SKILL.md)
- [artifact-lifecycle-bridge-at2026-03-16-23-58.md](artifact-lifecycle-bridge-at2026-03-16-23-58.md)
