#!/usr/bin/env python3
"""agent-parser 공용 유틸리티."""

import os
import sys
from datetime import datetime
from pathlib import Path

# 크로스플랫폼 파일 락
if os.name == "nt":
    import msvcrt
    def _lock(f): msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    def _unlock(f): msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:
    import fcntl
    def _lock(f): fcntl.flock(f, fcntl.LOCK_EX)
    def _unlock(f): fcntl.flock(f, fcntl.LOCK_UN)


def read_input(file_path: str = None) -> str | None:
    """파일 또는 stdin에서 텍스트를 읽는다."""
    if file_path:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] 파일 없음: {file_path}", file=sys.stderr)
            return None
        try:
            return path.read_text(encoding="utf-8")
        except IOError as e:
            print(f"[ERROR] 파일 읽기 실패: {e}", file=sys.stderr)
            return None
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except IOError as e:
            print(f"[ERROR] stdin 읽기 실패: {e}", file=sys.stderr)
            return None
    print("[ERROR] --file 또는 stdin 입력이 필요합니다.", file=sys.stderr)
    return None


def save_feedback(content: str, source_desc: str):
    """gemini_feedback.md에 결과를 append (크로스플랫폼 lock)."""
    feedback_path = Path.cwd() / "plans" / "gemini" / "gemini_feedback.md"
    for candidate in [feedback_path, Path(__file__).resolve().parent.parent.parent.parent / "plans" / "gemini" / "gemini_feedback.md"]:
        if candidate.parent.exists():
            feedback_path = candidate
            break
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] {source_desc}\n\n{content}\n"
    try:
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        with open(feedback_path, "a", encoding="utf-8") as f:
            _lock(f)
            try:
                f.write(entry)
            finally:
                _unlock(f)
        print(f"[저장됨] {feedback_path}", file=sys.stderr)
    except IOError as e:
        print(f"[ERROR] 저장 실패: {e}", file=sys.stderr)


def shorten_text(text: str, max_chars: int = 240) -> str:
    """텍스트를 한 줄 요약으로 정규화하고 길이를 제한."""
    normalized = " ".join(str(text).split())
    if not normalized:
        return "(없음)"
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."
