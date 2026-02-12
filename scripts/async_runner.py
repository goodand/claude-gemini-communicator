"""Async Runner: 백그라운드에서 Gemini 호출을 실행합니다.

call_gemini_async()에 의해 별도 프로세스로 spawn됩니다.
인자는 JSON 파일로 전달받고, 완료 후 파일을 삭제합니다.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        sys.exit(1)

    args_path = sys.argv[1]

    # 인자 읽기
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

    # 브릿지 모듈 임포트
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from a2a_bridge import call_gemini

    content = args.get("content", "")
    prompt = args.get("prompt", "")
    config = args.get("config", {})
    file_path = args.get("file_path")
    source = args.get("source", "Async")
    feedback_path = args.get("feedback_path")

    # async_mode를 False로 오버라이드하여 재귀 방지
    config["async_mode"] = False

    # Gemini 호출 (이 프로세스 자체가 비동기 핸들러이므로 동기 호출)
    try:
        feedback = call_gemini(content, prompt, config, file_path)
    except Exception as e:
        feedback = f"[ASYNC_ERROR] 백그라운드 Gemini 호출 실패: {e}"

    # 피드백 저장
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
