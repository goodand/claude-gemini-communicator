# 사용자 의도 파악

* 목표 기능: `git worktree`로 병렬 에이전트를 돌릴 때, `main` 쪽에서 무엇을 하고 `sub/worktree` 쪽에서 무엇을 하는지 AI에 명시하고, 역할별 skill 분리와 bridge/routing까지 갖춘 오픈소스 repo를 찾는 것.
* 필수 요구사항: `F1_worktree_parallel=1`, `F2_main_vs_sub_role_split=1`, `F3_skill_or_profile_layer=1`, `F4_bridge_or_handoff=1`, `F5_repo_level_and_module_level_evidence=1`.
* 선택 요구사항: `O1_retry_or_review_loop=1`, `O2_main_dir_guardrail=1`, `O3_tests_or_examples=1`, `O4_runtime_entrypoint=1`.
* 제외 조건: `X1_issue_or_blog_only=1`, `X2_worktree_only_without_role_skill=1`, `X3_multi_agent_claim_but_coordination_gap_high=1`.
* 성공 판정 기준: `S1_repo_pass=1 && S2_core_module_set_accept=1 && S3_same_repo_alt_checked_before_repo_switch=1`.

# 라우팅 / 루프 진입 전의 Task

* 사용자 요구를 검색 가능한 키워드와 검증 가능한 기능 단위로 정규화
  `K = {git worktree, parallel agents, role skill, main branch, subagent, bridge, orchestrator, retry, review loop}`
  `U = {U1_worktree_isolation, U2_main/sub role split, U3_skill bridge, U4_router, U5_execution loop}`

* GitHub 검색 쿼리 생성
  `Q1 = "GitHub repository git worktree parallel agents Main Coder Sub Coder skills bridge routing"`
  `Q2 = "site:github.com worktree agent parallel coding skills routing"`
  `Q3 = "site:github.com \"git worktree\" \"sub agent\" coding"`
  `Q4 = "site:github.com \".claude/skills\" worktree main branch subagent"`

* repo 후보 수집
  `C1=SpillwaveSolutions/parallel-worktrees`, `C2=enuno/claude-command-and-control`, `C3=gabrielkoerich/orchestrator`, `C4=ComposioHQ/agent-orchestrator`, `C5=RunMaestro/Maestro`, `C6=nwiizo/ccswarm`를 수집했다. `C1`은 병렬 worktree skill과 spawn/sync/cleanup 스크립트를, `C2`는 role skill/bridge/worktree skill을, `C3`는 role·skills·tools·constraints를 생성하는 router와 main-dir sandbox를, `C4`는 worktree/PR 중심 런타임을, `C5`는 worktree sub-agent와 moderator routing을, `C6`는 git worktree와 session infra를 노출한다. ([GitHub][1])

* repo 초기 점수화
  점수는 `0.0~1.0` 분석자 점수다.
  `C1: fit=0.68, vis=0.84, run=0.89, maint=0.28, gap=0.42`
  `C2: fit=0.93, vis=0.96, run=0.47, maint=0.39, gap=0.11`
  `C3: fit=0.87, vis=0.83, run=0.81, maint=0.35, gap=0.19`
  `C4: fit=0.75, vis=0.78, run=0.92, maint=0.95, gap=0.34`
  `C5: fit=0.72, vis=0.54, run=0.84, maint=0.79, gap=0.33`
  `C6: fit=0.61, vis=0.74, run=0.69, maint=0.57, gap=0.64`

* 검증 전략 초기화
  `L1 -> R1`로 repo 적합성 선별, `L2 -> R2,R3`로 module 후보를 core/supporting과 run mode로 분기, `L3 -> R4`로 실제 실행/트러블슈팅 후 accept/fallback을 결정했다.

# 라우팅 규칙

## R1. Repo 적합성 라우팅

* `ID: R1-RepoFit`
* `parent scope: L1-RepoScan`
* `vars: fit_core, module_vis, run_surface, maint_signal, impl_gap`
* `Pass := (fit_core >= 0.80) && (module_vis >= 0.70) && (impl_gap <= 0.25)`
* `Hold := (fit_core >= 0.55) && (impl_gap <= 0.55) && ((module_vis < 0.70) || (run_surface < 0.50) || (maint_signal < 0.45))`
* `Reject := (fit_core < 0.55) || (impl_gap > 0.55)`

