# 사용자 의도 파악

## 정규화된 목표 기능

* 정규화된 목표는 **“코드베이스를 실제로 분석한 결과를 바탕으로, task/workflow/progress를 선택·추적·검증·수정하는 skills/commands/agents 중심 GitHub repo”**를 찾는 것이다.
* 이 기능은 repo 어딘가에 부수적으로 존재하면 안 되고, **core/primary subsystem**이어야 한다.

## 필수 요구사항

* 코드베이스 분석이 README 문구가 아니라 **실제 명령/모듈/파서/맵핑 계층**으로 드러날 것.
* 분석 결과가 **progress/workflow/task state**와 연결될 것.
* **핵심 module 또는 파일 묶음**을 식별할 수 있을 것.
* **문서 + 실제 소스코드**로 교차 검증 가능할 것.
* 가능하면 **skills/commands/agents** 구조가 분명할 것.

## 선택 요구사항

* AST/IR/MCP 같은 **parser-first 설계**.
* task 선택 → 계획 → 구현 → 검증 → 배송까지 이어지는 **단계형 workflow**.
* persistent state, retry/fallback, drift detection.
* permissive license, 유지보수 신호, test/example 흔적.

## 제외 조건

* 코드베이스 분석이 **향후 예정 기능**이거나 이슈 수준에서만 제안된 경우.
* task manager는 강하지만 **codebase-analysis가 peripheral**인 경우.
* repo 이름/인기도만으로 맞아 보이는 경우.
* 핵심 module을 특정할 수 없는 경우.

## 성공 판정 기준

* 성공 추천은 **repo-level fit**과 **module-level fit**이 모두 높고, 추천 module이 왜 core인지 설명 가능해야 한다.
* 구조적 증거: 디렉터리/명령/상태파일/파서 계층이 타깃 기능을 직접 뒷받침할 것.
* test/example 증거: 기능 관련 명령 흐름, 예시, 테스트 구조가 존재할 것.
* runtime 증거: 있으면 가산점이지만, 이번 조사에서는 **정적/구조 증거 우선**으로 판정했다.

# 표현 및 계측 전략

## R0. 표현 / 파서 / 프레임워크 선택 라우팅

### 평가 기준

* route_depth_estimate = 3
* loop_nesting_depth_estimate = 2
* need_parent_scope_tracking = true
* need_metric_attachment = true
* need_runtime_traceability = true
* need_round_trip_validation = true

### 분류 결과

* parser_required = true
* latex_primary = true
* langfuse_primary = true
* mermaid_secondary = false
* hybrid_representation = true

### 선택된 parser / SDK / framework

* selected_parser_or_sdk = `GitHub raw/tree source inspection + repo-native parser evidence (agentsys의 ast-grep repo-map, ABCoder의 UniAST/MCP)`
* selection_reason = 이번 타깃이 “코드베이스 분석 기반”이므로, README 매칭보다 **실제 파서/맵/AST 계층이 있는 repo**를 우선 평가하는 것이 맞았다. `agentsys`는 `ast-grep` 기반 `/repo-map`과 `/drift-detect`, 상태파일 기반 workflow를 갖고 있고, `ABCoder`는 UniAST/MCP/`/abcoder:schedule`-`task`-`recheck` 체인을 제공한다. ([GitHub][1])
* why_manual_parsing_was_not_used_first = 중첩 라우팅(repo→module→validation)과 state/evidence 비교가 필요해서, regex/감으로 읽는 방식 대신 **실제 source tree와 raw module**을 먼저 확인했다. ([GitHub][2])

### IR 정규화 계획

* IR_required = true
* IR fields used = `node_id, node_type, parent_scope, scope_path, purpose, inputs, outputs, thresholds, fallback_policy, evidence_links, confidence`
* round_trip_validation_plan = 후보 repo와 module을 IR로 축약한 뒤, repo-level / module-level / validation-level 표와 로그로 다시 투영했다. 자동 재생성까지 하지는 않았고, **수동 round-trip** 수준으로 수행했다.

### LaTeX / Mermaid / Langfuse 생성 계획

* LaTeX = planned
* Mermaid = skipped
* Langfuse = planned
* reason = 이번 결과는 **구조 + 점수 + fallback 로그**가 중요해서 LaTeX/Langfuse 쪽이 더 적합했다. Mermaid는 보조 시각화로는 가능하지만, 이번처럼 repo-level과 module-level 판정을 함께 담기에는 효용이 낮았다.

# 제어 구조 개요

## 노드 타입 정의

* Task = 정규화, 검색, 수집, module 추출처럼 명시적 작업을 수행하는 노드
* Router = 점수/증거/제약으로 분기하는 노드
* Loop = repo/module/실행 재시도 단위의 반복 노드
* Exit = 성공/부분성공/실패 종료 노드

## 노드 인덱스

