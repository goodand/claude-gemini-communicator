# Graphviz ↔ Mermaid Conversion Tools Knowledge Base
- ver: `v0.2.0`
- generated_at: `2026-03-20`
- updated_at: `2026-03-21` (v0.2.0: hybrid_kb 성격 명시, 경계 문장 추가)
- kb_type: `hybrid_kb` — 도구 5개 조사 자산(URL/메타데이터)을 넓게 유지하면서 Canonical Design Takeaways로 닫는 구조
- format: `- [한 줄 설명](URL)`
- generation_method: `GitHub README 직접 조사 + API 메타데이터 확인`
- total_urls: `5`
- paper_like_urls: `0`
- other_urls: `5`

## Scope Boundary

이 KB는 **DOT ↔ Mermaid 포맷 변환 도구**만 다룬다.
변환 결과를 Neo4j/Cytoscape/Gephi에 적재하거나 코드베이스 분석에 쓰는 흐름은 `codebase-graph-analysis-tools-kb.md`가 담당한다.
두 KB 모두 mermaid-authoring-strategy의 conversion/tooling 축 KB이며, core canonical KB는 `mermaid-safe-authoring-kb.md`이다.

## Document Map

| 문서 | 역할 |
|------|------|
| `SKILL.md` | mermaid-authoring-strategy 진입점 (4축 전략) |
| `knowledge_bases/mermaid-safe-authoring-kb.md` | parser-safe 작성 규칙 canonical KB (**core source of truth**) |
| `knowledge_bases/graphviz-mermaid-conversion-tools-kb.md` (이 파일) | conversion/tooling strategy — DOT ↔ Mermaid 도구 조사 (hybrid KB) |
| `knowledge_bases/codebase-graph-analysis-tools-kb.md` | visualization ecosystem — Neo4j/Cytoscape/Gephi (hybrid KB) |
| `references/relation-modeling.md` | 엣지 타입별 Mermaid 변환 규칙 |

## Table of Contents
- [Mermaid → DOT 도구](#mermaid--dot-도구)
- [DOT → Mermaid 도구](#dot--mermaid-도구)
- [양방향 / IR 기반 도구](#양방향--ir-기반-도구)
- [Canonical Design Takeaways](#canonical-design-takeaways)

## Mermaid → DOT 도구

- [utensil/mermaid2dot — Mermaid flowchart를 Graphviz DOT로 변환하는 JS 프로토타입](https://github.com/utensil/mermaid2dot)
  - sources: `GitHub README`
  - agent: `Claude Code`
  - taxonomy: [[mermaid-to-dot]] · Converter
  - key_idea: Mermaid 0.4 AST를 Handlebars 템플릿으로 DOT 변환하는 초기 PoC.
  - execution_conditions: Node.js, npm install (미발행 패키지)
  - pseudocode_3lines:
    - 1) Mermaid 0.4 파서로 flowchart AST를 추출한다.
    - 2) Handlebars 템플릿으로 DOT 문자열을 생성한다.
    - 3) `npm run inspect`로 결과를 확인한다.
  - lang: `JavaScript`
  - stars: `21`
  - last_push: `2015-05-19`
  - license: `MIT`
  - status: **사실상 폐기**. mermaid 0.4에 고정 (현재 v11+). CLI 없음, npm 미발행. TODO 미완료.
  - usable_today: **No** — 현대 Mermaid 구문 파싱 불가.
  - install: `npm install` (로컬 빌드 전용)

## DOT → Mermaid 도구

- [r3code/dot2mermaid — Go 기반 CLI로 DOT를 MermaidJS flowchart로 변환](https://github.com/r3code/dot2mermaid)
  - sources: `GitHub README`
  - agent: `Claude Code`
  - taxonomy: [[dot-to-mermaid]] · CLI Tool
  - key_idea: stdin/파일에서 DOT를 읽어 Mermaid flowchart 구문으로 변환하는 단일 Go 바이너리.
  - execution_conditions: Go 1.21+, `go install` 또는 소스 빌드
  - pseudocode_3lines:
    - 1) gographviz로 DOT 파일을 파싱한다.
    - 2) DOT 노드 shape을 Mermaid 노드 shape으로 매핑한다.
    - 3) stdout에 Mermaid flowchart 텍스트를 출력한다.
  - lang: `Go`
  - stars: `13`
  - last_push: `2024-03-18`
  - license: `MIT`
  - status: 적당히 유지중. 테스트 있음. GitHub release/tag 없음.
  - usable_today: **Yes** — Go 바이너리로 빠르게 사용 가능.
  - install: `go install dot2mermaidjs@latest`
  - limitations: README 한 줄. flowchart 출력만 지원. 패키지 레지스트리 미등록.

- [HoseynAAmiri/dot2mermaid — Python 라이브러리로 DOT를 Mermaid + Markdown으로 변환](https://github.com/HoseynAAmiri/dot2mermaid)
  - sources: `GitHub README`
  - agent: `Claude Code`
  - taxonomy: [[dot-to-mermaid]] · Python Library
  - key_idea: code2flow로 Python 소스 → DOT → pygraphviz 파싱 → Mermaid flowchart 변환.
  - execution_conditions: Python, `pip install dot2mermaid`, 시스템 graphviz + pygraphviz 헤더
  - pseudocode_3lines:
    - 1) code2flow로 Python 소스에서 DOT 호출 그래프를 생성한다.
    - 2) pygraphviz로 DOT를 파싱하여 노드/엣지를 추출한다.
    - 3) LR flowchart 형태의 Mermaid 텍스트로 변환하여 Markdown에 삽입한다.
  - lang: `Python`
  - stars: `7`
  - last_push: `2024-10-18`
  - license: `MIT`
  - status: 소규모 코드베이스 (~2 파일). PyPI 발행됨.
  - usable_today: **Partial** — code2flow에 강하게 결합. 범용 DOT→Mermaid로는 제한적.
  - install: `pip install dot2mermaid` + 시스템 graphviz
  - limitations: code2flow 의존. pygraphviz 설치 까다로움 (특히 Windows). LR flowchart만 출력.

