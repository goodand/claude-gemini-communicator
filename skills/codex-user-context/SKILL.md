---
name: codex-user-context
description: cross-agent-bridge family의 raw Codex CLI executor. Codex CLI를 headless로 실행하고 prompt/file/session/sandbox를 제어하는 전용 specialist. bridge.py 리뷰나 full workflow는 cross-agent-bridge를 사용하라.
---

# Codex User Context

`cross-agent-bridge` family의 **raw Codex CLI execution specialist**.

> **Full workflow가 필요하면 `cross-agent-bridge`를 먼저 사용하세요.** 이 skill은 Codex CLI 직접 실행 전용입니다.

Claude가 Codex CLI를 비대화형(headless) 모드로 호출한다.
API 키 불필요 — OpenAI 계정 로그인만 있으면 동작.

## Workflow

1. `scripts/run_codex_user_context.sh`로 Codex를 호출한다.
2. 기본 모델은 `gpt-5.3-codex`, 권한 오류 시 `gpt-5`로 자동 fallback.
3. `--file`로 파일 내용을 프롬프트에 첨부할 수 있다.
4. `--sandbox danger-full-access`로 네트워크 접근을 허용한다.
5. `--save`로 결과를 `plans/codex/codex_feedback.md`에 기록한다.
6. `--full-auto`로 도구 사용 자동 승인 모드를 활성화한다.
7. 경로 해석은 `--project` 우선, 없으면 git root, 마지막으로 현재 디렉토리.

## Commands

```bash
# 기본 (로그인 컨텍스트 + gpt-5.3-codex)
zsh skills/codex-user-context/scripts/run_codex_user_context.sh "Reply exactly: OK"

# 세션 이어서 실행 (기억 연속성 유지)
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --resume SESSION_ID "프롬프트"

# 환경변수로 고정 세션 지정
export CODEX_RESUME_SESSION=SESSION_ID
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --resume "프롬프트"

# 코드 리뷰 (파일 첨부)
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --file src/app.py "이 코드를 리뷰해줘"

# stdin 파이프
cat src/app.py | zsh skills/codex-user-context/scripts/run_codex_user_context.sh "리뷰해줘"

# 네트워크 접근 허용
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --sandbox danger-full-access "외부 API 조사해줘"

# 자동 실행 + 피드백 기록
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --full-auto --save "설계안 작성해줘"

# 모델 변경
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --model gpt-5 "코드 리뷰해줘"

# 실행 전 검증
zsh skills/codex-user-context/scripts/run_codex_user_context.sh --dry-run "test"
```

## Sandbox Modes

- `read-only` — 기본값, 네트워크 차단, 파일 읽기만
- `workspace-write` — 작업 디렉토리 쓰기 허용
- `danger-full-access` — 네트워크 포함 전체 접근

## 다른 프로젝트에 설치

```bash
cp -r skills/codex-user-context /path/to/other-project/.claude/skills/
```
