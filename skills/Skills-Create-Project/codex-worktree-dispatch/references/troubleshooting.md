# Troubleshooting — codex-worktree-dispatch

## CASE-001: locked_paths에 path traversal (`..`) 허용

**증상**: `locked_paths: ["../secret"]`가 `validate` exit 0으로 통과
**원인**: `validate_dispatch()`에서 locked_paths의 빈 값만 검사하고 `..`/절대경로 검증 없음
**해결**: locked_paths 각 항목에 `".."` 포함 또는 `/` 시작 시 에러 반환
**교훈**: dispatch-fields.md에 "경로 정규화: `..` 및 symlink 방지"라고 명시했지만 validate에 구현하지 않으면 문서만의 약속. 문서에 규칙을 쓰면 반드시 validate에도 반영할 것.

## CASE-002: retry 초과 시 _do_transition이 상태를 먼저 변경 후 예외

**증상**: `failed→running` 전이에서 `retry_count > max_retries`일 때 ValueError가 나지만, 객체의 status가 이미 `running`으로, retry_count가 이미 증가한 상태로 오염됨
**원인**: `_do_transition()`에서 상태/history 변경 코드가 retry_count 검사보다 먼저 실행
**해결**: retry_count 초과 검사를 상태 변경 **전**으로 이동. 검사 통과 후에만 status/history/retry_count 변경
**교훈**: 예외를 던질 수 있는 검증은 반드시 부수효과(side-effect) 전에 수행. "검증 → 변경" 순서를 지켜야 rollback이 필요 없다.

## CASE-003: locked_paths에 symlink가 통과됨

**증상**: `locked_paths: ["src_link"]`(symlink)가 validate를 통과하여, 실제 대상 경로와 다른 경로를 lock할 수 있음
**원인**: validate_dispatch()에서 `..`와 절대경로만 검사하고 symlink 여부를 확인하지 않음. dispatch-fields.md:94에 "symlink 방지"라고 명시되어 있었으나 미구현
**해결**: `os.path.exists(resolved) and os.path.islink(resolved)` 검사 추가
**교훈**: CASE-001과 동일 패턴 — 문서에 규칙을 썼으면 validate에도 반드시 구현. `..`, 절대경로, symlink는 경로 정규화 3종 세트로 항상 함께 검증

## CASE-004: dirty-main false positive (릴리스/테스트 결과 오염)

**증상**: 릴리스 검증 또는 테스트를 main worktree에서 실행했을 때 오해를 낳는 결과가 나온다. 예: 필요한 테스트 파일이 없다고 표시되거나 collected 0이 반환되거나, 반대로 local-only 파일이 있는 것처럼 보여 체크가 통과됨
**원인**: main worktree가 `origin/main`과 다른 상태(uncommitted 변경, 미추적 파일, 스테이징된 패치 등)로 diverge되어 있어 검증 결과가 실제 릴리스 상태를 반영하지 않음
**해결**: 릴리스 검증과 테스트는 `origin/main`(또는 대상 base 커밋)을 체크아웃한 clean audit worktree에서 실행한다. 예: `git worktree add /tmp/<repo>-origin-main-audit origin/main`
**교훈**: dirty main은 참조 전용(reference-only)이다. merge-after-review 루프에서 clean worktree 검증 단계를 건너뛰면 오탐(false-positive/negative)이 발생한다.

## CASE-005: local-file-exists but untracked (Path.exists()로 릴리스 바운드 오판)

**증상**: 릴리스 바운드로 선언한 파일이 `Path.exists()` 체크는 통과하지만 실제 릴리스에는 포함되지 않음. 배포 후 파일 누락 오류가 발생하거나, required-paths 게이트가 false-pass됨
**원인**: 파일이 dirty worktree에 untracked 상태로 존재한다. `Path.exists()`는 파일시스템 존재만 확인하므로 git 추적 여부를 알 수 없음
**해결**: 릴리스 바운드 파일 확인은 `git ls-files <path>` (출력이 비면 untracked) 또는 `git ls-tree --name-only <commit> <path>`로 대상 커밋 트리 기준으로 수행한다. clean origin/main audit worktree에서 실행해야 최종 확인이 된다
**교훈**: `Path.exists()` ≠ 릴리스 증명. release-bound 경로 게이트는 반드시 `git ls-files` 또는 커밋 트리 기준으로 동작해야 한다.
