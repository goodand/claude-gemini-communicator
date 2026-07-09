GitHub 기준으로 codex-worktree-dispatch와 가장 가까운 레퍼런스를 다시 찾겠다. 기준은 단순 worktree 사용이 아니라,
  작업 분배, 상태 추적, 병렬 에이전트 운영까지 포함하는 저장소다.

• Searched site:github.com git worktree multi agent coding repo worktree parallel agents

• Searched site:github.com "git worktree" task queue agent repo

• Searched site:github.com "orchestration layer" "git worktrees" coding agents

• Searched https://github.com/generalaction/emdash

• Searched 'Parallel Worktree & Session Manager' in https://github.com/coplane/par

• Searched https://github.com/d-kuro/gwq

• Searched 'task queue' in https://github.com/d-kuro/gwq

─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

• 찾아봤고, codex-worktree-dispatch와 가장 가까운 GitHub 레퍼런스는 “worktree 생성기”보다 task/worktree/session을 함
  께 관리하는 쪽이야.

  가장 추천하는 레퍼런스 순위

  1. generalaction/emdash (https://github.com/generalaction/emdash)

  - 가장 상위 레벨 참고용.
  - 이유:
      - 여러 coding agent를 병렬로 돌리고
      - 각 agent를 별도 git worktree에 격리하고
      - ticket을 agent에 넘기고
      - diff/PR/CI까지 연결함.
  - GitHub 설명에도 multiple coding agents in parallel, each isolated in its own git worktree, pass Linear, GitHub,
    or Jira tickets to an agent가 직접 나온다.
  - dispatch 관점에서 가져올 것:
      - task -> agent -> worktree 매핑
      - ticket 기반 handoff
      - merge 직전 review gate

  2. coplane/par (https://github.com/coplane/par)

  - codex-worktree-dispatch에 제일 직접적인 CLI 레퍼런스다.
  - 이유:
      - par start가 worktree + branch + tmux session을 같이 만든다
      - par ls, par open, par send, Overview Mode가 있다
      - label 중심으로 session/worktree를 전역 관리한다
  - dispatch에서 가져올 것:
      - task label 또는 dispatch label 설계
      - task -> branch -> worktree -> session 일괄 생성 흐름
      - global registry / naming convention
  - 특히 session naming convention까지 공개돼 있어서 네 구조 설계에 바로 도움 된다.

  3. kbwo/ccmanager (https://github.com/kbwo/ccmanager)

  - 상태 추적과 후크 설계 참고용으로 가장 좋다.
  - 이유:
      - 여러 AI coding assistant 세션을 git worktree 위에서 관리함
      - state detection strategies
      - status change hooks
      - worktree hooks
      - session data copying
      - automatic worktree directory generation
  - dispatch에서 가져올 것:
      - 상태 전이 모델
      - worktree 생성 후 hook
      - 세션 상태와 dispatch 상태 연결
      - worktree 생성 시 context/session transfer

  4. ben-rogerson/git-worktree-toolbox (https://github.com/ben-rogerson/git-worktree-toolbox)

  - MCP/CLI 관점의 worktree lifecycle 참고용으로 좋다.
  - 이유:
      - new, archive, changes, grab, pr, prompt, doctor, clean
      - AI agent prompt resume 기능까지 있음
  - dispatch에서 가져올 것:
      - metadata 복구용 doctor
      - archive/cleanup lifecycle
      - worktree별 prompt/session resume 개념
      - “canonical worktree metadata” 관리 아이디어

  5. AryaLabsHQ/agentree (https://github.com/AryaLabsHQ/agentree)

  - 가장 단순한 spawn/bootstrap 레퍼런스다.
  - 이유:
      - 새 branch
      - isolated worktree
      - env file 복사
      - dependency install
      - 병렬 agent 실행
  - dispatch에서 가져올 것:
      - post-create bootstrap
      - env/dependency sync
      - 빠른 spawn UX

  6. d-kuro/gwq (https://github.com/d-kuro/gwq)

  - 경량형 상태/실행 보조 참고용.
  - 이유:
      - status --watch
      - exec
      - tmux
      - parallel AI coding workflow를 직접 언급
  - dispatch에서 가져올 것:
      - watch/status 대시보드
      - worktree 대상 command execution
      - tmux 연동 최소 인터페이스

  7. carlsverre/kosho (https://github.com/carlsverre/kosho)

  - 간단한 worktree registry + hook 구조 참고용.
  - 이유:
      - .kosho/worktrees
      - list
      - prune
      - create hook
  - dispatch에서 가져올 것:
      - 로컬 전용 registry 디렉토리 구조
      - hook 기반 post-create automation
      - cleanup/prune 패턴

  직접성 기준으로 요약

  - dispatch core에 가장 가까움: par, ccmanager
  - workflow orchestration 참고: emdash
  - metadata/lifecycle 참고: git-worktree-toolbox
  - spawn/bootstrap 참고: agentree
  - lightweight status/watch 참고: gwq, kosho

  내 추천
  codex-worktree-dispatch 설계 레퍼런스는 이 3개를 우선 보면 된다.

  1. coplane/par (https://github.com/coplane/par)
  2. kbwo/ccmanager (https://github.com/kbwo/ccmanager)
  3. ben-rogerson/git-worktree-toolbox (https://github.com/ben-rogerson/git-worktree-toolbox)

  이유:

  - par는 dispatch의 골격
  - ccmanager는 dispatch의 상태/후크
  - git-worktree-toolbox는 dispatch의 운영 lifecycle

  추가 판단

  - 정확히 codex-worktree-dispatch와 1:1인 repo는 못 찾았다.
  - 가장 가까운 구현 방향은
      - par의 label/session/worktree orchestration
      - ccmanager의 state hooks / worktree hooks
      - git-worktree-toolbox의 archive/doctor/prompt-resume
        를 합치는 쪽이다.

  사용한 소스:

  - GitHub 검색 결과와 각 저장소 README 페이지
  - emdash (https://github.com/generalaction/emdash)
  - par (https://github.com/coplane/par)
  - ccmanager (https://github.com/kbwo/ccmanager)
  - git-worktree-toolbox (https://github.com/ben-rogerson/git-worktree-toolbox)
  - agentree (https://github.com/AryaLabsHQ/agentree)
  - gwq (https://github.com/d-kuro/gwq)
  - kosho (https://github.com/carlsverre/kosho)