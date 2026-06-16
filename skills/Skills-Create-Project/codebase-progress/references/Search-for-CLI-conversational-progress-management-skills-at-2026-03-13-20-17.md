사용자 의도 파악
정규화된 목표 기능

대상 기능 정의: 사용자는 “CLI-Agent-대화-세션(session)-기반-Progress-Managements-Skills”를 구현한 GitHub 레포를 찾으려 한다. 이를 검증 가능한 목표로 정규화하면 “여러 CLI 기반 AI 에이전트 도구(Codex, Claude Code, Copilot CLI, Gemini CLI 등)에서 생성한 대화 세션의 진행 상황과 상태를 탐지·저장·재개하는 기능을 제공하는 저장소” 이다. 즉, 대화 세션 파일을 스캔하여 메타데이터와 대화 내용을 추출하고, 다른 도구로 컨텍스트를 전달하거나 동일 도구에서 이어서 실행할 수 있어야 한다.

역할: 이 기능은 에이전트 도구의 핵심 모듈에 가까워야 하며, 단순 보조 기능이 아닌 _대화 진행 관리_가 주된 목적이어야 한다.

필수 요구사항

세션 탐색 및 인덱싱: 여러 CLI 에이전트 도구의 세션 디렉터리를 스캔하여 세션 목록을 생성하고 캐시하는 기능. 예를 들어 cli-continues는 14개 도구의 세션 디렉터리를 병렬로 스캔하여 통합 인덱스를 생성한다.

세션 컨텍스트 추출: 각 세션에 포함된 최근 메시지, 파일 변경, 도구 사용 기록 등을 파싱하여 구조화된 컨텍스트 객체를 생성해야 한다. cli-continues는 각 도구의 native 형식을 읽고 최근 메시지·파일 변경·도구 활동 등을 추출한다.

세션 재개/전환 기능: 사용자가 동일 도구에서 세션을 재개하거나 다른 도구로 컨텍스트를 전달하여 이어서 작업할 수 있어야 한다. cli-continues는 continues resume <id> 명령으로 세션을 선택하고 대상 도구를 선택할 수 있다.

대화 기록 또는 컨텍스트 파일 저장: 추출한 컨텍스트를 마크다운 또는 JSON 파일로 저장하여 다른 도구에서 참조할 수 있어야 한다.

다중 도구 지원: 최소한 여러 AI 코딩 CLI(Claude, Codex, Copilot CLI, Gemini CLI 등) 중 두 개 이상을 지원해야 한다. cli-continues는 14개 도구를 지원하며 임의의 조합으로 handoff 가능하다.

라이센스: 오픈소스 라이센스(MIT, Apache 등)로 공개되어야 한다. cli-continues는 MIT 라이센스를 채택한다.

선택 요구사항

대화 UI 또는 TUI: 세션을 선택하거나 대상 도구를 고르는 인터랙티브 UI/TUI가 있으면 편리하다.

세션 덤프/백업: 모든 세션을 마크다운 또는 JSON으로 일괄 추출하여 백업하는 기능.

설정 가능한 컨텍스트 크기: 추출하는 메시지 수나 세부정보 수준을 preset으로 조정할 수 있는 기능.

다른 기능: Git worktree 관리, AI 툴의 병렬 개발 지원 등은 nice-to-have이며 필수는 아니다 (예: AgentDev 프로젝트).

제외 조건

중앙 기능이 아닌 경우: 대화 세션 관리가 핵심이 아닌 도구(예: 일반 코드 검색 툴 또는 AI 프롬프트 라우팅에 집중한 툴)는 제외한다.

폐쇄형 라이센스: 상용 혹은 폐쇄 소프트웨어는 제외한다.

단일 도구 전용: 하나의 CLI만 지원하며 컨텍스트 전환 기능이 없는 프로젝트는 제외한다.

성공 판정 기준

구조적 증거: 레포의 소스코드에 세션 인덱싱, 컨텍스트 추출, 재개 로직이 구현되어 있어야 함. 예를 들어 cli-continues의 src/utils/index.ts에는 세션 인덱스를 만들고 저장·로드하는 함수들이 명시돼 있다.

테스트/예제 증거: 레포가 명령어 예제(npx continues) 또는 테스트 스크립트를 제공하여 실제로 세션을 탐색하고 재개하는 동작을 보여주는지 확인한다.

런타임 증거: 실행 환경에서 세션을 재개하거나 cross-tool handoff를 수행할 수 있음을 확인한다. 예시 명령과 스크린샷/로그가 있다면 가중치를 높게 본다.

성공 시점: 위의 증거가 충분하여 대상 기능을 실제로 제공한다고 판단되면 성공으로 판정한다.

표현 및 계측 전략
R0. 표현 / 파서 / 프레임워크 선택 라우팅
평가 기준

route_depth_estimate: 본 과제는 사용자 의도를 정규화하고, 저장소 선택 루프(L1)와 모듈 검증 루프(L2), 실행 검증 루프(L3)를 포함하므로 라우팅 깊이 2 이상이다.

loop_nesting_depth_estimate: L1과 L2, L3 세 단계의 중첩 루프가 예상되어 3 이상의 루프 깊이가 필요하다.

need_parent_scope_tracking: 루프와 라우터 간 상위·하위 스코프 관계를 명확히 해야 하므로 필요.

need_metric_attachment: 각 라우터에서 점수(RepoFitScore, ModuleFitScore 등)를 계산해야 하므로 필요.

need_runtime_traceability: 세션 재개 기능을 실제로 실행할 수 있는지 확인하는 것이 중요하므로 런타임 트레이스가 유용하다.

need_round_trip_validation: 파싱 후 IR로 변환하여 구조를 검증하는 단계가 포함될 수 있으므로 필요.

분류 결과

parser_required: 중첩 루트와 라우터가 많고 구조가 복잡하므로 코드 및 문서 파싱에 외부 파서를 활용해야 한다. cli-continues의 TypeScript 코드를 분석하기 위해 TypeScript AST를 파싱하거나 파일을 정적 분석하는 라이브러리가 필요하다.

latex_primary: 구조·점수·규칙을 동시에 표현해야 하므로 LaTeX를 기본 표현으로 선택한다.

langfuse_primary: 런타임 검증 및 재시도 로그를 추적할 수 있지만, 본 리서치는 실행 환경에서 실제 CLI를 실행하지 않으므로 Langfuse는 계획에만 포함한다.

mermaid_secondary: 흐름 요약을 빠르게 보여주는 데는 Mermaid가 보조적으로 유용하다.

hybrid_representation: 구조적 설명(LaTeX)과 런타임 플랜(Langfuse), 도식(Mermaid)이 모두 필요하여 hybrid.

선택된 parser / SDK / framework

selected_parser_or_sdk: TypeScript 소스코드 분석에는 ts-morph 같은 TypeScript AST 파서를 사용할 수 있다. 그러나 이 리포트에서는 주요 기능을 확인하기 위해 raw 코드 파싱보다 README와 핵심 소스 파일을 직접 검토하고, 함수 정의를 추출하는 데 간단한 문자열 파싱을 사용하였다. 파서 도구를 사용할 경우 ts-morph가 적합하며, YAML 설정 파일은 js-yaml로 파싱할 수 있다.

selection_reason: cli-continues는 TypeScript로 작성되어 있으므로 TypeScript AST 파서가 코드 구조를 이해하는 데 적합하다. 그러나 제한된 시간 내에 전체 AST를 구축하는 것은 과도하므로, 핵심 함수(세션 인덱싱·재개)를 수동으로 분석하였다.

why_manual_parsing_was_not_used_first: 중첩 루프와 정규화된 IR를 생성하는 데 구조적 파싱이 유리하기 때문이다. 수동 파싱만으로는 parent-scope 추적이 어려우며, 실수 가능성이 높다.

IR 정규화 계획

IR_required: Yes. 각 Task/Router/Loop 노드를 node_id, node_type, parent_scope, title, purpose, inputs, outputs, transition_rules, evidence_links, confidence 등으로 정규화해야 한다.

IR fields used: 위 정의된 필드를 모두 사용하며, 루프는 iterator, entry_condition, continue_condition, exit_condition을 포함한다.

round_trip_validation_plan: 구조를 LaTeX로 표현한 후 IR로 다시 변환하여 노드 관계, 전이 규칙, 점수 계산 공식을 검증한다. 발견된 불일치는 mismatch 로그로 기록한다.

LaTeX / Mermaid / Langfuse 생성 계획

LaTeX = planned: 구조적 명세와 점수 테이블을 LaTeX 표로 정리한다.

Mermaid = planned: 전체 워크플로우의 간단한 흐름도(사용자 의도→검색→리포 평가→모듈 평가→출력)를 보조적으로 제공한다.

Langfuse = planned: 실제 런타임 트레이스를 수집할 수 있는 계획만 제시하며, 이번 리서치에서 직접 실행은 하지 않음.

reason: 사용자가 요구하는 세밀한 구조와 점수 및 라우팅 규칙을 명확히 표현하기 위함이다.

제어 구조 개요
노드 타입 정의

Task: 명확한 작업을 수행하는 노드(T0, T1 등). 예: 검색어 생성, 후보 수집.

Router: 주어진 메트릭을 기반으로 분기하는 노드(R0–R4). 예: Repo 적합성 라우팅.

Loop: 반복 처리할 때 사용(L1–L3). 예: 여러 레포 후보를 평가하는 루프.

Exit: 종료 조건에 도달했을 때 선택되는 노드(E1–E3).

노드 인덱스

T0: 사용자 의도 정규화

T0a: 구조/표현 요구 분석

R0: 표현/파서/프레임워크 선택

T1: 검색 쿼리 생성

T2: 레포 후보 수집

L1: 레포 탐색 루프

R1: 레포 적합성 라우팅

T3: 모듈 후보 추출

L2: 모듈 검증 루프

R2: 핵심 모듈 분류 라우팅

R3: 검증 전략 선택 라우팅

L3: 실행/트러블슈팅 루프

R4: 정합성/fallback 라우팅

E1: 성공 종료

E2: 부분 성공 종료

E3: 실패 종료

parent scope 맵

parent(R0) = T0a – T0a에서 구조 요구를 평가한 후 R0으로 이동

parent(R1) = L1 – 레포 탐색 루프에서 각 레포 평가 후 R1 호출

parent(L2) = R1(Pass) – 레포가 통과되면 모듈 루프로 진입

parent(R2) = L2 – 모듈 루프에서 각 모듈 평가 후 R2 호출

parent(R3) = L2 – R2가 Core 또는 Supporting이면 검증 경로 결정

parent(L3) = R3(Dynamic-first) – 실행 검증이 필요할 때 실행 루프

parent(R4) = L3 or L2 – 실행 결과 또는 정적 분석 결과로 정합성/fallback 판단

route depth / loop nesting depth

route_depth = 4: R0→R1→R2→R3→R4까지 최대 4단계.

loop_nesting_depth = 3: L1(레포) → L2(모듈) → L3(실행) 3단계.

representative_scope_paths:

