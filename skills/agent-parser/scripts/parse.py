#!/usr/bin/env python3
"""통합 에이전트 출력 파서: Codex/Gemini/Claude 자동 감지 + 파싱.

Usage:
    # 자동 감지
    python3 parse.py --file output.jsonl
    cat output.json | python3 parse.py

    # 에이전트 명시
    python3 parse.py --file output.jsonl --agent codex
    python3 parse.py --file output.json --agent gemini

    # JSON 출력 + 저장
    python3 parse.py --file transcript.jsonl --format json --save
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from _common import read_input, save_feedback
from _codex_parser import parse_jsonl_events, render_summary as codex_summary
from _gemini_parser import parse_gemini_json, render_summary as gemini_summary
from _transcript_parser import parse_transcript_jsonl, render_summary as transcript_summary


def detect_agent(raw_text: str) -> str | None:
    """첫 번째 유효 JSON 라인의 시그니처로 에이전트를 자동 감지."""
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue

        # Codex: thread.started / item.started / item.completed / turn.completed
        obj_type = str(obj.get("type", ""))
        if obj_type in ("thread.started", "item.started", "item.completed", "turn.completed"):
            return "codex"

        # Gemini: stats + response (또는 session_id + response)
        if "stats" in obj and "response" in obj:
            return "gemini"
        if "session_id" in obj and "response" in obj and "stats" in obj:
            return "gemini"

        # Claude transcript: type=user|assistant + message
        if obj_type in ("user", "assistant") and "message" in obj:
            return "claude"

    return None


def parse_and_render(raw_text: str, agent: str, fmt: str, last_n: int | None = None) -> str | None:
    """감지된 에이전트에 맞는 파서로 파싱 + 렌더링."""
    if agent == "codex":
        parsed = parse_jsonl_events(raw_text)
        if fmt == "json":
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        return codex_summary(parsed)

    elif agent == "gemini":
        parsed = parse_gemini_json(raw_text)
        if parsed is None:
            return None
        if fmt == "json":
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        return gemini_summary(parsed)

    elif agent == "claude":
        parsed = parse_transcript_jsonl(raw_text, last_n=last_n)
        if fmt == "json":
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        return transcript_summary(parsed)

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="통합 에이전트 출력 파서 (Codex/Gemini/Claude 자동 감지)"
    )
    parser.add_argument("--file", "-f", help="입력 파일 경로")
    parser.add_argument(
        "--agent", "-a",
        choices=["codex", "gemini", "claude", "auto"],
        default="auto",
        help="에이전트 지정 (기본: auto)",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="출력 형식 (기본: summary)",
    )
    parser.add_argument("--save", "-s", action="store_true", help="gemini_feedback.md에 저장")
    parser.add_argument("--last-n", type=int, default=None, help="마지막 N개 메시지만 파싱 (Claude)")
    args = parser.parse_args()

    raw_text = read_input(args.file)
    if raw_text is None:
        return 0

    # 에이전트 감지
    agent = args.agent
    if agent == "auto":
        agent = detect_agent(raw_text)
        if agent is None:
            print("[ERROR] 에이전트 형식을 자동 감지할 수 없습니다. --agent로 지정하세요.", file=sys.stderr)
            return 1
        print(f"[감지됨] {agent}", file=sys.stderr)

    # 파싱 + 렌더링
    output = parse_and_render(raw_text, agent, args.format, last_n=args.last_n)
    if output is None:
        print("[ERROR] 파싱 실패.", file=sys.stderr)
        return 1

    print(output)

    if args.save:
        source = f"Agent Parser ({agent})"
        if args.file:
            source += f" | 대상: `{args.file}`"
        save_feedback(output, source)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
