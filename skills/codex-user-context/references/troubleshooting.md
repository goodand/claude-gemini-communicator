# Troubleshooting

## 1) 모델 권한 오류

증상:

- `does not exist or you do not have access`
- `not supported when using Codex with a ChatGPT account`

확인:

```bash
codex exec -m gpt-5.3-codex "Reply exactly: OK"
codex exec -m gpt-5 "Reply exactly: OK"
```

대응:

- 5.3-codex가 실패하고 gpt-5가 성공하면 권한/플랜 이슈다.
- 운영 기본 모델을 접근 가능한 모델로 고정한다.
- `run_codex_user_context.sh`는 5.3 권한 오류 문구를 감지하면 `gpt-5`로 자동 재시도한다.

## 2) 사용자와 에이전트 실행 결과가 다름

원인:

- HOME 또는 환경변수 컨텍스트가 다를 수 있음.
- 작업 디렉토리 해석이 달라 프로젝트 루트가 어긋날 수 있음.

대응:

```bash
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --dry-run "test"
```

- `HOME`, `MODEL`, `CMD`를 확인한 뒤 실제 실행한다.
- 필요 시 `--project /path/to/repo`를 명시한다.

## 3) 환경변수 충돌

원인:

- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_ORG_ID`가 인증 경로를 바꿈.

대응:

- 래퍼 스크립트가 위 변수를 자동으로 `unset`한다.
- 직접 실행 시에도 동일하게 unset 후 테스트한다.
