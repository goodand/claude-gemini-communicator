# Setup Context

- recorded_at: `2026-03-18-22-47`
- purpose: `상위 agent가 codex-subagent-setup skill을 시작할 때 먼저 읽는 context file`

## Load this first

- [SKILL.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/SKILL.md)
- [setup knowledge base](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/knowledge_bases/codex-subagent-setup-knowledge_base-at2026-03-18-22-47.md)
- [3-layer production KB](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/knowledge_bases/codex-subagent-setup-3layer-production-kb-at2026-03-20-17-21.md)
- [agent package layout](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/agent-package-layout-at2026-03-18-22-47.md)
- [progressive context routing](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/references/progressive-context-routing-at2026-03-18-22-47.md)

## Then choose one agent package

- [reviewer](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/reviewer/AGENT.md)
- [context-broker](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/context-broker/AGENT.md)
- [dependency-graph-analyst](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/dependency-graph-analyst/AGENT.md)
- [dependency-risk-auditor](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/dependency-risk-auditor/AGENT.md)
- [synthesizer](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codex-subagent-setup/agents/synthesizer/AGENT.md)
- planning tool: `dependency-slice-planner` skill is external to this package directory and should be invoked separately when slice planning is needed.

## Rule

상위 agent는 모든 agent package를 한 번에 preload하지 않는다. 선택한 role의 `context-links`만 다음 단계에서 주입한다.