* T0 = 사용자 의도 정규화
* T0a = 구조/표현 요구 분석
* R0 = 표현 / 파서 / 프레임워크 선택
* T1 = 검색 쿼리 생성
* T2 = repo 후보 수집
* L1 = repo 탐색 루프
* R1 = repo 적합성 라우팅
* T3 = module 후보 추출
* L2 = module 검증 루프
* R2 = 핵심 module 분류 라우팅
* R3 = 검증 전략 선택 라우팅
* L3 = 실행 / 트러블슈팅 루프
* R4 = 정합성 / fallback 라우팅
* E1 = 성공 종료
* E2 = 부분 성공 종료
* E3 = 실패 종료

## parent scope 맵

* parent(R0) = global
* parent(R1) = L1
* parent(L2) = L1
* parent(R2) = L2
* parent(R3) = L2
* parent(L3) = R3
* parent(R4) = L3 또는 L2

## route depth / loop nesting depth

* route_depth = 3
* loop_nesting_depth = 2
* representative_scope_paths =

  * `L1 > R1 > L2 > R2`
  * `L1 > R1 > L2 > R3 > R4`

# 라우팅 / 루프 진입 전의 Task

## T0. 사용자 요구 정규화

* input = `"코드베이스-Analysis-기반-Progress-Managements-Skills"` + 제공된 탐색/검증 템플릿
* output = “코드베이스 분석을 실제로 사용해 progress/workflow/task를 관리하는 skill-centric repo와 핵심 module 추천”
* assumptions =

  * MAX_REPO_CANDIDATES = 3
  * MAX_MODULES_PER_REPO = 3
  * MAX_EXEC_RETRIES = 2
  * SMALL_CORE_LOC_THRESHOLD = 200
  * MEDIUM_CORE_LOC_THRESHOLD = 800
  * MIN_REPO_ACCEPT_SCORE = 82
  * MIN_MODULE_ACCEPT_SCORE = 80
  * MIN_ALIGNMENT_ACCEPT_SCORE = 80
  * OUTPUT_LANGUAGE = 한국어
* hidden_constraints_inferred =

  * “progress management”는 단순 kanban이 아니라 **code-aware progress/workflow**를 뜻함.
  * “skills”라는 단어 때문에 **재사용 가능한 skill/command/agent 단위**가 중요함.
  * parser-first 성향이 강하므로 README-only 후보는 탈락 가능성이 높음.

## T1. GitHub 검색 쿼리 생성

* broad queries = `codebase analysis workflow skills github`, `ai task progress repo map drift detect github`, `AST driven coding workflow progress github`
* targeted queries = `site:github.com agent-sh/agentsys repo-map drift-detect workflow`, `site:github.com cloudwego/abcoder schedule recheck UniAST`, `site:github.com eyaltoledano/claude-task-master scan existing codebase`
* fallback queries = `github task management codebase analysis skills`, `github repo plan vs implementation drift workflow`
* negative filters = `-awesome-list -curated -prompt-only -readme-only`

## T2. repo 후보 수집 및 초기 점수화

* collected_candidates = [`agent-sh/agentsys`, `cloudwego/abcoder`, `eyaltoledano/claude-task-master`]
* initial_shortlist = [`agent-sh/agentsys`, `cloudwego/abcoder`, `eyaltoledano/claude-task-master`]
* initial_reasons =

  * `agentsys`: `/next-task`, `/drift-detect`, `/repo-map`, skills, state files가 모두 보여서 가장 균형이 좋다. ([GitHub][3])
  * `abcoder`: UniAST/MCP 기반 parser-first 설계와 `schedule → task → recheck` 흐름이 매우 강하다. ([GitHub][4])
  * `claude-task-master`: progress/task 관리 자체는 강하지만, 코드베이스 분석은 아직 보강 중인 흔적이 있다. ([GitHub][5])

## T3. 현재 repo 내부 module 후보 추출

* source_tree_signals = `agentsys/lib` 아래 `drift-detect`, `repo-map`, `state`, `discovery`가 공존하고, 문서에서는 `/next-task`가 exploration/planning/review/delivery를 하나의 흐름으로 묶는다. ([GitHub][2])
* likely_modules = [`lib/repo-map`, `lib/drift-detect`, `workflow-core bundle (lib/state/workflow-state.js + repo-map + drift-detect)`]
* likely_entrypoints = [`/next-task`, `/repo-map`, `/drift-detect`]. ([GitHub][6])
* likely_tests_examples = README/CLAUDE의 command examples, repo-wide test signal(3,751 tests), state files(`tasks.json`, `flow.json`). ([GitHub][3])

# 라우팅 규칙

## R1. Repo 적합성 라우팅

### 입력 신호

