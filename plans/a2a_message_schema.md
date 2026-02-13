# A2A 메시지 스키마 설계안

## 목적

현재 Claude↔Gemini 간 통신은 단순 문자열(프롬프트 텍스트 → 응답 텍스트)입니다.
이를 **구조화된 JSON 프로토콜**로 전환하여:
- 요청/응답의 타입과 메타데이터를 명확히 전달
- 평가 결과를 구조적으로 파싱 가능하게 함
- 향후 Agent Teams, Gemini Extension의 통신 기반 마련

## 현재 상태 (비구조적)

```
Claude → Gemini:
  "다음 문서를 평가해줘:\n- 논리적 일관성\n- 실현 가능성\n...\n\n파일 경로: plans/test.md\n\n파일 내용:\n..."

Gemini → Claude:
  "### 논리적 일관성\n매우 높음...\n### 실현 가능성\n..."
```

문제점:
- 응답 파싱이 불안정 (마크다운 형식에 의존)
- 메타데이터 없음 (모델명, 소요시간, 토큰 수 등)
- 에러와 정상 응답 구분이 문자열 prefix에 의존

## 설계안: A2A Message Protocol v1

### 요청 스키마 (Claude → Gemini)

```json
{
  "a2a_version": "1.0",
  "message_type": "evaluation_request",
  "request_id": "uuid-v4",
  "timestamp": "2026-02-12T11:30:00+09:00",
  "source": {
    "agent": "claude",
    "hook": "PostToolUse"
  },
  "payload": {
    "task": "evaluate_document",
    "file_path": "plans/test.md",
    "content": "문서 전체 내용...",
    "criteria": ["논리적 일관성", "실현 가능성", "누락된 고려사항", "개선 제안"]
  },
  "config": {
    "response_format": "structured",
    "language": "ko",
    "max_length": 2048
  }
}
```

### 응답 스키마 (Gemini → Claude)

```json
{
  "a2a_version": "1.0",
  "message_type": "evaluation_response",
  "request_id": "uuid-v4 (요청과 동일)",
  "timestamp": "2026-02-12T11:30:05+09:00",
  "source": {
    "agent": "gemini",
    "model": "gemini-2.5-flash"
  },
  "status": "success",
  "payload": {
    "evaluation": {
      "논리적 일관성": {
        "score": "높음",
        "detail": "목표와 구현 단계가 명확하게 연결됨"
      },
      "실현 가능성": {
        "score": "보통",
        "detail": "3주 일정은 촉박할 수 있음"
      },
      "누락된 고려사항": [
        "보안: 비밀번호 해싱",
        "에러 처리 방안"
      ],
      "개선 제안": [
        "API 명세 구체화",
        "테스트 케이스 상세화"
      ]
    },
    "summary": "전반적으로 양호하나 보안과 일정 부분에서 보완 필요"
  },
  "metadata": {
    "duration_ms": 3200,
    "input_tokens": 1500,
    "output_tokens": 800
  }
}
```

### 메시지 타입 정의

| message_type | 방향 | 설명 |
|---|---|---|
| `evaluation_request` | Claude → Gemini | 문서/계획 평가 요청 |
| `evaluation_response` | Gemini → Claude | 평가 결과 응답 |
| `classification_request` | Claude → Gemini | Plan 여부 분류 요청 |
| `classification_response` | Gemini → Claude | 분류 결과 ("예"/"아니오") |
| `error` | 양방향 | 에러 응답 |

### 에러 응답 스키마

```json
{
  "a2a_version": "1.0",
  "message_type": "error",
  "request_id": "uuid-v4",
  "status": "error",
  "error": {
    "code": "RATE_LIMITED",
    "message": "429 Too Many Requests",
    "retryable": true,
    "retry_after_seconds": 30
  }
}
```

## 구현 범위

### a2a_bridge.py 변경
1. `build_a2a_request()` — 요청 JSON 생성
2. `parse_a2a_response()` — 응답 JSON 파싱 (Gemini가 JSON으로 응답하도록 프롬프트에 스키마 포함)
3. `call_gemini()` 내부에서 A2A 래핑/언래핑

### config.json 변경
- `"a2a_schema_enabled": true` 추가 (false면 기존 문자열 모드 유지)

### 프롬프트 변경
- 평가 프롬프트에 "반드시 다음 JSON 형식으로 응답하라" 지시 추가
- JSON 스키마를 프롬프트에 포함

### gemini_feedback.md 형식
- A2A 모드: JSON에서 `summary` + 각 criteria의 `detail`을 마크다운으로 변환하여 기록
- 비A2A 모드: 기존 형식 유지

### 하위 호환성
- `a2a_schema_enabled: false` (기본값)로 기존 동작 유지
- Phase 2까지의 모든 기능과 충돌 없음