## R2. 핵심 module 라우팅

* `ID: R2-ModuleRole`
* `parent scope: L2-ModuleScan`
* `vars: user_fit, entrypoint, example_or_test, dep_complexity`
* `Core := (user_fit >= 0.75) && (entrypoint = 1)`
* `Supporting := (user_fit >= 0.45) && (entrypoint >= 0)`
* `Irrelevant := (user_fit < 0.45)`

## R3. 코드 양 / 실행 가능성 라우팅

* `ID: R3-RunMode`
* `parent scope: L2-ModuleScan`
* `vars: loc_core, exec_entry, env_cost, doc_precision`
* `Dynamic-first := (exec_entry = 1) && (env_cost <= 0.60)`
* `Static-first := (exec_entry = 0) && (doc_precision >= 0.70)`
* `Structure-only := (exec_entry = 1) && (env_cost > 0.60)`

## R4. 정합성 / fallback 라우팅

* `ID: R4-ConsistencyFallback`
* `parent scope: {L2-ModuleScan, L3-ExecTroubleshoot}`
* `vars: intent_fit, exec_fit, mismatch_severity, same_repo_alt_remaining`
* `Accept := (intent_fit >= 0.80) && (mismatch_severity <= 0.20)`
* `Retry_with_other_module_in_same_repo := (same_repo_alt_remaining = 1) && ((intent_fit < 0.80) || (exec_fit < 0.80))`
* `Retry_with_another_repo := (same_repo_alt_remaining = 0) && ((intent_fit < 0.80) || (mismatch_severity > 0.20))`

# 루프

## L1. Repo 후보 탐색 루프

* `ID: L1-RepoScan`

* `parent scope: ROOT`

* `entry := (candidate_count > 0)`

* `exit := (accepted_repo_found = 1) || (candidate_exhausted = 1)`

* `C1=SpillwaveSolutions/parallel-worktrees`
  `R1 => Hold`
  이유: worktree 생성/정리/동기화 스크립트와 background agent 상태 규약은 분명하지만, role-split skill이나 dedicated bridge module은 드러나지 않았다. ([GitHub][1])

* `C2=enuno/claude-command-and-control`
  `R1 => Pass`
  이유: repo 트리에 `agent-skill-bridge`, `architect-role-skill`, `builder-role-skill`, `skill-orchestrator`, `subagent-driven-development`, `using-git-worktrees`가 함께 있고, 문서에서도 orchestrator가 skill-loaded worker를 spawn하고 architect는 main branch, builder들은 worktree에서 병렬 작업하는 패턴을 직접 설명한다. ([GitHub][2])

* `C3=gabrielkoerich/orchestrator`
  `R1 => Pass`
  이유: task router가 agent+complexity+profile을 만들고, skills catalog를 prompt에 주입하며, retry/recovery와 worktree lifecycle, main project dir read-only sandbox를 명시한다. ([GitHub][3])

* `C4=ComposioHQ/agent-orchestrator`
  `R1 => Hold`
  이유: worktree/branch/PR 중심 런타임과 retryable reactions는 강하지만, 명시적인 main-coder/sub-coder형 skill split과 bridge는 repo 표면에서 보이지 않았다. ([GitHub][4])

* `C5=RunMaestro/Maestro`
  `R1 => Hold`
  이유: worktree sub-agent와 moderator routing은 있으나, skills는 “provider에 이미 설정된 것”을 pass-through 하는 구조라 native role-skill bridge repo로는 한 단계 부족했다. ([GitHub][5])

* `C6=nwiizo/ccswarm`
  `R1 => Reject`
  이유: README가 Git worktrees는 working이라 하면서도 AI execution은 simulated, parallel executor는 partial, coordination loop는 not implemented라고 인정한다. ([GitHub][6])

## L2. Repo 내부 module 검증 루프

* `ID: L2-ModuleScan`

* `parent scope: {C1, C2}`

* `entry := (repo_status = Pass) || (repo_status = Hold && repo_run_surface >= 0.80)`

* `exit := (core_module_set_accept = 1) || (module_candidate_exhausted = 1)`