* README / docs evidence = `agentsys`는 `/next-task`, `/drift-detect`, `/repo-map`, 32 skills, state files를 명시한다. `abcoder`는 UniAST, MCP, slash commands, AST-driven workflow를 명시한다. `task-master`는 CLI 중심 task management와 progress를 강하게 내세운다. ([GitHub][3])
* code structure evidence = `agentsys/lib`에는 `drift-detect`, `repo-map`, `state`, `discovery`가 있고, `workflow-state.js`는 `tasks.json`/`flow.json`을 직접 다룬다. `abcoder`는 `main.go`에 `parse`, `mcp`, `init-spec`, `agent`가 있고, `.claude` 자산에 schedule/recheck가 있다. `task-master`는 `src/progress/*`, `index.js`, `packages/tm-core`가 보인다. ([GitHub][2])
* tests/examples evidence = `agentsys`는 3,751 tests와 E2E workflow testing을 주장한다. `abcoder`는 explicit slash-command workflow와 AST tool chain이 있다. `task-master`는 unit/integration/e2e 구조와 80% coverage 목표가 있다. ([GitHub][3])
* execution feasibility evidence = `agentsys`는 Node.js 18+, Git, GitHub/GitLab CLI, `/repo-map`용 `ast-grep`가 필요하다. `abcoder`는 `go install`, `parse`, `mcp`, `init-spec` 흐름이 분명하다. `task-master`는 CLI와 MCP 사용 흐름이 분명하다. ([GitHub][3])

### 평가 기준

* FunctionalMatchScore = 92
* CoreModuleVisibilityScore = 91
* ExecutionFeasibilityScore = 70
* TestExampleEvidenceScore = 78
* StructuralClarityScore = 89
* ExclusionPenalty = 5
* MaintenanceSignalScore = 87
* DocumentationSupportScore = 90

### 집계 방식

* RepoFitScore formula = `0.25*FunctionalMatch + 0.15*CoreModuleVisibility + 0.10*ExecutionFeasibility + 0.15*TestExampleEvidence + 0.15*StructuralClarity + 0.10*MaintenanceSignal + 0.10*DocumentationSupport - 0.05*ExclusionPenalty`
* RepoFitScore actual = `86.2 / 100`

### 구체적인 분류 방법

* Pass 조건 = `RepoFitScore >= 82` 이고 hard exclusion 없음
* Hold 조건 = `78~81.9` 또는 핵심성은 높지만 증거가 한 축에서 비어 있음
* Reject 조건 = 코드베이스 분석이 peripheral 이거나, core module 식별이 안 되거나, 구조상 타깃과 다른 경우

### 현재 판정

* decision = Pass (`agent-sh/agentsys`)
* why_this_branch = 코드베이스 분석(`/repo-map`, `/drift-detect`)과 progress/workflow(`/next-task`, `tasks.json`, `flow.json`)가 **같은 런타임 안에 결합**되어 있고, skills까지 명시돼 있다. ([GitHub][3])
* why_not_other_branches = `abcoder`는 analysis 쪽은 매우 강하지만 persistent progress/workflow state가 약하고, `task-master`는 progress 쪽은 강하지만 codebase-analysis가 아직 중심 기능으로 완성되지 않았다. ([GitHub][4])
* next_node = L2

## R2. 핵심 module 라우팅

### 입력 신호

* module candidate = `workflow-core bundle (/next-task orchestration backed by lib/state/workflow-state.js + lib/repo-map + lib/drift-detect)`
* anchoring files = `lib/state/workflow-state.js`, `lib/repo-map/index.js`, `lib/drift-detect/collectors.js`
* entrypoints = `/next-task`, `/repo-map`, `/drift-detect`
* tests/examples = `/next-task`의 12-phase 문서, state file 문서, `/repo-map`/`/drift-detect` 설명과 raw source

### 평가 기준

* FeatureCentralityScore = 94
* EntrypointPresenceScore = 89
* TestCoverageForFeatureScore = 62
* ExampleCoverageScore = 80
* DependencyFocusScore = 5
* ArchitecturalProximityScore = 93
* InvocationClarityScore = 87
* DocumentationMentionScore = 90

### 집계 방식

* ModuleFitScore formula = `0.30*FeatureCentrality + 0.15*EntrypointPresence + 0.10*TestCoverage + 0.05*ExampleCoverage + 0.15*ArchitecturalProximity + 0.15*InvocationClarity + 0.10*DocumentationMention - 0.10*DependencyFocusPenalty`
* ModuleFitScore actual = `87.2 / 100`

### 구체적인 분류 방법

* Core 조건 = `ModuleFitScore >= 80` 이고 분석 결과가 progress/workflow를 실질적으로 구동
* Supporting 조건 = 분석 또는 진행관리 한 축만 강함
* Irrelevant 조건 = wrapper/utility 수준이거나 타깃 기능이 주변부

### 현재 판정

* decision = Core
* why_this_module_is_or_is_not_core = `lib/repo-map`만 보면 분석 substrate라서 Supporting이고, `lib/drift-detect`만 보면 plan-vs-implementation 정합성 점검이라 강하지만 범위가 좁다. 반면 `workflow-state.js`는 `tasks.json`/`flow.json`으로 진행 상태를 영속화하고, `/next-task`는 exploration→planning→review→delivery까지 12단계를 강제한다. 그래서 **단일 파일보다는 이 세 파일/명령의 결합이 실제 타깃 기능의 핵심 구현 묶음**이다. ([GitHub][7])
* next_node = R3

