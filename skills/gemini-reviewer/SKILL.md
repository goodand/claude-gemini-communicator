---
name: gemini-reviewer
description: Gemini에게 코드나 문서 리뷰를 요청할 때 사용한다. 코드 파일(.py, .js, .ts 등) 작성/수정 후, 설계 문서나 계획 완성 후, 또는 사용자가 "리뷰해줘", "평가해줘", "검토해줘"라고 요청했을 때 트리거한다. SDK 우선 호출(Exponential Backoff 재시도) + CLI 폴백 이중화. text/json 출력 지원.
---

# Gemini Reviewer

Gemini에 코드/문서 리뷰를 요청하는 크로스 에이전트 스킬.

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
