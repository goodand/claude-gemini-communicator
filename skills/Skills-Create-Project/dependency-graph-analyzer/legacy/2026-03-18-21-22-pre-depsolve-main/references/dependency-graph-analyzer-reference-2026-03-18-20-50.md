# dependency-graph-analyzer Reference
- version: `v0.1.0`
- created_at: `2026-03-18`
- purpose: `dependency-graph-analyzer` 설계 기준이 되는 로컬 skill/codebase와 외부 GitHub reference를 정리한다.

## 1. 로컬 기준점

### depsolve-analyzer
- 경로: `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/depsolve-analyzer/SKILL.md`
- 강점:
  - phantom dependency 탐지
  - cycle/diamond/version conflict
  - Mermaid graph
  - bridge 기반 통합
- 이 skill에서 가져올 것:
  - 패키지/manifest 계층 분석
  - graph summary와 risk report 구조

### codebase-architecture-mapper
- 경로: `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/codebase-architecture-mapper/SKILL.md`
- 강점:
  - source-level module/class/import edges 추출
  - Python/JS analyzer 분기
  - LLM context 문서화
- 가져올 것:
  - source import graph 추출
  - edge-list 표준화
  - architecture summary 생성

### graph-structure-classifier
- 경로: `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/graph-structure-classifier/SKILL.md`
- 강점:
  - Tree/DAG/cycle 분류
  - topological 건전성 판단
- 가져올 것:
  - graph health classification
  - SCC/cycle 표현

### runtime-flow-tracer-web-preview
- 경로: `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/runtime-flow-tracer-web-preview/SKILL.md`
- 강점:
  - runtime call graph
  - API graph
  - Mermaid 변환
- 가져올 것:
  - static graph와 runtime graph를 분리하는 책임 경계

## 2. 외부 GitHub reference

### dependency-cruiser
- URL: `https://github.com/sverweij/dependency-cruiser`
- 핵심: JS/TS dependency validation + visualization + rule enforcement
- 시사점:
  - 단순 그래프보다 rule violation을 함께 본다
  - output format을 text/json/html/mermaid까지 폭넓게 둔다

### madge
- URL: `https://github.com/pahen/madge`
- 핵심: 빠른 dependency graph와 circular dependency 탐지
- 시사점:
  - MVP extractor는 간단해야 한다
  - 초기 그래프 산출의 UX는 단순할수록 좋다

### pydeps
- URL: `https://github.com/thebjorn/pydeps`
- 핵심: Python import dependency visualization
- 시사점:
  - Python codebase의 module graph는 별도 최적화가 필요하다
  - Graphviz export와 clustering 아이디어 참고 가능

### import-linter
- URL: `https://github.com/seddonym/import-linter`
- 핵심: Python import dependency를 contract로 검증
- 시사점:
  - dependency graph는 단순 시각화보다 architecture contract enforcement에 더 가치가 있다

### swark
- URL: `https://github.com/swark-io/swark`
- 핵심: 코드베이스에서 아키텍처 다이어그램 생성
- 시사점:
  - 발표/설계 문서용 요약 그래프와 분석 그래프를 분리해야 한다

### mermaid-mcp-server
- URL: `https://github.com/peng-shawn/mermaid-mcp-server`
- 핵심: Mermaid 렌더링 MCP
- 시사점:
  - analyzer는 graph 생성에 집중하고 렌더링은 별도 MCP에 위임할 수 있다

### claude-mermaid
- URL: `https://github.com/veelenga/claude-mermaid`
- 핵심: Mermaid live preview MCP
- 시사점:
  - iterative diagram refinement에 유리

### openai-agents-python / openai-agents-js
- URL: `https://github.com/openai/openai-agents-python`
- URL: `https://github.com/openai/openai-agents-js`
- 핵심: subagent orchestration, handoff, tracing
- 시사점:
  - dependency-graph-analyzer를 단일 agent가 아니라 subagent fan-out 구조에 연결할 때 orchestration reference가 된다

## 3. 설계 결론
- v0.1은 `depsolve-analyzer + codebase-architecture-mapper + graph-structure-classifier` 조합이 가장 현실적이다
- static dependency graph와 runtime flow graph는 한 skill에 섞지 않는다
- output은 최소 `edge_list.json`, `graph_summary.json`, `mermaid.mmd`, `risk_report.md`, `parallel_slices.json`이 필요하다