## R3. 코드 양 / 실행 가능성 라우팅

### 입력 신호

* estimated_core_loc = Medium (대략 300~700 LOC 수준의 핵심 의미 경로)
* runnable_entrypoint_exists = true
* environment_ready = false
* tests/examples_available = partial
* dependency_complexity = medium

### 평가 기준

* LOC bucket = Medium
* static_semantic_readability = high
* runtime_value = medium-high
* runtime_feasibility = medium-low
* structure_only_risk = medium

### 구체적인 분류 방법

* Static-first 조건 = 핵심 의미 경로를 raw source로 읽을 수 있고, 추천 판단에 필요한 구조 증거가 충분할 때
* Dynamic-first 조건 = 환경 의존성이 낮고 feature-specific 실행이 작게 재현 가능할 때
* Structure-only 조건 = raw source보다 tree/docs만 있고 코드 의미 판독이 부족할 때

### 현재 판정

* decision = Static-first
* why_this_path_was_selected = `workflow-state.js`, `repo-map`, `drift-detect`의 실제 소스가 열려 있고, 문서도 `/next-task`의 12단계와 state files를 자세히 보여 준다. 반면 live runtime은 Claude Code, GitHub CLI, `ast-grep` 등 환경 의존성이 있어 이번 조사 범위에서는 정적 검증이 더 효율적이었다. ([GitHub][7])
* next_node = R4

## R4. 정합성 / fallback 라우팅

### 입력 신호

* intent-module alignment evidence = 코드베이스 분석(`/repo-map`, `drift-detect`)과 진행 상태(`tasks.json`, `flow.json`)가 한 흐름 안에서 연결됨
* execution output evidence = 직접 실행은 없음. 다만 `/next-task` 실사용 중 delivery-validator 이슈가 기록돼 있다.
* structure consistency evidence = source tree와 raw source, README/CLAUDE 설명이 서로 잘 맞음
* mismatch log = runtime-proof gap, delivery-validator known issue, feature가 여러 파일에 분산됨

### 평가 기준

* IntentModuleAlignmentScore = 88
* ExecutionOutputAlignmentScore = 55
* StructuralConsistencyScore = 91
* DocumentationConsistencyScore = 89
* MismatchSeverityScore = 32
* ConfidenceScore = 81

### 구체적인 분류 방법

* Accept 조건 = 구조/코드/실행 증거가 모두 강함
* Retry_with_other_module_in_same_repo 조건 = mismatch가 module-local일 때
* Retry_with_another_repo 조건 = repo-level mismatch 또는 구조적 불일치일 때
* Partial_accept_with_limitations 조건 = 구조/코드 증거는 강하지만 runtime proof가 부족할 때
* Reject_current_path 조건 = 핵심성이나 정합성이 부족할 때

### 현재 판정

* decision = Partial_accept_with_limitations
* why_this_branch = 추천 자체는 충분히 가능하지만, 이번 조사에서는 live execution을 하지 않았고, 실제 `/next-task` 흐름의 delivery-validator에 2026-02-04 런타임 이슈가 보고된 적이 있다. ([GitHub][8])
* why_not_other_branches = same-repo 대안(`repo-map`, `drift-detect`)은 이미 검토했지만 각각 분석 또는 정합성 점검에 치우쳐 있었고, cross-repo 대안인 `abcoder`는 parser-first는 더 강하지만 progress state가 약했다. ([GitHub][1])
* next_node = E2

# 루프

## L1. Repo 후보 탐색 루프

### iterator

* repo_candidates = [`agent-sh/agentsys`, `cloudwego/abcoder`, `eyaltoledano/claude-task-master`]

### entry

* entry_condition = shortlist가 1개 이상 존재

### body

* main_tasks = 후보 repo 수집 → docs/source/tree 확인 → R1 점수화 → 통과 repo만 module 검증
* routers_invoked = R1

### continue

* continue_condition = accepted_result가 확정되지 않았거나, 비교 가치가 높은 대안 repo가 남아 있음

### exit

* exit_condition = 최고 적합 repo가 정해지고, 대안 repo의 탈락/보류 이유가 충분히 설명됨
* actual_exit_reason = `agentsys`가 1위였고, `abcoder`/`task-master`의 비교 탈락 이유도 확보됨

### iteration log

* iteration_1 = `agent-sh/agentsys` → Pass → L2 진입
* iteration_2 = `cloudwego/abcoder` → Hold(강한 대안) → 비교 보류
* iteration_3 = `eyaltoledano/claude-task-master` → Reject

## L2. Repo 내부 module 검증 루프

### iterator

* module_candidates = [`lib/repo-map`, `lib/drift-detect`, `workflow-core bundle`]

### entry

* entry_condition = `agentsys`가 R1을 통과

### body

* main_tasks = module 후보 추출 → R2로 core/supporting 분류 → R3로 검증 경로 선택
* routers_invoked = R2, R3

### continue

* continue_condition = 아직 Core 모듈이 확정되지 않았고, 같은 repo 안의 대안 module이 남아 있음

