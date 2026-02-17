"""이전 피드백 컨텍스트 빌더 — 프롬프트에 과거 피드백을 주입하여 중복 방지."""

import json
from pathlib import Path

from src.shared.config import get_jsonl_path


def build_feedback_context(config: dict,
                           file_path: str | None = None,
                           max_entries: int = 3) -> str:
    """최근 피드백을 요약하여 프롬프트 컨텍스트로 반환한다.

    1. JSONL에서 최근 evaluation_response 이벤트 조회
    2. file_path가 있으면 해당 파일 관련만 필터
    3. 최대 max_entries건의 피드백 요약 생성
    4. 빈 문자열이면 이전 피드백 없음
    """
    fc_config = config.get("feedback_context", {})
    if not fc_config.get("enabled", False):
        return ""

    max_entries = fc_config.get("max_entries", max_entries)

    jsonl_config = config.get("jsonl_bus", {})
    if not jsonl_config.get("enabled"):
        return ""

    jsonl_path = get_jsonl_path(config)
    if not jsonl_path.exists():
        return ""

    # JSONL에서 evaluation_response 이벤트 수집
    responses = []
    try:
        for line in jsonl_path.read_text("utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("message_type") != "evaluation_response":
                continue

            # file_path 필터
            if file_path and event.get("file_path") and event["file_path"] != file_path:
                continue

            feedback = event.get("feedback", "")
            if not feedback or feedback.startswith("["):
                continue

            responses.append({
                "timestamp": event.get("timestamp", "")[:16],
                "feedback": feedback[:200].replace("\n", " ").strip(),
                "file_path": event.get("file_path", ""),
            })
    except IOError:
        return ""

    if not responses:
        return ""

    # 최근 N건만
    recent = responses[-max_entries:]

    lines = ["[이전 피드백 컨텍스트]"]
    for r in recent:
        fp_info = f" ({r['file_path']})" if r["file_path"] else ""
        lines.append(f"- {r['timestamp']}: \"{r['feedback']}\"{fp_info}")
    lines.append("위 피드백을 참고하여 중복되지 않는 새로운 관점으로 평가하라.")

    return "\n".join(lines)
