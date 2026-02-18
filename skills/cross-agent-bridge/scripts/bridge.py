#!/usr/bin/env python3
"""Cross-Agent Bridge — 통합 오케스트레이터.

에이전트 간 협업을 위한 CLI 도구.

Usage:
    python3 bridge.py review --file <파일경로>
    python3 bridge.py review --file code.py --mode code --format json
    python3 bridge.py codex-review --file plan.md --model gpt-5
    python3 bridge.py parse --file output.jsonl
    python3 bridge.py parse --file output.jsonl --agent codex --format json
    python3 bridge.py doctor
    python3 bridge.py setup [--output config.json]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from _common import load_env, read_input, save_feedback

CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".c", ".cpp", ".rb", ".sh"}

PROMPTS = {
    "code": (
        "다음 코드를 리뷰해줘:\n"
        "- 버그 또는 잠재적 오류\n"
        "- 보안 취약점 (인젝션, 하드코딩된 비밀 등)\n"
        "- 에러 처리 누락\n"
        "- 개선 제안\n"
        "간결하게 한국어로 답해줘."
    ),
    "doc": (
        "다음 문서를 평가해줘:\n"
        "- 논리적 일관성\n"
        "- 실현 가능성\n"
        "- 누락된 고려사항\n"
        "- 개선 제안\n"
        "간결하게 한국어로 답해줘."
    ),
}


def cmd_review(args):
    """Gemini에 코드/문서 리뷰 요청."""
    from _config import load_config
    from _gemini_client import call_gemini

    load_env()
    config = load_config()

    content = read_input(args.file)
    if content is None:
        print("[ERROR] 입력이 필요합니다.", file=sys.stderr)
        return 1

    # 모드 결정
    mode = args.mode
    if not mode:
        if args.file:
            ext = Path(args.file).suffix.lower()
            mode = "code" if ext in CODE_EXTENSIONS else "doc"
        else:
            mode = "doc"

    prompt = args.prompt or PROMPTS[mode]
    if args.file:
        prompt = f"{prompt}\n\n파일 경로: {args.file}"

    result, model_used = call_gemini(content, prompt, config, file_path=args.file)

    if args.format == "json":
        output = json.dumps({
            "mode": mode,
            "file_path": args.file,
            "feedback": result,
            "model_used": model_used,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2)
    else:
        output = result

    print(output)

    if args.save:
        save_feedback(result, source="Cross-Agent Bridge Review", file_path=args.file)
    return 0


def _run_codex_exec(prompt: str, model: str | None, timeout: int) -> tuple[int, str]:
    """codex exec를 호출하고 최종 메시지를 반환."""
    cmd = ["codex", "exec"]
    if model:
        cmd.extend(["-m", model])

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    try:
        cmd.extend(["--output-last-message", temp_file.name, prompt])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        last_message = Path(temp_file.name).read_text(encoding="utf-8").strip()
        if last_message:
            return result.returncode, last_message

        fallback = result.stdout.strip() or result.stderr.strip()
        return result.returncode, fallback
    except subprocess.TimeoutExpired:
        return 124, "[ERROR] codex exec timeout"
    except FileNotFoundError:
        return 127, "[ERROR] codex command not found"
    finally:
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass


def cmd_codex_review(args):
    """Codex에 코드/문서 리뷰 요청."""
    content = read_input(args.file)
    if content is None:
        print("[ERROR] 입력이 필요합니다.", file=sys.stderr)
        return 1

    mode = args.mode
    if not mode:
        if args.file:
            ext = Path(args.file).suffix.lower()
            mode = "code" if ext in CODE_EXTENSIONS else "doc"
        else:
            mode = "doc"

    prompt = args.prompt or PROMPTS[mode]
    if args.file:
        prompt = f"{prompt}\n\n파일 경로: {args.file}"
    full_prompt = f"{prompt}\n\n---\n{content}"

    rc, result = _run_codex_exec(full_prompt, args.model, args.timeout)
    model_used = args.model or "default"
    if rc != 0 and not result.startswith("[ERROR]"):
        result = f"[ERROR] codex exec failed (exit={rc})\n{result}"

    if args.format == "json":
        output = json.dumps(
            {
                "mode": mode,
                "file_path": args.file,
                "feedback": result,
                "model_used": model_used,
                "provider": "codex",
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        output = result

    print(output)
    if args.save:
        save_feedback(result, source="Cross-Agent Bridge Codex Review", file_path=args.file)
    return 0


def cmd_parse(args):
    """에이전트 출력 파싱 (Codex/Gemini/Claude 자동 감지)."""
    raw_text = read_input(args.file)
    if raw_text is None:
        print("[ERROR] 입력이 필요합니다.", file=sys.stderr)
        return 1

    agent = args.agent
    if agent == "auto":
        agent = _detect_agent(raw_text)
        if agent is None:
            print("[ERROR] 에이전트 형식을 자동 감지할 수 없습니다. --agent로 지정하세요.", file=sys.stderr)
            return 1
        print(f"[감지됨] {agent}", file=sys.stderr)

    output = _parse_and_render(raw_text, agent, args.format, last_n=args.last_n)
    if output is None:
        print("[ERROR] 파싱 실패.", file=sys.stderr)
        return 1

    print(output)

    if args.save:
        save_feedback(output, source=f"Cross-Agent Bridge Parse ({agent})", file_path=args.file)
    return 0


def _detect_agent(raw_text: str) -> str | None:
    """첫 유효 JSON 라인 시그니처로 에이전트 감지."""
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
        obj_type = str(obj.get("type", ""))
        if obj_type in ("thread.started", "item.started", "item.completed", "turn.completed"):
            return "codex"
        if "stats" in obj and "response" in obj:
            return "gemini"
        if obj_type in ("user", "assistant") and "message" in obj:
            return "claude"
    return None


def _parse_and_render(raw_text: str, agent: str, fmt: str, last_n: int = None) -> str | None:
    """감지된 에이전트 파서로 파싱 + 렌더링."""
    if agent == "codex":
        return _parse_codex(raw_text, fmt)
    elif agent == "gemini":
        return _parse_gemini(raw_text, fmt)
    elif agent == "claude":
        return _parse_claude(raw_text, fmt, last_n)
    return None


# ── 내장 파서 (자립성: agent-parser 의존 없음) ──

def _parse_codex(raw_text: str, fmt: str) -> str:
    """Codex JSONL 간이 파서."""
    events = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                events.append(obj)
        except json.JSONDecodeError:
            continue

    thread_id = None
    messages = []
    commands = []
    errors = []

    for e in events:
        t = str(e.get("type", ""))
        if t == "thread.started":
            thread_id = e.get("thread_id")
        item = e.get("item") if isinstance(e.get("item"), dict) else None
        if item:
            it = str(item.get("type", ""))
            if it == "agent_message" and item.get("text"):
                messages.append(item["text"])
            elif it == "command_execution":
                commands.append({
                    "command": item.get("command", ""),
                    "exit_code": item.get("exit_code"),
                })
            elif "error" in it.lower():
                errors.append(item.get("message", "error"))

    parsed = {
        "agent": "codex", "thread_id": thread_id,
        "event_count": len(events), "messages": len(messages),
        "commands": len(commands), "errors": len(errors),
        "final_message": messages[-1] if messages else None,
    }

    if fmt == "json":
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    lines = [
        "# Codex 요약",
        f"- thread_id: {thread_id or '(없음)'}",
        f"- 이벤트: {len(events)}, 메시지: {len(messages)}, 명령: {len(commands)}, 에러: {len(errors)}",
    ]
    if messages:
        lines.append(f"\n## 최종 메시지\n{messages[-1]}")
    return "\n".join(lines)


def _parse_gemini(raw_text: str, fmt: str) -> str | None:
    """Gemini JSON 간이 파서."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return None

    parsed = {
        "agent": "gemini",
        "session_id": data.get("session_id"),
        "response": data.get("response"),
        "has_stats": "stats" in data,
        "error": data.get("error"),
    }

    if fmt == "json":
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    lines = [
        "# Gemini 요약",
        f"- session_id: {parsed['session_id'] or '(없음)'}",
        f"- error: {parsed['error'] or '없음'}",
    ]
    resp = parsed.get("response")
    if resp:
        lines.append(f"\n## 응답\n{resp[:500]}")
    return "\n".join(lines)


