---
name: cross-agent-bridge
description: Claude Code, Codex CLI, Gemini CLI/SDK를 하나의 CLI로 오케스트레이션할 때 사용한다. 에이전트 간 리뷰 요청(review/codex-review), 출력 파싱(parse), 환경 진단(doctor), 초기 설정(setup)이 필요할 때 트리거한다. 단일 스킬 설치로 상호 피드백 워크플로우를 재사용할 수 있다.
---

# Cross Agent Bridge

에이전트 협업을 위한 **workflow owner**. review, parse, context dispatch의 통합 진입점.

## This skill is the family owner

이 skill은 cross-agent family의 orchestrator입니다. 개별 에이전트를 직접 호출하기 전에 이 skill을 먼저 사용하세요.

### Specialist delegates

| Task | Delegate | When to use directly |
|---|---|---|
| Codex/Gemini/Claude 출력 파싱 | `agent-parser` | parse-only, bridge.py 없이 scripts/parse.py 직접 호출할 때 |
| Gemini SDK/CLI 리뷰 호출 | `gemini-reviewer` | Gemini review-only, bridge.py 없이 scripts/evaluate.py 직접 호출할 때 |
| Gemini CLI 비대화형 실행 | `gemini-cli-context` | raw Gemini CLI execution, bridge.py 우회하고 run_gemini_cli.sh 직접 호출할 때 |
| Codex CLI 비대화형 실행 | `codex-user-context` | raw Codex CLI execution, bridge.py 우회하고 run_codex_user_context.sh 직접 호출할 때 |

**원칙**: full workflow (setup → doctor → review/parse → save)가 필요하면 이 skill을 사용. 단일 atomic 작업만 필요하면 delegate를 직접 호출해도 됨.

## When to use

Use it when:
- 에이전트 간 리뷰 요청/결과 수집이 필요할 때
- 환경 진단(doctor)이나 초기 설정(setup)이 필요할 때
- review → parse → save 전체 워크플로우를 실행할 때
- 어떤 에이전트를 쓸지 판단이 필요할 때

Do not use it for:
- parse-only → `agent-parser` 직접 사용
- Gemini review-only → `gemini-reviewer` 직접 사용
- raw CLI execution만 → `gemini-cli-context` 또는 `codex-user-context` 직접 사용

## Workflow

1. `setup`으로 기본 `config/config.json`과 `.env` 템플릿을 준비한다.
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
