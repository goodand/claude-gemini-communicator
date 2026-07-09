# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-16`
- updated_at: `2026-03-16` (v0.1.0: initial contract-to-concept-mapper KB)
- format: `- [한 줄 설명](URL)`
- generation_method: `GitHub/Paper reference 수집 후 contract-to-concept-mapper 설계에 맞게 선별·축약`
- total_urls: `14`
- paper_like_urls: `8`
- other_urls: `6`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 워크플로우 |
| `contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md` (이 파일) | GitHub/논문 URL 인덱스 |
| [contract-to-concept-mapper-github-search-at2026-03-16.md](../references/contract-to-concept-mapper-github-search-at2026-03-16.md) | GitHub shortlist 및 선택 근거 |
| [contract-to-concept-mapper-paper-search-at2026-03-16.md](../references/contract-to-concept-mapper-paper-search-at2026-03-16.md) | 논문 shortlist 및 선택 근거 |
| [contract-to-concept-mapper-issues-at2026-03-16.md](./contract-to-concept-mapper-issues-at2026-03-16.md) | 현재 이슈와 필요성 |

## Table of Contents
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Paper-like URLs

- [CodeBERT - 프로그래밍 언어와 자연어의 shared representation](https://aclanthology.org/2020.findings-emnlp.139/)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[pl_nl_bridge]] · shared representation`
  - key_idea: 코드/계약과 자연어 설명을 공통 표현 공간에서 다룰 수 있다는 기본 관점을 제공한다.
  - execution_conditions: contract artifact를 텍스트나 구조화 표현으로 정규화할 중간 계층 필요
  - pseudocode_3lines:
    - 1) 실행 계약 아티팩트를 공통 표현으로 정규화한다.
    - 2) 상위 의미와 가까운 자연어 표현을 찾는다.
    - 3) concept summary와 trace link를 함께 남긴다.

- [CODE2SEQ - 구조화된 코드 표현을 자연어 시퀀스로 변환](https://openreview.net/forum?id=H1gKYo09tX)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[structured_to_text]] · sequence generation`
  - key_idea: AST/path 같은 구조화 입력에서 요약 시퀀스를 생성하는 접근이 contract-to-concept lifting의 기술적 비유가 된다.
  - execution_conditions: checklist/schema/task를 구조화 unit로 분해하는 선행 단계 필요
  - pseudocode_3lines:
    - 1) 계약 항목을 구조화 unit로 분해한다.
    - 2) unit 간 관계를 유지한 채 summary 단위를 생성한다.
    - 3) 전체 concept narrative로 다시 묶는다.

- [Neural Architecture for Generating Natural Language Descriptions from Source Code Changes](https://aclanthology.org/P17-2045/)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[change_to_description]] · summarization`
  - key_idea: 변화 집합에서 상위 설명을 복원하는 방식이 실행 계약 변화나 checklist 변화를 개념 설명으로 올리는 데 유용하다.
  - execution_conditions: diff나 변경된 contract unit을 입력으로 취급할 수 있어야 함
  - pseudocode_3lines:
    - 1) 변경된 계약 항목을 수집한다.
    - 2) 변화가 뜻하는 상위 의미를 요약한다.
    - 3) 변경 설명과 기존 개념 모델 차이를 보고한다.

- [Content Aware Source Code Change Description Generation](https://aclanthology.org/W18-6513/)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[change_context]] · context-aware description`
  - key_idea: 현재 artifact만이 아니라 주변 문맥을 함께 봐야 올바른 설명이 나온다.
  - execution_conditions: project context 또는 neighboring contract context를 함께 읽어야 함
  - pseudocode_3lines:
    - 1) 핵심 계약 항목을 고른다.
    - 2) 주변 context와 함께 해석한다.
    - 3) 경계와 목적을 포함한 설명으로 올린다.

- [ProConSuL - 프로젝트 컨텍스트를 활용한 코드 요약](https://aclanthology.org/2024.emnlp-industry.65/)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[project_context]] · context-aware summarization`
  - key_idea: 개별 함수/항목이 아니라 project-level context를 넣어야 summary의 의미 왜곡이 줄어든다.
  - execution_conditions: 단일 checklist 항목이 아니라 skill 단위 context를 묶는 기능 필요
  - pseudocode_3lines:
    - 1) 현재 contract unit을 선택한다.
    - 2) project-level contract context를 함께 불러온다.
    - 3) 전체 skill 관점의 concept summary를 만든다.

