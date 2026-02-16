---
name: codex-user-context
description: Claude가 Codex CLI를 호출할 때 사용자 로그인 인증 컨텍스트(HOME, ~/.codex, 환경변수)를 강제해야 할 때 사용한다. Codex 모델 권한 오류, 계정/세션 불일치, 쉘별 동작 차이가 발생할 때 트리거한다. run_codex_user_context.sh로 동일 컨텍스트 실행을 표준화하고, 필요 시 references의 Codex CLI 메뉴얼/트러블슈팅을 참조한다.
---

# Codex User Context

Claude가 Codex를 호출할 때 사용자 로그인 컨텍스트를 일관되게 강제한다.

## Workflow

1. `scripts/run_codex_user_context.sh`로 Codex를 호출한다.
2. 기본 모델은 `gpt-5.3-codex`를 사용한다.
3. `gpt-5.3-codex` 권한 오류 시 스크립트가 자동으로 `gpt-5`로 fallback한다.
4. 문제 재현 시 `--dry-run`으로 HOME/모델/명령을 먼저 확인한다.
5. 상세 옵션/오류는 `references/codex-cli-manual.md`와 `references/troubleshooting.md`를 확인한다.
6. 경로 해석은 `--project` 우선, 없으면 git root, 마지막으로 현재 디렉토리를 사용한다.

## Commands

```bash
# 기본(로그인 컨텍스트 + gpt-5.3-codex)
zsh skills/codex-user-context/scripts/run_codex_user_context.sh "Reply exactly: OK"

# 모델 fallback
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --model gpt-5 "Reply exactly: OK"

# fallback 모델 지정
CODEX_FALLBACK_MODEL=gpt-5 zsh skills/codex-user-context/scripts/run_codex_user_context.sh "Reply exactly: OK"

# 실행 전 검증
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --dry-run "test prompt"
```
