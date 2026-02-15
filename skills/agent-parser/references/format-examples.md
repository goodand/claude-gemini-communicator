# 에이전트 출력 포맷 예시

## Codex JSONL (`codex exec --json`)

```json
{"type":"thread.started","thread_id":"thread_abc123"}
{"type":"item.started","item":{"type":"reasoning","text":"분석 중..."}}
{"type":"item.started","item":{"type":"command_execution","id":"cmd_1","command":"ls -la"}}
{"type":"item.completed","item":{"type":"command_execution","id":"cmd_1","command":"ls -la","exit_code":0,"aggregated_output":"total 16\ndrwxr-xr-x ..."}}
{"type":"item.started","item":{"type":"agent_message","text":"작업 완료했습니다."}}
{"type":"turn.completed","usage":{"input_tokens":1500,"cached_input_tokens":200,"output_tokens":300}}
```

감지 기준: `type` 필드가 `thread.started`, `item.started`, `item.completed`, `turn.completed` 중 하나.

## Gemini JSON (headless)

```json
{
  "session_id": "session_xyz",
  "response": "분석 결과입니다...",
  "stats": {
    "models": {
      "gemini-2.5-flash": {
        "api": {"totalRequests": 5, "totalErrors": 0, "totalLatencyMs": 12000},
        "tokens": {"input": 3000, "prompt": 500, "candidates": 1200, "total": 4700}
      }
    },
    "tools": {
      "totalCalls": 3, "totalSuccess": 3, "totalFail": 0,
      "byName": {"readFile": {"count": 2, "success": 2}}
    },
    "files": {"totalLinesAdded": 45, "totalLinesRemoved": 12}
  }
}
```

감지 기준: `stats` + `response` 키 동시 존재.

## Claude Transcript JSONL

```json
{"type":"user","sessionId":"sess_001","message":{"role":"user","content":"코드를 분석해줘"}}
{"type":"assistant","sessionId":"sess_001","message":{"role":"assistant","content":[{"type":"thinking","text":"..."},{"type":"text","text":"분석 결과..."},{"type":"tool_use","name":"Read","input":{"file_path":"..."}}]}}
```

감지 기준: `type`이 `user` 또는 `assistant`이고 `message` 키 존재.
