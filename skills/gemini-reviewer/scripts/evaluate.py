#!/usr/bin/env python3
"""Gemini Reviewer — 독립 실행 가능한 Gemini 코드/문서 평가 스크립트.

Agent Skill용 standalone 스크립트. a2a_bridge.py 의존 없이 동작합니다.
Codex CLI, Claude Code, Cursor 등 어떤 AI 코딩 도구에서든 사용 가능.

Usage:
    # 파일 리뷰
    python3 evaluate.py --file path/to/code.py
    python3 evaluate.py --file path/to/plan.md --mode doc

    # stdin 리뷰
    echo "코드 내용" | python3 evaluate.py --mode code

    # 커스텀 프롬프트
    python3 evaluate.py --file code.py --prompt "보안 취약점만 분석해줘"

    # 결과 저장
    python3 evaluate.py --file code.py --save
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── 기본 프롬프트 ──

PROMPTS = {
    "code": (
        "다음 코드를 리뷰해줘:\n"
        "- 버그 또는 잠재적 오류\n"
        "- 보안 취약점 (인젝션, 하드코딩된 비밀 등)\n"
        "- 에러 처리 누락\n"
        "- 개선 제안\n"
        "간결하게 한국어로 답해줘."
    ),
    "doc": (
        "다음 문서를 평가해줘:\n"
        "- 논리적 일관성\n"
        "- 실현 가능성\n"
        "- 누락된 고려사항\n"
        "- 개선 제안\n"
        "간결하게 한국어로 답해줘."
    ),
}

CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".c", ".cpp", ".rb", ".sh"}


def detect_mode(file_path: str) -> str:
    """파일 확장자로 모드를 자동 감지합니다."""
    ext = Path(file_path).suffix.lower()
    return "code" if ext in CODE_EXTENSIONS else "doc"


def read_content(file_path: str = None) -> str:
    """파일 또는 stdin에서 내용을 읽습니다."""
    if file_path:
        path = Path(file_path)
        if not path.exists():
            print(f"[ERROR] 파일 없음: {file_path}", file=sys.stderr)
            sys.exit(1)
        content = path.read_text(encoding="utf-8")
        if len(content) > 50000:
            content = content[:50000] + f"\n\n... (truncated, {len(content)} chars)"
        return content
    elif not sys.stdin.isatty():
        return sys.stdin.read()
    else:
        print("[ERROR] --file 또는 stdin 입력이 필요합니다.", file=sys.stderr)
        sys.exit(1)


def load_env():
    """프로젝트 루트의 .env 파일을 로드합니다."""
    for candidate in [Path.cwd() / ".env", Path(__file__).parent.parent.parent.parent / ".env"]:
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


def call_gemini_sdk(content: str, prompt: str) -> str:
    """google-genai SDK로 Gemini를 호출합니다."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        # 추가 키 탐색
        for k, v in os.environ.items():
            if k.startswith("GEMINI_API_KEY") and v:
                api_key = v
                break

    if not api_key:
        return None

    full_prompt = f"{prompt}\n\n---\n{content}"
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    for model in models:
        try:
            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(
                model=model,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.3,
                    http_options=types.HttpOptions(timeout=90000),
                ),
            )
            text = response.text.strip() if response.text else ""
            if text:
                return text
        except Exception:
            continue

    return None


def call_gemini_cli(content: str, prompt: str) -> str:
    """Gemini CLI로 호출합니다 (SDK 불가 시 폴백)."""
    import subprocess

    gemini_cmd = "/usr/local/bin/gemini"
    if not Path(gemini_cmd).exists():
        return None

    full_prompt = f"{prompt}\n\n---\n{content[:10000]}"
    try:
        result = subprocess.run(
            [gemini_cmd, full_prompt],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def call_gemini(content: str, prompt: str) -> str:
    """Gemini 호출 (SDK 우선, CLI 폴백)."""
    result = call_gemini_sdk(content, prompt)
    if result:
        return result

    result = call_gemini_cli(content, prompt)
    if result:
        return f"[CLI] {result}"

    print("[ERROR] Gemini 호출 실패. GEMINI_API_KEY를 확인하세요.", file=sys.stderr)
    sys.exit(1)


def save_feedback(feedback: str, file_path: str = None):
    """gemini_feedback.md에 결과를 저장합니다."""
    feedback_path = Path.cwd() / "gemini_feedback.md"
    # 프로젝트 루트 탐색
    for candidate in [feedback_path, Path(__file__).parent.parent.parent.parent / "gemini_feedback.md"]:
        if candidate.parent.exists():
            feedback_path = candidate
            break

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target = f" | 대상: `{file_path}`" if file_path else ""
    entry = f"\n---\n\n## [{timestamp}] Gemini Reviewer Skill{target}\n\n{feedback}\n"

    with open(feedback_path, "a", encoding="utf-8") as f:
        f.write(entry)
    print(f"[저장됨] {feedback_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Gemini 코드/문서 리뷰")
    parser.add_argument("--file", "-f", help="리뷰할 파일 경로")
    parser.add_argument("--mode", "-m", choices=["code", "doc"], help="리뷰 모드 (자동 감지)")
    parser.add_argument("--prompt", "-p", help="커스텀 프롬프트")
    parser.add_argument("--save", "-s", action="store_true", help="gemini_feedback.md에 저장")
    args = parser.parse_args()

    load_env()

    # 내용 읽기
    content = read_content(args.file)

    # 모드 결정
    mode = args.mode
    if not mode:
        mode = detect_mode(args.file) if args.file else "doc"

    # 프롬프트 결정
    if args.prompt:
        prompt = args.prompt
    else:
        prompt = PROMPTS[mode]

    if args.file:
        prompt = f"{prompt}\n\n파일 경로: {args.file}"

    # Gemini 호출
    result = call_gemini(content, prompt)
    print(result)

    # 저장
    if args.save:
        save_feedback(result, args.file)


if __name__ == "__main__":
    main()