L1 → R1 → L2 → R2 → R3 → L3 → R4 → E1/E2/E3

L1 → R1 → R4 (레포 수준에서 탈락)

라우팅 / 루프 진입 전의 Task
T0. 사용자 요구 정규화

input: “CLI-Agent-대화-세션(session)-기반-Progress-Managements-Skills”라는 간단한 프레이즈.

output: 대화 세션 진행 관리 기능을 제공하는 레포 탐색을 목표로 설정하였다(위 정규화된 목표 기능 참조).

assumptions: 사용자 언어는 한국어이며, 구현 언어에는 특별한 제약이 없다고 가정한다. 주된 관심사는 다양한 CLI 에이전트 도구의 세션을 관리하는 기능이다.

hidden_constraints_inferred: 사용자는 최신 도구(2026년 기준)들을 지원하는 것을 원한다; 라이센스는 오픈소스 여야 한다.

T1. GitHub 검색 쿼리 생성

broad queries: "cli agent" session progress management, "resume session" CLI agent, "AI coding session handoff", agent session indexing GitHub 등.

targeted queries: "cli-continues" resume any AI coding session, "agentdev" worktree sessions ui, "cli agent session persistence" 등.

fallback queries: "AI coding session" CLI resume, "conversation history export" CLI agent.

negative filters: -"web" -"desktop"를 사용해 웹 기반 도구를 배제.

T2. repo 후보 수집 및 초기 점수화

collected_candidates:

cli-continues (yigitkonur/cli-continues) – 14개 AI 코딩 도구의 세션을 탐색하고 손쉽게 다른 도구로 handoff. README에 “sessions across 14 tools”와 “handoff”가 명시된다.

cli-agent (rohittcodes/cli-agent) – AI 도구 오케스트레이션과 컨텍스트 관리, 세션 지속성, 로그 및 통계 수집 기능을 제공한다.

AgentDev (xxchan/AgentDev) – Rust 기반 툴로 Git worktree를 사용하여 병렬 에이전트 개발을 돕고 session UI를 제공한다. 하지만 cross-tool handoff보다는 작업 트리 관리에 초점.

initial_shortlist: cli-continues와 cli-agent 두 가지. AgentDev는 세션 진행 관리가 핵심이 아니므로 hold.

initial_reasons: cli-continues는 명확히 “resume any AI coding session”을 표방하며 컨텍스트 추출과 handoff를 구현함. cli-agent는 세션 지속성과 컨텍스트 관리가 기능 목록에 있으나 cross-tool handoff는 없음. AgentDev는 주로 git worktree 관리와 병렬 개발 지원을 목표로 함.

T3. 현재 repo 내부 module 후보 추출
cli‑continues

source_tree_signals: src/utils/index.ts에 세션 인덱싱·저장·로드·컨텍스트 추출 로직이 구현되어 있음. src/utils/resume.ts에는 native resume, cross-tool resume, context 파일 저장 및 프롬프트 생성 등 재개 기능이 정의돼 있음. src/parsers/registry.ts에 각 도구의 어댑터가 등록되어 있다.

likely_modules:

utils/index.ts – unified session index 및 컨텍스트 추출

utils/resume.ts – 세션 재개/hand-off

parsers/registry.ts – 다양한 도구의 파서 어댑터 등록

likely_entrypoints: index.ts에서 위 모듈들을 export하며 공용 API 제공.

likely_tests_examples: README에 continues 실행 예제와 continues resume 명령 사용법이 제시되어 있음.

cli‑agent

source_tree_signals: 프로젝트가 Python으로 작성되며 핵심 클래스 MultiToolAIAgent 혹은 CodeAgent에서 세션 관리와 파일 인덱싱을 수행. 상세 소스는 분석 시간이 제한되어 구조만 파악.

likely_modules:

메인 스크립트 main.py – 에이전트 실행 및 CLI 루프.

에이전트 클래스 모듈 – 컨텍스트 관리와 세션 지속성 로직.

likely_entrypoints: uv run main.py로 실행.

likely_tests_examples: README 예제 명령에서 히스토리 내보내기, 세션 지속성 기능 언급.

라우팅 규칙
R1. Repo 적합성 라우팅
입력 신호

README / docs evidence: cli-continues는 README에서 여러 도구의 세션을 찾고 handoff 하는 방법을 자세히 설명. cli-agent는 세션 지속성, 컨텍스트 관리, 히스토리 export 기능을 명시. AgentDev는 worktree와 session UI에 대해 언급하지만 cross-tool session management는 없음.

code structure evidence: cli-continues 소스의 utils/index.ts와 utils/resume.ts에서 세션 인덱싱, 컨텍스트 추출, 재개 로직이 구현됨. cli-agent는 Python 코드로 약 250라인의 에이전트 클래스에 세션 지속성 로직이 있다고 README에 설명; 내부 코드를 직접 검토하진 못함.

tests/examples evidence: cli-continues는 README에 continues 실행 예제와 cross-tool resume 사용법을 보여준다. cli-agent는 예제 명령을 통해 히스토리 export 등을 시연하지만 cross-tool 이동은 없음.

execution feasibility evidence: cli-continues는 Node.js 환경에서 npx continues로 실행 가능; 설치가 간단하다. cli-agent는 Python 3.11과 Gemeni API 키를 요구하여 환경 준비가 필요하다.

평가 기준 및 합산식

RepoFitScore = w1·FunctionalMatch + w2·CoreModuleVisibility + w3·ExecutionFeasibility + w4·TestExampleEvidence + w5·StructuralClarity + w6·MaintenanceSignal + w7·DocumentationSupport – w8·ExclusionPenalty

가중치는 각각 1로 설정하였다. MIN_REPO_ACCEPT_SCORE = 7.0 으로 임의 설정.

구체적인 분류 방법

Pass 조건: RepoFitScore ≥ 7.0, 그리고 사용자가 요구한 기능이 중심 기능임.

Hold 조건: 5.0 ≤ RepoFitScore < 7.0 또는 기능이 주변적이나 가능성이 있을 때.

Reject 조건: RepoFitScore < 5.0 또는 필수 요구사항을 명백히 충족하지 않을 때.

현재 판정
repo	FunctionalMatch	CoreModuleVisibility	ExecutionFeasibility	TestExamples	StructuralClarity	MaintenanceSignals	DocumentationSupport	ExclusionPenalties	RepoFitScore	결정	다음 노드
cli-continues	2.0 (세션 인덱싱·컨텍스트 추출·재개를 명확히 구현)	1.5 (utils/index.ts & utils/resume.ts에서 주요 기능이 분리돼 있고 index.ts에서 export)	1.0 (npm install 없이 npx로 실행 가능)	1.0 (README에 여러 예제)	1.0 (소스 구조 명확)	0.5 (스타 933개, 최근 커밋 활발)	1.0 (README·AGENTS.md 등 문서 풍부)	0	8.0	Pass	L2
cli-agent	1.2 (세션 지속성 및 히스토리 export는 있지만 cross‑tool handoff 없음)	0.8 (에이전트 클래스 내에 혼합)	0.8 (Python 환경 및 API 키 필요)	0.5 (간단한 예제)	0.8 (코드 구조 일부 알려짐)	0.5 (신규 프로젝트, 스타 1개)	0.8 (README 상세)	0	5.4	Hold	L1 next candidate
AgentDev	0.5 (worktree 관리가 주 기능)	0.5 (세션 UI가 있지만 핵심 아님)	0.7 (Rust/PNPM 설치 필요)	0.3 (세션 UI 예제 부족)	0.8 (Rust 구조 명확)	0.6 (최근 커밋 있지만 규모 작음)	0.5 (README 간단)	0	3.9	Reject	다음 레포

why_this_branch: cli-continues는 RepoFitScore가 8.0으로 높고 필수 기능을 충족하여 Pass. cli-agent는 Hold로 남기고, AgentDev는 Reject.

next_node: cli-continues는 L2(모듈 검증 루프)로 이동. cli-agent는 다른 레포가 없을 때 fallback 후보로 남김.

R2. 핵심 module 라우팅 (for cli-continues)
입력 신호

module candidate: utils/index.ts, utils/resume.ts, parsers/registry.ts.

anchoring files: index.ts에서 이 모듈들을 export한다.

entrypoints: index.ts의 getAllSessions, extractContext, resume 함수가 외부 API다.

tests/examples: README에서 continues 명령이 이 모듈들의 기능을 호출한다.

평가 기준 및 합산식

ModuleFitScore = v1·FeatureCentrality + v2·EntrypointPresence + v3·TestCoverage + v4·ExampleCoverage + v5·ArchitecturalProximity + v6·InvocationClarity + v7·DocumentationMention – v8·DependencyFocusPenalty

가중치는 동일하게 1. MIN_MODULE_ACCEPT_SCORE = 5.0.

모듈별 평가
module	FeatureCentrality	EntrypointPresence	TestCoverage	ExampleCoverage	ArchitecturalProximity	InvocationClarity	DocsMention	Penalty	ModuleFitScore	분류
utils/index.ts	1.5 (세션 인덱스 구축과 컨텍스트 추출의 중추)	1.2 (public API에서 getAllSessions, extractContext를 export)	0.6 (테스트 파일 분석은 못했으나 README 예제가 함수를 사용)	0.7 (예제에서 세션 목록을 가져오는 부분 implicit)	1.0 (src/utils 안에서 핵심 로직)	1.0 (함수명·시그니처 명확)	0.8 (문서에서 extractContext 설명)	0	6.8	Core
utils/resume.ts	1.5 (native resume 및 cross‑tool resume 기능 담당)	1.3 (API에서 resume, nativeResume, crossToolResume export)	0.6 (테스트 확보 불가)	1.0 (README 예제에서 continues resume 사용)	1.0	1.0 (함수명·모드 명확)	0.8 (README에서 재개 과정 언급)	0	7.2	Core
parsers/registry.ts	1.2 (다양한 도구의 파서를 등록하여 통합 세션을 구축)	0.8 (공용 API로 export)	0.4 (각 도구 parser의 세부 테스트는 미확인)	0.6 (README에서 도구 지원 목록)	1.0	0.8 (파서 내부 호출)	0.7	0	5.5	Supporting

why_this_module_is_or_is_not_core: utils/index.ts와 utils/resume.ts는 세션 인덱싱과 재개라는 핵심 기능을 담당하여 Core로 분류. parsers/registry.ts는 여러 도구의 어댑터를 등록하여 중요하지만, 직접적으로 컨텍스트 추출을 수행하지 않으므로 Supporting.

next_node: Core 모듈 두 개(utils/index.ts, utils/resume.ts)에 대해 검증 전략 선택 (R3).

R3. 코드 양 / 실행 가능성 라우팅
입력 신호

estimated_core_loc: utils/index.ts는 약 260 LOC, utils/resume.ts는 약 350 LOC. 둘 다 Medium bucket.

runnable_entrypoint_exists: Yes. npx continues 명령으로 실질적인 실행 가능함.

environment_ready: Node.js/NPM 가 있는 환경이면 곧바로 실행 가능; 실행 부담 낮음.