def _parse_claude(raw_text: str, fmt: str, last_n: int = None) -> str:
    """Claude transcript JSONL 간이 파서."""
    messages = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("type") in ("user", "assistant"):
            messages.append(obj)

    if last_n is not None and last_n > 0:
        messages = messages[-last_n:]

    user_count = sum(1 for m in messages if m.get("type") == "user")
    asst_count = sum(1 for m in messages if m.get("type") == "assistant")

    parsed = {
        "agent": "claude",
        "messages_analyzed": len(messages),
        "user_count": user_count,
        "assistant_count": asst_count,
    }

    if fmt == "json":
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    return f"# Claude 요약\n- 메시지: {len(messages)} (user: {user_count}, assistant: {asst_count})"


def cmd_doctor(args):
    """시스템 진단."""
    from _config import load_config
    from _doctor import run_doctor

    load_env()
    config = load_config()
    run_doctor(config)
    return 0


def cmd_setup(args):
    """초기 설정 (config 생성, .env 템플릿)."""
    from _config import generate_config

    config_dir = Path.cwd() / "config"
    config_dir.mkdir(exist_ok=True)
    output = Path(args.output) if args.output else config_dir / "config.json"
    if output.exists():
        print(f"[SKIP] 이미 존재: {output}")
    else:
        generate_config(output)

    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        env_path.write_text(
            "# Gemini API Key\nGEMINI_API_KEY=your-api-key-here\n",
            encoding="utf-8",
        )
        print(f"[생성됨] {env_path}")
    else:
        print(f"[SKIP] .env 이미 존재")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Agent Bridge — 통합 오케스트레이터"
    )
    subparsers = parser.add_subparsers(dest="command", help="서브커맨드")

    # review
    p_review = subparsers.add_parser("review", help="Gemini 코드/문서 리뷰")
    p_review.add_argument("--file", "-f", help="리뷰할 파일 경로")
    p_review.add_argument("--mode", "-m", choices=["code", "doc"], help="리뷰 모드")
    p_review.add_argument("--prompt", "-p", help="커스텀 프롬프트")
    p_review.add_argument("--format", choices=["text", "json"], default="text", help="출력 형식")
    p_review.add_argument("--save", "-s", action="store_true", help="피드백 저장")

    # codex-review
    p_creview = subparsers.add_parser("codex-review", help="Codex 코드/문서 리뷰")
    p_creview.add_argument("--file", "-f", help="리뷰할 파일 경로")
    p_creview.add_argument("--mode", "-m", choices=["code", "doc"], help="리뷰 모드")
    p_creview.add_argument("--prompt", "-p", help="커스텀 프롬프트")
    p_creview.add_argument("--format", choices=["text", "json"], default="text", help="출력 형식")
    p_creview.add_argument("--model", default="gpt-5", help="Codex 모델")
    p_creview.add_argument("--timeout", type=int, default=120, help="실행 타임아웃(초)")
    p_creview.add_argument("--save", "-s", action="store_true", help="피드백 저장")

    # parse
    p_parse = subparsers.add_parser("parse", help="에이전트 출력 파싱")
    p_parse.add_argument("--file", "-f", help="입력 파일 경로")
    p_parse.add_argument("--agent", "-a", choices=["codex", "gemini", "claude", "auto"], default="auto")
    p_parse.add_argument("--format", choices=["summary", "json"], default="summary")
    p_parse.add_argument("--save", "-s", action="store_true")
    p_parse.add_argument("--last-n", type=int, default=None, help="마지막 N개 (Claude)")

    # doctor
    subparsers.add_parser("doctor", help="시스템 진단")

    # setup
    p_setup = subparsers.add_parser("setup", help="초기 설정")
    p_setup.add_argument("--output", "-o", help="config.json 출력 경로")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "review": cmd_review,
        "codex-review": cmd_codex_review,
        "parse": cmd_parse,
        "doctor": cmd_doctor,
        "setup": cmd_setup,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(0)
