"""Hook I/O 유틸리티 — Hook stdout 포맷팅 및 파일 읽기.

a2a_bridge.py의 format_hook_output() + _read_file_content()를 분리한 모듈.
"""

import json
from pathlib import Path


def format_hook_output(feedback: str) -> str:
    """Claude Hook용 JSON stdout을 생성한다."""
    short = feedback[:500] if len(feedback) > 500 else feedback
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"[Gemini 평가] {short}"
        }
    }
    return json.dumps(output, ensure_ascii=False)


def read_file_content(file_path: str, max_chars: int = 50000) -> str:
    """파일 내용을 읽어 반환한다. SDK 호출 시 사용."""
    try:
        path = Path(file_path)
        if not path.exists():
            return f"[파일을 찾을 수 없습니다: {file_path}]"
        content = path.read_text(encoding="utf-8")
        if len(content) > max_chars:
            content = content[:max_chars] + f"\n\n... (truncated, {len(content)} chars total)"
        return content
    except Exception as e:
        return f"[파일 읽기 실패: {e}]"
