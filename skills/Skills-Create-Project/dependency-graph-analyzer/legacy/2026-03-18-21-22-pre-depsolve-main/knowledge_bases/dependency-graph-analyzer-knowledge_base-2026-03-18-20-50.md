# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-18`
- updated_at: `2026-03-18` (v0.1.0: dependency-graph-analyzer reference seed 추가)
- format: `- [한 줄 설명](URL)`
- generation_method: `local codebase scan + targeted GitHub repository review for dependency graph analysis and MCP visualization`
- total_urls: `8`
- paper_like_urls: `0`
- other_urls: `8`

## Document Map

| 문서 | 역할 |
|------|------|
| `references/dependency-graph-analyzer-reference-2026-03-18-20-50.md` | 로컬 skill + 외부 GitHub reference 해석 |
| `checklist-forconsistency-evaluation/dependency-graph-analyzer-checklist-2026-03-18-20-50.md` | 코드베이스 구현 정합성 체크리스트 |
| `references/Boundary-of-Responsibility-2026-03-18-20-50.md` | 책임 경계 |
| `references/subagent-design-2026-03-18-20-50.md` | subagent 역할 설계 |

## Table of Contents
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Paper-like URLs

- 없음

## Other research References URLs

- [dependency-cruiser는 JS/TS 의존성 그래프를 시각화하면서 규칙 위반까지 검증하는 정적 분석기다](https://github.com/sverweij/dependency-cruiser)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 소스 트리에서 의존성 edge를 추출한다.
    - 2) 금지 규칙과 cycle/unknown dependency를 검사한다.
    - 3) json/html/mermaid류 산출물로 리포트한다.

- [madge는 빠르게 모듈 의존성 그래프와 circular dependency를 찾는 경량 extractor다](https://github.com/pahen/madge)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) entry/source set에서 import graph를 만든다.
    - 2) cycle을 식별한다.
    - 3) 그래프 아웃풋을 시각화에 넘긴다.

- [pydeps는 Python module dependency graph를 그리는 도구다](https://github.com/thebjorn/pydeps)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) Python import machinery 기준으로 의존성 관계를 수집한다.
    - 2) clustering/depth filter로 graph를 정리한다.
    - 3) Graphviz 기반으로 render-ready graph를 만든다.

- [import-linter는 Python import dependency를 architecture contract로 검사한다](https://github.com/seddonym/import-linter)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 모듈 경계 계약을 선언한다.
    - 2) import graph를 검사한다.
    - 3) 위반을 리포트한다.

- [swark는 코드베이스에서 아키텍처 다이어그램을 생성하는 상위 요약 도구다](https://github.com/swark-io/swark)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 코드베이스 구조를 읽는다.
    - 2) 상위 아키텍처 블록을 추론한다.
    - 3) 다이어그램으로 출력한다.

- [mermaid-mcp-server는 Mermaid 코드를 PNG/SVG로 렌더링하는 MCP다](https://github.com/peng-shawn/mermaid-mcp-server)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) Mermaid 텍스트를 입력받는다.
    - 2) 브라우저 기반으로 렌더링한다.
    - 3) SVG 또는 PNG를 반환한다.

- [claude-mermaid는 Mermaid live preview를 제공하는 MCP 서버다](https://github.com/veelenga/claude-mermaid)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) Mermaid 초안을 빠르게 렌더링한다.
    - 2) 수정 루프를 짧게 만든다.
    - 3) diagram QA를 지원한다.

- [OpenAI Agents Python/JS는 subagent orchestration과 handoff 구조의 공식 레퍼런스다](https://github.com/openai/openai-agents-python)
  - sources: `github_readme_manual_review_2026-03-18`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 상위 agent가 하위 agent를 호출한다.
    - 2) 결과를 orchestrator가 모은다.
    - 3) tracing과 handoff로 fan-in 한다.
