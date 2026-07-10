"""PostToolUse Hook: Write/Edit 도구 사용 후 자동으로 Gemini 평가를 트리거한다.

stdin으로 Claude Hook JSON을 수신하고, .md 파일 변경 시 Gemini 평가.
"""

import json
import os
import sys
import uuid

# src/ 패키지 import를 위해 프로젝트 루트를 path에 추가
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.shared.config import load_config, load_env
from src.shared.feedback import save_feedback, log_jsonl_event
from src.shared.hook_io import format_hook_output
from src.core.cooldown import check_cooldown
from src.core.llm_registry import get_provider
from src.core.a2a_protocol import (
    build_a2a_request,
    build_a2a_evaluation_prompt,
    parse_a2a_response,
    a2a_response_to_markdown,
)
from src.core.router import resolve_target
from src.core.feedback_context import build_feedback_context

# GeminiProvider 모듈 로드 → 레지스트리 자동 등록
import src.core.gemini_service  # noqa: F401


def main():
    load_env()

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
    if not config.get("auto_hooks_enabled", True):
        sys.exit(0)

    # 확장자 확인
    extensions = config.get("watch_extensions", [".md"])
    if not any(file_path.endswith(ext) for ext in extensions):
        sys.exit(0)

    # 제외 파일 확인 (basename 또는 경로 부분 매칭)
    exclude_files = config.get("exclude_files", [])
    basename = os.path.basename(file_path)
    if any(basename == os.path.basename(ex) or file_path.endswith(ex)
           for ex in exclude_files):
        sys.exit(0)

    # 쿨다운 확인
    if not check_cooldown(file_path, config):
        sys.exit(0)

    # 프롬프트 결정
    code_exts = config.get("code_extensions", [".py", ".js", ".ts", ".jsx", ".tsx"])
    if any(file_path.endswith(ext) for ext in code_exts):
        prompt = config.get("code_evaluation_prompt", "이 코드를 리뷰해줘.")
    else:
        prompt = config.get("evaluation_prompt", "이 문서를 평가해줘.")
    prompt = build_a2a_evaluation_prompt(prompt, config)

    # 피드백 컨텍스트 주입
    context = build_feedback_context(config, file_path=file_path)
    if context:
        prompt = context + "\n\n" + prompt

    # 라우팅: 대상 에이전트 결정
    target_agent = resolve_target("evaluation_request", config, file_path=file_path)
    provider = get_provider(target_agent)

    # 비동기 모드
    if config.get("async_mode", False):
        pending_msg = provider.call_async(
            content="", prompt=prompt, config=config,
            file_path=file_path, source="PostToolUse Hook",
        )
        print(format_hook_output(pending_msg))
        sys.exit(0)

    # 동기 모드: 요청 엔벨로프 생성 + JSONL 기록
    req_envelope = build_a2a_request(
        "evaluation_request", {"file_path": file_path}, hook_source="PostToolUse",
        target_agent=target_agent,
    )
    request_id = req_envelope["request_id"]
    req_message_id = req_envelope["message_id"]

    # 요청 이벤트 JSONL 기록
    jsonl_config = config.get("jsonl_bus")
    log_jsonl_event(jsonl_config, {
        "message_id": req_message_id,
        "request_id": request_id,
        "message_type": "evaluation_request",
        "source_agent": "claude",
        "target_agent": target_agent,
        "source": "PostToolUse Hook",
        "file_path": file_path,
    })

    raw_feedback = provider.call(
        content="", prompt=prompt, config=config, file_path=file_path,
    )

    # A2A 모드: 구조화된 응답 파싱
    if config.get("a2a_schema_enabled", False):
        a2a_resp = parse_a2a_response(raw_feedback, request_id=request_id)
        feedback = a2a_response_to_markdown(a2a_resp)
    else:
        feedback = raw_feedback

    a2a_envelope = {
        "message_id": str(uuid.uuid4()),
        "message_type": "evaluation_response",
        "source_agent": target_agent,
        "target_agent": "claude",
        "parent_message_id": req_message_id,
    }
    save_feedback(feedback, source="PostToolUse Hook", file_path=file_path,
                  request_id=request_id, jsonl_config=jsonl_config,
                  a2a_envelope=a2a_envelope)
    print(format_hook_output(feedback))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
