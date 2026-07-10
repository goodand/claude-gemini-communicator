---
name: gemini-reviewer
description: Gemini SDK/CLI로 코드나 문서 리뷰를 요청할 때 사용한다. Gemini review-only 작업에 직접 사용. full workflow(setup → review → parse → save)나 Codex 리뷰가 필요하면 cross-agent-bridge를 먼저 사용하라.
---

# Gemini Reviewer

`cross-agent-bridge` family의 **Gemini review specialist**. Gemini 리뷰만 필요할 때 직접 호출한다.

> **Full workflow가 필요하면 `cross-agent-bridge`를 먼저 사용하세요.** 이 skill은 Gemini review-only direct call 전용입니다.

## 워크플로우

1. 대상 파일 경로 또는 stdin으로 내용을 전달
2. 파일 확장자로 code/doc 모드 자동 감지 (--mode로 수동 지정 가능)
3. Gemini SDK 호출 (429/5xx 시 Exponential Backoff 재시도, 최대 3회)
4. SDK 실패 시 Gemini CLI 폴백
5. 결과를 stdout 출력, --save로 gemini_feedback.md 저장

## 사용법

```bash
# 파일 리뷰 (모드 자동 감지)
python3 scripts/evaluate.py --file <파일경로>

# 코드 리뷰 명시
python3 scripts/evaluate.py --file code.py --mode code

# JSON 출력
python3 scripts/evaluate.py --file code.py --format json

# stdin + 커스텀 프롬프트
echo "내용" | python3 scripts/evaluate.py --prompt "보안 취약점 분석"

# 결과 저장
python3 scripts/evaluate.py --file plan.md --save
```

## Codex 연동

Codex CLI의 notify hook으로 `codex_notify.py`를 등록하면 agent-turn-complete 시 Plan 감지 -> 자동 평가.

```toml
# ~/.codex/config.toml
notify = ["python3", "/path/to/skills/gemini-reviewer/scripts/codex_notify.py"]
```

## 사전 요구사항

- `GEMINI_API_KEY` 환경변수 (또는 .env 파일)
- `google-genai` 패키지