* `repo=C1 parallel-worktrees`

  * `M1=scripts/spawn-parallel.sh` → `R2=Core`, `R3=Dynamic-first`
  * `M2=scripts/sync-worktrees.sh` → `R2=Core`, `R3=Dynamic-first`
  * `M3=scripts/cleanup-worktrees.sh` → `R2=Supporting`, `R3=Dynamic-first`
  * `M4=SKILL.md` → `R2=Supporting`, `R3=Static-first`
  * 판정: 이 repo는 worktree lifecycle은 확실하지만, `role_split_gap=1`, `bridge_gap=1`이 남았다. 같은 repo 안에서 `SKILL.md + scripts` 조합까지 확인했지만 main/sub 역할 분리와 bridge 모듈이 채워지지 않아 `R4 => Retry_with_another_repo`로 넘겼다. README는 세 스크립트와 background status contract를 설명한다. ([GitHub][1])

* `repo=C2 enuno/claude-command-and-control`

  * `M1=skills/using-git-worktrees/SKILL.md` → `R2=Core`, `R3=Static-first`
  * `M2=skills/architect-role-skill/SKILL.md` → `R2=Core`, `R3=Static-first`
  * `M3=skills/builder-role-skill/SKILL.md` → `R2=Core`, `R3=Static-first`
  * `M4=skills/agent-skill-bridge/SKILL.md` → `R2=Core`, `R3=Static-first`
  * `M5=skills/skill-orchestrator/SKILL.md` → `R2=Core`, `R3=Static-first`
  * `M6=skills/subagent-driven-development/SKILL.md` → `R2=Supporting`, `R3=Static-first`
  * 로컬 다운로드 기준 LOC는 `213 / 872 / 773 / 657 / 680 / 240`으로, 사용자 의도를 커버하는 문서형 모듈 surface가 충분했다.
  * 판정: `intent_fit=0.91`, `mismatch_severity=0.09`, `same_repo_alt_remaining=1` → `R4=Accept`.
    근거: `using-git-worktrees`는 디렉터리 우선순위, `CLAUDE.md` 확인, `.gitignore` 검증, baseline test 확인을 강제하고, `architect-role-skill`은 설계 산출물과 Builder handoff를, `builder-role-skill`은 TDD 구현과 phase handoff를, `agent-skill-bridge`는 skill↔agent handoff JSON과 orchestration pattern을, `skill-orchestrator`는 dependency graph·parallel group·retry를, `subagent-driven-development`는 implementer→spec reviewer→code reviewer의 중첩 리뷰 루프를 제공한다. ([GitHub][7])

## L3. 실행 / 트러블슈팅 루프

* `ID: L3-ExecTroubleshoot`

* `parent scope: repo=C1 parallel-worktrees`

* `entry := (run_mode = Dynamic-first)`

* `exit := (exec_success = 1 && exec_fit >= 0.80) || (retry_budget = 0) || (repo_switch = 1)`

* `attempt_1_env_check`

  * `bash_n_ok=1` for `spawn-parallel.sh`, `sync-worktrees.sh`, `cleanup-worktrees.sh`.

* `attempt_2_dummy_repo_spawn`

  * 로컬 dummy git repo에서 `spawn-parallel.sh featurex 2 main` 실행.
  * `spawn_ok=1`: `.worktrees/featurex-1`, `.worktrees/featurex-2` 생성, `.gitignore`에 `.worktrees/` 추가, `git worktree list` 정상.

* `attempt_3_status_flow`

  * `.agent-status/featurex-1.json`, `.agent-status/featurex-2.json`, `RESULTS.md`를 넣고 `sync-worktrees.sh --status` 실행.
  * `status_ok=1`: COMPLETE/RUNNING 상태와 RESULTS.md 존재를 정상 출력.

* `attempt_4_cleanup_flow`

  * dirty worktree 1개 포함 상태에서 `cleanup-worktrees.sh featurex --delete-branches` 실행.
  * `cleanup_ok=1`: prompt 후 worktree와 branch가 제거됨.

* `troubleshooting_findings`

  * `headless_friction=1`: dirty worktree cleanup은 interactive prompt가 걸려 CI/headless에 바로 쓰기엔 마찰이 있다.
  * `role_skill_gap=1`: 실행은 되지만 main/sub role skill과 bridge가 채워지지 않는다.
  * 결과적으로 `exec_fit=0.84`였지만 `intent_fit=0.68`이어서 `R4 => Retry_with_another_repo`가 발동했다.

# 최종 출력

