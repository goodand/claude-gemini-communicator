# agent-graph-ir entrypoint details

## First slice ownership

- typed JSON IR for `AgentSpec` and `AgentRun`
- static validator for ids, scope references, router edges, loop metadata, condition refs
- run validator for router selection, loop iteration monotonicity, stop reason presence, observe artifact fields
- DOT / Mermaid derived renderers
- Langfuse-compatible trace JSON emitter
- OpenAI screenshot policy based capture route planner
- file-backed typed observe event emitter for PNG screenshot artifacts
- OpenAI curated screenshot skill stdout path-list bridge for multi-capture observe events
- subprocess-based partial capture-run bridge that wraps screenshot helper stdout into `AgentRun`

## CLI

```bash
python3 scripts/agent_graph_ir.py emit-json-schema
python3 scripts/agent_graph_ir.py validate-spec --input spec.json
python3 scripts/agent_graph_ir.py validate-run --spec spec.json --run run.json
python3 scripts/agent_graph_ir.py render-dot --input spec.json
python3 scripts/agent_graph_ir.py render-mermaid --input spec.json
python3 scripts/agent_graph_ir.py emit-trace-json --spec spec.json --run run.json
python3 scripts/agent_graph_ir.py plan-capture --input capture_request.json
python3 scripts/agent_graph_ir.py emit-observe-event --request capture_request.json --artifact capture.png
python3 scripts/agent_graph_ir.py emit-observe-events-from-screenshot-output --request capture_request.json --stdout-file captures.txt
python3 scripts/agent_graph_ir.py run-screenshot-bridge --request capture_request.json --trace-id tr_001 --session-id sess_001 --command python3 take_screenshot.py --mode temp
```

## Boundaries

- `graphviz`, `pydot`, `langfuse`, `jsonschema` are not required for the first slice
- Mermaid import parser is out of scope for v0.1
- actual OS-level screenshot execution, OCR, and UI tree extraction are still out of scope
- runtime adapter does not implement OS capture logic itself; it delegates execution to a helper command and normalizes resulting PNG artifacts/stdout into typed IR

## Upstream capture policy

- screenshot-based agent flow를 모델링할 때 capture policy는 OpenAI curated screenshot skill을 upstream reference로 본다
- 우선순위는 tool-specific capture first, OS-level screenshot fallback이다
- reference: `https://github.com/openai/skills/blob/main/skills/.curated/screenshot/SKILL.md`

## Source of truth

- canonical SoT is the Pydantic model
- DOT and Mermaid are always regenerated from IR
- runtime trace JSON is generated from `AgentRun` instead of being handwritten
