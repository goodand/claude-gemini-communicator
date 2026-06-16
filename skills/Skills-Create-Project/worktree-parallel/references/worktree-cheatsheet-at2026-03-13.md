# Git Worktree 병렬 에이전트 치트시트

## 기본 worktree 명령

```bash
# worktree 생성 (새 브랜치)
git worktree add .worktrees/feature-auth -b feature-auth

# worktree 생성 (기존 브랜치)
git worktree add .worktrees/fix-bug fix-bug

# worktree 목록
git worktree list

# worktree 제거
git worktree remove .worktrees/feature-auth

# 정리 (삭제된 worktree 참조 제거)
git worktree prune
```

## 역할 분리 패턴 (Architect + Builder)

### Architect (Main Branch)
- 전체 설계 문서 작성 (`PLAN.md`, `TASKS.md`)
- 작업을 독립 단위로 분할
- Builder에게 worktree 할당 + 작업 지시
- 완료된 worktree를 main으로 merge
- 코드 리뷰 및 충돌 해결

### Builder (Worktree)
- 할당된 worktree에서만 작업
- TDD: 테스트 먼저 → 구현 → 검증
- 완료 시 상태 파일 업데이트 (`.agent-status/<name>.json`)
- main branch 직접 수정 금지

## Handoff JSON 규약

```json
{
  "task_id": "feature-auth",
  "worktree": ".worktrees/feature-auth",
  "branch": "feature-auth",
  "status": "in_progress|complete|failed",
  "assigned_to": "builder-1",
  "files_modified": ["src/auth.py", "tests/test_auth.py"],
  "notes": "OAuth2 통합 완료, 테스트 3개 추가"
}
```

## 병렬 실행 워크플로

```bash
# Step 1: worktree 생성 (3개 병렬 작업)
git worktree add .worktrees/auth -b feat/auth
git worktree add .worktrees/api -b feat/api
git worktree add .worktrees/ui -b feat/ui

# Step 2: 각 worktree에서 독립 작업 (별도 터미널/에이전트)
cd .worktrees/auth && # Builder 1 작업
cd .worktrees/api && # Builder 2 작업
cd .worktrees/ui && # Builder 3 작업

# Step 3: 상태 확인
cat .agent-status/*.json | python3 -m json.tool

# Step 4: 완료된 작업 merge
git merge feat/auth
git merge feat/api
git merge feat/ui    # 충돌 시 수동 해결

# Step 5: 정리
git worktree remove .worktrees/auth
git worktree remove .worktrees/api
git worktree remove .worktrees/ui
git branch -d feat/auth feat/api feat/ui
```

## Orchestrator 패턴

```
Architect (main)
├── spawn worktree-1 → Builder-1 (feat/auth)
├── spawn worktree-2 → Builder-2 (feat/api)
├── spawn worktree-3 → Builder-3 (feat/ui)
├── monitor status files
├── merge completed worktrees
└── cleanup
```

### 병렬 그룹 (dependency graph)

```
[독립 그룹 A] auth, api  →  병렬 실행
[의존 그룹 B] ui          →  A 완료 후 실행
```

## 주의사항

| 항목 | 설명 |
|------|------|
| `.worktrees/` | `.gitignore`에 추가 필수 |
| main 직접 수정 | 금지 — merge만 |
| 파일 겹침 | 같은 파일을 여러 worktree에서 수정하면 충돌 → 분할 시 최소화 |
| dirty worktree | `git worktree remove`는 uncommitted 변경이 있으면 실패 → `--force` 필요 |
| 브랜치 삭제 | worktree 제거 후에만 가능 |
| `.agent-status/` | `.gitignore`에 추가, 상태 추적용 |

## 참조 오픈소스

- `enuno/claude-command-and-control` — architect/builder role skill + bridge + orchestrator
- `SpillwaveSolutions/parallel-worktrees` — spawn/sync/cleanup 스크립트
- `ScientiaCapital/skills` — agent-teams + worktree-manager + capability-matrix
- `codingagentsystem/cas` — supervisor/worker + shared context database