* 추천 repo: `enuno/claude-command-and-control`
  이 repo가 가장 잘 맞는다. 이유는 role-skill 분해(`architect-role-skill`, `builder-role-skill`), bridge(`agent-skill-bridge`), router(`skill-orchestrator`), worktree policy(`using-git-worktrees`), 실행/리뷰 루프(`subagent-driven-development`)가 한 repo 안에서 연결되기 때문이다. 또한 문서 예시가 architect를 main branch에 두고 builder들을 worktree에 병렬 배치하는 구조를 직접 보여 준다. ([GitHub][2])

* 추천 핵심 module

  * `skills/using-git-worktrees/SKILL.md` — main repo와 worktree의 경계를 잡는 기본 정책. `.worktrees/worktrees` 우선순위, `CLAUDE.md` 확인, `.gitignore` 검증, baseline test까지 포함한다. ([GitHub][7])
  * `skills/architect-role-skill/SKILL.md` — Main Coder에 가장 가까운 모듈. 설계 문서 생성과 Builder handoff를 포함한다. ([GitHub][8])
  * `skills/builder-role-skill/SKILL.md` — Sub Coder에 가장 가까운 모듈. TDD 구현, phase integration, validator handoff를 포함한다. ([GitHub][9])
  * `skills/agent-skill-bridge/SKILL.md` — skill↔agent 간 handoff/return schema와 orchestration pattern을 제공한다. ([GitHub][10])
  * `skills/skill-orchestrator/SKILL.md` — dependency graph, parallel group, retry, synthesis를 담당한다. ([GitHub][11])
  * `skills/subagent-driven-development/SKILL.md` — 구현→spec review→quality review의 중첩 루프를 제공한다. ([GitHub][12])

* 검증 근거

  * repo tree 수준에서 이미 role/bridge/worktree/orchestrator module이 한데 묶여 있다. ([GitHub][2])
  * 문서 수준에서 architect는 main branch, builders는 각 worktree에서 병렬 구현하는 패턴을 명시한다. ([GitHub][2])
  * module 수준에서 main/sub 역할 분리, bridge JSON, parallel orchestration, retry, review loop가 각각 독립 모듈로 검증됐다. ([GitHub][7])

* 발견한 불일치

  * exact label은 `Main Coder / Sub Coder`가 아니라 `Architect / Builder`다. 다만 기능 매핑은 매우 자연스럽다. ([GitHub][8])
  * repo 성격은 “turnkey daemon”보다 “skills/templates-first”에 가깝다. 즉, 런타임 오케스트레이터 자체보다 AI 행동 규약과 라우팅 설계에 더 강하다. ([GitHub][2])

* 같은 repo 내 대안 module

  * `skills/validator-role-skill/` — Builder 다음 단계의 merge gate를 강화할 때 적합하다. tree에 명시되어 있다. ([GitHub][2])
  * `skills/using-superpowers/` — skill discovery와 invocation을 더 자동화하고 싶을 때 보조 모듈로 좋다. tree에 명시되어 있다. ([GitHub][2])

* 필요 시 다음 repo로 넘어간 이유

  * `SpillwaveSolutions/parallel-worktrees`는 로컬 재현까지 포함해 worktree lifecycle은 가장 빨리 검증됐지만, same-repo 대안 모듈을 확인해도 role split과 bridge가 비어 있어서 탈락시켰다. README 기준으로는 spawn/sync/cleanup과 `.agent-status`/`RESULTS.md` contract까지만 강하다. ([GitHub][1])
  * runtime enforcement를 더 중시한다면 다음 후보는 `gabrielkoerich/orchestrator`다. 이 repo는 `route_task.sh`에서 skills catalog/selected_skills/profile/fallback executor를 다루고, system prompt에서 main project dir를 read-only로 두며, retry 시 `git diff main`과 `git log main..HEAD`를 먼저 보라고 강제한다. 다만 role-skill 분리의 명시성은 `enuno`보다 약해서 2순위로 뒀다. ([GitHub][13])

