---
name: gemini-cli-context
description: Claude가 Gemini CLI를 비대화형으로 호출하여 코드 리뷰, 문서 평가, 아키텍처 비판 등을 수행한다. API 키 없이 Google OAuth 인증만으로 동작하며, 다른 프로젝트에 cp -r로 설치 가능하다.
---

# Gemini CLI Context

Claude가 Gemini CLI를 비대화형(headless) 모드로 호출한다.
API 키 불필요 — Google OAuth 인증(gemini CLI 로그인)만 있으면 동작.

## Workflow

1. `scripts/run_gemini_cli.sh`로 Gemini CLI를 호출한다.
2. `-p` (prompt) 모드로 비대화형 실행, 결과를 stdout으로 반환한다.
3. 파일 경로를 지정하면 파일 내용을 stdin으로 전달한다.
4. `--model`로 모델을 변경할 수 있다 (기본: gemini-2.5-flash).
5. `--dry-run`으로 실행 전 명령을 미리 확인할 수 있다.
6. `--yolo` 모드로 도구 사용 자동 승인이 가능하다.

## Commands

```bash
# 기본 (코드 리뷰)
zsh skills/gemini-cli-context/scripts/run_gemini_cli.sh "이 코드를 리뷰해줘" --file src/core/router.py

# 문서 평가
zsh skills/gemini-cli-context/scripts/run_gemini_cli.sh "이 설계안을 비판해줘" --file plans/project_handoff.md

# 프롬프트만 (파일 없이)
zsh skills/gemini-cli-context/scripts/run_gemini_cli.sh "Python에서 파일 락의 크로스 플랫폼 방법은?"

# 모델 변경
zsh skills/gemini-cli-context/scripts/run_gemini_cli.sh --model gemini-2.5-pro "심층 분석해줘" --file src/cli.py

# 실행 전 확인
zsh skills/gemini-cli-context/scripts/run_gemini_cli.sh --dry-run "test"

# stdin 파이프
cat src/core/router.py | zsh skills/gemini-cli-context/scripts/run_gemini_cli.sh "이 코드를 리뷰해줘"
```

## 다른 프로젝트에 설치

```bash
cp -r skills/gemini-cli-context /path/to/other-project/.claude/skills/
```