- [antononcube/Raku-Graphviz-DOT-Grammar — Raku 기반 DOT 풀파서 + Mermaid/PlantUML/SVG 다포맷 출력](https://github.com/antononcube/Raku-Graphviz-DOT-Grammar)
  - sources: `GitHub README`
  - agent: `Claude Code`
  - taxonomy: [[dot-to-mermaid]] · Parser/Interpreter
  - key_idea: DOT 언어 전체를 파싱하고 Mermaid-JS, PlantUML, SVG, JSON, Mathematica 등 다포맷으로 번역.
  - execution_conditions: Raku 런타임 + zef 패키지 매니저
  - pseudocode_3lines:
    - 1) Raku grammar로 DOT 소스를 파싱하여 AST를 생성한다.
    - 2) 대상 포맷 interpreter를 선택한다 (mermaid, plantuml, svg 등).
    - 3) `from-dot input.dot --to mermaid`로 변환 결과를 출력한다.
  - lang: `Raku (Perl 6)`
  - stars: `0`
  - last_push: `2024-11-18`
  - license: `Artistic License 2.0`
  - status: 잘 문서화되어 있으나 Raku 생태계 한정. 채택률 극히 낮음.
  - usable_today: **Yes (if Raku installed)** — CLI `from-dot` 제공. 하지만 Raku 설치 장벽 높음.
  - install: `zef install Graphviz::DOT::Grammar`
  - limitations: Raku 런타임 필수 (니치 언어). 0 stars = 극히 낮은 채택.

## 양방향 / IR 기반 도구

- [statelyai/graph — JSON IR 기반 유니버설 그래프 라이브러리, DOT import + Mermaid export](https://github.com/statelyai/graph)
  - sources: `GitHub README`
  - agent: `Claude Code`
  - taxonomy: [[graph-ir]] [[bidirectional]] · TypeScript Library
  - key_idea: plain JSON 객체 기반 Graph IR을 중심으로 DOT/Mermaid/GraphML/GEXF/Cytoscape 등 다포맷 직렬화.
  - execution_conditions: Node.js, `npm install @statelyai/graph`, optional peer deps (dotparser 등)
  - pseudocode_3lines:
    - 1) DOT를 dotparser로 읽어 JSON Graph IR로 변환한다.
    - 2) Graph IR 위에서 BFS/DFS/위상정렬 등 알고리즘을 실행한다.
    - 3) Graph IR을 Mermaid flowchart/state/sequence 등 다양한 포맷으로 직렬화한다.
  - lang: `TypeScript`
  - stars: `22`
  - last_push: `2026-03-19`
  - version: `0.7.0`
  - license: `MIT`
  - status: **활발히 개발중** (Stately.ai — XState 팀). pre-1.0이라 API 변경 가능.
  - usable_today: **Yes** — 가장 활발하고 가장 범용적.
  - install: `npm install @statelyai/graph`
  - supported_formats: DOT (import/export), Mermaid (export: flowchart, state, sequence, class, ER, mindmap, block), GraphML, GEXF, GML, TGF, Cytoscape JSON, D3 JSON, adjacency list, edge list
  - limitations: Mermaid import 미지원 (export만). DOT import는 `dotparser` peer dep 필요. 레이아웃 엔진 미내장 (elkjs로 별도 처리). pre-1.0.

## Canonical Design Takeaways

### T-G1: 실용적 조합

현실적으로 가장 쓸 만한 조합은 두 가지:
- **간단한 변환**: `r3code/dot2mermaid` (Go CLI, stdin→stdout)
- **프로그래머블 파이프라인**: `statelyai/graph` (JSON IR 허브)

### T-G2: Mermaid → DOT 방향은 사실상 빈자리

`utensil/mermaid2dot`는 2015년 PoC로 폐기 상태. 현대 Mermaid(v11+)를 DOT로 직접 변환하는 성숙한 도구가 현재 없다.
대안: `statelyai/graph`에서 Mermaid import가 추가되면 양방향이 가능해진다.

### T-G3: IR 기반이 장기적으로 우세

`statelyai/graph`처럼 중간 JSON IR을 두면 `toDOT()`, `toMermaid()`, `toGraphML()` 등을 독립적으로 붙일 수 있다.
직접 변환(DOT→Mermaid)은 빠르지만, 포맷이 3개 이상 되면 IR 허브가 유지보수에 유리하다.

### T-G4: mermaid-authoring-strategy과의 연결

DOT→Mermaid 변환 후에도 이 스킬의 워크플로우를 따라야 한다:
1. 변환 출력을 인접리스트로 먼저 검증
2. 최소 `graph TD` + `-->` 로 축소하여 렌더 확인
3. 점진적으로 라벨, subgraph, 스타일 추가

변환 도구의 출력을 그대로 쓰지 않는다 — 파서 안전성은 변환 도구가 보장하지 않는다.

### T-G5: 도구 선택 판단 기준

| 상황 | 추천 |
|------|------|
| DOT 파일 하나를 빠르게 Mermaid로 | `r3code/dot2mermaid` (Go CLI) |
| JS/TS 프로젝트 내 그래프 조작 + 포맷 변환 | `statelyai/graph` |
| Python 소스 → 호출 그래프 → Mermaid | `HoseynAAmiri/dot2mermaid` |
| Mermaid → DOT (현재) | 성숙한 도구 없음 — 수동 변환 또는 대기 |
