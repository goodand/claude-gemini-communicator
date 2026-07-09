# Skill Usage Details

- recorded_at: `2026-03-21-23-25`
- purpose: `entrypoint를 얇게 유지하고, setup/orchestration 상세 사용 지침과 보조 링크를 분리하기 위한 detail page`

## Details

- setup context: [setup-context-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/setup-context-at2026-03-18-22-47.md)
- agent package layout: [agent-package-layout-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/agent-package-layout-at2026-03-18-22-47.md)
- progressive context routing: [progressive-context-routing-at2026-03-18-22-47.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/progressive-context-routing-at2026-03-18-22-47.md)
- agent flow: [agent-flow-at2026-03-20-01-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/agent-flow-at2026-03-20-01-14.md)
- agent class policy: [agent-class-policy-at2026-03-20-01-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/agent-class-policy-at2026-03-20-01-14.md)
- orchestration consistency checklist: [consistency-checklist-at2026-03-20-17-21.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/checklist-forconsistency-evaluation/consistency-checklist-at2026-03-20-17-21.md)
- 3-layer graphviz view: [codex-subagent-setup-3layer-kb-at2026-03-20-17-32.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/graphviz/codex-subagent-setup-3layer-kb-at2026-03-20-17-32.md)
- troubleshooting: [troubleshooting.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/troubleshooting.md)

## Built-in agent packages

- `agents/reviewer/AGENT.md`
- `agents/context-broker/AGENT.md`
- `agents/dependency-graph-analyst/AGENT.md`
- `agents/dependency-risk-auditor/AGENT.md`
- `agents/synthesizer/AGENT.md`

## Execution entrypoints

- root entrypoint: `SKILL.md`
- setup bootstrap: `references/setup-context-at2026-03-18-22-47.md`
- per-role entrypoint: `agents/<role>/AGENT.md`

## Notes

- 현재 skill은 재사용 가능한 subagent setup/orchestration layer를 다룬다.
- 각 subagent package는 `AGENT.md + knowledge_bases/ + references/ + bridges/ + scripts/` 구조를 가진다.
- `AGENT.md`는 entrypoint로 유지하고, 길어지는 역할/순서/입출력/handoff/context 설명은 `package_details` 링크로 분리한다.
- tool/permission 정보는 `AGENT.md` 본문에 뭉개지지 않고 `references/tool-capability-policy-*.md`에 분리한다.
- 상위 agent용 setup context와 하위 agent용 code/context 링크는 분리한다.
- 하위 agent에는 필요한 파일 링크만 주고 점진적으로 context를 주입한다.
- flow는 시간표가 아니라 artifact gate 기반 절차로 관리한다.
- agent는 `persistent structural`, `run-scoped interpretive`, `artifact-backed synthesizer` 클래스로 구분한다.
- lint/static warning은 subagent discipline enforcement로 사용하고, 가능하면 subagent 실행 구간에만 켠다.
- analysis 전용 graph/export/schema는 `codebase-analysis`에 두고, 이 skill은 orchestration layer만 유지한다.
