---
name: worktree-parallel
description: >-
  Delegation Orchestration family의 workflow owner. Use this skill when
  multiple AI agents must be coordinated in parallel using git worktrees,
  role separation, bridge handoff, dependency-aware task ordering, and merge
  coordination. direct packet/dispatch/runtime setup은 agent-task-packet,
  codex-delegation-protocol, codex-worktree-dispatch, codex-tmux-orchestrator,
  codex-subagent-setup을 사용하라.
---

# Worktree Parallel

Architect(main branch)가 설계하고, Builder(worktree)가 병렬 구현하는 패턴.

## When to use

- 큰 작업을 여러 에이전트에게 병렬로 나눠서 시킬 때
- main에서 설계/리뷰, worktree에서 구현을 분리할 때
- 작업 간 의존성이 있어 순서 조율이 필요할 때
- 병렬 작업 결과를 안전하게 merge/통합할 때

## Do not use

- handoff packet 하나만 만들면 될 때 → `agent-task-packet`
- delegation prompt만 조립하면 될 때 → `codex-delegation-protocol`
- dispatch state만 관리하면 될 때 → `codex-worktree-dispatch`
- tmux session에 launch만 하면 될 때 → `codex-tmux-orchestrator`
- subagent setup만 준비하면 될 때 → `codex-subagent-setup`

## Family Roles

- owner:
  - `worktree-parallel`
- direct-call specialists:
  - `agent-task-packet`
  - `codex-delegation-protocol`
  - `codex-worktree-dispatch`
  - `codex-tmux-orchestrator`
  - `codex-subagent-setup`

## Workflow

1. **작업 분할 + 의존성 그래프** — 전체 task를 독립 work item으로 분해하고, 의존 관계를 파악하여 병렬 그룹(동시 실행 가능)과 순차 그룹(선행 완료 필요)으로 나눈다 (→ cheatsheet Orchestrator 패턴)
2. **worktree 생성** — `scripts/worktree_manager.py spawn`으로 작업별 worktree + branch 생성. `.worktrees/`, `.agent-status/`를 `.gitignore`에 자동 추가
3. **Architect/Builder 할당** — Architect는 main에서 설계 문서와 handoff JSON 작성. Builder는 각 worktree에서 독립 구현. main branch 직접 코드 수정 금지 (→ cheatsheet Handoff JSON 규약)
4. **병렬 실행 + 모니터링** — Builder가 작업하는 동안 `scripts/worktree_manager.py status`로 `.agent-status/*.json` 확인. 파일 겹침이 있으면 즉시 작업 재분할
5. **통합** — 병렬 그룹 완료 후 Architect가 main으로 merge. 충돌 시 `git diff main` 기반 해결. 순차 그룹은 선행 merge 완료 후 시작
6. **정리** — `scripts/worktree_manager.py cleanup --delete-branches`로 worktree + branch 삭제

## Scripts

- `scripts/worktree_manager-at2026-03-13.py` — spawn/status/validate/merge-check/list/cleanup 통합 래퍼. `python3 scripts/worktree_manager-at2026-03-13.py --help`
- `scripts/worktree_verify-at2026-03-14.py` — 환경 검증 (git 설치, .gitignore, 브랜치 규칙, 상태 파일, dirty/stale 감지, 파일 겹침). `python3 scripts/worktree_verify-at2026-03-14.py --help`

## References

- `references/worktree-cheatsheet-at2026-03-13.md` — git worktree 커맨드, Architect/Builder 역할, Handoff JSON, Orchestrator 패턴, 주의사항
- `references/git-worktree-기반-에이전트-병렬-실행-SKills-search-at2026-03-13-20-34.md` — 오픈소스 6개 repo 심층 비교 (enuno 추천, 라우팅 규칙, 실행 검증 로그)
- `checklist.md` — Main Coder / Sub Coder 역할, Skill 구조, handoff, 검증, merge 상세 체크리스트
- `references/troubleshooting.md` — 실행 중 발견된 오류·해결 사례 (spawn 실패, sandbox 제약 등)
- `references/subagent-audit-and-remote-baseline-at2026-06-15-20-22.md` — concern별 subagent audit(PASS/FAIL/PASS_WITH_RISK + evidence path), branch/PR sequencing, remote baseline loop, self-report 경고

## Notes

- `.worktrees/`와 `.agent-status/`는 `.gitignore`에 추가 필수
- main에서 직접 코드 수정 금지 — merge만 수행 (Architect 규칙)
- 같은 파일을 여러 worktree에서 수정하면 충돌 — 작업 분할 시 파일 겹침 최소화
- dirty worktree는 `git worktree remove`가 실패 → `--force` 필요
- `spawn`은 git 실패 시 exit 1 반환 — 상태 파일은 실제 worktree 생성 성공 시에만 생성됨
- `cleanup`은 고아 상태 파일(worktree 없이 JSON만 남은 것)도 자동 정리
- Codex sandbox에서 `spawn` 불가 — `status`, `validate`, `merge-check`만 할당 (→ `references/troubleshooting.md`)
