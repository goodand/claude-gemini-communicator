"""Stop Hook: Claude 응답 완료 시 계획(Plan) 감지 후 Gemini 평가를 트리거합니다.

stdin으로 Claude Stop Hook JSON을 수신하고,
마지막 출력이 소프트웨어 개발 계획이면 Gemini CLI로 평가합니다.
"""

import json
import os
import sys

try:
    from a2a_bridge import (
        call_gemini,
        format_hook_output,
        load_config,
        save_feedback,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from a2a_bridge import (
        call_gemini,
        format_hook_output,
        load_config,
        save_feedback,
    )


def extract_last_assistant_text(stop_input: dict) -> str:
    """Stop Hook 입력에서 Claude의 마지막 텍스트 출력을 추출합니다."""
    # stop_hook_input에는 transcript_path 또는 직접 transcript가 포함될 수 있음
    transcript_path = stop_input.get("transcript_path", "")

    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            # JSONL에서 마지막 assistant 메시지 추출
            for line in reversed(lines):
                try:
                    entry = json.loads(line.strip())
                    if entry.get("role") == "assistant":
                        content = entry.get("content", "")
                        if isinstance(content, list):
                            texts = [
                                block.get("text", "")
                                for block in content
                                if block.get("type") == "text"
                            ]
                            return "\n".join(texts)
                        return str(content)
                except json.JSONDecodeError:
                    continue
        except IOError:
            pass

    # stop_input에 직접 포함된 경우
    message = stop_input.get("message", "")
    if message:
        return message

    # stop_hook_input의 content 필드
    content = stop_input.get("content", "")
    if isinstance(content, list):
        texts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(texts)

    return str(content) if content else ""


def main():
    try:
        stop_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    config = load_config()

    # 마지막 assistant 텍스트 추출
    text = extract_last_assistant_text(stop_input)

    # 빠른 필터: 최소 길이 미달 시 스킵
    min_length = config.get("min_content_length", 300)
    if len(text) < min_length:
        sys.exit(0)

    # Gemini Flash로 Plan 여부 분류
    plan_prompt = config.get(
        "plan_detection_prompt",
        "이 텍스트는 소프트웨어 개발 계획입니까? '예' 또는 '아니오'로만 답하시오.",
    )
    classification = call_gemini(
        content=text[:2000],  # 분류용이므로 앞부분만 전달
        prompt=plan_prompt,
        config=config,
    )

    # "예" 응답이 아니면 스킵
    if "예" not in classification:
        sys.exit(0)

    # Plan으로 감지됨 → 전체 평가
    eval_prompt = config.get("evaluation_prompt", "이 문서를 평가해줘.")

    # 비동기 모드: 백그라운드에서 평가, 즉시 리턴
    if config.get("async_mode", False):
        from a2a_bridge import call_gemini_async
        pending_msg = call_gemini_async(
            content=text, prompt=eval_prompt, config=config,
            source="Stop Hook (Plan 감지)",
        )
        print(format_hook_output(pending_msg))
        sys.exit(0)

    # 동기 모드: 평가 완료까지 대기
    feedback = call_gemini(
        content=text,
        prompt=eval_prompt,
        config=config,
    )

    # 피드백 저장
    save_feedback(feedback, source="Stop Hook (Plan 감지)")

    # Claude에 피드백 전달
    print(format_hook_output(feedback))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
