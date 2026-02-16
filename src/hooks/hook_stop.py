"""Stop Hook: Claude 응답 완료 시 (1) Plan 감지 (2) 에러 감지를 수행한다.

stdin으로 Claude Stop Hook JSON을 수신하고,
- 마지막 출력이 소프트웨어 개발 계획이면 Gemini 평가
- transcript에 반복 에러가 있으면 Gemini 에러 분석 (Lazy Analysis)
"""

import json
import os
import sys

# src/ 패키지 import를 위해 프로젝트 루트를 path에 추가
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.shared.config import load_config, load_env
from src.shared.feedback import save_feedback
from src.shared.hook_io import format_hook_output
from src.core.gemini_service import call_gemini, call_gemini_async
from src.core.a2a_protocol import (
    build_a2a_classification_prompt,
    build_a2a_evaluation_prompt,
    parse_a2a_response,
    a2a_response_to_markdown,
)
from src.core.error_analyzer import scan_transcript_for_errors, check_error_and_analyze


def extract_last_assistant_text(stop_input: dict) -> str:
    """Stop Hook 입력에서 Claude의 마지막 텍스트 출력을 추출한다."""
    transcript_path = stop_input.get("transcript_path", "")

    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
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

    message = stop_input.get("message", "")
    if message:
        return message

    content = stop_input.get("content", "")
    if isinstance(content, list):
        texts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(texts)

    return str(content) if content else ""


def handle_plan_detection(text: str, config: dict) -> str | None:
    """Plan 감지 → Gemini 평가. 피드백 문자열 또는 None 반환."""
    min_length = config.get("min_content_length", 300)
    if len(text) < min_length:
        return None

    plan_prompt = config.get(
        "plan_detection_prompt",
        "이 텍스트는 소프트웨어 개발 계획입니까? '예' 또는 '아니오'로만 답하시오.",
    )
    plan_prompt = build_a2a_classification_prompt(plan_prompt, config)
    classification = call_gemini(content=text[:2000], prompt=plan_prompt, config=config)

    is_plan = False
    if config.get("a2a_schema_enabled", False):
        try:
            parsed = json.loads(classification.strip().strip("`").replace("json", "", 1).strip())
            is_plan = parsed.get("is_plan", False)
        except (json.JSONDecodeError, ValueError):
            is_plan = "예" in classification
    else:
        is_plan = "예" in classification

    if not is_plan:
        return None

    eval_prompt = config.get("evaluation_prompt", "이 문서를 평가해줘.")
    eval_prompt = build_a2a_evaluation_prompt(eval_prompt, config)

    if config.get("async_mode", False):
        return call_gemini_async(
            content=text, prompt=eval_prompt, config=config,
            source="Stop Hook (Plan 감지)",
        )

    raw_feedback = call_gemini(content=text, prompt=eval_prompt, config=config)

    if config.get("a2a_schema_enabled", False):
        a2a_resp = parse_a2a_response(raw_feedback)
        feedback = a2a_response_to_markdown(a2a_resp)
    else:
        feedback = raw_feedback

    save_feedback(feedback, source="Stop Hook (Plan 감지)")
    return feedback


def handle_error_detection(stop_input: dict, config: dict) -> str | None:
    """Transcript에서 에러 스캔 → Lazy Analysis → Gemini 분석."""
    error_config = config.get("error_detection", {})
    if not error_config.get("enabled", False):
        return None

    transcript_path = stop_input.get("transcript_path", "")
    if not transcript_path:
        return None

    tail_lines = error_config.get("tail_lines", 50)
    errors = scan_transcript_for_errors(transcript_path, tail_lines)
    if not errors:
        return None

    return check_error_and_analyze(errors, config)


def main():
    load_env()

    try:
        stop_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    config = load_config()
    outputs = []

    # Plan 감지
    text = extract_last_assistant_text(stop_input)
    plan_feedback = handle_plan_detection(text, config)
    if plan_feedback:
        outputs.append(plan_feedback)

    # 에러 감지
    error_feedback = handle_error_detection(stop_input, config)
    if error_feedback:
        outputs.append(error_feedback)

    if outputs:
        combined = "\n\n".join(outputs)
        print(format_hook_output(combined))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
