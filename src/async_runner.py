"""Async Runner: 백그라운드에서 Gemini 호출을 실행한다.

call_gemini_async()에 의해 별도 프로세스로 spawn된다.
인자는 JSON 파일로 전달받고, 완료 후 파일을 삭제한다.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# src/ 패키지 import를 위해 프로젝트 루트를 path에 추가
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    args_path = sys.argv[1]

    try:
        with open(args_path, "r", encoding="utf-8") as f:
            args = json.load(f)
    except (json.JSONDecodeError, IOError):
        sys.exit(1)
    finally:
        try:
            os.unlink(args_path)
        except OSError:
            pass

    from src.shared.config import load_env
    from src.core.gemini_service import call_gemini

    load_env()

    content = args.get("content", "")
    prompt = args.get("prompt", "")
    config = args.get("config", {})
    file_path = args.get("file_path")
    source = args.get("source", "Async")
    feedback_path = args.get("feedback_path")

    # async_mode를 False로 오버라이드하여 재귀 방지
    config["async_mode"] = False

    try:
        feedback = call_gemini(content, prompt, config, file_path)
    except Exception as e:
        feedback = f"[ASYNC_ERROR] 백그라운드 Gemini 호출 실패: {e}"

    if feedback_path:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        target_info = f" | 대상: `{file_path}`" if file_path else ""
        entry = f"\n---\n\n## [{timestamp}] {source} (비동기){target_info}\n\n{feedback}\n"

        try:
            with open(feedback_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except IOError:
            pass


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
