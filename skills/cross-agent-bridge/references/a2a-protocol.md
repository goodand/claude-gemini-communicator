# A2A Protocol (v1.0)

## Request Envelope

```json
{
  "a2a_version": "1.0",
  "message_type": "evaluation_request",
  "request_id": "uuid",
  "timestamp": "ISO-8601",
  "source": { "agent": "claude", "hook": "manual|hook-name" },
  "payload": { "content": "...", "prompt": "..." }
}
```

## Response Envelope

```json
{
  "a2a_version": "1.0",
  "message_type": "evaluation_response",
  "request_id": "uuid",
  "timestamp": "ISO-8601",
  "source": { "agent": "gemini" },
  "status": "success",
  "payload": {
    "evaluation": {
      "논리적 일관성": { "score": "높음|보통|낮음", "detail": "..." },
      "실현 가능성": { "score": "높음|보통|낮음", "detail": "..." },
      "누락된 고려사항": ["..."],
      "개선 제안": ["..."]
    },
    "summary": "..."
  }
}
```

## Parsing Rule

- 순서: strict JSON 파싱 -> fenced code block 내부 JSON 파싱 -> 잘린 JSON 복구 시도.
- 파싱 실패 시 `payload.raw_text`로 강등 저장.
