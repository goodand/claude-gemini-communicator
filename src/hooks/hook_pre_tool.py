"""PreToolUse Hook: 위험한 명령 실행 전 사전 경고/차단한다.

stdin으로 Claude PreToolUse Hook JSON을 수신하고,
Bash 명령이 위험 패턴에 매칭되면 차단(block) 판정을 반환한다.

이 hook은 `auto_hooks_enabled`(자동 평가 hook kill-switch)의 대상이 아니다 —
안전가드는 자체 스위치 `pre_tool_guard.enabled`로만 제어된다(command_guard.py에서 판정).
"""

import json
import os
import sys

# src/ 패키지 import를 위해 프로젝트 루트를 path에 추가
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.shared.command_guard import check_command
from src.shared.config import load_config, load_env


def main():
    load_env()

    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    config = load_config()
    result = check_command(command, config)

    if result is None:
        sys.exit(0)

    if result["severity"] == "block":
        output = {
            "decision": "block",
            "reason": f"⚠️ 위험 명령 차단: {result['reason']}\n명령어: {command[:200]}",
        }
        print(json.dumps(output, ensure_ascii=False))
    elif result["severity"] == "warn":
        output = {
            "decision": "allow",
            "hookSpecificOutput": {
                "additionalContext": f"⚠️ 주의: {result['reason']}\n명령어: {command[:200]}",
            },
        }
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
