# Worktree-Parallel Troubleshooting Cases

## CASE-001: spawn 성공 메시지인데 실제 worktree 미생성

- **증상**: `[OK] worktree 생성 완료` 출력됐지만 `.worktrees/` 비어있음
- **원인**: `run_git()`이 git 에러를 stderr에만 출력하고 returncode를 무시. 상태 파일은 생성됨
- **해결법**: `run_git()` 반환값을 `(returncode, stdout)` 튜플로 변경. `rc != 0`이면 건너뛰고 `sys.exit(1)` (2026-03-15 수정 완료)
- **예방책**: 모든 git wrapper는 반드시 returncode 확인

## CASE-002: cleanup이 고아 상태 파일을 정리하지 않음

- **증상**: worktree가 없는데 `.agent-status/*.json`이 남아있음
- **원인**: `cleanup`이 `.worktrees/` 디렉토리만 순회. 상태 파일만 남은 경우 누락
- **해결법**: cleanup에 고아 상태 파일 정리 로직 추가 (2026-03-15 수정 완료)
- **예방책**: cleanup은 worktree + 상태 파일 + branch를 원자적으로 정리

## CASE-003: Codex sandbox에서 git worktree 생성 실패

- **증상**: `fatal: cannot lock ref 'refs/heads/feat/test-a': unable to create directory`
- **원인**: Codex sandbox (seatbelt/workspace-write)에서 `.git/refs/heads/` 하위 디렉토리 생성 권한 제한
- **해결법**: worktree 생성은 sandbox 밖에서 사전 실행. Codex에게는 읽기 전용 명령만 할당
- **예방책**: Codex에게 `spawn` 대신 `status`, `validate`, `merge-check` 할당

## CASE-004: merge-check가 in_progress에서 실패

- **증상**: `merge-check` 실행 시 exit 1 — "status=in_progress (complete 필요)"
- **원인**: 의도된 동작. merge-check는 status=complete만 허용
- **해결법**: 작업 완료 후 상태 파일의 status를 "complete"로 변경 후 실행
- **예방책**: merge-check 전 반드시 `validate`로 상태 확인

---

## 케이스 추가 템플릿

```markdown
## CASE-XXX: [짧은 제목]

- **증상**: [에러 메시지 또는 관찰된 동작]
- **원인**: [근본 원인]
- **해결법**: [구체적 해결 방법]
- **예방책**: [재발 방지 방법]
```

## CASE-005: subagent self-report without evidence

- **증상**: subagent가 "PASS 확인", "완료했습니다" 등 결과를 보고하지만 파일 경로, 명령, diff 출력 중 어느 것도 제시하지 않음
- **원인**: 자가 보고(self-report)는 실제 실행 결과와 다를 수 있음. subagent가 수행했다고 주장하는 것과 실제로 수행한 것은 별개
- **해결법**: 판정을 미검증(unverified)으로 표기. evidence path (파일:줄번호, 실행 명령, 또는 diff 출력)를 요청한 뒤 수락
- **예방책**: fan-out 패킷에 "모든 PASS/FAIL은 evidence path를 포함해야 함" 조건을 명시. `FAIL` 판정은 remediation owner + evidence path 없이 수락 금지

## CASE-006: editing dirty main directly (release work)

- **증상**: main 브랜치에서 직접 코드 수정 후 release 작업 진행. 로컬 변경이 섞인 상태에서 validator/테스트 실행
- **원인**: main에 uncommitted 또는 unreviewed 변경이 있으면 audit 결과를 신뢰할 수 없음. dirty main은 truth source가 아님
- **해결법**: `git worktree add /tmp/<repo>-origin-main-audit origin/main`으로 clean audit worktree를 생성. validator와 테스트를 해당 worktree에서 실행
- **예방책**: release 작업은 반드시 clean worktree (origin/main 기준) 에서 검증. main 직접 수정 금지 — worktree에서 구현 후 merge만 수행
