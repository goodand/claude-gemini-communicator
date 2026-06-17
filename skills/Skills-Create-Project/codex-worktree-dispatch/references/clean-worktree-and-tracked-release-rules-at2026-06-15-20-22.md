# Clean Worktree and Tracked-Release Rules

작성일: 2026-06-15-20-22
범위: dispatch ownership 경계 / dirty-main 취급 / 릴리스 바운드 파일 판별 / 의존성 ready 게이트 / merge-after-review 루프

---

## 1. Dispatch canonical ownership

dispatch는 아래 필드의 canonical mutable owner다.

| 소유 필드 | 설명 |
|-----------|------|
| `branch` | 생성된 git branch |
| `worktree_path` | git worktree 경로 |
| `locked_paths` | 이 dispatch가 점유하는 경로 |
| `assigned_agent` | 배정된 agent 식별자 |
| `status` | 현재 상태 (상태 머신 참조) |
| `history` | 상태 전이 이력 (append-only) |
| 런타임 allocation pointer | `session_id`, `heartbeat_path`, `log_path` — 예약 필드, tmux-orchestrator/session-monitor가 채움 |

dispatch가 소유하지 않는 필드 (packet의 계약 내용):

- `goal`, `done_definition`, `required_checks` — 이미 packet에 존재하며 validator의 forbidden-field 집합으로 강제됨
- dispatch에 중복 저장하면 SSOT 위반이다

핵심 원칙: dispatch는 "누가, 어디서, 어떤 상태인지"를 관리한다. "무엇을, 왜"는 packet이 소유한다.

---

## 2. Clean worktree safety (dirty-main is reference-only)

### dirty main worktree의 의미

main 브랜치 워킹 디렉토리가 `origin/main`과 다를 때 (uncommitted 변경, 미추적 파일, 스테이징된 패치 등) 이 worktree는 **참조 전용(reference-only)** 으로 취급한다.

### 규칙

- PR 구현 및 릴리스 검증은 `origin/main`(또는 대상 base)을 체크아웃한 **clean worktree**에서 수행한다.
- clean worktree 예시 경로: `/tmp/<repo>-origin-main-audit`
- dirty main을 직접 편집해 릴리스 작업을 수행하지 않는다.

### 이유

dirty main에서 실행한 테스트/검증 결과는 실제 릴리스 상태를 반영하지 않는다. 예를 들어:

- 로컬에만 존재하는 파일이 "있는 것처럼" 보여 체크를 통과할 수 있다.
- 삭제된 파일이 아직 남아 있어 수집 결과가 왜곡될 수 있다.
- 테스트가 0개 수집(collected 0)되는 등 오탐(false-positive/negative)이 발생한다.

### clean worktree 생성 예시

```bash
# origin/main 기준 clean audit worktree 생성
git worktree add /tmp/my-repo-origin-main-audit origin/main

# 검증 후 정리
git worktree remove /tmp/my-repo-origin-main-audit
```

---

## 3. Tracked-file release rule (git ls-files 기준)

### `Path.exists()`는 릴리스 증명이 아니다

파일이 로컬 파일시스템에 존재한다고 해서 릴리스 대상임을 보장하지 않는다.

릴리스 바운드(release-bound) 경로는 반드시 아래 중 하나로 확인한다:

| 확인 방법 | 명령 |
|-----------|------|
| 현재 브랜치 tracked 파일 | `git ls-files <path>` — 출력이 비어 있으면 untracked |
| 특정 커밋 트리 | `git ls-tree --name-only <commit> <path>` |
| PR merge 대상 커밋 | clean worktree에서 위 명령 실행 |

### 실패 패턴 (real regression)

required-paths 게이트가 dirty worktree 위에서 `Path.exists()`만으로 동작하면:

- untracked 파일이 "릴리스에 있다"고 판정 → false-pass
- 릴리스에 없는 파일이 게이트를 통과해 배포 후 문제가 됨

### 올바른 절차

```bash
# 예: 릴리스 바운드 파일 확인
git ls-files src/rag/graph.py        # 출력 있으면 tracked
git ls-tree --name-only HEAD src/    # HEAD 트리 기준 목록
```

clean origin/main audit worktree에서 위 명령을 실행해야 최종 확인이 된다.

---

## 4. Dependency-ready rule (upstream pass state 게이트)

의존성이 있는 dispatch는 upstream dispatch가 required pass state에 도달해야만 `ready`로 전이한다.

### 규칙

- 의존성 dispatch의 status가 `complete` 또는 `merged`가 아닌 경우, 하위 dispatch는 `ready` 전이 불가 → `blocked` 유지
- `dispatch_manager.py ready <dispatch_id>` 실행 시 이 게이트를 자동으로 검사한다

### 예시

```
DISPATCH-0002: Env Gate 구현 → status: complete
DISPATCH-0003: depends_on_dispatch_ids: ["DISPATCH-0002"]
  - DISPATCH-0002 complete 이전: status=blocked
  - DISPATCH-0002 complete 이후: ready 명령 → status=ready 전이 가능
```

### history 기록 예시

```json
{"from": "blocked", "to": "ready", "at": "2026-06-15T20:22:00+09:00",
 "by": "claude", "reason": "upstream DISPATCH-0002 complete 확인, 경로 점유 없음"}
```

---

## 5. Merge-after-review loop

PR을 merge한 뒤 선언적으로 "완료"라고 하지 않는다. 아래 루프를 완전히 돌아야 release done이다.

```
1. PR merge (reviewed head commit 기준이 있으면 해당 커밋으로)
2. git fetch <remote>  — 원격 상태를 로컬에 반영
3. clean worktree(origin/main 기준)에서 merge된 커밋 검증
   - git ls-files 로 release-bound 파일 확인
   - 필요한 테스트/체크 실행
4. 검증 통과 → release done 선언
```

### 주의

- `git fetch` 없이 로컬 원격 ref만으로 확인하면 merge 결과가 반영되지 않을 수 있다.
- clean worktree 없이 dirty main에서 검증하면 3항의 위험이 그대로 적용된다.
- reviewed head commit이 명시된 경우, 다른 커밋으로 merge하면 리뷰 결과가 무효가 된다.

---

## 6. Cross-link

불변 task 계약(goal, done_definition, required_checks, scope) 소유 측은:

`../agent-task-packet/SKILL.md`

dispatch는 이 packet을 `packet_path`로 참조하며 내용을 복사하지 않는다.