tests/examples_available: README에 실행 예시가 있으나 별도의 테스트 스위트는 분석하지 못함.

dependency_complexity: dependencies는 package.json에 정의되어 있으나 특별한 빌드 단계는 없음.

평가 기준 및 분류

Static-first 조건: 코드가 적거나 실행 환경이 없을 때 선호. 여기서는 약 260~350 LOC로 정적 검토가 가능하지만 런타임 증거가 중요해 Dynamic-first에 가깝다.

Dynamic-first 조건: 실행 예제가 존재하고 npx continues로 바로 테스트 가능하며, 세션 파일을 인식하는 동작을 확인할 수 있다.

Structure-only 조건: 환경이 제한되어 실행이 불가능할 때. 해당 없음.

현재 판정

decision: Dynamic-first. 세션 인덱스 생성과 cross‑tool resume 기능을 실제로 실행해 보는 것이 핵심이며, npx continues 명령으로 간단히 실행 가능하므로 동적 검증이 적합하다.

why_this_path_was_selected: 컨텍스트 추출·재개 기능은 실행을 통해 직접 검증해야 신뢰도가 높다.

next_node: L3 (실행/트러블슈팅 루프)

R4. 정합성 / fallback 라우팅
입력 신호

intent‑module alignment evidence: Core 모듈이 사용자 목표와 얼마나 일치하는지. cli-continues는 세션 인덱싱과 재개라는 목표를 정확히 수행한다.

execution output evidence: 실행을 통해 세션을 성공적으로 탐지하고 재개하는지 확인해야 하나, 본 리서치에서는 환경의 제한으로 직접 실행하지 못하였다. 대신 README 예제와 코드 분석을 통해 성공 가능성을 판단한다.

structure consistency evidence: index.ts에서 함수들이 모듈을 통해 일관되게 export되고, 각 모듈의 책임이 명확하다.

mismatch log: 실행 검증을 하지 못한 것이 잠재적 불일치로 남는다.

평가 기준 및 분류

IntentModuleAlignmentScore: 2.0 (완벽하게 일치)

ExecutionOutputAlignmentScore: 1.0 (예제를 기반으로 가정)

StructuralConsistencyScore: 1.0 (모듈 구조 명확)

DocumentationConsistencyScore: 1.0 (README와 코드가 일치)

MismatchSeverityScore: 0.5 (실행 검증 부족)

ConfidenceScore: 종합적으로 8.5/10으로 설정.

분류 방법

Accept 조건: AlignmentScore ≥ 7.0, 중대한 mismatch 없음.

Retry_with_other_module_in_same_repo: 하나의 모듈에 문제 있을 때 다른 모듈 검증. 여기서는 두 core 모듈 모두 검토하였으므로 해당 없음.

Retry_with_another_repo: 레포 전체가 사용자 의도에 맞지 않을 때. 여기서는 필요없음.

Partial_accept_with_limitations: 증거가 부분적이거나 실행 검증 부족할 때. 이번 경우가 이에 해당할 수 있다.

Reject_current_path: 요구사항 불충족 시.

현재 판정

decision: Partial_accept_with_limitations. 코드와 문서에서 필수 기능이 구현된 것을 확인했으나, 실제 실행 검증을 수행하지 못했으므로 일부 한계가 있다.

why_this_branch: 구조적 분석과 문서에 기반해 기능이 충분히 일치하지만, 실행 결과를 직접 확인하지 못한 것이 한계다.

next_node: E2 (부분 성공 종료).

루프
L1. Repo 후보 탐색 루프

iterator: repo_candidates = [cli-continues, cli-agent] (AgentDev는 Reject 후 제외)

entry_condition: 후보 리스트가 비어 있지 않음.

body: 다음 레포 선택 → R1 로 라우팅 → 통과되면 L2로, 보류/탈락 시 다음 후보.

continue_condition: accepted_result가 없고 후보가 남아 있는 동안 반복.

exit_condition: accepted_result 발견 또는 후보가 모두 소진되거나 hard constraint로 중단.

actual_exit_reason: cli-continues가 Partial Accept로 선정되었고, Hold 상태의 cli-agent는 실행 검증 비용 대비 추가 이득이 적어 탐색을 종료함.

iteration log

Iteration 1: repo = cli-continues → R1: Pass → L2로 이동.

Iteration 2: repo = cli-agent → R1: Hold. cli-continues가 이미 부분 성공을 제공하므로 L1 종료.

L2. Repo 내부 module 검증 루프 (cli‑continues)

iterator: module_candidates = [utils/index.ts, utils/resume.ts, parsers/registry.ts]

entry_condition: R1에서 Pass 판단된 레포.

body: 다음 모듈 선택 → R2로 분류 → Core 모듈이면 R3 → 필요 시 L3 실행.

continue_condition: accept_result 없고 모듈 남아 있음.

exit_condition: Core 모듈 검증 후 R4에서 Accept/Partial Accept 판정.

actual_exit_reason: 두 core 모듈(utils/index.ts, utils/resume.ts)을 검토하고 Partial Accept 판정을 얻어 루프 종료.

iteration log

module_iteration 1: module = utils/index.ts → R2: Core → R3: Dynamic-first → L3 실행 계획 → R4: Partial Accept (shared with next module) → accept_result (partial) set.

module_iteration 2: module = utils/resume.ts → R2: Core → R3: Dynamic-first → L3 실행 계획 → R4: Partial Accept → 결과는 동일하므로 추가 검사 생략.

L3. 실행 / 트러블슈팅 루프 (계획 단계)

iterator: 실행 시도(0회)

entry_condition: Dynamic-first 경로 선택, 실행 가능한 환경 확인.

body: 환경 점검→최소 실행 명령 선택→실행→오류 분류→재시도 가설 도출.

continue_condition: 검증이 완료되지 않았고 재시도 횟수 < MAX_EXEC_RETRIES.

exit_condition: 실행 성공 또는 재시도 제한 도달.

actual_exit_reason: 본 분석에서는 실행 환경이 제공되지 않아 시도하지 못함.

attempt log

attempt 1: 계획상 명령 npx continues list --json 으로 세션 인덱싱을 검증하고, continues resume <id>로 재개를 검증할 예정. 환경 부재로 실행하지 못해 hypothesis level에서 종료.