- [Automatic Extraction of Security-Rich Dataflow Diagrams for Microservice Applications written in Java](https://www.sciencedirect.com/science/article/pii/S0164121223001176)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[architecture_recovery]] · model reconstruction`
  - key_idea: 코드에서 상위 모델과 다이어그램을 추출하되 traceability를 유지하는 관점이 핵심이다.
  - execution_conditions: contract unit에서 relation graph를 만들 수 있어야 함
  - pseudocode_3lines:
    - 1) 계약 단위 간 연결 관계를 추출한다.
    - 2) 상위 개념 그래프로 재구성한다.
    - 3) 다이어그램과 trace link를 함께 출력한다.

- [Interpretable Rule-Based Data-to-Text Systems with LLMs](https://aclanthology.org/2024.inlg-main.48/)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[interpretable_d2t]] · explainable generation`
  - key_idea: 자연어 출력보다 중간의 해석 가능한 규칙 기반 표현이 더 중요하다는 점을 보여준다.
  - execution_conditions: contract unit -> concept unit intermediate representation 설계 필요
  - pseudocode_3lines:
    - 1) 구조화 입력을 해석 가능한 규칙으로 바꾼다.
    - 2) 규칙을 기반으로 concept text를 생성한다.
    - 3) 규칙과 문장 간 연결을 보존한다.

- [Explainability Meets Text Summarization: A Survey](https://aclanthology.org/2024.inlg-main.49/)
  - sources: `contract-to-concept-mapper-paper-search-at2026-03-16.md`
  - agent: `A00`
  - taxonomy: `[[explainable_summary]] · survey`
  - key_idea: contract-to-concept 문제는 단순 summarization이 아니라 explainability task라는 점을 뒷받침한다.
  - execution_conditions: 생성 결과와 근거 unit 간 명시적 연결 필요
  - pseudocode_3lines:
    - 1) 요약 결과를 만든다.
    - 2) 각 결과 문장을 근거 unit에 연결한다.
    - 3) 근거가 약한 문장은 uncertainty로 표시한다.

## Other research References URLs

- [Structurizr DSL - DSL로 상위 아키텍처 개념과 다이어그램 생성](https://github.com/structurizr/dsl)
  - sources: `contract-to-concept-mapper-github-search-at2026-03-16.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 구조화된 입력을 DSL 요소로 바꾼다.
    - 2) 요소 간 관계를 선언한다.
    - 3) 다이어그램/문서로 렌더링한다.

- [code2flow - 코드 호출 구조를 flow diagram으로 lift](https://github.com/scottrogowski/code2flow)
  - sources: `contract-to-concept-mapper-github-search-at2026-03-16.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 코드 구조를 읽는다.
    - 2) 호출 관계를 흐름 그래프로 바꾼다.
    - 3) 상위 flow 표현을 출력한다.

- [code2DFD - 소스 코드와 설정에서 DFD 같은 상위 모델 복원](https://github.com/tuhh-softsec/code2DFD)
  - sources: `contract-to-concept-mapper-github-search-at2026-03-16.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 입력 artifact에서 의미 있는 unit을 추출한다.
    - 2) unit 간 관계를 상위 모델로 재구성한다.
    - 3) traceability를 유지한 출력으로 내보낸다.

- [Doxygen - 소스 구조에서 문서와 개념 요약 추출](https://github.com/doxygen/doxygen)
  - sources: `contract-to-concept-mapper-github-search-at2026-03-16.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 소스 구조를 읽는다.
    - 2) 문서화 가능한 개념 단위를 식별한다.
    - 3) 요약과 구조 설명을 생성한다.

- [pydoclint - 시그니처와 문서 의미 정합성 검사](https://github.com/jsh9/pydoclint)
  - sources: `contract-to-concept-mapper-github-search-at2026-03-16.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 함수 시그니처를 읽는다.
    - 2) 문서 섹션과 비교한다.
    - 3) 의미 차이나 누락을 표시한다.

- [Swark - 코드베이스에서 Mermaid 아키텍처 다이어그램 생성](https://github.com/swark-io/swark)
  - sources: `contract-to-concept-mapper-github-search-at2026-03-16.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 코드베이스를 읽는다.
    - 2) 상위 아키텍처 설명을 생성한다.
    - 3) Mermaid 다이어그램으로 출력한다.
