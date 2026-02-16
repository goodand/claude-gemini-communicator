"""피드백 저장 — fcntl 파일 락으로 동시 쓰기 보호.

a2a_bridge.py의 save_feedback()를 분리한 모듈.
프로젝트 내 유일한 정본 (skills/는 자체 _common.py 복사본 사용).
"""

import fcntl
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
FEEDBACK_PATH = PROJECT_ROOT / "plans" / "gemini" / "gemini_feedback.md"


def save_feedback(feedback: str, source: str, file_path: str | None = None) -> None:
    """gemini_feedback.md에 피드백을 추가한다 (file lock으로 동시 쓰기 보호)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_info = f" | 대상: `{file_path}`" if file_path else ""

    entry = f"\n---\n\n## [{timestamp}] {source}{target_info}\n\n{feedback}\n"

    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(entry)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
