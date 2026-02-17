"""피드백 저장 — fcntl 파일 락으로 동시 쓰기 보호.

a2a_bridge.py의 save_feedback()를 분리한 모듈.
프로젝트 내 유일한 정본 (skills/는 자체 _common.py 복사본 사용).
"""

import fcntl
import json
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FEEDBACK_PATH = PROJECT_ROOT / "plans" / "gemini" / "gemini_feedback.md"


def save_feedback(feedback: str, source: str, file_path: str | None = None,
                  request_id: str | None = None,
                  jsonl_config: dict | None = None,
                  a2a_envelope: dict | None = None) -> None:
    """gemini_feedback.md에 피드백을 추가한다 (file lock으로 동시 쓰기 보호).

    jsonl_config가 enabled이면 JSONL 파일에도 병행 기록한다.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_info = f" | 대상: `{file_path}`" if file_path else ""
    rid_info = f" | request_id: {request_id}" if request_id else ""

    entry = f"\n---\n\n## [{timestamp}] {source}{target_info}{rid_info}\n\n{feedback}\n"

    # 1) Markdown append (기존 유지)
    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(entry)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)

    # 2) JSONL append (jsonl_config.enabled == true일 때)
    if jsonl_config and jsonl_config.get("enabled"):
        _append_jsonl(jsonl_config, feedback, source, file_path,
                      request_id, a2a_envelope)


def _append_jsonl(jsonl_config: dict, feedback: str, source: str,
                  file_path: str | None, request_id: str | None,
                  a2a_envelope: dict | None) -> None:
    """JSONL 파일에 구조화된 이벤트를 추가한다."""
    jsonl_path = PROJECT_ROOT / jsonl_config.get("path", "plans/gemini/a2a_events.jsonl")
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "request_id": request_id,
        "file_path": file_path,
        "feedback": feedback,
    }
    # a2a_envelope 필드 병합 (message_type, source_agent 등)
    if a2a_envelope:
        record.update(a2a_envelope)

    line = json.dumps(record, ensure_ascii=False) + "\n"

    with open(jsonl_path, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(line)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
