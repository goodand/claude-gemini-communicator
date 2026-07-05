---
name: runtime-flow-tracer
description: Use when tracing actual function calls at runtime, debugging execution paths, profiling call sequences, generating dynamic call graphs, running tests with call tracing, or capturing web browser and network traffic. Triggers on "런타임 추적", "실행 흐름", "call graph", "함수 호출 추적", "pyftrace", "njstrace", "dynamic analysis", "호출 순서", "execution trace", "test trace", "테스트 실패 분석", "positional encoding", "브라우저 추적", "playwright", "mitmproxy", "네트워크 캡처", "web tracing", "API call graph".
---

# Runtime Flow Tracer

**Canonical runtime tracer** for this skill set. Trace actual function calls at runtime and export as structured call graphs. **Zero dependencies for core features** - uses Python standard library only.

Supports:
- **Python** (sys.settrace - 의존성 없음)
- **Node.js** (기본 추적 - 의존성 없음, njstrace 선택적)
- **Web Browser** (Playwright + JS injection - pip 설치 필요)
- **Network Traffic** (Mitmproxy - pip 설치 필요)

## Family role

이 skill은 runtime-flow-tracer family의 **canonical tracer**입니다.

| Variant | Role | When to use directly |
|---|---|---|
| `runtime-flow-tracer` (this) | canonical tracer | Python/Node/Web/Network 추적 전반 |
| `runtime-flow-tracer-web-preview` | Playwright MCP specialization | Playwright MCP 도구 출력을 tracer 형식으로 변환할 때만 |

대부분의 경우 이 skill을 먼저 사용하세요. `web-preview`는 Playwright MCP bridge가 필요한 경우에만 직접 호출합니다.

## When to Use

**Use when:**
- Debugging "why was this function called?"
- Profiling actual execution paths (not just imports)
- Generating call graphs for LLM context injection
- Analyzing test execution with failure archiving
- Comparing static vs dynamic code coverage
- **Capturing browser JS execution** (fetch, events, DOM)
- **Analyzing API call patterns** (HTTP/WebSocket)

**Don't use for:**
- Static import analysis → use `codebase-architecture-mapper`
- Simple code reading → just read the file
- Production profiling → use dedicated profilers (cProfile, perf)
- **Playwright MCP 출력 변환만** → use `runtime-flow-tracer-web-preview` directly

---

## Quick Start

### Script Tracing (Python/Node.js)
```bash
# Python 추적
python tracer.py python my_script.py

# JavaScript 추적  
python tracer.py node app.js

# Positional Encoding (레이아웃 좌표 포함)
python tracer.py python my_script.py --format positional
```

### Web Browser Tracing (Playwright)
```bash
# 기본 웹 추적
python web_tracer.py https://example.com

# Interactive 모드 (브라우저 열어두기)
python web_tracer.py https://example.com --interactive --no-headless

# 액션 실행 후 추적
python web_tracer.py https://example.com --actions "click:#btn,wait:2000"

# Mermaid 출력
python web_tracer.py https://example.com --format mermaid
```

### Network Traffic Capture (Mitmproxy)
```bash
# 프록시 시작
mitmdump -s network_proxy.py -p 8080 --set output=network.json

# 웹 추적과 함께 사용
python web_tracer.py https://example.com --proxy localhost:8080
```

### Test Suite Tracing
```bash
# 테스트 실패 아카이빙
python test_tracer.py pytest tests/ --archive-dir ./failures
```

---

## Quick Reference

| Script | Purpose | Example |
|--------|---------|---------|
| `tracer.py` | Python/Node 추적 | `python tracer.py python app.py` |
| `web_tracer.py` | 브라우저 추적 | `python web_tracer.py https://site.com` |
| `network_proxy.py` | 네트워크 캡처 | `mitmdump -s network_proxy.py` |
| `test_tracer.py` | 테스트 아카이빙 | `python test_tracer.py pytest tests/` |
| `bridge.py` | 데이터 통합 | `python bridge.py combine ...` |

| Format | Flag | Use Case |
|--------|------|----------|
| JSON | `--format json` | 상세 분석 |
| Unified | `--format unified` | 통합 형식 |
| Positional | `--format positional` | 좌표 + centrality |
| Edge List | `--format edge-list` | classifier 입력 |
| Mermaid | `--format mermaid` | 시각화 |

---

## Pipeline Integration

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ codebase-mapper │    │ runtime-tracer  │    │ graph-classifier│
│    (정적)       │───▶│    (동적)       │───▶│   (구조 분류)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
   tracer.py           web_tracer.py        network_proxy.py
  (Python/Node)         (Browser)            (HTTP/WS)
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              ▼
                         bridge.py
                      (데이터 통합)
```

**Bridge 명령어:**
```bash
# 정적 + 동적 병합
python bridge.py merge mapper.json trace.json

# 여러 소스 통합 (런타임 + 웹 + 네트워크)
python bridge.py combine runtime.json --web web.json --network network.json

# 커버리지 리포트
python bridge.py report mapper.json trace.json -o ARCHITECTURE.md
```

---

## Web Browser Tracer Details

**JS Injector 캡처 대상:**
- 함수 호출 (`window.__traceFunction__`)
- 이벤트 리스너 (click, submit 등)
- 네트워크 요청 (fetch, XHR)
- DOM 변경 (MutationObserver)
- 전역 변수 변화

**브라우저 콘솔에서 수동 확인:**
```javascript
window.__getTraceData__()   // 트레이스 데이터 조회
window.__clearTraces__()    // 트레이스 초기화
window.__exportTraces__()   // JSON 파일 다운로드
```

---

## Common Mistakes

**❌ 빈 결과** → 스크립트에 함수 호출이 있는지 확인
**❌ JS 추적 부분적** → 복잡한 JS는 njstrace 권장 (`npm install -g njstrace`)
**❌ playwright 미설치** → `pip install playwright && playwright install chromium`
**❌ mitmproxy 미설치** → `pip install mitmproxy`

---

## Prerequisites

### 즉시 실행 가능 (표준 라이브러리만)
```bash
# Python 추적, 테스트 실행, 데이터 통합
python tracer.py python script.py       # ✅ 바로 실행
python test_tracer.py pytest tests/     # ✅ 바로 실행 (pytest 필요)
python bridge.py merge a.json b.json    # ✅ 바로 실행
python network_proxy.py trace.json      # ✅ 분석 모드
```

### 선택적 의존성 (고급 기능)
```bash
# 웹 브라우저 추적
pip install playwright && playwright install chromium

# 네트워크 프록시 캡처
pip install mitmproxy

# JS 고급 추적 (선택)
npm install -g njstrace
```

## References

- `references/OUTPUT_FORMAT.md` - 출력 형식 상세
- `references/TOOLS_SETUP.md` - 도구 설치 가이드
