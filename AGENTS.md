# AGENTS.md — Claude-Gemini Communicator

## Project Overview

AI 코딩 에이전트가 코드/문서를 작성하면 Gemini가 자동으로 평가하는 크로스-에이전트 협업 시스템.

## Available Skills

### gemini-reviewer
코드나 문서를 Gemini에게 리뷰받는 스킬.

```bash
# 파일 리뷰 (확장자로 code/doc 자동 감지)
python3 skills/gemini-reviewer/scripts/evaluate.py --file <path>

# 코드 리뷰 명시
python3 skills/gemini-reviewer/scripts/evaluate.py --file <path> --mode code

# 커스텀 프롬프트
python3 skills/gemini-reviewer/scripts/evaluate.py --file <path> --prompt "보안 취약점 분석"

# 결과 저장
python3 skills/gemini-reviewer/scripts/evaluate.py --file <path> --save
```

결과는 stdout 출력 + `--save` 시 `gemini_feedback.md`에 append.

## Key Files

| File | Role |
|---|---|
| `scripts/a2a_bridge.py` | Core orchestrator (Gemini SDK/CLI dual mode) |
| `scripts/config.json` | Configuration |
| `skills/gemini-reviewer/` | Cross-platform Gemini review skill |
| `gemini_feedback.md` | Gemini feedback log (append-only) |

## Conventions

- Korean comments, English identifiers
- All scripts guarantee `exit(0)` — never block the caller
- `gemini_feedback.md` is auto-generated, avoid manual edits
- API keys in `.env` only, never hardcoded

## Environment

- `GEMINI_API_KEY` required (set in `.env`)
- Python 3.10+, `google-genai` package
