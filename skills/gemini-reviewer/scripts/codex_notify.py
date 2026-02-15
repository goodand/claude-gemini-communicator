#!/usr/bin/env python3
"""Codex CLI notify hook: agent-turn-complete 시 Gemini 평가를 트리거합니다.

Codex의 notify 설정에 등록하여 사용합니다.
Claude Code의 Stop Hook과 동일한 역할 (Plan 감지 -> Gemini 평가).

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

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from _common import load_env, save_feedback


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
    try:
        from evaluate import call_gemini, PROMPTS
        result, _ = call_gemini(text, PROMPTS["doc"])
        return result
    except Exception as e:
        return f"[ERROR] Gemini 호출 실패: {e}"


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
    if not text or not is_plan(text):
        return 0

    # Gemini 평가
    feedback = evaluate_with_gemini(text)
    if feedback:
        save_feedback(feedback, source="Codex Notify Hook (Plan 감지)", file_path=None)
        # stdout으로도 출력 (Codex가 표시할 수 있도록)
        print(f"[Gemini 평가] {feedback[:500]}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
