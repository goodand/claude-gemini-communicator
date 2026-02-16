# Codex CLI Manual (Quick)

## Core Commands

```bash
codex
codex --version
codex --help
codex exec --help
```

## Non-interactive Execution

```bash
codex exec "Reply exactly: OK"
codex exec -m gpt-5 "리뷰해줘"
codex exec --json "작업 지시"
codex exec --output-last-message /tmp/last.txt "요약해줘"
```

## Useful Options (`codex exec --help`)

- `-m, --model`: 모델 지정
- `-C, --cd`: 작업 디렉토리 지정
- `--json`: 이벤트를 JSONL로 출력
- `--output-last-message`: 마지막 응답만 파일로 저장
- `--full-auto`: 자동 실행 모드
- `--sandbox [read-only|workspace-write|danger-full-access]`

## Config Path

- `~/.codex/config.toml`

예시:

```toml
model = "gpt-5"
personality = "pragmatic"
```

## Notes

- 모델 이름이 존재해도 계정 권한이 없으면 호출 실패한다.
- 권한 오류 시 먼저 `codex exec -m <model> "Reply exactly: OK"`로 단건 검증한다.