### exit

* exit_condition = codebase-analysis와 progress-management를 함께 담는 core 묶음을 찾음
* actual_exit_reason = `workflow-core bundle`을 Core로 확정

### iteration log

* module_iteration_1 = `lib/repo-map` → Supporting (분석 substrate는 강함, progress 관리 단독 책임은 아님)
* module_iteration_2 = `lib/drift-detect` → Supporting/Core-borderline (plan-vs-implementation 정합성은 강함, 전체 progress lifecycle은 아님)
* module_iteration_3 = `workflow-core bundle` → Core (분석 + state + workflow가 결합)

## L3. 실행 / 트러블슈팅 루프

### iterator

* troubleshooting_attempts = 0

### entry

* entry_condition = R3가 Dynamic-first를 택할 때

### body

* environment inspection = not entered
* execution command selection = not entered
* execution = not entered
* error classification = not entered
* retry hypothesis = not entered

### continue

* continue_condition = not entered

### exit

* exit_condition = R3가 Static-first를 선택하여 L3 미진입
* actual_exit_reason = 정적/구조 검증으로 추천 판단 임계치를 넘김

### attempt log

* attempt_1 = not entered
* attempt_2 = not entered

# Repo 검증 로그

## 후보별 요약

| repo                            | claimed feature                                   | repo fit score | status | main evidence                                                   | main rejection or acceptance reason              |
| ------------------------------- | ------------------------------------------------- | -------------- | ------ | --------------------------------------------------------------- | ------------------------------------------------ |
| agent-sh/agentsys               | codebase-aware workflow orchestration with skills | 86.2           | Pass   | `/next-task`, `/drift-detect`, `/repo-map`, skills, state files | 분석과 진행관리의 균형이 가장 좋음                              |
| cloudwego/abcoder               | parser-first AST-driven coding workflow           | 82.1           | Hold   | UniAST, MCP, `schedule/task/recheck`, `parse/mcp`               | 분석은 최고 수준이나 persistent progress state가 약함        |
| eyaltoledano/claude-task-master | AI task/progress management                       | 77.0           | Reject | `task-master next`, `src/progress/*`, tests                     | 진행관리는 강하지만 codebase-analysis가 아직 중심 기능으로 완성되지 않음 |

이 표의 근거는 `agentsys`의 명령/skills/state files 및 lib 구조, `abcoder`의 UniAST/MCP/AST-driven workflow, `task-master`의 task/progress CLI와 동시에 존재하는 “intelligent scan” 보강 이슈에서 왔다. ([GitHub][3])

## 보류/탈락 repo 상세

* repo = `cloudwego/abcoder`

* status = Hold

* reason = 코드베이스 분석 정확도와 parser-first 구조는 세 후보 중 가장 강하다. 다만 `schedule → task → recheck → coding`은 **계획/검증**에는 강하지만, `agentsys`처럼 task selection·workflow state·delivery validation·ship까지 잇는 진행관리 런타임은 약하다. ([GitHub][4])

* whether_same_feature_exists_but_peripheral = 아니오. feature는 core지만, “progress management” 범위가 상대적으로 좁다.

* whether_execution_path_was_viable = 부분적으로 예. `parse`, `mcp`, `init-spec`는 명확하지만, `agent`는 WIP라고 명시되어 있다. ([GitHub][4])

* repo = `eyaltoledano/claude-task-master`

* status = Reject

* reason = task/progress 관리와 CLI, 테스트 구조는 강하지만, 기존 코드베이스를 똑똑하게 훑는 `scan`은 2025-04-01 기준 enhancement issue로 열려 있었고, PRD 재파싱 시 기존 코드베이스를 분석해 task를 갱신하자는 요구도 2026년 이슈로 남아 있었다. 즉 **codebase-analysis-backed** progress management가 아직 중심 구현으로 닫히지 않았다. ([GitHub][5])

* whether_same_feature_exists_but_peripheral = 예. progress는 core지만 codebase analysis는 보강 중이다. ([GitHub][9])

* whether_execution_path_was_viable = 예. `task-master next`, `parse-prd`, MCP/CLI 흐름은 존재한다. ([GitHub][10])

# 핵심 module 검증 로그

## module 후보별 요약

| repo                            | module                     | module fit score | classification                     | validation path | main evidence                                              | main reason                            |
| ------------------------------- | -------------------------- | ---------------- | ---------------------------------- | --------------- | ---------------------------------------------------------- | -------------------------------------- |
| agent-sh/agentsys               | `lib/repo-map`             | 80.1             | Supporting                         | Static-first    | AST symbol/import mapping                                  | 분석 substrate는 강하지만 progress 핵심은 아님     |
| agent-sh/agentsys               | `lib/drift-detect`         | 83.4             | Supporting                         | Static-first    | deterministic collectors, plan-vs-implementation           | 정합성 점검은 강하지만 전체 lifecycle은 아님          |
| agent-sh/agentsys               | `workflow-core bundle`     | 87.2             | Core                               | Static-first    | `tasks.json`/`flow.json` + `/next-task` + analysis modules | 분석과 진행관리의 결합점                          |
| cloudwego/abcoder               | `AST-Driven Coding bundle` | 85.5             | Core                               | Static-first    | UniAST + slash commands + MCP                              | parser-first 최고 수준, progress state는 약함 |
| eyaltoledano/claude-task-master | `src/progress/*`           | 77.5             | Core(로컬) / overall target mismatch | Static-first    | progress trackers, CLI                                     | progress는 강하나 codebase-analysis 부족     |

