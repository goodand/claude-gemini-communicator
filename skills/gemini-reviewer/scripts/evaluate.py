#!/usr/bin/env python3
"""Gemini Reviewer — 독립 실행 가능한 코드/문서 평가 스크립트.

Agent Skill용 standalone 스크립트. a2a_bridge.py 의존 없이 동작합니다.
Codex CLI, Claude Code, Cursor 등 어떤 AI 코딩 도구에서든 사용 가능.

Usage:
    # 파일 리뷰
    python3 evaluate.py --file path/to/code.py
    python3 evaluate.py --file path/to/plan.md --mode doc

    # stdin 리뷰
    echo "코드 내용" | python3 evaluate.py --mode code

    # JSON 출력
    python3 evaluate.py --file code.py --format json

    # 커스텀 프롬프트
    python3 evaluate.py --file code.py --prompt "보안 취약점만 분석해줘"

    # 결과 저장
    python3 evaluate.py --file code.py --save
"""

import argparse
import json
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from _common import load_env, detect_mode, read_input, save_feedback, CODE_EXTENSIONS

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

# ── Exponential Backoff 설정 ──

RETRY_BASE = 1.0
RETRY_MAX_DELAY = 30.0
RETRY_MAX_ATTEMPTS = 3


def _retry_delay(attempt: int) -> float:
    """Exponential Backoff + jitter 지연 시간 계산."""
    return min(RETRY_BASE * (2 ** attempt) + random.random(), RETRY_MAX_DELAY)


def call_gemini_sdk(content: str, prompt: str) -> tuple[str | None, str]:
    """google-genai SDK로 Gemini 호출 + Exponential Backoff.

    Returns:
        (결과 텍스트 또는 None, 사용된 모델명)
    """
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None, ""

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        for k, v in os.environ.items():
            if k.startswith("GEMINI_API_KEY") and v:
                api_key = v
                break
    if not api_key:
        return None, ""

    full_prompt = f"{prompt}\n\n---\n{content}"
    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]

    for model in models:
        for attempt in range(RETRY_MAX_ATTEMPTS):
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
                    return text, model
            except Exception as e:
                err_str = str(e)
                status = getattr(e, "status_code", None) or getattr(e, "code", None)
                is_retryable = (
                    (status == 429)
                    or (status and int(str(status)) >= 500)
                    or "429" in err_str
                    or "500" in err_str
                    or "503" in err_str
                )
                if is_retryable and attempt < RETRY_MAX_ATTEMPTS - 1:
                    delay = _retry_delay(attempt)
                    print(
                        f"[RETRY] {model} attempt {attempt + 1}/{RETRY_MAX_ATTEMPTS}, "
                        f"대기 {delay:.1f}초...",
                        file=sys.stderr,
                    )
                    time.sleep(delay)
                    continue
                break  # non-retryable 또는 마지막 시도 → 다음 모델로

    return None, ""


def call_gemini_cli(content: str, prompt: str) -> tuple[str | None, str]:
    """Gemini CLI 폴백 호출."""
    import subprocess

    gemini_cmd = "/usr/local/bin/gemini"
    if not Path(gemini_cmd).exists():
        return None, ""

    full_prompt = f"{prompt}\n\n---\n{content[:10000]}"
    try:
        result = subprocess.run(
            [gemini_cmd, "-p", full_prompt],
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), "cli"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None, ""


def call_gemini(content: str, prompt: str) -> tuple[str, str]:
    """Gemini 호출 (CLI 계정 로그인 우선, SDK API key 폴백).

    Returns:
        (결과 텍스트, 사용된 모델명)
    """
    # 1) CLI 우선 (계정 로그인 — 기본/주 방식)
    result, model = call_gemini_cli(content, prompt)
    if result:
        return result, model

    # 2) SDK 폴백 (API key 방식)
    result, model = call_gemini_sdk(content, prompt)
    if result:
        return f"[FALLBACK] CLI 실패 → SDK 사용\n{result}", model

    print("[ERROR] Gemini 호출 실패. gemini CLI 로그인 또는 GEMINI_API_KEY를 확인하세요.", file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Gemini 코드/문서 리뷰")
    parser.add_argument("--file", "-f", help="리뷰할 파일 경로")
    parser.add_argument("--mode", "-m", choices=["code", "doc"], help="리뷰 모드 (자동 감지)")
    parser.add_argument("--prompt", "-p", help="커스텀 프롬프트")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="출력 형식 (기본: text)",
    )
    parser.add_argument("--save", "-s", action="store_true", help="gemini_feedback.md에 저장")
    args = parser.parse_args()

    load_env()

    # 내용 읽기
    content = read_input(args.file)

    # 모드 결정
    mode = args.mode or (detect_mode(args.file) if args.file else "doc")

    # 프롬프트 결정
    prompt = args.prompt or PROMPTS[mode]
    if args.file:
        prompt = f"{prompt}\n\n파일 경로: {args.file}"

    # Gemini 호출
    result, model_used = call_gemini(content, prompt)

    # 출력
    if args.format == "json":
        output = json.dumps(
            {
                "mode": mode,
                "file_path": args.file,
                "feedback": result,
                "model_used": model_used,
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        output = result

    print(output)

    # 저장
    if args.save:
        save_feedback(result, file_path=args.file)


if __name__ == "__main__":
    main()
