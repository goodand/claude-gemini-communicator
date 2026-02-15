#!/usr/bin/env python3
"""Codex JSONL 파서: codex exec --json 출력을 구조화 요약으로 변환."""

import json


def summarize_output(text: str, max_chars: int = 240) -> str:
    """command output을 짧은 요약 문자열로 만든다."""
    if not text:
        return "(출력 없음)"
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def parse_jsonl_events(raw_text: str) -> dict:
    """JSONL 이벤트를 파싱해 구조화된 결과를 반환."""
    events = []
    parse_errors = []

    for idx, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
            else:
                parse_errors.append({"line": idx, "message": "JSON 객체가 아님"})
        except json.JSONDecodeError as e:
            parse_errors.append({"line": idx, "message": f"JSON 파싱 실패: {e.msg}"})

    thread_id = None
    reasoning_list: list[str] = []
    agent_messages: list[str] = []
    command_exec_map: dict[str, dict] = {}
    file_changes: list[dict] = []
    errors: list[dict] = []
    usage_total = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
    }

    def upsert_command(item: dict):
        item_id = str(item.get("id", f"unknown_{len(command_exec_map)}"))
        if item_id not in command_exec_map:
            command_exec_map[item_id] = {
                "id": item_id,
                "command": "",
                "exit_code": None,
                "status": "",
                "output": "",
                "output_summary": "(출력 없음)",
            }

        rec = command_exec_map[item_id]
        if item.get("command"):
            rec["command"] = item.get("command", "")
        if "exit_code" in item:
            rec["exit_code"] = item.get("exit_code")
        if item.get("status"):
            rec["status"] = item.get("status", "")

        output = item.get("aggregated_output")
        if isinstance(output, str):
            rec["output"] = output
            rec["output_summary"] = summarize_output(output)

    for event in events:
        event_type = str(event.get("type", ""))

        if event_type == "thread.started" and event.get("thread_id"):
            thread_id = event.get("thread_id")

        item = event.get("item") if isinstance(event.get("item"), dict) else None
        item_type = str(item.get("type", "")) if item else ""

        if event_type in ("item.started", "item.completed") and item:
            if item_type == "reasoning":
                reasoning_text = item.get("text", "")
                if isinstance(reasoning_text, str) and reasoning_text:
                    reasoning_list.append(reasoning_text)

            elif item_type == "agent_message":
                message_text = item.get("text", "")
                if isinstance(message_text, str) and message_text:
                    agent_messages.append(message_text)

            elif item_type == "command_execution":
                upsert_command(item)

            elif item_type == "file_change":
                file_changes.append(item)

            elif "error" in item_type.lower():
                errors.append(
                    {
                        "event_type": event_type,
                        "item_type": item_type,
                        "message": item.get("message") or item.get("text") or "item error",
                        "raw": item,
                    }
                )

        # file_change 이벤트가 item 외부에 있는 경우도 수용
        if event_type == "file_change":
            file_changes.append(event)

        # error 이벤트 수집
        if "error" in event_type.lower() or event.get("error") is not None:
            err_payload = event.get("error")
            message = ""
            if isinstance(err_payload, dict):
                message = err_payload.get("message", "")
            elif isinstance(err_payload, str):
                message = err_payload

            errors.append(
                {
                    "event_type": event_type,
                    "item_type": item_type or None,
                    "message": message or "error event",
                    "raw": event,
                }
            )

        if event_type == "turn.completed":
            usage = event.get("usage")
            if isinstance(usage, dict):
                usage_total["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
                usage_total["cached_input_tokens"] += int(usage.get("cached_input_tokens", 0) or 0)
                usage_total["output_tokens"] += int(usage.get("output_tokens", 0) or 0)

    usage_total["total_input_tokens"] = (
        usage_total["input_tokens"] + usage_total["cached_input_tokens"]
    )

    command_executions = list(command_exec_map.values())

    return {
        "thread_id": thread_id,
        "reasoning": reasoning_list,
        "agent_messages": agent_messages,
        "final_message": agent_messages[-1] if agent_messages else None,
        "command_executions": command_executions,
        "file_changes": file_changes,
        "errors": errors,
        "usage": usage_total,
        "event_count": len(events),
        "parse_errors": parse_errors,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약 생성."""
    lines = []

    lines.append("# Codex JSONL 요약")
    lines.append("")
    lines.append(f"- thread_id: {parsed.get('thread_id') or '(없음)'}")
    lines.append(f"- 이벤트 수: {parsed.get('event_count', 0)}")
    lines.append(f"- reasoning 수: {len(parsed.get('reasoning', []))}")
    lines.append(f"- agent_message 수: {len(parsed.get('agent_messages', []))}")
    lines.append(f"- command_execution 수: {len(parsed.get('command_executions', []))}")
    lines.append(f"- file_change 수: {len(parsed.get('file_changes', []))}")
    lines.append(f"- error 수: {len(parsed.get('errors', []))}")
    lines.append(f"- parse_error 수: {len(parsed.get('parse_errors', []))}")
    lines.append("")

    final_message = parsed.get("final_message")
    lines.append("## 최종 agent_message")
    if final_message:
        lines.append(final_message)
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## Command Executions")
    commands = parsed.get("command_executions", [])
    if commands:
        for idx, cmd in enumerate(commands, start=1):
            lines.append(
                f"{idx}. command={cmd.get('command')!r}, exit_code={cmd.get('exit_code')}, "
                f"status={cmd.get('status')}, output_summary={cmd.get('output_summary')!r}"
            )
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## Usage")
    usage = parsed.get("usage", {})
    lines.append(f"- input_tokens: {usage.get('input_tokens', 0)}")
    lines.append(f"- cached_input_tokens: {usage.get('cached_input_tokens', 0)}")
    lines.append(f"- output_tokens: {usage.get('output_tokens', 0)}")
    lines.append(f"- total_input_tokens: {usage.get('total_input_tokens', 0)}")
    lines.append("")

    if parsed.get("errors"):
        lines.append("## Errors")
        for idx, err in enumerate(parsed.get("errors", []), start=1):
            lines.append(
                f"{idx}. event_type={err.get('event_type')}, "
                f"item_type={err.get('item_type')}, message={err.get('message')!r}"
            )
        lines.append("")

    if parsed.get("parse_errors"):
        lines.append("## Parse Errors")
        for pe in parsed.get("parse_errors", []):
            lines.append(f"- line {pe.get('line')}: {pe.get('message')}")

    return "\n".join(lines).rstrip() + "\n"
