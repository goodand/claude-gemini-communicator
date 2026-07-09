# Subagent Audit and Remote Baseline Patterns

작성일: 2026-06-15-20-22

---

## 1. Subagent Audit 패턴 (누락 범위 감사)

### 핵심 원칙

범위(scope)가 불명확하거나 누락된 게이트를 감사할 때는 **concern 단위로 subagent를 fan-out**한다.
하나의 subagent가 모든 게이트를 처리하면 커버리지가 흐려진다. 각 concern 하나당 subagent 하나.

### 판정 결과 레이블

각 subagent는 반드시 세 값 중 하나로 판정을 반환한다.

| 판정 | 의미 |
|------|------|
| `PASS` | 해당 concern 완전히 커버됨 |
| `FAIL` | 결함 또는 누락 — remediation owner + evidence path 필수 |
| `PASS_WITH_RISK` | 현재는 통과하나 위험 요소 존재 — 조건 명시 필수 |

### FAIL 처리 규칙

`FAIL` 판정은 반드시 다음 두 가지를 포함해야 한다.

1. **remediation owner** — 누가 수정할 책임인가 (역할명 또는 파일 경로)
2. **evidence path** — 실제 결함 위치 (파일:줄번호, 실행 가능한 명령, 또는 diff 출력)

`FAIL` 판정에 evidence path가 없으면 미검증 상태로 처리한다.

### Coverage-Matrix 레이아웃

감사 결과는 아래 형태의 coverage matrix로 정리한다.
각 행은 concern/gate, 각 열은 커버리지 상태.

```
| Concern/Gate            | Validator Coverage | Test Coverage | Audit Status    |
|-------------------------|--------------------|---------------|-----------------|
| auth token validation   | PARTIAL            | WEAK          | FAIL            |
| schema migration safety | PASS               | PASS          | PASS            |
| retry on 5xx            | WEAK               | PARTIAL       | PASS_WITH_RISK  |
| idempotency keys        | PASS               | PASS          | PASS            |
```

상태 레이블: `WEAK` / `PARTIAL` / `PASS` / `FAIL`

### Fan-out 실행 예시

```
Orchestrator
├── subagent-A → concern: schema validation       → verdict: PASS
├── subagent-B → concern: auth boundary           → verdict: FAIL
│               evidence: src/auth.py:L42, cmd: pytest tests/test_auth.py -k boundary
│               owner: backend-team
├── subagent-C → concern: retry logic coverage    → verdict: PASS_WITH_RISK
│               risk: 503 not covered
└── subagent-D → concern: migration rollback path → verdict: PASS
```

---

## 2. Branch/PR Sequencing

### Merge 전 분류

현재 브랜치와 PR 의존성을 merge 실행 **전에** 분류한다.

```
[ Product code PR ]   → 기능 변경, 로직 수정
[ Docs/artifact PR ]  → 참조 문서, 체크리스트, 설정 파일
[ Release-gate PR ]   → 버전 태깅, CHANGELOG, 배포 설정
```

의존성이 있는 경우 순서: product code → docs/artifact → release-gate.
세 종류를 하나의 PR에 혼합하면 rollback 경계가 불명확해진다.

### 파괴적 정리 전 plan-only audit

`git worktree remove --force`, 광범위 staging (`git add -A`), 브랜치 일괄 삭제 등
**파괴적 작업 실행 전**에 반드시 plan-only audit을 실행한다.

```bash
# 예시: 삭제 전 영향 범위 확인 (실제 삭제 없음)
git worktree list
git branch --merged main | grep -v main
# 위 출력을 검토 후 삭제 명령 실행
```

plan-only audit은 실제 변경 없이 영향 범위만 출력한다. 확인 후 실행.

---

## 3. Remote Baseline Loop

외부 기준(origin/main)을 신뢰 소스로 삼아 검증하는 반복 루프.

### 단계별 절차

```
1. 깨끗한 audit worktree 생성 (origin/main 기준)
   git worktree add /tmp/<repo>-origin-main-audit origin/main

2. audit worktree에서 validator + 테스트 실행
   cd /tmp/<repo>-origin-main-audit
   python3 scripts/quick_validate.py .
   pytest tests/

3. PR merge
   git merge <pr-branch>

4. git fetch (remote 최신화)
   git fetch origin

5. audit worktree 재생성 또는 갱신
   git worktree remove /tmp/<repo>-origin-main-audit
   git worktree add /tmp/<repo>-origin-main-audit origin/main

6. validator + 테스트 재실행 → merge 전후 비교
```

### 핵심 규칙

- **truth source**: `/tmp/<repo>-origin-main-audit` 같은 clean audit worktree
- **dirty main은 truth source가 아니다** — 로컬 수정이 섞여 있을 수 있음
- audit worktree 경로는 일관성 있게 유지 (다른 작업자와 공유 가능하도록 명명)
- `git fetch` 없이 audit worktree를 재사용하면 stale 상태가 된다

---

## 4. WARNING: Subagent Self-Report는 증거가 아니다

> **자가 보고(self-report)만으로는 PASS 판정을 수락하지 않는다.**

subagent가 "완료했습니다" 또는 "PASS입니다"라고 보고하더라도,
**파일 경로, 실행 명령, 또는 diff 출력** 중 하나를 제시하지 않으면
해당 판정은 **미검증(unverified)** 으로 처리한다.

### 수락 가능한 evidence 형태

```
# 파일:줄번호
src/validator.py:L88 — assertion 추가됨

# 실행 가능한 명령
pytest tests/test_validator.py -k test_boundary_pass --tb=short

# diff 출력
--- a/src/auth.py
+++ b/src/auth.py
@@ -40,6 +40,8 @@
+    if token is None:
+        raise ValueError("token required")
```

### 수락 불가 형태

```
# 증거 없는 자가 보고 — 미검증으로 처리
"검토했고 문제 없습니다."
"PASS 확인했습니다."
"테스트 통과했습니다." (명령/출력 없이)
```

---

## 5. Cross-Links

이 문서는 다음 specialist skill과 연계된다.

- 직접 호출 패킷(immutable contract) 설정: `../agent-task-packet/SKILL.md`
- 런타임 dispatch 상태 관리: `../codex-worktree-dispatch/SKILL.md`

범위 분리:
- 이 문서 → audit pattern, PR sequencing, remote baseline loop
- `agent-task-packet` → 패킷 구조, 범위 계약, 완료 조건
- `codex-worktree-dispatch` → dispatch 상태, branch/worktree 연결, queued→merged 전환
