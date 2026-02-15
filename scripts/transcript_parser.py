#!/usr/bin/env python3
"""Claude Code transcript(JSONL)를 파싱하여 구조화 요약을 생성합니다."""

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


def shorten_text(text: str, max_chars: int) -> str:
    """텍스트를 한 줄 요약으로 정규화하고 길이를 제한합니다."""
    normalized = " ".join(str(text).split())
    if not normalized:
        return "(없음)"
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def extract_user_text(content) -> str:
    """user content가 문자열/배열일 때 텍스트를 추출합니다."""
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
    """transcript JSONL을 파싱하여 집계 결과를 생성합니다."""
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
    """사람이 읽기 좋은 텍스트 요약을 생성합니다."""
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


def save_feedback(content: str, source_desc: str):
    """gemini_feedback.md에 결과를 append합니다."""
    feedback_path = Path.cwd() / "gemini_feedback.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] {source_desc}\n\n{content}\n"

    try:
        with open(feedback_path, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"[저장됨] {feedback_path}", file=sys.stderr)
    except IOError as e:
        print(f"[ERROR] 저장 실패: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Claude transcript(JSONL) 파서: 구조화 요약 생성"
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
    parser.add_argument(
        "--last-n",
        type=int,
        default=None,
        help="마지막 N개 메시지만 파싱",
    )
    args = parser.parse_args()

    raw_text = read_jsonl_input(args.file)
    if raw_text is None:
        return 0

    parsed = parse_transcript_jsonl(raw_text, last_n=args.last_n)

    if args.format == "json":
        output = json.dumps(parsed, ensure_ascii=False, indent=2)
    else:
        output = render_summary(parsed)

    print(output)

    if args.save:
        source = "Transcript Parser"
        if args.file:
            source += f" | 대상: `{args.file}`"
        save_feedback(output, source)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
