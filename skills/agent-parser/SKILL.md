---
name: agent-parser
description: Codex JSONL, Gemini JSON, Claude transcript 출력을 파싱하여 구조화 요약을 생성할 때 사용한다. 에이전트 세션 분석, 토큰 사용량 확인, 명령 실행 결과 집계, 대화 흐름 요약이 필요할 때 트리거한다. 자동 포맷 감지로 --agent auto 지원.
---

# Agent Parser

Codex, Gemini, Claude 출력을 통합 파싱하는 크로스 에이전트 스킬.

## 지원 포맷

| 에이전트 | 입력 형식 | 시그니처 키 |
|---------|----------|------------|
| Codex   | JSONL    | `type: thread.started/item.started` |
| Gemini  | JSON     | `stats` + `response` |
| Claude  | JSONL    | `type: user/assistant` + `message` |

## 워크플로우

1. --file 또는 stdin으로 에이전트 출력을 전달
2. 자동 감지: 첫 유효 JSON 라인의 시그니처 키 분석
3. 해당 파서로 구조화 파싱 (이벤트 집계, 토큰 통계 등)
4. summary(텍스트) 또는 json 형식으로 출력

## 사용법

```bash
# 자동 감지
python3 scripts/parse.py --file output.jsonl

# 에이전트 명시
python3 scripts/parse.py --file codex.jsonl --agent codex
python3 scripts/parse.py --file gemini.json --agent gemini
python3 scripts/parse.py --file transcript.jsonl --agent claude

# JSON 출력
python3 scripts/parse.py --file output.jsonl --format json

# Claude: 마지막 N개 메시지만
python3 scripts/parse.py --file transcript.jsonl --agent claude --last-n 10

# 결과 저장
python3 scripts/parse.py --file output.jsonl --save
```

## 사전 요구사항

- Python 3.10+
- 외부 패키지 불필요 (표준 라이브러리만 사용)