[1]: https://github.com/spillwavesolutions/parallel-worktrees "GitHub - SpillwaveSolutions/parallel-worktrees: Runs parallel subagents and then syncs them with git worktrees · GitHub"
[2]: https://github.com/enuno/claude-command-and-control "GitHub - enuno/claude-command-and-control: Claude command & AI agent creation best practices and templates · GitHub"
[3]: https://github.com/gabrielkoerich/orchestrator/blob/main/specs.md "https://github.com/gabrielkoerich/orchestrator/blob/main/specs.md"
[4]: https://github.com/ComposioHQ/agent-orchestrator "GitHub - ComposioHQ/agent-orchestrator: Agentic orchestrator for parallel coding agents — plans tasks, spawns agents, and autonomously handles CI    fixes, merge conflicts, and code reviews. · GitHub"
[5]: https://github.com/pedramamini/Maestro/blob/main/README.md "https://github.com/pedramamini/Maestro/blob/main/README.md"
[6]: https://github.com/nwiizo/ccswarm "https://github.com/nwiizo/ccswarm"
[7]: https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/using-git-worktrees/SKILL.md "raw.githubusercontent.com"
[8]: https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/architect-role-skill/SKILL.md "raw.githubusercontent.com"
[9]: https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/builder-role-skill/SKILL.md "https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/builder-role-skill/SKILL.md"
[10]: https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/agent-skill-bridge/SKILL.md "raw.githubusercontent.com"
[11]: https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/skill-orchestrator/SKILL.md "https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/skill-orchestrator/SKILL.md"
[12]: https://raw.githubusercontent.com/enuno/claude-command-and-control/main/skills/subagent-driven-development/SKILL.md "raw.githubusercontent.com"
[13]: https://raw.githubusercontent.com/gabrielkoerich/orchestrator/main/scripts/route_task.sh "https://raw.githubusercontent.com/gabrielkoerich/orchestrator/main/scripts/route_task.sh"


업로드된 메모는 이전 보고서가 요구사항 정리, 후보 탐색, 핵심 모듈 평가, 실행 검증, 불일치 요인, 추가 탐색 가치까지 담고 있다고만 적혀 있고, 실제 본문은 여기서 바로 노출되지는 않았다. 그래서 이번 보강은 GitHub 원문 기준으로 다시 검증했다. 

이번에 추가로 넣어야 할 조사 축은 세 개다. 첫째는 role/bridge-first skills 저장소, 둘째는 worktree/runtime 저장소, 셋째는 AGENTS.md·CLAUDE.md로 “메인 세션이 서브 세션과 어떻게 상호작용하는지”를 가르치는 project-level 패턴이다. 이 기준으로 보면 `enuno/claude-command-and-control`은 여전히 단일 repo 기준 최상위 후보다. repo 자체에 `agent-skill-bridge`, `architect-role-skill`, `builder-role-skill`, `using-git-worktrees`, `skill-orchestrator`가 함께 있고, 문서 축에도 Agent Skills vs Multi-Agent, Git Worktree Integration, hybrid multi-git-worktree development가 잡혀 있다. `architect-role-skill`은 구현은 `builder-role-skill`로 넘기라고 명시하고, `agent-skill-bridge`는 skill→agent / agent→skill / orchestrator handoff와 JSON 반환 구조를 정의하며, `skill-orchestrator`는 dependency graph와 parallel group, synthesis를 다룬다. ([GitHub][1])

가장 크게 보강해야 할 새 후보는 `ScientiaCapital/skills`다. 이 repo는 README 수준에서 이미 `worktree-manager`, `agent-teams`, `subagent-teams`, `agent-capability-matrix`, `workflow-orchestrator`를 하나의 skill library로 묶고, progressive disclosure와 skill-level integration tests까지 선언한다. module 수준으로 내려가면 `agent-teams`는 team lead가 worktree를 만들고 `WORKTREE_TASK.md`를 써서 개별 Claude 세션을 띄운 뒤 merge를 조정하는 구조를 설명하고, `subagent-teams`는 worktree가 필요 없는 in-session fan-out과 worktree 기반 `agent-teams`의 경계 조건을 분리하며, `agent-capability-matrix`는 task type→agent/skill/model/fallback을 매핑하고, `workflow-orchestrator`는 Builder+Observer 이중 팀을 기본 세션 구조로 둔다. 즉 “repo 단위 라우팅 + module 단위 라우팅”이 가장 선명하게 드러나는 새 자료다. ([GitHub][2])

runtime 쪽 보강 후보로는 `codingagentsystem/cas`가 강하다. CAS는 supervisor가 작업을 쪼개고 worker를 각 git worktree에 배치해 병렬 실행하며, 동시에 CAS database에 memories, tasks, rules, skills를 공유하는 구조를 명시한다. 즉 역할 분리는 supervisor/worker로 깔끔하고, 세션 간 coordination은 파일만이 아니라 별도 context system까지 포함한다. 다만 SKILL.md 중심의 역할-bridge repo라기보다는 “실행 플랫폼”에 더 가깝다. ([GitHub][3])