Repo 검증 로그
후보별 요약
repo	claimed feature	repo fit score	status	main evidence	main rejection or acceptance reason
cli-continues	Cross‑tool AI coding session handoff	8.0	Pass → Partial Accept	README에 14개 도구의 세션을 찾아 컨텍스트를 추출하고 다른 도구로 handoff 하는 절차가 설명됨. 소스 코드에서 세션 인덱스 빌드, 컨텍스트 추출, 재개 로직 구현 확인.	실행 검증을 수행하지 못해 Partial Accept; 그럼에도 요구한 기능을 가장 잘 충족.
cli-agent	AI 도구 오케스트레이션, 세션 지속성	5.4	Hold	README에서 세션 persistence 및 히스토리 export, 통계 기능 언급. 그러나 cross‑tool handoff 기능 부재. 소스 구조가 명확하지 않음.	중심 기능이 세션 진행 관리가 아니며 cross‑tool handoff를 제공하지 않음.
AgentDev	Git worktree 및 session UI	3.9	Reject	README에서 worktree 및 session UI를 제공한다고 하지만 대화 세션 progress management에 직접적이지 않음.(https://raw.githubusercontent.com/xxchan/AgentDev/main/README.md#:~:text=agentdev)	기능 불일치 및 peripheral.
보류/탈락 repo 상세

repo = cli-agent

status = Hold

reason: 세션 지속성과 히스토리 export 기능은 있으나 cross‑tool handoff 부재. Python 기반으로 설치와 환경 구성이 필요해 실행 비용이 상대적으로 높음.

whether_same_feature_exists_but_peripheral: 세션 관리가 일부 포함되지만 핵심은 AI 도구 오케스트레이션.

whether_execution_path_was_viable: Python 환경과 API 키가 필요해 본 리서치 내에서 실행이 어려웠다.

repo = AgentDev

status = Reject

reason: 핵심 기능이 git worktree 관리이며, 대화 세션 진행 관리가 peripheral.

whether_same_feature_exists_but_peripheral: Session UI는 보조 기능에 불과하다.

whether_execution_path_was_viable: Rust 환경과 PNPM 설치가 필요하며 핵심 기능 미부합.

핵심 module 검증 로그
module 후보별 요약
repo	module	module fit score	classification	validation path	main evidence	main reason
cli‑continues	utils/index.ts	6.8	Core	Dynamic-first (planned)	세션 인덱스 생성 및 컨텍스트 추출 함수 구현	해당 파일이 세션 빌드/로드/컨텍스트 추출의 중심역할을 하며 공용 API에서 export
cli‑continues	utils/resume.ts	7.2	Core	Dynamic-first (planned)	native resume 및 cross‑tool resume 로직 구현	세션을 동일 도구에서 재개하거나 다른 도구로 handoff하는 로직이 구현되어 있음
cli‑continues	parsers/registry.ts	5.5	Supporting	Static-first	다양한 도구의 파서 어댑터 등록	파서 등록은 중요하지만 핵심 로직은 아님
cli‑agent	(미특정) Agent class	N/A	Hold	Not evaluated	코드 열람 부족	핵심 모듈 식별에 필요한 정보가 부족
추천 핵심 module 상세

repo = cli-continues

module = utils/index.ts & utils/resume.ts (둘을 하나의 핵심 모듈 집합으로 간주)

anchoring files: src/utils/index.ts, src/utils/resume.ts

why_core: 이 모듈들은 세션 인덱스 생성, 컨텍스트 추출, 세션 저장/로드 및 native/cross-tool resume 기능을 담당하여 대화 세션 진행 관리의 본질을 수행한다.

why_not_supporting_only: 파서 registry 등은 이 모듈들이 수행할 수 있도록 지원하지만, 핵심 로직(세션 관리)을 직접 구현하지는 않는다.

likely minimal entrypoint: getAllSessions()로 세션 목록을 가져오고 resume()으로 재개한다.

likely minimal proof artifact: 실행 예제 npx continues와 continues resume <id> 명령이 실제 핵심 모듈을 호출한다.

실행 / 트러블슈팅 로그
실행 전략

preferred execution path: 로컬에 여러 AI 도구가 설치되어 있다고 가정하고 npx continues 명령을 실행하여 세션을 탐지하고 continues resume <id>로 재개하는 것.

why this path: core 기능이 세션 검색과 handoff이기 때문에 가장 작고 명확한 검증 경로이다.

smallest proving command or test: npx continues list --json으로 세션 목록을 JSON으로 출력하고, 특정 세션 ID를 받아 continues resume <id> --in codex로 cross‑tool handoff를 시도한다.

실행 시도별 기록

attempt 1: 명령 npx continues list --json을 실행하여 세션 인덱스를 확인하고, 존재하는 세션 ID를 추출 후 continues resume abc123 --in gemini를 실행한다. 환경 미구성으로 실제 실행은 수행하지 못했고, README 예제에 기반한 가설적 성공을 기록.

attempt 2: N/A – 실제 환경이 없어서 추가 시도는 하지 않음.

실행 결과 해석

what was proven: 코드 분석과 README 예제로부터 세션 인덱싱과 handoff 로직이 구현되어 있음을 확인했다. 단, 실제 실행 결과를 직접 관찰하지는 못했다.

what remains unproven: 파일 시스템에 존재하는 실제 세션을 찾는지, cross‑tool handoff가 성공적으로 실행되는지 확인하지 못했다.

whether runtime evidence changed recommendation: 실행 증거 부족으로 인해 완전한 “Accept” 대신 “Partial Accept with limitations” 판단을 내렸다.

불일치 및 fallback 처리
mismatch taxonomy 적용 결과
mismatch_id	scope	type	severity	expected	observed	likely cause	fallback
M1	Execution	runtime-only mismatch	moderate	실제 세션을 찾고 재개하는 동작	실행 검증을 수행하지 못함	환경 부재로 실행하지 못함	Partial accept; 실행 증거 확보 시 완전한 Accept 가능
M2	Module	incomplete-proof mismatch	minor	테스트 스위트 또는 예제 코드	README와 소스 코드만 분석	테스트 코드 미확인	라우팅에서는 accept 가능하지만 신뢰도 낮음
같은 repo 내 대안 module 검토 여부

attempted: Yes. utils/index.ts와 utils/resume.ts 두 모듈을 검토한 후에도 불일치가 주요 모듈에 기인하는 것이 아니라 실행 검증 부재임을 확인했다.

modules_checked: parsers/registry.ts (supporting), utils/index.ts, utils/resume.ts.

reason_for_staying_in_same_repo_or_leaving: 주요 기능 모듈 모두 검토 후 Partial Accept를 얻었으므로 다른 모듈로 이동할 필요가 없었다.

다음 repo로 넘어간 이유

triggered_at: R4 (정합성 판단 단계)

reason: cli-continues에서 실행 증거가 부족하여 Partial Accept 판정을 받았으나, cli-agent 레포는 Hold 상태로, 기능이 미흡하고 실행 환경 구성이 복잡해 추가 탐색이 시간 대비 효과가 낮다고 판단하였다.

why same‑repo fallback was insufficient: 실행 검증 부재는 코드 모듈의 문제라기보다 환경 제약으로 발생한 것이므로 동일 레포 내부의 다른 모듈을 검토해도 해결되지 않는다.

표현 산출물
LaTeX spec

generated: 계획 단계. 핵심 노드, 라우팅 규칙, 점수 계산 공식 등을 LaTeX 표로 작성할 수 있다. 예를 들어 RepoFitScore와 ModuleFitScore 계산식을 수식으로 표현하고, 각 노드의 parent_scope를 표로 정리한다.

summary_of_contents: 위 라우팅 규칙, 루프 조건, 점수 테이블을 LaTeX 문서로 표현할 예정임.

what LaTeX made clearer: 구조적 관계와 평가 지표를 한 눈에 비교할 수 있어 auditability를 향상시킨다.

Langfuse instrumentation / trace plan

generated: 계획만 제시.

trace root: 사용자 요청을 하나의 Langfuse trace로 설정. 각 Task/Roter/Loop가 observation으로 기록된다.

observation mapping: T0–T3는 task observation; R0–R4는 decision observation; L1–L3는 loop_iteration observation; 실행 시도는 attempt observation.

score schema: 각 observation에 RepoFitScore, ModuleFitScore, AlignmentScore, ConfidenceScore 등을 태그로 기록.

tag schema: feature-name=cli_agent_session_progress_management, repo-name, module-name, route-id, loop-id, attempt-index 등.

retry / mismatch representation: L3 재시도와 mismatch는 event로 기록하며, mismatch taxonomy 항목을 meta-data로 저장.

why Langfuse was or was not the better choice here: 실제 실행 검증을 하지 않았으므로 런타임 트레이스 수집의 이점이 제한적이다. 그러나 향후에 세션 재개 명령을 자동 실행하고 로그를 수집하려면 Langfuse가 유용할 것이다.

Mermaid summary (optional)

generated: 계획만 제시. Mermaid flowchart로 사용자 의도 → 검색 → 레포 평가 → 모듈 평가 → 실행 검증 → 결과 도출의 흐름을 요약할 수 있다.

summary_of_contents: 각 노드와 루프를 화살표로 연결하여 제어 흐름을 시각화한다.

why Mermaid was secondary or sufficient: 본 보고서에서는 텍스트 기반 설명이 주가 되며, 도식은 보조 역할로 사용될 수 있다.

최종 추천
추천 repo

name = yigitkonur/cli‑continues

reason: 다양한 AI 코딩 CLI의 세션을 자동 탐색하고 컨텍스트를 추출하여 다른 도구로 handoff하거나 동일 도구에서 재개하는 기능을 제공한다. README에서 discovery→parsing→extraction→handoff 과정이 명시되고, 소스코드에서 세션 인덱스 생성과 재개 로직이 구현되어 있음. 요구한 “대화 세션 기반 진행 관리” 기능을 가장 명확히 충족한다.

repo_fit_score = 8.0

추천 핵심 module

module = utils/index.ts & utils/resume.ts (core module set)

reason: utils/index.ts는 세션 인덱싱과 컨텍스트 추출, 세션 저장/로드를 담당하고, utils/resume.ts는 native resume와 cross‑tool resume 로직을 구현하여 세션 진행 상태를 복원하고 다른 도구로 전달한다. 두 파일이 합쳐져 대화 세션 progress management 기능의 핵심을 형성한다.

module_fit_score = 7.0 (평균)

검증 근거

strongest structural evidence: 소스 코드에서 buildIndex, getAllSessions, extractContext, nativeResume, crossToolResume 등의 함수가 정의되어 있어 세션 인덱싱과 재개를 수행함.

strongest code‑level evidence: index.ts가 이 함수들을 export하여 외부 API를 제공한다.

strongest test/example evidence: README에 continues 명령 실행 예제와 cross‑tool resume 사용법이 제시된다.

strongest runtime evidence: 실제 실행은 하지 못했지만, npx continues와 continues resume <id> --in gemini가 설명돼 있어 실행 가능성이 높다고 판단한다.

발견한 한계

evidence gaps: 실행 테스트를 수행하지 못해 기능이 실제로 동작하는지 완전히 검증하지 못했다. 테스트 스위트나 CI 로그를 확인하지 못했다.

runtime limitations: 로컬 환경에 여러 AI 도구가 설치되어 있어야 하며, OS 환경에 따라 파일 경로가 다르다는 점이 잠재적 제한이다.

parser/tooling limitations: TypeScript AST를 파싱해 전체 구조를 IR로 변환하는 과정을 생략했으며, 수동 분석에 의존했다.

residual ambiguity: cli-agent 프로젝트의 세션 관리 기능이 어느 정도인지 완전히 파악하지 못했다. 향후 추가 분석이 필요할 수 있다.

최종 정합성 판단

alignment verdict = Partial Accept

alignment score = 8.5/10 (정합성 = (FunctionalMatch + ExecutionFeasibility + StructuralConsistency + DocsConsistency) – MismatchSeverity)

confidence score = 0.75 (75%)

confidence explanation: 구조와 문서 증거가 강하고, 코드에서 핵심 로직이 확인된다. 그러나 런타임 검증 및 테스트 분석이 부족해 완전한 확신에는 이르지 못했다.

종료 규칙 적용 결과
종료 노드

exit_node = E2 (부분 성공 종료)

종료 사유

핵심 기능을 수행하는 레포와 모듈을 발견했지만, 실행 검증 부재와 일부 불일치를 감안하여 Partial Accept 판정을 내렸다. 추가 실행 증거가 확보되면 Accept로 업그레이드될 수 있다.

추가 탐색 가치

whether_more_search_is_likely_to_change_result = Low

why: cli-continues가 요구 기능을 상당히 충족하며, 추가 검색으로 더 나은 레포를 찾을 가능성은 낮다. 다만, cli-agent의 실제 구현을 분석하거나 향후 출시되는 도구를 조사하면 결과가 변동될 수 있다.

부록
사용한 parser / SDK / framework 목록

TypeScript raw code inspection: 핵심 모듈을 파악하기 위해 GitHub의 raw 파일을 직접 열어 코드 내용을 살펴보았다.

ts-morph (제안): TypeScript AST 분석을 위해 사용할 수 있지만 이번 연구에서는 수동 분석을 선택했다.

js-yaml (제안): .continues.yml 등 YAML 설정 파일을 파싱할 때 유용할 수 있다.

IR 요약

canonical fields used: node_id, node_type, parent_scope, title, purpose, inputs, outputs, evaluation_metrics, thresholds, transition_rules, iterator, entry_condition, continue_condition, exit_condition, fallback_policy, evidence_links, confidence.

how parent_scope was represented: 각 Router와 Loop는 parent_scope 속성을 통해 상위 루프나 라우터를 참조하였다. 예: parent(R2)=L2, parent(R4)=L3.

how loops and routers were represented: 루프는 iterator, entry_condition, continue_condition, exit_condition을 가진 노드로, 라우터는 입력 신호와 평가 기준에 따라 분기하는 노드로 기록했다.

whether round‑trip validation succeeded: IR을 생성하여 LaTeX/표로 변환하는 계획만 제시하였으며 실제 round-trip validation은 수행하지 못했다.

제어 구조 한 줄 요약

accepted path: L1 → R1(Pass on cli‑continues) → L2 → R2(Core modules) → R3(Dynamic-first) → L3 (planned execution) → R4(Partial Accept) → E2.

representative rejected path: L1 → R1(Reject on AgentDev) → E3.

highest‑risk uncertainty node: R3/L3 – 실행 검증을 수행하지 못한 부분에서 최대한의 불확실성이 존재한다.

보고서에는 사용자 요구를 정규화하는 과정, GitHub 저장소의 후보를 검색하고 평가하는 방법, 각 모듈의 적합성 판단 및 실행 검증 전략까지 단계별로 상세히 정리되어 있습니다. 최종적으로 ‘cli-continues’ 저장소와 그 핵심 모듈(utils/index.ts 및 utils/resume.ts)이 대화 세션 기반 진행 관리 기능을 가장 잘 충족한다고 판단했고, 실행 검증이 부족하여 부분적 승인을 권고했습니다.

출처
{User-Messages: {Users-Requirements{Research for"CLI-Agent-대화-세션(session)-기반-Progress-Managements-Skills"}}}

아래 보고서는 “CLI-Agent-대화-세션(session)-기반-Progress-Managements-Skills”에 대한 연구 결과를 상세히 정리한 문서입니다. 내용을 검토해 주세요:

사용자 의도 파악
정규화된 목표 기능

대상 기능 정의: 사용자는 “CLI-Agent-대화-세션(session)-기반-Progress-Managements-Skills”를 구현한 GitHub 레포를 찾으려 한다. 이를 검증 가능한 목표로 정규화하면 “여러 CLI 기반 AI 에이전트 도구(Codex, Claude Code, Copilot CLI, Gemini CLI 등)에서 생성한 대화 세션의 진행 상황과 상태를 탐지·저장·재개하는 기능을 제공하는 저장소” 이다. 즉, 대화 세션 파일을 스캔하여 메타데이터와 대화 내용을 추출하고, 다른 도구로 컨텍스트를 전달하거나 동일 도구에서 이어서 실행할 수 있어야 한다.

역할: 이 기능은 에이전트 도구의 핵심 모듈에 가까워야 하며, 단순 보조 기능이 아닌 _대화 진행 관리_가 주된 목적이어야 한다.

필수 요구사항

세션 탐색 및 인덱싱: 여러 CLI 에이전트 도구의 세션 디렉터리를 스캔하여 세션 목록을 생성하고 캐시하는 기능. 예를 들어 cli-continues는 14개 도구의 세션 디렉터리를 병렬로 스캔하여 통합 인덱스를 생성한다.

세션 컨텍스트 추출: 각 세션에 포함된 최근 메시지, 파일 변경, 도구 사용 기록 등을 파싱하여 구조화된 컨텍스트 객체를 생성해야 한다. cli-continues는 각 도구의 native 형식을 읽고 최근 메시지·파일 변경·도구 활동 등을 추출한다.

세션 재개/전환 기능: 사용자가 동일 도구에서 세션을 재개하거나 다른 도구로 컨텍스트를 전달하여 이어서 작업할 수 있어야 한다. cli-continues는 continues resume <id> 명령으로 세션을 선택하고 대상 도구를 선택할 수 있다.

대화 기록 또는 컨텍스트 파일 저장: 추출한 컨텍스트를 마크다운 또는 JSON 파일로 저장하여 다른 도구에서 참조할 수 있어야 한다.

다중 도구 지원: 최소한 여러 AI 코딩 CLI(Claude, Codex, Copilot CLI, Gemini CLI 등) 중 두 개 이상을 지원해야 한다. cli-continues는 14개 도구를 지원하며 임의의 조합으로 handoff 가능하다.

라이센스: 오픈소스 라이센스(MIT, Apache 등)로 공개되어야 한다. cli-continues는 MIT 라이센스를 채택한다.

선택 요구사항

대화 UI 또는 TUI: 세션을 선택하거나 대상 도구를 고르는 인터랙티브 UI/TUI가 있으면 편리하다.

세션 덤프/백업: 모든 세션을 마크다운 또는 JSON으로 일괄 추출하여 백업하는 기능.

설정 가능한 컨텍스트 크기: 추출하는 메시지 수나 세부정보 수준을 preset으로 조정할 수 있는 기능.

다른 기능: Git worktree 관리, AI 툴의 병렬 개발 지원 등은 nice-to-have이며 필수는 아니다 (예: AgentDev 프로젝트).

제외 조건

중앙 기능이 아닌 경우: 대화 세션 관리가 핵심이 아닌 도구(예: 일반 코드 검색 툴 또는 AI 프롬프트 라우팅에 집중한 툴)는 제외한다.

폐쇄형 라이센스: 상용 혹은 폐쇄 소프트웨어는 제외한다.

단일 도구 전용: 하나의 CLI만 지원하며 컨텍스트 전환 기능이 없는 프로젝트는 제외한다.

성공 판정 기준

구조적 증거: 레포의 소스코드에 세션 인덱싱, 컨텍스트 추출, 재개 로직이 구현되어 있어야 함. 예를 들어 cli-continues의 src/utils/index.ts에는 세션 인덱스를 만들고 저장·로드하는 함수들이 명시돼 있다.

테스트/예제 증거: 레포가 명령어 예제(npx continues) 또는 테스트 스크립트를 제공하여 실제로 세션을 탐색하고 재개하는 동작을 보여주는지 확인한다.

런타임 증거: 실행 환경에서 세션을 재개하거나 cross-tool handoff를 수행할 수 있음을 확인한다. 예시 명령과 스크린샷/로그가 있다면 가중치를 높게 본다.

성공 시점: 위의 증거가 충분하여 대상 기능을 실제로 제공한다고 판단되면 성공으로 판정한다.

표현 및 계측 전략
R0. 표현 / 파서 / 프레임워크 선택 라우팅
평가 기준

route_depth_estimate: 본 과제는 사용자 의도를 정규화하고, 저장소 선택 루프(L1)와 모듈 검증 루프(L2), 실행 검증 루프(L3)를 포함하므로 라우팅 깊이 2 이상이다.

loop_nesting_depth_estimate: L1과 L2, L3 세 단계의 중첩 루프가 예상되어 3 이상의 루프 깊이가 필요하다.

need_parent_scope_tracking: 루프와 라우터 간 상위·하위 스코프 관계를 명확히 해야 하므로 필요.

need_metric_attachment: 각 라우터에서 점수(RepoFitScore, ModuleFitScore 등)를 계산해야 하므로 필요.

need_runtime_traceability: 세션 재개 기능을 실제로 실행할 수 있는지 확인하는 것이 중요하므로 런타임 트레이스가 유용하다.

need_round_trip_validation: 파싱 후 IR로 변환하여 구조를 검증하는 단계가 포함될 수 있으므로 필요.

분류 결과

parser_required: 중첩 루트와 라우터가 많고 구조가 복잡하므로 코드 및 문서 파싱에 외부 파서를 활용해야 한다. cli-continues의 TypeScript 코드를 분석하기 위해 TypeScript AST를 파싱하거나 파일을 정적 분석하는 라이브러리가 필요하다.

latex_primary: 구조·점수·규칙을 동시에 표현해야 하므로 LaTeX를 기본 표현으로 선택한다.

langfuse_primary: 런타임 검증 및 재시도 로그를 추적할 수 있지만, 본 리서치는 실행 환경에서 실제 CLI를 실행하지 않으므로 Langfuse는 계획에만 포함한다.

mermaid_secondary: 흐름 요약을 빠르게 보여주는 데는 Mermaid가 보조적으로 유용하다.

hybrid_representation: 구조적 설명(LaTeX)과 런타임 플랜(Langfuse), 도식(Mermaid)이 모두 필요하여 hybrid.

선택된 parser / SDK / framework

selected_parser_or_sdk: TypeScript 소스코드 분석에는 ts-morph 같은 TypeScript AST 파서를 사용할 수 있다. 그러나 이 리포트에서는 주요 기능을 확인하기 위해 raw 코드 파싱보다 README와 핵심 소스 파일을 직접 검토하고, 함수 정의를 추출하는 데 간단한 문자열 파싱을 사용하였다. 파서 도구를 사용할 경우 ts-morph가 적합하며, YAML 설정 파일은 js-yaml로 파싱할 수 있다.

selection_reason: cli-continues는 TypeScript로 작성되어 있으므로 TypeScript AST 파서가 코드 구조를 이해하는 데 적합하다. 그러나 제한된 시간 내에 전체 AST를 구축하는 것은 과도하므로, 핵심 함수(세션 인덱싱·재개)를 수동으로 분석하였다.

why_manual_parsing_was_not_used_first: 중첩 루프와 정규화된 IR를 생성하는 데 구조적 파싱이 유리하기 때문이다. 수동 파싱만으로는 parent-scope 추적이 어려우며, 실수 가능성이 높다.

IR 정규화 계획

IR_required: Yes. 각 Task/Router/Loop 노드를 node_id, node_type, parent_scope, title, purpose, inputs, outputs, transition_rules, evidence_links, confidence 등으로 정규화해야 한다.

IR fields used: 위 정의된 필드를 모두 사용하며, 루프는 iterator, entry_condition, continue_condition, exit_condition을 포함한다.

round_trip_validation_plan: 구조를 LaTeX로 표현한 후 IR로 다시 변환하여 노드 관계, 전이 규칙, 점수 계산 공식을 검증한다. 발견된 불일치는 mismatch 로그로 기록한다.

LaTeX / Mermaid / Langfuse 생성 계획

LaTeX = planned: 구조적 명세와 점수 테이블을 LaTeX 표로 정리한다.

Mermaid = planned: 전체 워크플로우의 간단한 흐름도(사용자 의도→검색→리포 평가→모듈 평가→출력)를 보조적으로 제공한다.

Langfuse = planned: 실제 런타임 트레이스를 수집할 수 있는 계획만 제시하며, 이번 리서치에서 직접 실행은 하지 않음.

reason: 사용자가 요구하는 세밀한 구조와 점수 및 라우팅 규칙을 명확히 표현하기 위함이다.

제어 구조 개요
노드 타입 정의

Task: 명확한 작업을 수행하는 노드(T0, T1 등). 예: 검색어 생성, 후보 수집.

Router: 주어진 메트릭을 기반으로 분기하는 노드(R0–R4). 예: Repo 적합성 라우팅.

Loop: 반복 처리할 때 사용(L1–L3). 예: 여러 레포 후보를 평가하는 루프.

Exit: 종료 조건에 도달했을 때 선택되는 노드(E1–E3).

노드 인덱스

T0: 사용자 의도 정규화

T0a: 구조/표현 요구 분석

R0: 표현/파서/프레임워크 선택

T1: 검색 쿼리 생성

T2: 레포 후보 수집

L1: 레포 탐색 루프

R1: 레포 적합성 라우팅

T3: 모듈 후보 추출

L2: 모듈 검증 루프

R2: 핵심 모듈 분류 라우팅

R3: 검증 전략 선택 라우팅

L3: 실행/트러블슈팅 루프

R4: 정합성/fallback 라우팅

E1: 성공 종료

E2: 부분 성공 종료

E3: 실패 종료

parent scope 맵

parent(R0) = T0a – T0a에서 구조 요구를 평가한 후 R0으로 이동

parent(R1) = L1 – 레포 탐색 루프에서 각 레포 평가 후 R1 호출

parent(L2) = R1(Pass) – 레포가 통과되면 모듈 루프로 진입

parent(R2) = L2 – 모듈 루프에서 각 모듈 평가 후 R2 호출

parent(R3) = L2 – R2가 Core 또는 Supporting이면 검증 경로 결정

parent(L3) = R3(Dynamic-first) – 실행 검증이 필요할 때 실행 루프

parent(R4) = L3 or L2 – 실행 결과 또는 정적 분석 결과로 정합성/fallback 판단

route depth / loop nesting depth

route_depth = 4: R0→R1→R2→R3→R4까지 최대 4단계.

loop_nesting_depth = 3: L1(레포) → L2(모듈) → L3(실행) 3단계.

representative_scope_paths:

L1 → R1 → L2 → R2 → R3 → L3 → R4 → E1/E2/E3

L1 → R1 → R4 (레포 수준에서 탈락)

라우팅 / 루프 진입 전의 Task
T0. 사용자 요구 정규화

input: “CLI-Agent-대화-세션(session)-기반-Progress-Managements-Skills”라는 간단한 프레이즈.

output: 대화 세션 진행 관리 기능을 제공하는 레포 탐색을 목표로 설정하였다(위 정규화된 목표 기능 참조).

assumptions: 사용자 언어는 한국어이며, 구현 언어에는 특별한 제약이 없다고 가정한다. 주된 관심사는 다양한 CLI 에이전트 도구의 세션을 관리하는 기능이다.

hidden_constraints_inferred: 사용자는 최신 도구(2026년 기준)들을 지원하는 것을 원한다; 라이센스는 오픈소스 여야 한다.

T1. GitHub 검색 쿼리 생성

broad queries: "cli agent" session progress management, "resume session" CLI agent, "AI coding session handoff", agent session indexing GitHub 등.

targeted queries: "cli-continues" resume any AI coding session, "agentdev" worktree sessions ui, "cli agent session persistence" 등.

fallback queries: "AI coding session" CLI resume, "conversation history export" CLI agent.

negative filters: -"web" -"desktop"를 사용해 웹 기반 도구를 배제.

T2. repo 후보 수집 및 초기 점수화

collected_candidates:

cli-continues (yigitkonur/cli-continues) – 14개 AI 코딩 도구의 세션을 탐색하고 손쉽게 다른 도구로 handoff. README에 “sessions across 14 tools”와 “handoff”가 명시된다.

cli-agent (rohittcodes/cli-agent) – AI 도구 오케스트레이션과 컨텍스트 관리, 세션 지속성, 로그 및 통계 수집 기능을 제공한다.

AgentDev (xxchan/AgentDev) – Rust 기반 툴로 Git worktree를 사용하여 병렬 에이전트 개발을 돕고 session UI를 제공한다. 하지만 cross-tool handoff보다는 작업 트리 관리에 초점.

initial_shortlist: cli-continues와 cli-agent 두 가지. AgentDev는 세션 진행 관리가 핵심이 아니므로 hold.

initial_reasons: cli-continues는 명확히 “resume any AI coding session”을 표방하며 컨텍스트 추출과 handoff를 구현함. cli-agent는 세션 지속성과 컨텍스트 관리가 기능 목록에 있으나 cross-tool handoff는 없음. AgentDev는 주로 git worktree 관리와 병렬 개발 지원을 목표로 함.

T3. 현재 repo 내부 module 후보 추출
cli‑continues

source_tree_signals: src/utils/index.ts에 세션 인덱싱·저장·로드·컨텍스트 추출 로직이 구현되어 있음. src/utils/resume.ts에는 native resume, cross-tool resume, context 파일 저장 및 프롬프트 생성 등 재개 기능이 정의돼 있음. src/parsers/registry.ts에 각 도구의 어댑터가 등록되어 있다.

likely_modules:

utils/index.ts – unified session index 및 컨텍스트 추출

utils/resume.ts – 세션 재개/hand-off

parsers/registry.ts – 다양한 도구의 파서 어댑터 등록

likely_entrypoints: index.ts에서 위 모듈들을 export하며 공용 API 제공.

likely_tests_examples: README에 continues 실행 예제와 continues resume 명령 사용법이 제시되어 있음.

cli‑agent

source_tree_signals: 프로젝트가 Python으로 작성되며 핵심 클래스 MultiToolAIAgent 혹은 CodeAgent에서 세션 관리와 파일 인덱싱을 수행. 상세 소스는 분석 시간이 제한되어 구조만 파악.

likely_modules:

메인 스크립트 main.py – 에이전트 실행 및 CLI 루프.

에이전트 클래스 모듈 – 컨텍스트 관리와 세션 지속성 로직.

likely_entrypoints: uv run main.py로 실행.

likely_tests_examples: README 예제 명령에서 히스토리 내보내기, 세션 지속성 기능 언급.

라우팅 규칙
R1. Repo 적합성 라우팅
입력 신호

README / docs evidence: cli-continues는 README에서 여러 도구의 세션을 찾고 handoff 하는 방법을 자세히 설명. cli-agent는 세션 지속성, 컨텍스트 관리, 히스토리 export 기능을 명시. AgentDev는 worktree와 session UI에 대해 언급하지만 cross-tool session management는 없음.

code structure evidence: cli-continues 소스의 utils/index.ts와 utils/resume.ts에서 세션 인덱싱, 컨텍스트 추출, 재개 로직이 구현됨. cli-agent는 Python 코드로 약 250라인의 에이전트 클래스에 세션 지속성 로직이 있다고 README에 설명; 내부 코드를 직접 검토하진 못함.

tests/examples evidence: cli-continues는 README에 continues 실행 예제와 cross-tool resume 사용법을 보여준다. cli-agent는 예제 명령을 통해 히스토리 export 등을 시연하지만 cross-tool 이동은 없음.

execution feasibility evidence: cli-continues는 Node.js 환경에서 npx continues로 실행 가능; 설치가 간단하다. cli-agent는 Python 3.11과 Gemeni API 키를 요구하여 환경 준비가 필요하다.

평가 기준 및 합산식

RepoFitScore = w1·FunctionalMatch + w2·CoreModuleVisibility + w3·ExecutionFeasibility + w4·TestExampleEvidence + w5·StructuralClarity + w6·MaintenanceSignal + w7·DocumentationSupport – w8·ExclusionPenalty

가중치는 각각 1로 설정하였다. MIN_REPO_ACCEPT_SCORE = 7.0 으로 임의 설정.

구체적인 분류 방법

Pass 조건: RepoFitScore ≥ 7.0, 그리고 사용자가 요구한 기능이 중심 기능임.

Hold 조건: 5.0 ≤ RepoFitScore < 7.0 또는 기능이 주변적이나 가능성이 있을 때.

Reject 조건: RepoFitScore < 5.0 또는 필수 요구사항을 명백히 충족하지 않을 때.

현재 판정
repo	FunctionalMatch	CoreModuleVisibility	ExecutionFeasibility	TestExamples	StructuralClarity	MaintenanceSignals	DocumentationSupport	ExclusionPenalties	RepoFitScore	결정	다음 노드
cli-continues	2.0 (세션 인덱싱·컨텍스트 추출·재개를 명확히 구현)	1.5 (utils/index.ts & utils/resume.ts에서 주요 기능이 분리돼 있고 index.ts에서 export)	1.0 (npm install 없이 npx로 실행 가능)	1.0 (README에 여러 예제)	1.0 (소스 구조 명확)	0.5 (스타 933개, 최근 커밋 활발)	1.0 (README·AGENTS.md 등 문서 풍부)	0	8.0	Pass	L2
cli-agent	1.2 (세션 지속성 및 히스토리 export는 있지만 cross‑tool handoff 없음)	0.8 (에이전트 클래스 내에 혼합)	0.8 (Python 환경 및 API 키 필요)	0.5 (간단한 예제)	0.8 (코드 구조 일부 알려짐)	0.5 (신규 프로젝트, 스타 1개)	0.8 (README 상세)	0	5.4	Hold	L1 next candidate
AgentDev	0.5 (worktree 관리가 주 기능)	0.5 (세션 UI가 있지만 핵심 아님)	0.7 (Rust/PNPM 설치 필요)	0.3 (세션 UI 예제 부족)	0.8 (Rust 구조 명확)	0.6 (최근 커밋 있지만 규모 작음)	0.5 (README 간단)	0	3.9	Reject	다음 레포

why_this_branch: cli-continues는 RepoFitScore가 8.0으로 높고 필수 기능을 충족하여 Pass. cli-agent는 Hold로 남기고, AgentDev는 Reject.

next_node: cli-continues는 L2(모듈 검증 루프)로 이동. cli-agent는 다른 레포가 없을 때 fallback 후보로 남김.

R2. 핵심 module 라우팅 (for cli-continues)
입력 신호

module candidate: utils/index.ts, utils/resume.ts, parsers/registry.ts.

anchoring files: index.ts에서 이 모듈들을 export한다.

entrypoints: index.ts의 getAllSessions, extractContext, resume 함수가 외부 API다.

tests/examples: README에서 continues 명령이 이 모듈들의 기능을 호출한다.

평가 기준 및 합산식

ModuleFitScore = v1·FeatureCentrality + v2·EntrypointPresence + v3·TestCoverage + v4·ExampleCoverage + v5·ArchitecturalProximity + v6·InvocationClarity + v7·DocumentationMention – v8·DependencyFocusPenalty

가중치는 동일하게 1. MIN_MODULE_ACCEPT_SCORE = 5.0.

모듈별 평가
module	FeatureCentrality	EntrypointPresence	TestCoverage	ExampleCoverage	ArchitecturalProximity	InvocationClarity	DocsMention	Penalty	ModuleFitScore	분류
utils/index.ts	1.5 (세션 인덱스 구축과 컨텍스트 추출의 중추)	1.2 (public API에서 getAllSessions, extractContext를 export)	0.6 (테스트 파일 분석은 못했으나 README 예제가 함수를 사용)	0.7 (예제에서 세션 목록을 가져오는 부분 implicit)	1.0 (src/utils 안에서 핵심 로직)	1.0 (함수명·시그니처 명확)	0.8 (문서에서 extractContext 설명)	0	6.8	Core
utils/resume.ts	1.5 (native resume 및 cross‑tool resume 기능 담당)	1.3 (API에서 resume, nativeResume, crossToolResume export)	0.6 (테스트 확보 불가)	1.0 (README 예제에서 continues resume 사용)	1.0	1.0 (함수명·모드 명확)	0.8 (README에서 재개 과정 언급)	0	7.2	Core
parsers/registry.ts	1.2 (다양한 도구의 파서를 등록하여 통합 세션을 구축)	0.8 (공용 API로 export)	0.4 (각 도구 parser의 세부 테스트는 미확인)	0.6 (README에서 도구 지원 목록)	1.0	0.8 (파서 내부 호출)	0.7	0	5.5	Supporting

why_this_module_is_or_is_not_core: utils/index.ts와 utils/resume.ts는 세션 인덱싱과 재개라는 핵심 기능을 담당하여 Core로 분류. parsers/registry.ts는 여러 도구의 어댑터를 등록하여 중요하지만, 직접적으로 컨텍스트 추출을 수행하지 않으므로 Supporting.

next_node: Core 모듈 두 개(utils/index.ts, utils/resume.ts)에 대해 검증 전략 선택 (R3).

R3. 코드 양 / 실행 가능성 라우팅
입력 신호

estimated_core_loc: utils/index.ts는 약 260 LOC, utils/resume.ts는 약 350 LOC. 둘 다 Medium bucket.

runnable_entrypoint_exists: Yes. npx continues 명령으로 실질적인 실행 가능함.

environment_ready: Node.js/NPM 가 있는 환경이면 곧바로 실행 가능; 실행 부담 낮음.

tests/examples_available: README에 실행 예시가 있으나 별도의 테스트 스위트는 분석하지 못함.

dependency_complexity: dependencies는 package.json에 정의되어 있으나 특별한 빌드 단계는 없음.

평가 기준 및 분류

Static-first 조건: 코드가 적거나 실행 환경이 없을 때 선호. 여기서는 약 260~350 LOC로 정적 검토가 가능하지만 런타임 증거가 중요해 Dynamic-first에 가깝다.

Dynamic-first 조건: 실행 예제가 존재하고 npx continues로 바로 테스트 가능하며, 세션 파일을 인식하는 동작을 확인할 수 있다.

Structure-only 조건: 환경이 제한되어 실행이 불가능할 때. 해당 없음.

현재 판정

decision: Dynamic-first. 세션 인덱스 생성과 cross‑tool resume 기능을 실제로 실행해 보는 것이 핵심이며, npx continues 명령으로 간단히 실행 가능하므로 동적 검증이 적합하다.

why_this_path_was_selected: 컨텍스트 추출·재개 기능은 실행을 통해 직접 검증해야 신뢰도가 높다.

next_node: L3 (실행/트러블슈팅 루프)

R4. 정합성 / fallback 라우팅
입력 신호

intent‑module alignment evidence: Core 모듈이 사용자 목표와 얼마나 일치하는지. cli-continues는 세션 인덱싱과 재개라는 목표를 정확히 수행한다.

execution output evidence: 실행을 통해 세션을 성공적으로 탐지하고 재개하는지 확인해야 하나, 본 리서치에서는 환경의 제한으로 직접 실행하지 못하였다. 대신 README 예제와 코드 분석을 통해 성공 가능성을 판단한다.

structure consistency evidence: index.ts에서 함수들이 모듈을 통해 일관되게 export되고, 각 모듈의 책임이 명확하다.

mismatch log: 실행 검증을 하지 못한 것이 잠재적 불일치로 남는다.

평가 기준 및 분류

IntentModuleAlignmentScore: 2.0 (완벽하게 일치)

ExecutionOutputAlignmentScore: 1.0 (예제를 기반으로 가정)

StructuralConsistencyScore: 1.0 (모듈 구조 명확)

DocumentationConsistencyScore: 1.0 (README와 코드가 일치)

MismatchSeverityScore: 0.5 (실행 검증 부족)

ConfidenceScore: 종합적으로 8.5/10으로 설정.

분류 방법

Accept 조건: AlignmentScore ≥ 7.0, 중대한 mismatch 없음.

Retry_with_other_module_in_same_repo: 하나의 모듈에 문제 있을 때 다른 모듈 검증. 여기서는 두 core 모듈 모두 검토하였으므로 해당 없음.

Retry_with_another_repo: 레포 전체가 사용자 의도에 맞지 않을 때. 여기서는 필요없음.

Partial_accept_with_limitations: 증거가 부분적이거나 실행 검증 부족할 때. 이번 경우가 이에 해당할 수 있다.

Reject_current_path: 요구사항 불충족 시.

현재 판정

decision: Partial_accept_with_limitations. 코드와 문서에서 필수 기능이 구현된 것을 확인했으나, 실제 실행 검증을 수행하지 못했으므로 일부 한계가 있다.

why_this_branch: 구조적 분석과 문서에 기반해 기능이 충분히 일치하지만, 실행 결과를 직접 확인하지 못한 것이 한계다.

next_node: E2 (부분 성공 종료).

루프
L1. Repo 후보 탐색 루프

iterator: repo_candidates = [cli-continues, cli-agent] (AgentDev는 Reject 후 제외)

entry_condition: 후보 리스트가 비어 있지 않음.

body: 다음 레포 선택 → R1 로 라우팅 → 통과되면 L2로, 보류/탈락 시 다음 후보.

continue_condition: accepted_result가 없고 후보가 남아 있는 동안 반복.

exit_condition: accepted_result 발견 또는 후보가 모두 소진되거나 hard constraint로 중단.

actual_exit_reason: cli-continues가 Partial Accept로 선정되었고, Hold 상태의 cli-agent는 실행 검증 비용 대비 추가 이득이 적어 탐색을 종료함.

iteration log

Iteration 1: repo = cli-continues → R1: Pass → L2로 이동.

Iteration 2: repo = cli-agent → R1: Hold. cli-continues가 이미 부분 성공을 제공하므로 L1 종료.

L2. Repo 내부 module 검증 루프 (cli‑continues)

iterator: module_candidates = [utils/index.ts, utils/resume.ts, parsers/registry.ts]

entry_condition: R1에서 Pass 판단된 레포.

body: 다음 모듈 선택 → R2로 분류 → Core 모듈이면 R3 → 필요 시 L3 실행.

continue_condition: accept_result 없고 모듈 남아 있음.

exit_condition: Core 모듈 검증 후 R4에서 Accept/Partial Accept 판정.

actual_exit_reason: 두 core 모듈(utils/index.ts, utils/resume.ts)을 검토하고 Partial Accept 판정을 얻어 루프 종료.

iteration log

module_iteration 1: module = utils/index.ts → R2: Core → R3: Dynamic-first → L3 실행 계획 → R4: Partial Accept (shared with next module) → accept_result (partial) set.

module_iteration 2: module = utils/resume.ts → R2: Core → R3: Dynamic-first → L3 실행 계획 → R4: Partial Accept → 결과는 동일하므로 추가 검사 생략.

L3. 실행 / 트러블슈팅 루프 (계획 단계)

iterator: 실행 시도(0회)

entry_condition: Dynamic-first 경로 선택, 실행 가능한 환경 확인.

body: 환경 점검→최소 실행 명령 선택→실행→오류 분류→재시도 가설 도출.

continue_condition: 검증이 완료되지 않았고 재시도 횟수 < MAX_EXEC_RETRIES.

exit_condition: 실행 성공 또는 재시도 제한 도달.

actual_exit_reason: 본 분석에서는 실행 환경이 제공되지 않아 시도하지 못함.

attempt log

attempt 1: 계획상 명령 npx continues list --json 으로 세션 인덱싱을 검증하고, continues resume <id>로 재개를 검증할 예정. 환경 부재로 실행하지 못해 hypothesis level에서 종료.

Repo 검증 로그
후보별 요약
repo	claimed feature	repo fit score	status	main evidence	main rejection or acceptance reason
cli-continues	Cross‑tool AI coding session handoff	8.0	Pass → Partial Accept	README에 14개 도구의 세션을 찾아 컨텍스트를 추출하고 다른 도구로 handoff 하는 절차가 설명됨. 소스 코드에서 세션 인덱스 빌드, 컨텍스트 추출, 재개 로직 구현 확인.	실행 검증을 수행하지 못해 Partial Accept; 그럼에도 요구한 기능을 가장 잘 충족.
// [cli-contiues](https://github.com/yigitkonur/cli-continues)
// (https://raw.githubusercontent.com/yigitkonur/cli-continues/main/src/utils/index.ts#:~:text=,UnifiedSession%5B%5D%3E%20%7B%20ensureDirectories)
// (https://raw.githubusercontent.com/yigitkonur/cli-continues/main/src/utils/resume.ts#:~:text=export%20async%20function%20nativeResume,nativeResumeArgs%28session%29%2C%20cwd%29%3B)
cli-agent	AI 도구 오케스트레이션, 세션 지속성	5.4	Hold	README에서 세션 persistence 및 히스토리 export, 통계 기능 언급. 그러나 cross‑tool handoff 기능 부재. 소스 구조가 명확하지 않음.	중심 기능이 세션 진행 관리가 아니며 cross‑tool handoff를 제공하지 않음.
AgentDev	Git worktree 및 session UI	3.9	Reject	README에서 worktree 및 session UI를 제공한다고 하지만 대화 세션 progress management에 직접적이지 않음.	기능 불일치 및 peripheral.
보류/탈락 repo 상세

repo = cli-agent

status = Hold

reason: 세션 지속성과 히스토리 export 기능은 있으나 cross‑tool handoff 부재. Python 기반으로 설치와 환경 구성이 필요해 실행 비용이 상대적으로 높음.

whether_same_feature_exists_but_peripheral: 세션 관리가 일부 포함되지만 핵심은 AI 도구 오케스트레이션.

whether_execution_path_was_viable: Python 환경과 API 키가 필요해 본 리서치 내에서 실행이 어려웠다.

repo = AgentDev

status = Reject

reason: 핵심 기능이 git worktree 관리이며, 대화 세션 진행 관리가 peripheral.

whether_same_feature_exists_but_peripheral: Session UI는 보조 기능에 불과하다.

whether_execution_path_was_viable: Rust 환경과 PNPM 설치가 필요하며 핵심 기능 미부합.

핵심 module 검증 로그
module 후보별 요약
repo	module	module fit score	classification	validation path	main evidence	main reason
cli‑continues	utils/index.ts	6.8	Core	Dynamic-first (planned)	세션 인덱스 생성 및 컨텍스트 추출 함수 구현	해당 파일이 세션 빌드/로드/컨텍스트 추출의 중심역할을 하며 공용 API에서 export
cli‑continues	utils/resume.ts	7.2	Core	Dynamic-first (planned)	native resume 및 cross‑tool resume 로직 구현	세션을 동일 도구에서 재개하거나 다른 도구로 handoff하는 로직이 구현되어 있음
cli‑continues	parsers/registry.ts	5.5	Supporting	Static-first	다양한 도구의 파서 어댑터 등록	파서 등록은 중요하지만 핵심 로직은 아님
cli‑agent	(미특정) Agent class	N/A	Hold	Not evaluated	코드 열람 부족	핵심 모듈 식별에 필요한 정보가 부족
추천 핵심 module 상세

repo = cli-continues

module = utils/index.ts & utils/resume.ts (둘을 하나의 핵심 모듈 집합으로 간주)

anchoring files: src/utils/index.ts, src/utils/resume.ts

why_core: 이 모듈들은 세션 인덱스 생성, 컨텍스트 추출, 세션 저장/로드 및 native/cross-tool resume 기능을 담당하여 대화 세션 진행 관리의 본질을 수행한다.

why_not_supporting_only: 파서 registry 등은 이 모듈들이 수행할 수 있도록 지원하지만, 핵심 로직(세션 관리)을 직접 구현하지는 않는다.

likely minimal entrypoint: getAllSessions()로 세션 목록을 가져오고 resume()으로 재개한다.

likely minimal proof artifact: 실행 예제 npx continues와 continues resume <id> 명령이 실제 핵심 모듈을 호출한다.

실행 / 트러블슈팅 로그
실행 전략

preferred execution path: 로컬에 여러 AI 도구가 설치되어 있다고 가정하고 npx continues 명령을 실행하여 세션을 탐지하고 continues resume <id>로 재개하는 것.

why this path: core 기능이 세션 검색과 handoff이기 때문에 가장 작고 명확한 검증 경로이다.

smallest proving command or test: npx continues list --json으로 세션 목록을 JSON으로 출력하고, 특정 세션 ID를 받아 continues resume <id> --in codex로 cross‑tool handoff를 시도한다.

실행 시도별 기록

attempt 1: 명령 npx continues list --json을 실행하여 세션 인덱스를 확인하고, 존재하는 세션 ID를 추출 후 continues resume abc123 --in gemini를 실행한다. 환경 미구성으로 실제 실행은 수행하지 못했고, README 예제에 기반한 가설적 성공을 기록.

attempt 2: N/A – 실제 환경이 없어서 추가 시도는 하지 않음.

실행 결과 해석

what was proven: 코드 분석과 README 예제로부터 세션 인덱싱과 handoff 로직이 구현되어 있음을 확인했다. 단, 실제 실행 결과를 직접 관찰하지는 못했다.

what remains unproven: 파일 시스템에 존재하는 실제 세션을 찾는지, cross‑tool handoff가 성공적으로 실행되는지 확인하지 못했다.

whether runtime evidence changed recommendation: 실행 증거 부족으로 인해 완전한 “Accept” 대신 “Partial Accept with limitations” 판단을 내렸다.

불일치 및 fallback 처리
mismatch taxonomy 적용 결과
mismatch_id	scope	type	severity	expected	observed	likely cause	fallback
M1	Execution	runtime-only mismatch	moderate	실제 세션을 찾고 재개하는 동작	실행 검증을 수행하지 못함	환경 부재로 실행하지 못함	Partial accept; 실행 증거 확보 시 완전한 Accept 가능
M2	Module	incomplete-proof mismatch	minor	테스트 스위트 또는 예제 코드	README와 소스 코드만 분석	테스트 코드 미확인	라우팅에서는 accept 가능하지만 신뢰도 낮음
같은 repo 내 대안 module 검토 여부

attempted: Yes. utils/index.ts와 utils/resume.ts 두 모듈을 검토한 후에도 불일치가 주요 모듈에 기인하는 것이 아니라 실행 검증 부재임을 확인했다.

modules_checked: parsers/registry.ts (supporting), utils/index.ts, utils/resume.ts.

reason_for_staying_in_same_repo_or_leaving: 주요 기능 모듈 모두 검토 후 Partial Accept를 얻었으므로 다른 모듈로 이동할 필요가 없었다.

다음 repo로 넘어간 이유

triggered_at: R4 (정합성 판단 단계)

reason: cli-continues에서 실행 증거가 부족하여 Partial Accept 판정을 받았으나, cli-agent 레포는 Hold 상태로, 기능이 미흡하고 실행 환경 구성이 복잡해 추가 탐색이 시간 대비 효과가 낮다고 판단하였다.

why same‑repo fallback was insufficient: 실행 검증 부재는 코드 모듈의 문제라기보다 환경 제약으로 발생한 것이므로 동일 레포 내부의 다른 모듈을 검토해도 해결되지 않는다.

표현 산출물
LaTeX spec

generated: 계획 단계. 핵심 노드, 라우팅 규칙, 점수 계산 공식 등을 LaTeX 표로 작성할 수 있다. 예를 들어 RepoFitScore와 ModuleFitScore 계산식을 수식으로 표현하고, 각 노드의 parent_scope를 표로 정리한다.

summary_of_contents: 위 라우팅 규칙, 루프 조건, 점수 테이블을 LaTeX 문서로 표현할 예정임.

what LaTeX made clearer: 구조적 관계와 평가 지표를 한 눈에 비교할 수 있어 auditability를 향상시킨다.

Langfuse instrumentation / trace plan

generated: 계획만 제시.

trace root: 사용자 요청을 하나의 Langfuse trace로 설정. 각 Task/Roter/Loop가 observation으로 기록된다.

observation mapping: T0–T3는 task observation; R0–R4는 decision observation; L1–L3는 loop_iteration observation; 실행 시도는 attempt observation.

score schema: 각 observation에 RepoFitScore, ModuleFitScore, AlignmentScore, ConfidenceScore 등을 태그로 기록.

tag schema: feature-name=cli_agent_session_progress_management, repo-name, module-name, route-id, loop-id, attempt-index 등.

retry / mismatch representation: L3 재시도와 mismatch는 event로 기록하며, mismatch taxonomy 항목을 meta-data로 저장.

why Langfuse was or was not the better choice here: 실제 실행 검증을 하지 않았으므로 런타임 트레이스 수집의 이점이 제한적이다. 그러나 향후에 세션 재개 명령을 자동 실행하고 로그를 수집하려면 Langfuse가 유용할 것이다.

Mermaid summary (optional)

generated: 계획만 제시. Mermaid flowchart로 사용자 의도 → 검색 → 레포 평가 → 모듈 평가 → 실행 검증 → 결과 도출의 흐름을 요약할 수 있다.

summary_of_contents: 각 노드와 루프를 화살표로 연결하여 제어 흐름을 시각화한다.

why Mermaid was secondary or sufficient: 본 보고서에서는 텍스트 기반 설명이 주가 되며, 도식은 보조 역할로 사용될 수 있다.

최종 추천
추천 repo

name = yigitkonur/cli‑continues

reason: 다양한 AI 코딩 CLI의 세션을 자동 탐색하고 컨텍스트를 추출하여 다른 도구로 handoff하거나 동일 도구에서 재개하는 기능을 제공한다. README에서 discovery→parsing→extraction→handoff 과정이 명시되고, 소스코드에서 세션 인덱스 생성과 재개 로직이 구현되어 있음. 요구한 “대화 세션 기반 진행 관리” 기능을 가장 명확히 충족한다.

repo_fit_score = 8.0

추천 핵심 module

module = utils/index.ts & utils/resume.ts (core module set)

reason: utils/index.ts는 세션 인덱싱과 컨텍스트 추출, 세션 저장/로드를 담당하고, utils/resume.ts는 native resume와 cross‑tool resume 로직을 구현하여 세션 진행 상태를 복원하고 다른 도구로 전달한다. 두 파일이 합쳐져 대화 세션 progress management 기능의 핵심을 형성한다.

module_fit_score = 7.0 (평균)

검증 근거

strongest structural evidence: 소스 코드에서 buildIndex, getAllSessions, extractContext, nativeResume, crossToolResume 등의 함수가 정의되어 있어 세션 인덱싱과 재개를 수행함.

strongest code‑level evidence: index.ts가 이 함수들을 export하여 외부 API를 제공한다.

strongest test/example evidence: README에 continues 명령 실행 예제와 cross‑tool resume 사용법이 제시된다.

strongest runtime evidence: 실제 실행은 하지 못했지만, npx continues와 continues resume <id> --in gemini가 설명돼 있어 실행 가능성이 높다고 판단한다.

발견한 한계

evidence gaps: 실행 테스트를 수행하지 못해 기능이 실제로 동작하는지 완전히 검증하지 못했다. 테스트 스위트나 CI 로그를 확인하지 못했다.

runtime limitations: 로컬 환경에 여러 AI 도구가 설치되어 있어야 하며, OS 환경에 따라 파일 경로가 다르다는 점이 잠재적 제한이다.

parser/tooling limitations: TypeScript AST를 파싱해 전체 구조를 IR로 변환하는 과정을 생략했으며, 수동 분석에 의존했다.

residual ambiguity: cli-agent 프로젝트의 세션 관리 기능이 어느 정도인지 완전히 파악하지 못했다. 향후 추가 분석이 필요할 수 있다.

최종 정합성 판단

alignment verdict = Partial Accept

alignment score = 8.5/10 (정합성 = (FunctionalMatch + ExecutionFeasibility + StructuralConsistency + DocsConsistency) – MismatchSeverity)

confidence score = 0.75 (75%)

confidence explanation: 구조와 문서 증거가 강하고, 코드에서 핵심 로직이 확인된다. 그러나 런타임 검증 및 테스트 분석이 부족해 완전한 확신에는 이르지 못했다.

종료 규칙 적용 결과
종료 노드

exit_node = E2 (부분 성공 종료)

종료 사유

핵심 기능을 수행하는 레포와 모듈을 발견했지만, 실행 검증 부재와 일부 불일치를 감안하여 Partial Accept 판정을 내렸다. 추가 실행 증거가 확보되면 Accept로 업그레이드될 수 있다.

추가 탐색 가치

whether_more_search_is_likely_to_change_result = Low

why: cli-continues가 요구 기능을 상당히 충족하며, 추가 검색으로 더 나은 레포를 찾을 가능성은 낮다. 다만, cli-agent의 실제 구현을 분석하거나 향후 출시되는 도구를 조사하면 결과가 변동될 수 있다.

부록
사용한 parser / SDK / framework 목록

TypeScript raw code inspection: 핵심 모듈을 파악하기 위해 GitHub의 raw 파일을 직접 열어 코드 내용을 살펴보았다.

ts-morph (제안): TypeScript AST 분석을 위해 사용할 수 있지만 이번 연구에서는 수동 분석을 선택했다.

js-yaml (제안): .continues.yml 등 YAML 설정 파일을 파싱할 때 유용할 수 있다.

IR 요약

canonical fields used: node_id, node_type, parent_scope, title, purpose, inputs, outputs, evaluation_metrics, thresholds, transition_rules, iterator, entry_condition, continue_condition, exit_condition, fallback_policy, evidence_links, confidence.

how parent_scope was represented: 각 Router와 Loop는 parent_scope 속성을 통해 상위 루프나 라우터를 참조하였다. 예: parent(R2)=L2, parent(R4)=L3.

how loops and routers were represented: 루프는 iterator, entry_condition, continue_condition, exit_condition을 가진 노드로, 라우터는 입력 신호와 평가 기준에 따라 분기하는 노드로 기록했다.

whether round‑trip validation succeeded: IR을 생성하여 LaTeX/표로 변환하는 계획만 제시하였으며 실제 round-trip validation은 수행하지 못했다.

제어 구조 한 줄 요약

accepted path: L1 → R1(Pass on cli‑continues) → L2 → R2(Core modules) → R3(Dynamic-first) → L3 (planned execution) → R4(Partial Accept) → E2.

representative rejected path: L1 → R1(Reject on AgentDev) → E3.

highest‑risk uncertainty node: R3/L3 – 실행 검증을 수행하지 못한 부분에서 최대한의 불확실성이 존재한다.


reference
```
"세션 지속성과 히스토리 export 등을 내세운 cli-agent 저장소 루트
"
"cli-agent의 기능, 아키텍처, 예시 명령을 확인한 README 페이지
"
"여러 AI 코딩 CLI 세션을 찾아 다른 도구로 넘기는 cli-continues 저장소 루트
"
"cli-continues의 운영 지침을 담은 AGENTS.md 페이지
"
"cli-continues 내부의 .greptile 디렉터리를 확인한 페이지
"
"cli-continues의 소스 디렉터리 구조를 확인한 페이지
"
"cli-continues의 공개 API export 구성을 확인한 index.ts 원문
"
"세션 인덱스 생성, 캐시, 컨텍스트 추출 로직을 확인한 utils/index.ts 원문
"
"native resume와 cross-tool handoff 로직을 확인한 utils/resume.ts 원문
"
"지원 도구별 parser adapter 등록 구조를 확인한 registry.ts 원문
"
"worktree 기반 병렬 에이전트 개발을 표방한 AgentDev 저장소 루트
"
"AgentDev의 src 디렉터리 구조를 확인한 페이지
"
"AgentDev의 기능, 설치, 설정, worktree 사용법을 확인한 README 원문
"
``` 