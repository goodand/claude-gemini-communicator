"""A2A 구조화된 메시지 프로토콜.

a2a_bridge.py의 A2A 관련 함수들을 분리한 모듈.
JSON 요청/응답 빌드, 파싱, 마크다운 변환, 잘린 JSON 복구.
"""

import json
import uuid
from datetime import datetime, timezone

A2A_VERSION = "1.0"

_A2A_RESPONSE_INSTRUCTION = """반드시 아래 JSON 형식으로만 응답하라. JSON 외 다른 텍스트를 포함하지 마라.
각 detail과 항목은 반드시 1-2문장 이내로 간결하게 작성하라. 절대 긴 설명을 하지 마라.

{
  "evaluation": {
    "논리적 일관성": {"score": "높음|보통|낮음", "detail": "1문장"},
    "실현 가능성": {"score": "높음|보통|낮음", "detail": "1문장"},
    "누락된 고려사항": ["항목1", "항목2"],
    "개선 제안": ["제안1", "제안2"]
  },
  "summary": "한 줄 요약"
}"""

_A2A_CLASSIFICATION_INSTRUCTION = """반드시 아래 JSON 형식으로만 응답하라. JSON 외 다른 텍스트를 포함하지 마라.

{"is_plan": true 또는 false}"""


def build_a2a_request(message_type: str, payload: dict,
                      hook_source: str = "unknown") -> dict:
    """A2A 요청 메시지를 생성한다."""
    return {
        "a2a_version": A2A_VERSION,
        "message_type": message_type,
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {"agent": "claude", "hook": hook_source},
        "payload": payload,
    }


def _try_parse_json(text: str):
    """JSON 파싱을 시도한다. 실패 시 None."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _try_repair_json(text: str):
    """잘린 JSON을 복구 시도한다.

    토큰 제한으로 잘린 응답에서 닫히지 않은 괄호/따옴표를 보정.
    """
    for trim_target in [',\n', ',"', ', "', ',']:
        idx = text.rfind(trim_target)
        if idx > 0:
            candidate = text[:idx]
            open_braces = candidate.count('{') - candidate.count('}')
            open_brackets = candidate.count('[') - candidate.count(']')
            if open_braces >= 0 and open_brackets >= 0:
                candidate += ']' * open_brackets + '}' * open_braces
                result = _try_parse_json(candidate)
                if result is not None:
                    return result
    return None


def parse_a2a_response(raw_text: str, request_id: str | None = None) -> dict:
    """Gemini 응답 텍스트에서 A2A JSON을 파싱한다."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = []
        inside = False
        for line in lines:
            if line.strip().startswith("```") and not inside:
                inside = True
                continue
            elif line.strip() == "```" and inside:
                break
            elif inside:
                json_lines.append(line)
        text = "\n".join(json_lines).strip()

    parsed = _try_parse_json(text)
    if parsed is None:
        parsed = _try_repair_json(text)

    if parsed is not None:
        return {
            "a2a_version": A2A_VERSION,
            "message_type": "evaluation_response",
            "request_id": request_id or "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": {"agent": "gemini"},
            "status": "success",
            "payload": parsed,
        }

    return {
        "a2a_version": A2A_VERSION,
        "message_type": "evaluation_response",
        "request_id": request_id or "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {"agent": "gemini"},
        "status": "success",
        "payload": {"raw_text": raw_text},
    }


def a2a_response_to_markdown(response: dict) -> str:
    """A2A 응답을 gemini_feedback.md용 마크다운으로 변환한다."""
    payload = response.get("payload", {})

    if "raw_text" in payload:
        return payload["raw_text"]

    evaluation = payload.get("evaluation", {})
    summary = payload.get("summary", "")
    parts = []

    for key, value in evaluation.items():
        if isinstance(value, dict):
            score = value.get("score", "")
            detail = value.get("detail", "")
            parts.append(f"### {key}: {score}\n{detail}")
        elif isinstance(value, list):
            items = "\n".join(f"- {item}" for item in value)
            parts.append(f"### {key}\n{items}")

    if summary:
        parts.append(f"\n**요약:** {summary}")

    return "\n\n".join(parts)


def build_a2a_evaluation_prompt(base_prompt: str, config: dict) -> str:
    """A2A 모드일 때 JSON 응답을 강제하는 프롬프트를 생성한다."""
    if config.get("a2a_schema_enabled", False):
        return f"{base_prompt}\n\n{_A2A_RESPONSE_INSTRUCTION}"
    return base_prompt


def build_a2a_classification_prompt(base_prompt: str, config: dict) -> str:
    """A2A 모드일 때 분류 요청 프롬프트를 생성한다."""
    if config.get("a2a_schema_enabled", False):
        return f"{base_prompt}\n\n{_A2A_CLASSIFICATION_INSTRUCTION}"
    return base_prompt