module 단위 참고 자료로는 `jimmc414/claude-code-plugin-marketplace` 안의 `parallel-orchestrator`가 생각보다 중요하다. 이 모듈은 메인 세션을 “programming manager”로 정의하고, worker와의 유일한 통신 수단을 git worktrees와 commit prefixes로 제한하며, work item 추출→workstream split→worker kickoff prompt 생성→monitoring→integration→failure recovery까지 한 개 `SKILL.md` 안에 정리해 둔다. 런타임 자동화는 약하지만, “AI에게 main branch와 sub session 상호작용을 어떻게 가르칠지”라는 질문에는 아주 직접적인 재료다. ([GitHub][4])

순수 worktree 운영 레이어는 `max-sixty/worktrunk`를 같이 봐야 한다. Worktrunk는 worktree UX를 CLI로 단순화하고, `wt switch -c -x claude` 같은 방식으로 worktree 생성과 Claude 실행을 묶고, hooks·merge workflow·build cache copy 같은 운영 기능을 제공한다. 반면 role skill, bridge schema, retry/review loop는 약하므로 단독 정답보다는 `enuno`나 `ScientiaCapital` 같은 skill-first repo와 결합해서 보는 편이 맞다. ([GitHub][5])

보류 후보도 정리해 둘 가치가 있다. `SuperClaude_Framework`는 parallel development with git worktrees 지침과 parallel-first execution 패턴은 분명하지만, 역할 bridge는 수동적이고 plugin system v5는 아직 예정 상태다. `levnikolaevich/claude-code-skills`는 L0→L3 orchestrator-worker 계층, Agent Teams guide, 연구 근거가 매우 탄탄하지만, 현재 top-level evidence만으로는 worktree/main-sub 상호작용이 직접 드러나지 않아 한 단계 더 까봐야 한다. `cosmix/loom`은 agents/skills/hooks/CLAUDE.md를 함께 설치하고 `/loom-plan-writer` skill, worktree isolation, retry/recover/verify 루프까지 제공하지만, role-skill split은 stage orchestration 쪽에 더 가깝다. `meta-pytorch/OpenEnv`는 project-level `CLAUDE.md` 예시로는 훌륭해서, issue마다 worktree teammate를 만들고 lead agent가 stacked PR까지 조정하는 운영 규칙을 보여 준다. ([GitHub][6])

지금 기준으로는 이렇게 재정렬하는 게 맞다. 단일 repo 1위는 여전히 `enuno/claude-command-and-control`, 추가 조사 1순위는 `ScientiaCapital/skills`, 실행 플랫폼 보강은 `codingagentsystem/cas`, worktree ops 보강은 `max-sixty/worktrunk`, 모듈 설계 레퍼런스는 `parallel-orchestrator`다. 즉 앞으로는 “한 repo 더 찾기”보다 `enuno + ScientiaCapital + CAS/Worktrunk + parallel-orchestrator module` 조합으로 설계 기준을 만드는 편이 더 정확하다. ([GitHub][1])

[1]: https://github.com/enuno/claude-command-and-control?utm_source=chatgpt.com "enuno/claude-command-and-control"
[2]: https://github.com/ScientiaCapital/skills "GitHub - ScientiaCapital/skills: Reusable Claude Code skills library - trading signals, sales automation, RunPod deployment · GitHub"
[3]: https://github.com/codingagentsystem/cas "GitHub - codingagentsystem/cas: Multi-agent orchestration for Claude Code. Persistent memory, tasks, rules, and skills that make AI agents actually coordinate. · GitHub"
[4]: https://raw.githubusercontent.com/jimmc414/claude-code-plugin-marketplace/master/plugins/parallel-workflows/skills/parallel-orchestrator/SKILL.md "raw.githubusercontent.com"
[5]: https://github.com/max-sixty/worktrunk/blob/main/README.md "worktrunk/README.md at main · max-sixty/worktrunk · GitHub"
[6]: https://github.com/SuperClaude-Org/SuperClaude_Framework/blob/master/CLAUDE.md "SuperClaude_Framework/CLAUDE.md at master · SuperClaude-Org/SuperClaude_Framework · GitHub"
