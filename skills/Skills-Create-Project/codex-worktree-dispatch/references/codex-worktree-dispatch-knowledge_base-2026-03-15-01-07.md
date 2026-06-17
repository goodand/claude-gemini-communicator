# research URL Knowledge Base
  - ver: `v0.0.0`
  - generated_at: `2026-03-15`
  - updated_at: `2026-03-15` (v0.0.0: codex-worktree-dispatch reference 초안 추가)
  - format: `- [한 줄 설명](URL)`
  - generation_method: `manual curation based on GitHub repository README/repo pages for codex-worktree-dispatch
  design`
  - total_urls: `7`
  - paper_like_urls: `0`
  - other_urls: `7`

  ## Document Map

  | 문서 | 역할 |
  |------|------|
  | [PLAN.md](../gemini/PLAN.md) | 실행 계획 · 단계 · 에이전트 운영 규칙 |
  | `CODEX_WORKTREE_DISPATCH_KNOWLEDGE_BASE.md` (이 파일) | GitHub reference 7개 인덱스 |
  | [IMAGE_STRUCTURE_GRAPHS.md](../gemini/IMAGE_STRUCTURE_GRAPHS.md) | 병렬 실행/상태 흐름 다이어그램 연결 예정 |
  | [IMAGE_URL_MATCHES.md](../gemini/IMAGE_URL_MATCHES.md) | 이미지 URL ↔ 소스 매핑 예정 |

  ## Table of Contents
  - [Paper-like URLs](#paper-like-urls)
  - [Other research References URLs](#other-research-references-urls)

  ## Paper-like URLs

  - 없음

  ## Other research References URLs

  - [Emdash는 다중 코딩 에이전트를 각 git worktree에 격리해 병렬 실행하고 ticket handoff와 review 흐름까지 연결하는
  orchestration layer다](https://github.com/generalaction/emdash)
    - sources: `github_readme_manual_review_2026-03-15`
    - agent: `A00`
    - pseudocode_3lines:
      - 1) Task/ticket를 에이전트 단위 work item으로 분해한다.
      - 2) 각 에이전트를 독립 worktree에 배치하고 병렬 실행한다.
      - 3) diff/review/PR 단계로 다시 main 흐름에 fan-in한다.

  - [Par는 worktree와 tmux session을 함께 생성·관리하는 parallel worktree & session manager다](https://github.com/
  coplane/par)
    - sources: `github_readme_manual_review_2026-03-15`
    - agent: `A00`
    - pseudocode_3lines:
      - 1) 작업 label을 기준으로 branch, worktree, tmux session을 함께 만든다.
      - 2) 각 세션에서 AI coding assistant를 독립 실행한다.
      - 3) 전역 목록/상태/명령 전송 인터페이스로 병렬 작업을 운영한다.

  - [CCManager는 Claude Code, Gemini CLI, Codex CLI 등을 git worktree 단위로 관리하며 상태 감지와 hook 자동화를 제공
  하는 session manager다](https://github.com/kbwo/ccmanager)
    - sources: `github_readme_manual_review_2026-03-15`
    - agent: `A00`
    - pseudocode_3lines:
      - 1) 여러 프로젝트와 worktree에 대한 agent session registry를 유지한다.
      - 2) 세션 상태를 idle/busy/waiting 등으로 감지하고 hook을 실행한다.
      - 3) worktree 생성·상태 변경·session context 복사를 자동화한다.

  - [Git Worktree Toolbox는 MCP server/CLI로 worktree 생성, archive, PR, prompt resume, metadata doctor를 제공한다]
  (https://github.com/ben-rogerson/git-worktree-toolbox)
    - sources: `github_readme_manual_review_2026-03-15`
    - agent: `A00`
    - pseudocode_3lines:
      - 1) 새 worktree와 대응 branch를 만든다.
      - 2) 변경점 검토, prompt resume, PR 생성 같은 lifecycle 작업을 수행한다.
      - 3) doctor/clean/archive 기능으로 metadata와 workspace를 정리한다.

  - [Agentree는 AI coding agent용 isolated worktree를 빠르게 만들고 env 복사와 dependency 설치까지 한 번에 수행한다]
  (https://github.com/AryaLabsHQ/agentree)
    - sources: `github_readme_manual_review_2026-03-15`
    - agent: `A00`
    - pseudocode_3lines:
      - 1) 새 branch와 isolated worktree를 생성한다.
      - 2) env 파일, AI 설정 파일, dependency 설치를 bootstrap한다.
      - 3) 여러 agent가 바로 병렬 코딩을 시작할 수 있는 상태로 만든다.

  - [GWQ는 fuzzy finder 기반 git worktree manager로 status watch, tmux session, task queue까지 포함한 AI 병렬 코딩 워
  크플로우를 지원한다](https://github.com/d-kuro/gwq)
    - sources: `github_readme_manual_review_2026-03-15`
    - agent: `A00`
    - pseudocode_3lines:
      - 1) 여러 feature/bugfix용 worktree를 빠르게 생성한다.
      - 2) 각 worktree에서 독립 AI agent를 실행하고 status를 watch한다.
      - 3) task/dependency/resource 관점에서 병렬 개발 흐름을 관리한다.

  - [Kosho는 `.kosho/` 아래 worktree registry와 hook을 두고 concurrent development 환경을 관리하는 경량 CLI다]
  (https://github.com/carlsverre/kosho)
    - sources: `github_readme_manual_review_2026-03-15`
    - agent: `A00`
    - pseudocode_3lines:
      - 1) branch별 worktree를 `.kosho/worktrees/` 아래 생성하거나 재사용한다.
      - 2) list/run/prune와 hook을 통해 생성·실행·정리를 수행한다.
      - 3) lightweight registry를 바탕으로 concurrent agent 환경을 유지한다.

  참고 소스:

  - generalaction/emdash (https://github.com/generalaction/emdash)
  - coplane/par (https://github.com/coplane/par)
  - kbwo/ccmanager (https://github.com/kbwo/ccmanager)
  - ben-rogerson/git-worktree-toolbox (https://github.com/ben-rogerson/git-worktree-toolbox)
  - AryaLabsHQ/agentree (https://github.com/AryaLabsHQ/agentree)
  - d-kuro/gwq (https://github.com/d-kuro/gwq)
  - carlsverre/kosho (https://github.com/carlsverre/kosho)