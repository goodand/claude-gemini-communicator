# Progressive Context Routing

- recorded_at: `2026-03-18-22-47`
- purpose: `agent별로 다른 context를 파일 링크로 점진 주입하는 규칙`

## Routing order

1. top-level setup context
2. target agent `AGENT.md`
3. target agent `references/context-links-*.md`
4. target agent `references/tool-capability-policy-*.md`
5. target agent `bridges/*handoff-contract*.md`
6. only then inject local code or artifact links from that agent package

## Core rule

전체 codebase를 모든 subagent에 주지 않는다. 필요한 file link만 markdown으로 전달한다.

## Exception

`context-broker`만 full context owner가 될 수 있다. 나머지 worker는 compact link set을 받는다.
