#!/usr/bin/env python3
"""codex exec --json(JSONL) 출력을 파싱하여 구조화 요약을 생성합니다."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def read_jsonl_input(file_path: str | None) -> str | None:
    """--file 또는 stdin에서 JSONL 텍스트를 읽습니다."""
    if file_path:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] 파일 없음: {file_path}", file=sys.stderr)
            return None
        try:
            return path.read_text(encoding="utf-8")
        except IOError as e:
            print(f"[ERROR] 파일 읽기 실패: {e}", file=sys.stderr)
            return None

    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except IOError as e:
            print(f"[ERROR] stdin 읽기 실패: {e}", file=sys.stderr)
            return None

    print("[ERROR] --file 또는 stdin 입력이 필요합니다.", file=sys.stderr)
    return None


def summarize_output(text: str, max_chars: int = 240) -> str:
    """command output을 짧은 요약 문자열로 만듭니다."""
    if not text:
        return "(출력 없음)"

    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def parse_jsonl_events(raw_text: str) -> dict:
    """JSONL 이벤트를 파싱해 구조화된 결과를 반환합니다."""
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
    """사람이 읽기 좋은 텍스트 요약을 생성합니다."""
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


def save_feedback(content: str, source_desc: str):
    """gemini_feedback.md에 결과를 append합니다."""
    feedback_path = Path.cwd() / "plans" / "gemini" / "gemini_feedback.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] {source_desc}\n\n{content}\n"

    try:
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        with open(feedback_path, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"[저장됨] {feedback_path}", file=sys.stderr)
    except IOError as e:
        print(f"[ERROR] 저장 실패: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="codex exec --json(JSONL) 파서: 구조화 요약 생성"
    )
    parser.add_argument("--file", "-f", help="입력 JSONL 파일 경로")
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="출력 형식 (기본: summary)",
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="결과를 gemini_feedback.md에 append",
    )
    args = parser.parse_args()

    raw_text = read_jsonl_input(args.file)
    if raw_text is None:
        return 0

    parsed = parse_jsonl_events(raw_text)

    if args.format == "json":
        output = json.dumps(parsed, ensure_ascii=False, indent=2)
    else:
        output = render_summary(parsed)

    print(output)

    if args.save:
        source = "Codex JSON Parser"
        if args.file:
            source += f" | 대상: `{args.file}`"
        save_feedback(output, source)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
