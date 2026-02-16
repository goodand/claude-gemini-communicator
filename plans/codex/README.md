# Codex User Context Runner

Claude가 Codex를 호출할 때 사용자 로그인 컨텍스트를 강제하기 위한 스크립트.

## Files

- `plans/codex/run_codex_user_context.sh`

## Why

- Claude 런타임은 사용자 터미널과 다른 환경변수를 가질 수 있음.
- 이 스크립트는 `HOME`을 고정하고 `OPENAI_*` 충돌 변수를 제거해서
  `~/.codex` 로그인 토큰/설정을 일관되게 사용하도록 한다.

## Usage

```bash
chmod +x plans/codex/run_codex_user_context.sh

# 기본 모델: gpt-5.3-codex
plans/codex/run_codex_user_context.sh "Reply exactly: OK"

# 모델 강제
plans/codex/run_codex_user_context.sh --model gpt-5 "Reply exactly: OK"

# fallback 모델 지정
CODEX_FALLBACK_MODEL=gpt-5 plans/codex/run_codex_user_context.sh "Reply exactly: OK"

# 실행 전 확인
plans/codex/run_codex_user_context.sh --dry-run "test"
```

## Notes

- `gpt-5.3-codex` 권한 오류가 감지되면 스크립트가 자동으로 `gpt-5` 재시도를 수행한다.
- 필요 시 `--model` 또는 `CODEX_MODEL`/`CODEX_FALLBACK_MODEL`으로 동작을 제어한다.