근거 파일은 `agentsys`의 `workflow-state.js`, `repo-map/index.js`, `drift-detect/collectors.js`, `abcoder`의 `main.go`와 `.claude/commands`, `task-master`의 `src/progress/*`와 CLI entrypoint다. ([GitHub][7])

## 추천 핵심 module 상세

* repo = `agent-sh/agentsys`
* module = `workflow-core bundle (/next-task orchestration backed by lib/state/workflow-state.js + lib/repo-map + lib/drift-detect)`
* anchoring files = `lib/state/workflow-state.js`, `lib/repo-map/index.js`, `lib/drift-detect/collectors.js`
* why_core = `workflow-state.js`가 active task와 workflow progress를 영속화하고, `/next-task`가 exploration→planning→review→delivery를 강제하며, `repo-map`과 `drift-detect`가 코드베이스 분석/정합성 판정을 공급한다. 이 셋이 합쳐져야 “코드베이스 분석 기반 progress management”가 성립한다. ([GitHub][7])
* why_not_supporting_only = 단일 모듈로 보면 Supporting인 부분이 있지만, **사용자 타깃 기능 자체가 cross-cutting**이라 이 파일 묶음이 실제 핵심 구현 단위다.
* why_not_irrelevant = 세 파일 모두 타깃 기능과 직접 연결되고, wrapper 수준이 아니다.
* likely minimal entrypoint = `/next-task`
* likely minimal proof artifact = `.claude/flow.json` / `.claude/tasks.json` 갱신 + `/repo-map` 결과 캐시 + `/drift-detect` 결과

# 실행 / 트러블슈팅 로그

## 실행 전략

* preferred execution path = `agentsys` 설치 → `/repo-map init` → `/next-task` 최소 워크플로우 확인
* why this path = `/next-task`가 progress lifecycle을 가장 직접적으로 증명하고, `/repo-map`이 분석 substrate를 분리 검증할 수 있기 때문이다. ([GitHub][3])
* smallest proving command or test = `/next-task` 1회 + 생성된 `tasks.json`/`flow.json` 확인

## 실행 시도별 기록

### attempt 1

* command = not executed
* setup = not executed
* observed output = none
* error = none
* hypothesis = 이번 조사 범위에서는 구조/정적 증거로 1차 추천까지 가능
* result = skipped

### attempt 2

* command = not executed
* setup = not executed
* observed output = none
* error = none
* hypothesis = not applicable
* result = skipped

## 실행 결과 해석

* what was proven = source-level로는 state persistence, repo-map AST substrate, drift-detect deterministic collectors, `/next-task` 12단계 workflow를 확인했다. ([GitHub][7])
* what remains unproven = 내 환경에서 실제 `/next-task`가 end-to-end로 성공하는지
* whether runtime evidence changed recommendation = 예. 직접 실행을 안 했기 때문에 최종 verdict를 Accept가 아니라 **Partial Accept**로 낮췄다. 또한 실제 delivery-validator 런타임 이슈가 보고된 점도 반영했다. ([GitHub][8])

# 불일치 및 fallback 처리

## mismatch taxonomy 적용 결과

| mismatch_id | scope     | type                      | severity | expected                                 | observed                                         | likely cause                            | fallback                             |
| ----------- | --------- | ------------------------- | -------- | ---------------------------------------- | ------------------------------------------------ | --------------------------------------- | ------------------------------------ |
| M1          | repo      | scope mismatch            | moderate | codebase-analysis + progress 둘 다 강한 repo | `abcoder`는 analysis가 더 강하고 progress state는 약함    | 설계 초점이 parser-first coding context      | strong alternative로 Hold             |
| M2          | repo      | implementation mismatch   | high     | codebase-analysis가 현재 중심 기능              | `task-master`는 scan/codebase 분석이 아직 보강 중         | product focus가 task/progress management | Reject                               |
| M3          | module    | scope mismatch            | moderate | 단일 module이 분석+진행관리 모두 담당                 | `repo-map`은 분석만 강함                               | module 분리가 명확함                          | same-repo 다른 module 확인               |
| M4          | module    | scope mismatch            | moderate | 전체 progress lifecycle 담당                 | `drift-detect`는 정합성 점검에 치우침                      | feature 범위가 더 좁음                        | same-repo 다른 module 확인               |
| M5          | execution | incomplete-proof mismatch | moderate | 로컬 runtime 성공                            | live execution 미수행                               | 조사 범위 제한                                | Partial Accept                       |
| M6          | execution | runtime-only mismatch     | moderate | delivery validation 자동화 안정성              | `/next-task` phase 10에서 delivery-validator 이슈 보고 | Claude Code runtime 의존성                 | manual verification 또는 후속 runtime 검증 |

