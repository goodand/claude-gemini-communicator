"""PostToolUse Hook: Write/Edit 도구 사용 후 자동으로 Gemini 평가를 트리거합니다.

stdin으로 Claude Hook JSON을 수신하고, .md 파일 변경 시 Gemini CLI로 평가합니다.
"""

import json
import os
import sys

try:
    from a2a_bridge import (
        call_gemini,
        check_cooldown,
        format_hook_output,
        load_config,
        save_feedback,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from a2a_bridge import (
        call_gemini,
        check_cooldown,
        format_hook_output,
        load_config,
        save_feedback,
    )


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    config = load_config()

    # 확장자 확인
    extensions = config.get("watch_extensions", [".md"])
    if not any(file_path.endswith(ext) for ext in extensions):
        sys.exit(0)

    # 제외 파일 확인
    exclude_files = config.get("exclude_files", [])
    basename = os.path.basename(file_path)
    if basename in exclude_files:
        sys.exit(0)

    # 쿨다운 확인
    if not check_cooldown(file_path, config):
        sys.exit(0)

    # Gemini 평가 호출
    from a2a_bridge import build_a2a_evaluation_prompt, parse_a2a_response, a2a_response_to_markdown

    prompt = config.get("evaluation_prompt", "이 문서를 평가해줘.")
    prompt = build_a2a_evaluation_prompt(prompt, config)

    # 비동기 모드: 백그라운드에서 평가, 즉시 리턴
    if config.get("async_mode", False):
        from a2a_bridge import call_gemini_async
        pending_msg = call_gemini_async(
            content="", prompt=prompt, config=config,
            file_path=file_path, source="PostToolUse Hook",
        )
        print(format_hook_output(pending_msg))
        sys.exit(0)

    # 동기 모드: 평가 완료까지 대기
    raw_feedback = call_gemini(
        content="",
        prompt=prompt,
        config=config,
        file_path=file_path,
    )

    # A2A 모드: 구조화된 응답 파싱 → 마크다운 변환
    if config.get("a2a_schema_enabled", False):
        a2a_resp = parse_a2a_response(raw_feedback)
        feedback = a2a_response_to_markdown(a2a_resp)
    else:
        feedback = raw_feedback

    # 피드백 저장
    save_feedback(feedback, source="PostToolUse Hook", file_path=file_path)

    # Claude에 피드백 전달
    print(format_hook_output(feedback))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
