GitHub과 관련된 외부 검색·딥리서치 기능을 구현한 오픈 에이전트 스킬들은 대부분 GitHub CLI나 MCP(Server)를 활용해 검색·탐색 기능을 세분화한 것이 특징입니다. 아래는 주요 사례와 핵심 기능입니다.

### 주요 GitHub 검색/딥리서치 스킬

| 스킬명                                                      | 목적/주요 기능                                                                                                                   |
| -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **read-github**                                          | gitmcp.io를 통해 GitHub URL을 변환하고, 문서·코드·링크를 모아서 조회·검색(문서 검색·코드 검색·외부 URL 조회)                                                 |
| **github-kb / GitHub Knowledge Base**                    | `gh` CLI를 사용해 리포지터리/이슈/PR을 검색하고 로컬에 지식베이스를 구축, 토큰과 저장 경로를 설정 후 검색 명령을 실행                                                   |
| **gh-search-repos**                                      | `gh search repos` 명령으로 GitHub 전역에서 리포지터리 검색; 별 수·포크 수·언어·토픽·라이선스 등으로 필터링                                                   |
| **gh-search-issues**                                     | `gh search issues` 명령으로 여러 리포지터리의 이슈(또는 PR 포함)를 검색; 작성자·담당자·라벨·상태·작성일 등으로 조건 지정                                            |
| **gh-search-prs**                                        | `gh search prs` 명령으로 크로스‑리포지터리 Pull Request를 검색; 상태(merged, closed 등), 라벨, 리뷰 상태 등을 지정하고, 서술형 질의에는 `--` 구분자를 요구            |
| **gh-search-code**                                       | `gh search code`로 특정 함수나 파일을 리포지터리 전체에서 검색; 확장자·경로·언어 필터를 지원                                                               |
| **claude-github-kb‑skill (GitHub Intelligence Officer)** | 중국어 설명서 기반의 확장 스킬로, `gh search repos/issues/prs/code/commits` 명령을 체계적으로 활용; 리포지터리 탐색, 버그 해결, 코드 학습, 역사 추적 등을 명확한 절차와 함께 안내 |

### 사례별 설명

* **read‑github**: GitHub URL을 `gitmcp.io` 형식으로 변환하여 문서와 코드를 서비스적으로 제공하는 스킬입니다. 스킬 설명에서는 gitmcp.io를 사용하면 “문서에 대한 의미 기반 검색”과 정확한 파일 구조 탐색이 가능하며, README·docs·코드를 한 번에 가져오고 robots.txt를 존중하는 방식이 장점이라고 설명합니다. `gitmcp.py` 스크립트로 `fetch-docs`, `search-docs`, `search-code`, `fetch-url` 등의 명령을 실행해 문서 전체를 읽거나 특정 쿼리로 검색할 수 있습니다. 이 워크플로를 통해 먼저 문서를 가져오고, 특정 질문은 `search-docs`로, 구현 확인은 `search-code`로, 링크는 `fetch-url`로 처리합니다.

* **github‑kb (GitHub Knowledge Base)**: 기본적으로 `gh` CLI를 사용해 리포지터리·이슈·PR 검색을 수행하고, 로컬 지식베이스를 생성·보관하는 스킬입니다. 설명서에서는 GITHUB_TOKEN과 GITHUB_KB_PATH 환경변수를 설정하고 `gh search repos`, `gh search issues`, `gh search prs` 등 명령을 사용하여 검색하는 예제를 보여줍니다. 이 스킬은 클론된 리포지터리를 로컬에 저장하여 캐싱하며, 코드 양식(예: 빌드 스크립트)도 함께 제공해 검색 결과를 더 빠르게 활용할 수 있습니다.

* **gh‑search‑repos / gh‑search‑issues / gh‑search‑prs / gh‑search‑code**: aaddrick의 gh‑cli‑search 플러그인에 포함된 스킬로, GitHub CLI의 각 검색 명령을 감싼다.

  * `gh‑search‑repos`: GitHub 전역에서 리포지터리 검색 시 사용하며, 언어·주제·라이선스·비공개 여부 등을 필터링할 수 있고 별 수나 포크 수 같은 인기 지표로 정렬할 수 있습니다. 결과를 제외하려면 `-- "검색어 -qualifier:value"` 형식의 구분자를 사용해야 한다고 강조합니다.
  * `gh‑search‑issues`: 여러 리포지터리나 조직을 대상으로 이슈를 검색할 때 사용합니다. 스킬 문서는 `gh search issues`와 `gh issue list`의 차이를 명확히 설명하고, 작성자·담당자·라벨·상태·날짜 등 다양한 필터를 표로 정리합니다. exclusion(제외) 조건을 사용할 때는 `--` 구분자를 넣어야 한다는 점도 강조합니다.
  * `gh‑search‑prs`: PR 검색 전용 스킬로, draft 여부·merge 상태·리뷰 요청 상태·라벨 등을 조합해 검색할 수 있으며, 부정형 qualifier를 사용하려면 `--` 뒤에 인라인 쿼리를 넣어야 합니다.
  * `gh‑search‑code`: 코드 검색 스킬로, 파일 이름·경로·언어·확장자 등의 플래그를 통해 특정 함수나 설정 파일을 찾는 방법을 제시하며, 제외 조건을 쓸 때도 `--`를 명시합니다.

* **GitHub Intelligence Officer (claude‑github‑kb‑skill)**: JayTing511의 스킬은 “GitHub 情报官” 역할을 강조하며, `gh` CLI 명령으로 실시간 데이터를 가져와야 한다고 명시합니다. 스킬은 사용자 질문을 분석하여 어떤 `gh` 명령을 실행할지 선택하고, 예를 들어 라이브러리 찾기 질문에서는 `gh search repos` 명령과 언어·stars 필터를 조합한 예시를 제공하며, 오류 해결에는 `gh search issues`를 사용하여 특정 오류를 포함한 닫힌 이슈를 검색하고 라벨·저자·제외 조건을 조정하는 방법을 보여 줍니다. 또한 PR 검색, 코드 검색, 커밋 검색, 그리고 REST/GraphQL API 호출까지 단계적으로 안내하여 GitHub 전체에 대한 심층적인 정보 수집을 지원합니다.

이들 스킬은 공통적으로 “깊이 있는 GitHub 탐색”을 목표로 하며, GitHub CLI나 MCP를 이용해 기본 검색 이상의 능력을 제공합니다. 스킬 작성 시 명령어 구문(특히 `--` 구분자), 필터 사용법, 클라이언트 버전 요구 사항 등을 상세히 기술하여 에이전트가 GitHub 데이터를 신뢰할 수 있는 방식으로 호출하도록 설계되어 있습니다.