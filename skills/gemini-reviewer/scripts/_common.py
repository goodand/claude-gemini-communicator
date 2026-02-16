#!/usr/bin/env python3
"""gemini-reviewer 공용 유틸리티."""

import fcntl
import os
import sys
from datetime import datetime
from pathlib import Path

CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".jsx", ".tsx",
    ".java", ".go", ".rs", ".c", ".cpp", ".rb", ".sh",
}


def load_env():
    """프로젝트 루트의 .env 파일을 로드."""
    for candidate in [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
    ]:
        if candidate.exists():
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


def detect_mode(file_path: str) -> str:
    """파일 확장자로 code/doc 모드를 자동 감지."""
    return "code" if Path(file_path).suffix.lower() in CODE_EXTENSIONS else "doc"


def read_input(file_path: str = None, max_chars: int = 50000) -> str:
    """파일 또는 stdin에서 내용을 읽음."""
    if file_path:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] 파일 없음: {file_path}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... (truncated, {len(content)} chars)"
        return content
    if not sys.stdin.isatty():
        return sys.stdin.read()
    print("[ERROR] --file 또는 stdin 입력이 필요합니다.", file=sys.stderr)
    sys.exit(1)


def save_feedback(feedback: str, source: str = "Gemini Reviewer Skill", file_path: str = None):
    """gemini_feedback.md에 결과를 저장 (fcntl lock)."""
    feedback_path = Path.cwd() / "plans" / "gemini" / "gemini_feedback.md"
    for candidate in [
        feedback_path,
        Path(__file__).resolve().parent.parent.parent.parent / "plans" / "gemini" / "gemini_feedback.md",
    ]:
        if candidate.parent.exists():
            feedback_path = candidate
            break

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target = f" | 대상: `{file_path}`" if file_path else ""
    entry = f"\n---\n\n## [{timestamp}] {source}{target}\n\n{feedback}\n"

    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    with open(feedback_path, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(entry)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    print(f"[저장됨] {feedback_path}", file=sys.stderr)
