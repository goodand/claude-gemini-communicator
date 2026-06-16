# agent-graph-ir consistency checklist

> source of truth: `knowledge_bases/agent-graph-ir-kb-at2026-03-26.md`

## A. Canonical Source

- [ ] Pydantic model이 canonical source of truth다
- [ ] DOT와 Mermaid는 파생 출력이다

## B. Validation

- [ ] node_id, edge_id, scope_id uniqueness를 검증한다
- [ ] router scope는 최소 2개의 route edge를 요구한다
- [ ] loop scope는 break condition과 종료 이유 규칙을 가진다

## C. Runtime Trace

- [ ] run trace는 node_id와 scope_instance_id를 공유한다
- [ ] Langfuse-compatible trace JSON을 직접 생성할 수 있다
