가장 유사한 것들

  1. danielrosehill/Agent-Task-Repo-Pattern-With-MCP
     (https://github.com/danielrosehill/Agent-Task-Repo-Pattern-With-MCP)

  - 가장 비슷함.
  - 핵심 아이디어: 작업 하나를 구조화된 task bundle로 정의.
  - 구성도 거의 packet 사고방식이야:
      - project-outline
      - details
      - remote
      - secrets
      - mcp
      - success
      - logs
  - 네가 생각한 codex-task-packet의
      - goal
      - context
      - constraints
      - tooling
      - done_definition
      - artifact/logs
        와 거의 대응된다.
  - 차이: 단일 JSON packet이 아니라 repo-template + 여러 md 파일 방식.

  2. dtormoen/tsk-tsk (https://github.com/dtormoen/tsk-tsk)

  - 실전성은 이쪽이 더 높다.
  - 핵심 아이디어: task template + queue + parent chaining + parallel agent execution
  - 특히 유사한 부분:
      - --type
      - --name
      - --prompt
      - --parent
      - task status / branch / monitoring
  - {{PROMPT}} 템플릿 치환, task queue, parent-child chaining까지 있어서
    codex-task-packet을 실행 가능한 task object로 만들 때 가장 좋은 참고 repo다.
  - 네 설계에 바로 대응되는 필드:
      - task_type
      - task_name
      - prompt/body
      - parent_task_id
      - status
      - output_branch

  3. wild-card-ai/agents-json (https://github.com/wild-card-ai/agents-json)

  - 이건 coding-task용은 아니지만, machine-readable contract/schema 관점에서 매우 중요하다.
  - 핵심: agent interaction contract를 schema로 정의.
  - 네가 codex-task-packet.json 같은 검증 가능한 JSON Schema를 만들고 싶다면 가장 좋은 레퍼런스.
  - 차이: API/agent contract 중심이지 coding work item 중심은 아님.

  4. openai/openai-agents-python (https://github.com/openai/openai-agents-python)

  - packet 자체보다는 handoff semantics 참고용.
  - 핵심 개념:
      - agents
      - handoffs
      - sessions
      - tracing
  - 네가 codex-task-packet에
      - handoff_from
      - handoff_to
      - session_id
      - trace_id
      - guardrails
        를 넣고 싶다면 이 repo가 기준점이 된다.
  - 차이: framework이지, task packet schema repo는 아니다.

  인접하지만 덜 직접적인 것들
  5. ben-rogerson/git-worktree-toolbox (https://github.com/ben-rogerson/git-worktree-toolbox)

  - task context로 worktree를 만들고, 세션 ID를 저장하고, agent prompt를 resume하는 흐름이 있음.
  - task packet보다는 dispatch/session metadata 쪽에 가까움.

  6. Xuanwo/xlaude (https://github.com/Xuanwo/xlaude)

  - worktree별 agent session/state 관리.
  - codex-task-packet보다는 worktree-dispatch + session-monitor 쪽 참고용.

  7. AryaLabsHQ/agentree (https://github.com/AryaLabsHQ/agentree)

  - 병렬 AI agent용 isolated worktree 생성.
  - task schema는 약하지만, 병렬 실행 전제의 runtime 준비는 좋음.

  8. vercel-labs/coding-agent-template (https://github.com/vercel-labs/coding-agent-template)

  - task 생성, 진행률, 결과 branch, keep-alive sandbox 같은 task lifecycle 참고용.
  - packet schema보다 orchestration platform에 가까움.

  9. feiskyer/claude-code-settings (https://github.com/feiskyer/claude-code-settings)

  - codex-skill / autonomous-skill이 있어서 Claude -> Codex handoff task 관점 참고 가능.
  - 다만 packet spec보다는 skill package 쪽.

  보너스: repo는 아니지만 가장 직접적인 참고

  - cmux-multi-agent gist (https://gist.github.com/lark1115/409030b36c1889f8fc28c0448f05f95f)
  - 이건 거의 네가 말한 packet에 가까운 envelope + payload schema다.
  - required keys도 작게 잡혀 있음:
      - task
      - context
      - optional expected_output
  - 단일 JSON payload + envelope 구조를 원하면 이게 제일 직접적이다.

  내 판단

  - codex-task-packet 설계 참고 우선순위는 이 순서가 맞다:

  1. Agent-Task-Repo-Pattern-With-MCP
  2. tsk-tsk
  3. agents-json
  4. openai-agents-python

  이유

  - 1번은 무엇을 넣어야 하는지 알려주고
  - 2번은 그걸 어떻게 실행 task로 굴릴지 알려주고
  - 3번은 그걸 어떻게 schema로 고정할지 알려주고
  - 4번은 agent handoff/session 의미론을 보강해준다