`M2`는 `task-master`의 intelligent scan 제안 이슈와 lifecycle 개선 이슈에서, `M6`는 `agentsys`의 2026-02-04 delivery-validator 이슈에서 나온다. ([GitHub][9])

## 같은 repo 내 대안 module 검토 여부

* attempted = yes
* modules_checked = [`lib/repo-map`, `lib/drift-detect`, `workflow-core bundle`]
* reason_for_staying_in_same_repo_or_leaving = 먼저 `agentsys` 안에서 분석 중심 module과 진행관리 중심 module을 각각 검토한 뒤, 두 축을 묶는 bundle을 Core로 확정했다. 이 때문에 cross-repo 이동 전에 same-repo fallback 규칙을 지켰다.

## 다음 repo로 넘어간 이유

* triggered_at = `R1` and `R4`
* reason =

  * `task-master`는 R1에서 repo-level mismatch
  * `abcoder`는 R4 수준에서 “강한 대안이지만 최종 1위는 아님”으로 정리
* why same-repo fallback was insufficient = `agentsys` 내부에서는 이미 core bundle을 찾았고, `abcoder`/`task-master`는 repo 성격 자체가 달랐다.

# 표현 산출물

## LaTeX spec

* generated = planned
* summary_of_contents = node/loop/router 정의, RepoFit/ModuleFit 공식, fallback 정책, acceptance threshold
* what LaTeX made clearer = repo-level과 module-level 판정을 같은 문서에서 **정밀한 표 형식**으로 붙여 놓기 좋다

## Langfuse instrumentation / trace plan

* generated = planned
* trace root = `repo-validation-campaign: codebase-analysis-progress-management`
* observation mapping =

  * T0/T1/T2/T3 = preparation observations
  * R0/R1/R2/R3/R4 = decision observations
  * L1/L2/L3 = loop iteration groups
  * execution retries = attempt observations
* score schema = `repo_fit`, `module_fit`, `alignment`, `mismatch_severity`, `confidence`
* tag schema = `feature:codebase-progress`, `repo:agentsys|abcoder|task-master`, `module:workflow-core|repo-map|drift-detect`, `stage:R1|R2|R4`
* retry / mismatch representation = mismatch event에 `type`, `scope`, `severity`, `fallback_target` 기록
* why Langfuse was or was not the better choice here = 실제 runtime trace를 남길 때는 Mermaid보다 훨씬 낫다. 다만 이번 답변은 조사 보고서라 **instrumentation plan만 제시**했다.

## Mermaid summary (optional)

* generated = skipped
* summary_of_contents = not applicable
* why Mermaid was secondary or sufficient = 구조만 그리면 핵심 차이점(분석 강도 vs 진행관리 강도 vs runtime gap)이 잘 안 보인다

# 최종 추천

## 추천 repo

* name = `agent-sh/agentsys`
* reason = 세 후보 중 **코드베이스 분석**, **progress/workflow state**, **skills/commands/agents**, **drift detection**을 가장 균형 있게 한 repo다. `/next-task`, `/repo-map`, `/drift-detect`, `tasks.json`/`flow.json`, skills 구조가 서로 연결되어 있다. ([GitHub][3])
* repo_fit_score = `86.2 / 100`

## 추천 핵심 module

* module = `workflow-core bundle (/next-task orchestration backed by lib/state/workflow-state.js + lib/repo-map + lib/drift-detect)`
* reason = 사용자가 찾는 기능은 단일 파일보다 **분석 substrate + state persistence + workflow orchestration**의 결합으로 성립한다. 이 묶음이 그 최소 핵심 단위다. ([GitHub][7])
* module_fit_score = `87.2 / 100`

## 검증 근거

* strongest structural evidence = `agentsys/lib`에 `state`, `repo-map`, `drift-detect`, `discovery`가 공존하고, 문서상 `/next-task`가 exploration/planning/review/delivery를 하나의 단계형 workflow로 정의한다. ([GitHub][2])
* strongest code-level evidence = `workflow-state.js`가 `tasks.json`/`flow.json`을 직접 관리하고, `repo-map/index.js`가 `ast-grep` 기반 AST 맵을 생성하며, `drift-detect/collectors.js`가 deterministic JS collectors를 제공한다. ([GitHub][7])
* strongest test/example evidence = `agentsys`는 command examples와 repo-wide test signal(3,751 tests, E2E workflow testing)을 제시한다. ([GitHub][3])
* strongest runtime evidence = 직접 실행 증거는 없지만, `/next-task` phase 10의 delivery-validator bug issue는 해당 workflow가 실제 사용되고 있음을 간접적으로 보여 준다. ([GitHub][8])

## 발견한 한계

