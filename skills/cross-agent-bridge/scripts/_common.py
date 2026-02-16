#!/usr/bin/env python3
"""cross-agent-bridge 공용 유틸리티."""

import os
import sys
import fcntl
from datetime import datetime
from pathlib import Path


def load_env(env_path: Path = None):
    """프로젝트 루트의 .env 파일을 환경변수로 로드."""
    candidates = [env_path] if env_path else []
    candidates.extend([
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
    ])
    for candidate in candidates:
        if candidate and candidate.exists():
            try:
                for line in candidate.read_text("utf-8").splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, _, value = line.partition("=")
                    key, value = key.strip(), value.strip().strip("\"'")
                    if key and key not in os.environ:
                        os.environ[key] = value
            except IOError:
                pass
            break


def read_input(file_path: str = None, max_chars: int = 50000) -> str | None:
    """파일 또는 stdin에서 내용을 읽음."""
    if file_path:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] 파일 없음: {file_path}", file=sys.stderr)
            return None
        try:
            content = path.read_text(encoding="utf-8")
            if len(content) > max_chars:
                content = content[:max_chars] + f"\n\n... (truncated, {len(content)} chars)"
            return content
        except IOError as e:
            print(f"[ERROR] 파일 읽기 실패: {e}", file=sys.stderr)
            return None
    if not sys.stdin.isatty():
        try:
            return sys.stdin.read()
        except IOError as e:
            print(f"[ERROR] stdin 읽기 실패: {e}", file=sys.stderr)
            return None
    return None


def save_feedback(feedback: str, source: str, file_path: str = None):
    """gemini_feedback.md에 피드백을 추가 (fcntl lock)."""
    feedback_path = Path.cwd() / "plans" / "gemini" / "gemini_feedback.md"
    for candidate in [feedback_path, Path(__file__).resolve().parent.parent.parent.parent / "plans" / "gemini" / "gemini_feedback.md"]:
        if candidate.parent.exists():
            feedback_path = candidate
            break
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target = f" | 대상: `{file_path}`" if file_path else ""
    entry = f"\n---\n\n## [{timestamp}] {source}{target}\n\n{feedback}\n"
    try:
        feedback_path.parent.mkdir(parents=True, exist_ok=True)
        with open(feedback_path, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.write(entry)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except IOError as e:
        print(f"[ERROR] 피드백 저장 실패: {e}", file=sys.stderr)
