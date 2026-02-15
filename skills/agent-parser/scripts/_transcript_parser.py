#!/usr/bin/env python3
"""Claude Transcript 파서: Claude Code transcript(JSONL) 구조화 요약 생성."""

import json


def shorten_text(text: str, max_chars: int) -> str:
    """텍스트를 한 줄 요약으로 정규화하고 길이를 제한."""
    normalized = " ".join(str(text).split())
    if not normalized:
        return "(없음)"
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def extract_user_text(content) -> str:
    """user content가 문자열/배열일 때 텍스트를 추출."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks = []
        for block in content:
            if isinstance(block, str):
                chunks.append(block)
                continue
            if not isinstance(block, dict):
                continue
            block_type = str(block.get("type", ""))
            if block_type in ("text", "input_text"):
                text_value = block.get("text")
                if isinstance(text_value, str):
                    chunks.append(text_value)
            elif isinstance(block.get("text"), str):
                chunks.append(block.get("text"))
        return "\n".join(chunks).strip()

    return ""


def parse_transcript_jsonl(raw_text: str, last_n: int | None = None) -> dict:
    """transcript JSONL을 파싱하여 집계 결과를 생성."""
    records = []
    parse_errors = []

    for idx, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as e:
            parse_errors.append({"line": idx, "message": f"JSON 파싱 실패: {e.msg}"})
            continue

        if not isinstance(payload, dict):
            parse_errors.append({"line": idx, "message": "JSON 객체(dict)가 아님"})
            continue

        record_type = str(payload.get("type", ""))
        if record_type not in ("user", "assistant", "file-history-snapshot"):
            continue
        records.append(payload)

    messages = [r for r in records if str(r.get("type", "")) in ("user", "assistant")]
    if last_n is not None:
        if last_n < 0:
            last_n = 0
        messages = messages[-last_n:] if last_n > 0 else []

    session_id = None
    for msg in messages:
        value = msg.get("sessionId")
        if isinstance(value, str) and value:
            session_id = value
            break
    if session_id is None:
        for rec in records:
            value = rec.get("sessionId")
            if isinstance(value, str) and value:
                session_id = value
                break

    user_count = 0
    assistant_count = 0
    last_user_text = ""
    assistant_text_total_length = 0
    last_assistant_text = ""
    thinking_count = 0
    tool_use_counts: dict[str, int] = {}
    pending_user = 0
    turn_count = 0

    for msg in messages:
        record_type = str(msg.get("type", ""))
        message = msg.get("message") if isinstance(msg.get("message"), dict) else {}

        if record_type == "user":
            user_count += 1
            pending_user += 1
            user_text = extract_user_text(message.get("content"))
            if user_text:
                last_user_text = user_text
            continue

        if record_type != "assistant":
            continue

        assistant_count += 1
        if pending_user > 0:
            turn_count += 1
            pending_user -= 1

        content = message.get("content")
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = str(block.get("type", ""))

            if block_type == "text":
                text_value = block.get("text")
                if isinstance(text_value, str):
                    assistant_text_total_length += len(text_value)
                    if text_value.strip():
                        last_assistant_text = text_value

            elif block_type == "thinking":
                thinking_count += 1

            elif block_type == "tool_use":
                tool_name = block.get("name")
                if isinstance(tool_name, str) and tool_name:
                    tool_use_counts[tool_name] = tool_use_counts.get(tool_name, 0) + 1

    return {
        "session_id": session_id,
        "messages_analyzed": len(messages),
        "last_n_applied": last_n,
        "user": {
            "count": user_count,
            "last_message_summary": shorten_text(last_user_text, 120),
        },
        "assistant": {
            "count": assistant_count,
            "text_total_length": assistant_text_total_length,
            "last_text_summary": shorten_text(last_assistant_text, 200),
            "thinking_block_count": thinking_count,
            "tool_use_counts": dict(sorted(tool_use_counts.items())),
        },
        "turn_count": turn_count,
        "parse_errors": parse_errors,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약 생성."""
    lines = []
    lines.append("# Claude Transcript 요약")
    lines.append("")
    lines.append(f"- session_id: {parsed.get('session_id') or '(없음)'}")
    lines.append(f"- 분석한 메시지 수: {parsed.get('messages_analyzed', 0)}")
    lines.append(f"- last_n 적용값: {parsed.get('last_n_applied')}")
    lines.append(f"- 대화 턴 수(user+assistant 쌍): {parsed.get('turn_count', 0)}")
    lines.append("")

    user = parsed.get("user", {})
    lines.append("## User")
    lines.append(f"- 메시지 수: {user.get('count', 0)}")
    lines.append(f"- 마지막 메시지 요약: {user.get('last_message_summary', '(없음)')}")
    lines.append("")

    assistant = parsed.get("assistant", {})
    lines.append("## Assistant")
    lines.append(f"- 메시지 수: {assistant.get('count', 0)}")
    lines.append(f"- text 총 길이: {assistant.get('text_total_length', 0)}")
    lines.append(f"- 마지막 text 요약: {assistant.get('last_text_summary', '(없음)')}")
    lines.append(f"- thinking 블록 수: {assistant.get('thinking_block_count', 0)}")
    lines.append("")

    lines.append("## Tool Use 집계")
    tool_use_counts = assistant.get("tool_use_counts", {})
    if isinstance(tool_use_counts, dict) and tool_use_counts:
        for idx, (name, count) in enumerate(tool_use_counts.items(), start=1):
            lines.append(f"{idx}. {name}: {count}")
    else:
        lines.append("(없음)")
    lines.append("")

    parse_errors = parsed.get("parse_errors", [])
    lines.append(f"- parse_error 수: {len(parse_errors)}")
    if parse_errors:
        lines.append("## Parse Errors")
        for err in parse_errors:
            lines.append(f"- line {err.get('line')}: {err.get('message')}")

    return "\n".join(lines).rstrip() + "\n"
