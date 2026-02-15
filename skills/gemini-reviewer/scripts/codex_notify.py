#!/usr/bin/env python3
"""Codex CLI notify hook: agent-turn-complete 시 Gemini 평가를 트리거합니다.

Codex의 notify 설정에 등록하여 사용합니다.
Claude Code의 Stop Hook과 동일한 역할 (Plan 감지 → Gemini 평가).

Setup (config.toml):
    notify = ["python3", "/path/to/codex_notify.py"]

수신 JSON (sys.argv[1]):
    {
        "type": "agent-turn-complete",
        "thread-id": "...",
        "turn-id": "...",
        "cwd": "...",
        "input-messages": [...],
        "last-assistant-message": "..."
    }
"""

import json
import os
import sys
from pathlib import Path

# evaluate.py와 같은 디렉토리
SCRIPT_DIR = Path(__file__).parent


def load_env():
    """프로젝트 루트 .env 로드."""
    for candidate in [Path(os.getcwd()) / ".env", SCRIPT_DIR.parent.parent.parent / ".env"]:
        if candidate.exists():
            try:
                for line in candidate.read_text("utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip().strip("\"'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            except IOError:
                pass
            break


def is_plan(text: str, min_length: int = 300) -> bool:
    """텍스트가 소프트웨어 개발 계획인지 간단히 판별합니다.

    Gemini API 호출 없이 키워드 기반 휴리스틱으로 빠르게 판별.
    """
    if len(text) < min_length:
        return False

    plan_keywords = [
        "구현", "설계", "아키텍처", "단계", "phase",
        "implementation", "architecture", "design",
        "## ", "### ", "```",
    ]
    score = sum(1 for kw in plan_keywords if kw.lower() in text.lower())
    return score >= 3


def evaluate_with_gemini(text: str) -> str | None:
    """evaluate.py를 import하여 Gemini 평가를 실행합니다."""
    sys.path.insert(0, str(SCRIPT_DIR))
    try:
        from evaluate import call_gemini, PROMPTS, load_env as eval_load_env
        eval_load_env()
        return call_gemini(text, PROMPTS["doc"])
    except Exception as e:
        return f"[ERROR] Gemini 호출 실패: {e}"


def save_feedback(feedback: str, cwd: str):
    """gemini_feedback.md에 결과를 저장합니다."""
    from datetime import datetime
    feedback_path = Path(cwd) / "gemini_feedback.md"
    if not feedback_path.parent.exists():
        feedback_path = SCRIPT_DIR.parent.parent.parent / "gemini_feedback.md"

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] Codex Notify Hook (Plan 감지)\n\n{feedback}\n"

    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(entry)


def main():
    if len(sys.argv) < 2:
        # 테스트 모드: stdin에서 JSON 읽기
        try:
            notification = json.loads(sys.stdin.read())
        except (json.JSONDecodeError, IOError):
            return 0
    else:
        try:
            notification = json.loads(sys.argv[1])
        except (json.JSONDecodeError, ValueError):
            return 0

    if notification.get("type") != "agent-turn-complete":
        return 0

    load_env()

    # 마지막 어시스턴트 메시지 추출
    text = notification.get("last-assistant-message", "")
    if not text:
        return 0

    # Plan 감지
    if not is_plan(text):
        return 0

    # Gemini 평가
    feedback = evaluate_with_gemini(text)
    if feedback:
        cwd = notification.get("cwd", os.getcwd())
        save_feedback(feedback, cwd)
        # stdout으로도 출력 (Codex가 표시할 수 있도록)
        print(f"[Gemini 평가] {feedback[:500]}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
