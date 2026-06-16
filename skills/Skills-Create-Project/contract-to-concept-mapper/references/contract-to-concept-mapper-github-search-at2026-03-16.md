# GitHub Search Report — contract-to-concept-mapper

## 사용자 의도 파악

- 목표: checklist, task, schema, CLI contract, 함수 시그니처 같은 실행 계약 공간 아티팩트를 읽고 상위 개념 설명, 경계, Mermaid/수도코드 같은 개념 표현으로 다시 올리는 skill 설계에 필요한 GitHub 레퍼런스 수집
- 제외: 단순 다이어그램 렌더러, 일반 문서 생성기, 코드 실행기

## Shortlist

### 1. structurizr/dsl
- URL: https://github.com/structurizr/dsl
- 선택 이유:
  - 아키텍처 개념을 DSL로 표현하고 다이어그램/문서로 내보내는 구조가 명확하다
  - `contract -> concept model -> diagram` 흐름을 설계할 때 좋은 기준점이 된다

### 2. scottrogowski/code2flow
- URL: https://github.com/scottrogowski/code2flow
- 선택 이유:
  - 코드 호출 구조를 상위 flow 표현으로 바꾸는 축소판 사례다
  - execution artifact를 읽어 개념적 흐름으로 lift하는 출력 형태에 직접적이다

### 3. tuhh-softsec/code2DFD
- URL: https://github.com/tuhh-softsec/code2DFD
- 선택 이유:
  - 소스 코드와 설정 파일에서 증거를 모아 DFD 같은 상위 모델을 추출한다
  - traceability를 유지한 채 concept model로 올리는 방식이 특히 중요하다

### 4. doxygen/doxygen
- URL: https://github.com/doxygen/doxygen
- 선택 이유:
  - 소스 구조에서 문서와 개념 요약을 뽑아내는 오래된 표준 도구다
  - "무엇을 개념으로 승격할 것인가"에 대한 보수적인 기준을 배울 수 있다

### 5. jsh9/pydoclint
- URL: https://github.com/jsh9/pydoclint
- 선택 이유:
  - 함수 시그니처와 docstring 섹션의 의미 정합성을 검사한다
  - signature 수준 계약에서 상위 의미와 경계를 읽는 최소 사례로 적합하다

### 6. swark-io/swark
- URL: https://github.com/swark-io/swark
- 선택 이유:
  - 코드베이스에서 Mermaid 아키텍처 다이어그램을 생성하는 최근 사례다
  - LLM을 이용해 코드에서 개념 표현으로 바로 올라가는 출력 형식을 관찰할 수 있다
  - 다만 explainability와 traceability 통제가 약하므로 보조 사례로 본다

## Design Takeaways

- 핵심 단계는 `collect contracts -> segment units -> lift concepts -> render concepts`다
- 출력은 최소 세 층으로 분리하는 편이 좋다
  - `concept summary`
  - `boundary / relation map`
  - `render target` (`Mermaid`, `pseudocode`, `matrix`, `vector index`)
- 단순 요약보다 중요한 것은 **traceability**다
  - 어떤 checklist 항목/CLI contract/schema 조각이 어떤 개념으로 lift되었는지 남겨야 한다
- 코드에서 바로 concept를 생성하더라도 중간에 `contract unit` 계층이 있어야 drift를 추적하기 쉽다
- diagram generation repo는 많지만, "execution contract를 읽고 상위 의미를 복원"하는 도구는 드물다
  - 따라서 기존 도구를 그대로 복사하기보다 `architecture recovery + documentation + lint` 패턴을 조합해야 한다

## Reject / Hold

- cloud diagram renderer만 하는 repo는 contract-to-concept 복원과는 거리가 있다
- LLM 기반 diagram 생성 도구는 출력은 매력적이지만, 근거 추적이 약하면 canonical source로 쓰기 어렵다
