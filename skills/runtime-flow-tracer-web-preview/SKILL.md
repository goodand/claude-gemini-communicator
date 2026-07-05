---
name: runtime-flow-tracer-web-preview
description: Use when tracing runtime execution with web browser integration via Playwright MCP. Captures function calls, network traffic, console logs from both backend scripts and browser sessions. Triggers on "런타임 추적", "웹 추적", "브라우저 추적", "playwright mcp", "call graph", "network trace", "console trace", "API call graph", "execution flow", "web automation trace".
---

# Runtime Flow Tracer (Web Preview)

Trace runtime execution across backend scripts and web browsers. Integrates with **Playwright MCP** for seamless browser automation + tracing.

**Zero dependencies for core features** - uses Python standard library only.

## Supported Environments

| Environment | Tool | Dependencies |
|-------------|------|--------------|
| Python scripts | `tracer.py` | None ✅ |
| Node.js scripts | `tracer.py` | None ✅ |
| Test suites | `test_tracer.py` | pytest/npm (CLI) |
| **Playwright MCP** | `playwright_mcp_bridge.py` | None ✅ |
| Standalone browser | `web_tracer.py` | playwright (pip) |
| Network proxy | `network_proxy.py` | mitmproxy (pip) |

---

## Quick Start

### Backend Script Tracing
```bash
# Python
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/tracer.py python my_script.py

# Node.js
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/tracer.py node app.js

# With Mermaid output
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/tracer.py python script.py --format mermaid
```

### Playwright MCP Integration

**Step 1**: Capture data via Playwright MCP tools
```bash
# In your MCP client (Claude, Cursor, VS Code, etc.)
# Use browser_console_messages and browser_network_requests tools
# Save outputs to JSON files
```

**Step 2**: Convert to tracer format
```bash
# Parse console messages
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py console mcp_console.json

# Parse network requests → API call graph
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py network mcp_network.json --format mermaid

# Parse Playwright trace file
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py trace trace.zip

# Combine all sources
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py combine \
    --console console.json \
    --network network.json \
    -o combined_trace.json
```

**Step 3**: Integrate with backend traces
```bash
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/bridge.py combine backend.json --web browser.json
```

### Test Suite Tracing
```bash
# Run tests with failure archiving
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/test_tracer.py pytest tests/ --archive-dir ./failures
```

---

## Playwright MCP Bridge

Convert Playwright MCP tool outputs to tracer-compatible formats.

### Supported Inputs

| MCP Tool | Bridge Command | Output |
|----------|---------------|--------|
| `browser_console_messages` | `console` | Function call traces |
| `browser_network_requests` | `network` | API call graph |
| Playwright trace (.zip) | `trace` | Combined analysis |

### Usage Examples

```bash
# Console messages → trace
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py console console.json -o trace.json

# Network → Mermaid diagram
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py network network.json --format mermaid

# Playwright trace file
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py trace session-trace.zip

# Combine multiple sources
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

## Quick Reference

| Script | Purpose | Examples |
|--------|---------|---------|
| `tracer.py` | Python/Node tracing | `python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/tracer.py python app.py` |
| `test_tracer.py` | Test suite execution | `python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/test_tracer.py pytest tests/` |
| `playwright_mcp_bridge.py` | Playwright MCP → tracer | `python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py console c.json` |
| `bridge.py` | Data integration | `python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/bridge.py combine ...` |
| `web_tracer.py` | Standalone Playwright | `python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/web_tracer.py https://site.com` |
| `network_proxy.py` | HTTP proxy capture | `mitmdump -s $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/network_proxy.py` |

| Format | Flag | Use Case |
|--------|------|----------|
| JSON | `--format json` | Analysis, integration |
| Mermaid | `--format mermaid` | Visualization |
| Edge List | `--format edge-list` | classifier 연동 |

---

## Pipeline Integration

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Backend Code   │     │  Playwright MCP │     │  graph-classifier│
│  tracer.py      │────▶│  MCP bridge     │────▶│  구조 분류       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                       │
        │   ┌───────────────────┤
        │   │                   │
        ▼   ▼                   ▼
    bridge.py ◄──────── playwright_mcp_bridge.py
    (통합)                (MCP 변환)
```

### Full Workflow Example

```bash
# 1. Trace backend
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/tracer.py python server.py -o backend.json

# 2. Capture browser via Playwright MCP (in your MCP client)
#    → Save console/network outputs

# 3. Convert MCP outputs
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py combine \
    --console console.json \
    --network network.json \
    -o browser.json

# 4. Combine all traces
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/bridge.py combine backend.json --web browser.json -o full_trace.json

# 5. Visualize
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py network network.json --format mermaid > api_graph.mmd
```

---

## Common Mistakes

**❌ 빈 결과** → 스크립트에 함수 호출이 있는지 확인
**❌ MCP 출력 파싱 실패** → JSON 형식 확인, MCP 도구 raw 출력 저장
**❌ playwright 미설치** (standalone) → `pip install playwright && playwright install chromium`

---

## Prerequisites

### 즉시 실행 가능 (표준 라이브러리만)
```bash
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/tracer.py python script.py           # ✅ 바로 실행
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/playwright_mcp_bridge.py console c.json  # ✅ 바로 실행
python $SKILLS_ROOT/runtime-flow-tracer-web-preview/scripts/bridge.py combine a.json --web b.json    # ✅ 바로 실행
```

### 선택적 의존성 (고급 기능)
```bash
# Standalone 브라우저 추적 (Playwright MCP 없이)
pip install playwright && playwright install chromium

# HTTP 프록시 캡처
pip install mitmproxy
```

---

## References

- `references/OUTPUT_FORMAT.md` - 출력 형식 상세
- `references/TOOLS_SETUP.md` - 도구 설치 가이드
- [Playwright MCP](https://github.com/microsoft/playwright-mcp) - 브라우저 자동화 MCP
