---
name: cross-agent-bridge
description: Claude Code, Codex CLI, Gemini CLI/SDK를 하나의 CLI로 오케스트레이션할 때 사용한다. 에이전트 간 리뷰 요청(review/codex-review), 출력 파싱(parse), 환경 진단(doctor), 초기 설정(setup)이 필요할 때 트리거한다. 단일 스킬 설치로 상호 피드백 워크플로우를 재사용할 수 있다.
---

# Cross Agent Bridge

에이전트 협업을 위한 통합 진입점.

## Workflow

1. `setup`으로 기본 `config.json`과 `.env` 템플릿을 준비한다.
2. `doctor`로 API key, SDK, CLI, 피드백 파일 상태를 점검한다.
3. `review`로 Gemini 리뷰를 호출하거나 `codex-review`로 Codex 리뷰를 호출한다.
4. `parse`로 Codex JSONL / Gemini JSON / Claude transcript를 자동 감지해 요약한다.
5. 필요 시 `--save`로 `gemini_feedback.md`에 결과를 append한다.

## Commands

```bash
# 설정/진단
python3 scripts/bridge.py setup
python3 scripts/bridge.py doctor

# Gemini 리뷰
python3 scripts/bridge.py review --file README.md --format json

# Codex 리뷰
python3 scripts/bridge.py codex-review --file README.md --model gpt-5 --format json

# 파싱 (자동 감지)
python3 scripts/bridge.py parse --file output.jsonl --agent auto --format summary
```

## Requirements

- Python 3.10+
- Gemini 경로: `google-genai` + `GEMINI_API_KEY` 또는 `gemini` CLI
- Codex 경로: `codex` CLI 로그인 상태
