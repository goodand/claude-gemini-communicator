---
name: runtime-flow-tracer-web-preview
description: Playwright MCP 도구 출력(console, network, trace)을 tracer 형식으로 변환할 때 사용한다. MCP bridge 전용 variant. 범용 Python/Node/Web/Network 런타임 추적은 runtime-flow-tracer를 사용하라.
---

# Runtime Flow Tracer (Web Preview)

`runtime-flow-tracer` family의 **Playwright MCP specialization**. Playwright MCP 도구 출력을 tracer 형식으로 변환하는 전용 variant.

> **범용 런타임 추적이 필요하면 `runtime-flow-tracer`를 먼저 사용하세요.** 이 skill은 Playwright MCP bridge가 필요한 경우에만 직접 호출합니다.

## When to use directly

- Playwright MCP 도구 출력(console, network, trace)을 tracer-compatible JSON으로 변환할 때
- MCP client에서 캡처한 브라우저 데이터를 canonical tracer 형식으로 통합할 때

## Do not use for

- **Python/Node 스크립트 추적** → `runtime-flow-tracer`
- **Standalone Playwright 브라우저 추적** → `runtime-flow-tracer` (web_tracer.py)
- **테스트 실행 + failure archiving** → `runtime-flow-tracer` (test_tracer.py)
- **네트워크 프록시 캡처** → `runtime-flow-tracer` (network_proxy.py)

---

## Playwright MCP Bridge

Convert Playwright MCP tool outputs to tracer-compatible formats.

### Supported Inputs

| MCP Tool | Bridge Command | Output |
|----------|---------------|--------|
| `browser_console_messages` | `console` | Function call traces |
| `browser_network_requests` | `network` | API call graph |
| Playwright trace (.zip) | `trace` | Combined analysis |

### Usage

```bash
# Console messages → trace
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py console console.json -o trace.json

# Network → Mermaid diagram
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py network network.json --format mermaid

# Playwright trace file
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py trace session-trace.zip

# Combine multiple MCP sources
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py combine \
    --console c.json \
    --network n.json \
    --trace t.zip \
    --format mermaid
```

### MCP Tool Output Format

**browser_console_messages** (save as JSON):
```json
[
  {"type": "log", "text": "[init] Starting app", "location": "app.js:10"},
  {"type": "log", "text": "[fetchData] Loading...", "location": "api.js:25"}
]
```

**browser_network_requests** (save as JSON):
```json
[
  {"method": "GET", "url": "https://api.example.com/users", "status": 200},
  {"method": "POST", "url": "https://api.example.com/login", "status": 200}
]
```

---

## Handoff to canonical tracer

MCP 출력을 변환한 후 backend trace와 합치려면:

```bash
# 1. Convert MCP outputs (this skill)
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py combine \
    --console console.json --network network.json -o browser.json

# 2. Combine with backend trace (canonical tracer의 bridge.py)
python $SKILLS_ROOT/runtime-flow-tracer/scripts/bridge.py combine backend.json --web browser.json -o full_trace.json
```

---

## Prerequisites

```bash
# MCP bridge — 즉시 실행 가능 (표준 라이브러리만)
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py console c.json  # ✅
```

## References

- `references/OUTPUT_FORMAT.md` - 출력 형식 상세
- `references/TOOLS_SETUP.md` - 도구 설치 가이드
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) - 브라우저 자동화 MCP
