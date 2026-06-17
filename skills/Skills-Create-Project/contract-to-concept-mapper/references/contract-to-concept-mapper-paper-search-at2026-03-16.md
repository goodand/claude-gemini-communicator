# Paper Search Report — contract-to-concept-mapper

## 사용자 의도 파악

- 목표: 실행 계약 공간에서 개념 공간으로 되올리는 과정에 직접 도움 되는 학술 레퍼런스를 수집한다
- 초점:
  - structured code / contract -> natural language
  - code / change / project context -> summary
  - source -> diagram / architecture model
  - explainable summarization / interpretable data-to-text

## Shortlist

### 1. CodeBERT: A Pre-Trained Model for Programming and Natural Languages
- URL: https://aclanthology.org/2020.findings-emnlp.139/
- 선택 이유:
  - PL/NL shared representation이라는 기본 관점을 제공한다
  - `contract-to-concept-mapper`에서 코드/계약과 자연어 설명 사이의 공통 표현을 어떻게 볼지에 도움된다

### 2. CODE2SEQ: Generating Sequences from Structured Representations of Code
- URL: https://openreview.net/forum?id=H1gKYo09tX
- 선택 이유:
  - 구조화된 코드 표현을 자연어 시퀀스로 바꾸는 대표 사례다
  - checklist/schema 같은 구조화 입력을 concept summary로 바꾸는 방향의 기술적 비유가 된다

### 3. A Neural Architecture for Generating Natural Language Descriptions from Source Code Changes
- URL: https://aclanthology.org/P17-2045/
- 선택 이유:
  - 코드 변경에서 자연어 설명을 생성하는 초기 직접 사례다
  - "실행 흔적/변화"를 상위 설명으로 올리는 아이디어가 유효하다

### 4. Content Aware Source Code Change Description Generation
- URL: https://aclanthology.org/W18-6513/
- 선택 이유:
  - 코드 변경과 docstring 관계를 함께 본다
  - execution artifact와 기존 문서 의미를 결합해 concept를 복원하는 쪽에 더 가깝다

### 5. ProConSuL: Project Context for Code Summarization with LLMs
- URL: https://aclanthology.org/2024.emnlp-industry.65/
- 선택 이유:
  - 단일 함수가 아니라 project context를 넣어 summary를 개선한다
  - contract-to-concept도 개별 항목보다 project-level context를 함께 봐야 함을 뒷받침한다

### 6. Automatic Extraction of Security-Rich Dataflow Diagrams for Microservice Applications written in Java
- URL: https://www.sciencedirect.com/science/article/pii/S0164121223001176
- 보조 오픈 접근 URL: https://dblp.org/rec/journals/corr/abs-2304-12769.html
- 선택 이유:
  - 코드에서 상위 아키텍처/DFD 모델을 자동 추출하고 traceability까지 유지한다
  - concept lifting을 summary가 아닌 model reconstruction으로 보는 관점이 중요하다

### 7. Leveraging Large Language Models for Building Interpretable Rule-Based Data-to-Text Systems
- URL: https://aclanthology.org/2024.inlg-main.48/
- 선택 이유:
  - 구조화 입력에서 설명 가능한 rule-based text system을 만든다
  - 최종 출력이 자연어여도 중간 표현은 해석 가능해야 한다는 점이 핵심이다

### 8. Explainability Meets Text Summarization: A Survey
- URL: https://aclanthology.org/2024.inlg-main.49/
- 선택 이유:
  - 설명과 요약의 이중 관계를 정리한다
  - `execution contract -> concept summary`가 단순 요약이 아니라 explainability task라는 점을 뒷받침한다

## Design Takeaways

- `contract-to-concept-mapper`는 단순 요약기가 아니라 **설명 가능한 lifting system**으로 잡는 편이 맞다
- 자연어 출력만으로 끝내면 안 되고, 최소한 아래 중 하나는 같이 남겨야 한다
  - intermediate concept units
  - relation graph
  - trace links
- project context가 중요하다
  - checklist 한 줄, schema 한 필드만 보면 의미를 잘못 복원할 위험이 크다
- change description 연구는 `무엇이 달라졌는가`를, architecture extraction 연구는 `무엇이 상위 구조인가`를 보여준다
  - 둘을 합치면 `execution contract -> concept + boundary` 설계에 도움 된다
- interpretable data-to-text 관점은 매우 중요하다
  - 벡터나 LLM만으로 개념을 띄우더라도, rule-based or traceable intermediate representation이 필요하다

## Reject / Hold

- 순수 code summarization 모델은 유용하지만, checklist/schema/task 같은 비코드 계약 입력을 직접 다루지 못하는 경우가 많다
- LLM 요약만 강조하는 논문은 explainability와 traceability 요구가 약해 보류한다
