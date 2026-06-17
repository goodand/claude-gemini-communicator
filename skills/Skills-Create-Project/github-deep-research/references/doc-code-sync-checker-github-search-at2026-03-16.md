# GitHub Search Report — doc-code-sync-checker

## 사용자 의도 파악

- 목표: 문서에 정의된 규칙/필드/전이/제약이 코드에 반영됐는지 검증하고 drift를 보고하는 skill 설계에 필요한 GitHub 레퍼런스 수집
- 제외: 단순 문서 생성기, 일반 링크 크롤러만 하는 도구

## Shortlist

### 1. Coral-Protocol/Coral-RepoDocConsistencyChecker-Agent
- URL: https://github.com/Coral-Protocol/Coral-RepoDocConsistencyChecker-Agent
- 선택 이유:
  - repo 문서가 특정 파일 변경과 일치하는지 점검하는 목적이 정확히 맞음
  - agent 역할 정의가 직관적

### 2. OpenAPITools/openapi-diff
- URL: https://github.com/OpenAPITools/openapi-diff
- 선택 이유:
  - 두 계약 문서를 비교해 diff와 render를 내는 구조가 rule-set compare 설계에 도움
  - report 출력 포맷(HTML/Markdown/JSON) 아이디어를 가져올 수 있음

### 3. oasdiff/oasdiff
- URL: https://github.com/oasdiff/oasdiff
- 선택 이유:
  - `diff`, `breaking`, `changelog`, `checks`로 나뉜 명령 구조가 좋음
  - "변화 전체"와 "breaking subset"을 구분하는 관점이 유용

### 4. djmattyg007/doc-link-checker
- URL: https://github.com/djmattyg007/doc-link-checker
- 선택 이유:
  - 문서 스캔 -> reference 추출 -> 검증의 2단계 구조가 간단하지만 유효
  - 내부 reference 무결성 검사를 별도 rule type으로 둘 수 있음

### 5. doxygen/doxygen
- URL: https://github.com/doxygen/doxygen
- 선택 이유:
  - "문서를 소스에서 직접 추출하면 일관성 유지가 쉬워진다"는 관점 제공
  - undocumented source structure 추출은 code-side normalization 힌트

### 6. jsh9/pydoclint
- URL: https://github.com/jsh9/pydoclint
- 선택 이유:
  - docstring 섹션과 함수 시그니처/구현의 일치 여부를 검사
  - doc-code-sync-checker의 축소판 사례로 좋음

## Design Takeaways

- 핵심 단계는 `extract-doc`, `extract-code`, `normalize`, `compare`, `report`
- mismatch는 최소 세 종류로 나뉨:
  - `missing_in_code`
  - `missing_in_doc`
  - `shape_mismatch` 또는 `semantic_mismatch`
- 다이어그램/표/상수 dict처럼 표현이 다른 계약은 비교 전에 공통 IR로 정규화해야 함
- diff 전체와 실제 위험(breaking drift)을 분리하면 우선순위 보고가 쉬워짐

## Reject / Hold

- 일반 문서 생성기만으로는 drift detection을 해결하지 못함
- API diff 도구는 domain-specific이라 그대로 쓸 수는 없지만, 비교/보고 패턴은 매우 유용함