* evidence gaps = feature-specific test 파일까지는 내려가지 못했다
* runtime limitations = Claude Code / GitHub CLI / `ast-grep` 의존성 때문에 live run을 생략했다
* parser / tooling limitations = GitHub 웹 인터페이스 기반 조사라 로컬 AST 재구성은 하지 않았다
* residual ambiguity = “progress management”를 얼마나 넓게 볼지에 따라 `abcoder`를 1위로 볼 여지도 약간 있다

## 최종 정합성 판단

* alignment verdict = Partial Accept
* alignment score = `85 / 100`
* confidence score = `81 / 100`
* confidence explanation = 코드/구조 증거는 충분히 강하고, 대안 두 개와 비교했을 때 우위가 분명하다. 다만 직접 실행 검증이 없고, delivery-validator 관련 runtime issue가 있어 최종 confidence를 보수적으로 낮췄다. ([GitHub][8])

# 종료 규칙 적용 결과

## 종료 노드

* exit_node = E2

## 종료 사유

* reason = 가장 적합한 repo와 core module은 찾았지만, runtime proof가 완전하지 않아 부분 성공으로 종료

## 추가 탐색 가치

* whether_more_search_is_likely_to_change_result = 낮음
* why = 상위 대안 세 개가 서로 다른 극점을 대표한다. `agentsys`는 균형형, `abcoder`는 parser-first analysis 특화형, `task-master`는 pure progress/task 특화형이라, 추가 탐색이 결과를 뒤집기보다 세부 선호(예: parser 우선 vs state 우선)를 미세 조정할 가능성이 더 크다. ([GitHub][3])

# 부록

## 사용한 parser / SDK / framework 목록

* parser_or_sdk_1 = `agentsys /repo-map (ast-grep 기반)`

* purpose = 코드베이스 심볼/임포트 맵 생성

* why chosen = 추천 repo 내부에서 분석 substrate의 핵심 증거

* why alternatives were not preferred = regex/README-only 설명보다 구현 강도가 높다. ([GitHub][1])

* parser_or_sdk_2 = `ABCoder UniAST + MCP`

* purpose = parser-first 대안 repo 검증

* why chosen = 후보 중 가장 강한 AST/IR 지향 설계

* why alternatives were not preferred = progress management state는 상대적으로 약해 최종 1위는 아님. ([GitHub][4])

* parser_or_sdk_3 = `GitHub raw/tree source inspection`

* purpose = README를 넘어 실제 파일/명령/상태 구조 검증

* why chosen = 빠르게 module-level 근거를 확보할 수 있음

* why alternatives were not preferred = 로컬 clone+실행은 환경 노이즈가 커서 이번 1차 연구 범위와 맞지 않았다

## IR 요약

* canonical fields used = `node_id, node_type, parent_scope, scope_path, purpose, evidence_links, thresholds, fallback_policy, confidence`
* how parent_scope was represented = `R1∈L1`, `R2∈L2`, `R3∈L2`, `R4∈L2/L3`
* how loops and routers were represented = repo loop와 module loop를 분리하고, selected repo 안에서 same-repo fallback을 명시
* whether round-trip validation succeeded = partially succeeded

## 제어 구조 한 줄 요약

* accepted path = `T0 → R0 → T1/T2 → L1(agentsys Pass) → L2(repo-map Supporting → drift-detect Supporting → workflow-core Core) → R3 Static-first → R4 Partial_accept → E2`
* representative rejected path = `T0 → T1/T2 → L1(task-master) → R1 Reject`
* highest-risk uncertainty node = `R4` (runtime proof 미실행 + known runtime issue)

[1]: https://raw.githubusercontent.com/agent-sh/agentsys/main/lib/repo-map/index.js "https://raw.githubusercontent.com/agent-sh/agentsys/main/lib/repo-map/index.js"
[2]: https://github.com/agent-sh/agentsys/tree/main/lib "https://github.com/agent-sh/agentsys/tree/main/lib"
[3]: https://github.com/agent-sh/agentsys "https://github.com/agent-sh/agentsys"
[4]: https://github.com/cloudwego/abcoder "https://github.com/cloudwego/abcoder"
[5]: https://github.com/eyaltoledano/claude-task-master "https://github.com/eyaltoledano/claude-task-master"
[6]: https://github.com/agent-sh/agentsys/blob/main/CLAUDE.md "https://github.com/agent-sh/agentsys/blob/main/CLAUDE.md"
[7]: https://raw.githubusercontent.com/agent-sh/agentsys/main/lib/state/workflow-state.js "https://raw.githubusercontent.com/agent-sh/agentsys/main/lib/state/workflow-state.js"
[8]: https://github.com/agent-sh/agentsys/issues/170 "https://github.com/agent-sh/agentsys/issues/170"
[9]: https://github.com/eyaltoledano/claude-task-master/issues/78 "https://github.com/eyaltoledano/claude-task-master/issues/78"
[10]: https://github.com/eyaltoledano/claude-task-master/blob/main/docs/tutorial.md "https://github.com/eyaltoledano/claude-task-master/blob/main/docs/tutorial.md"
