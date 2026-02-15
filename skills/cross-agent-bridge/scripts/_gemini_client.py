#!/usr/bin/env python3
"""Gemini SDK/CLI 클라이언트 — Exponential Backoff + 모델 순회."""

import os
import random
import subprocess
import sys
import time
from pathlib import Path

# Retry 설정
RETRY_BASE = 1.0
RETRY_MAX_DELAY = 30.0
RETRY_MAX_ATTEMPTS = 3


def _retry_delay(attempt: int) -> float:
    """Exponential Backoff + jitter."""
    return min(RETRY_BASE * (2 ** attempt) + random.random(), RETRY_MAX_DELAY)


def _sdk_available() -> bool:
    """google-genai SDK 설치 여부."""
    try:
        from google import genai  # noqa: F401
        return True
    except ImportError:
        return False


def _get_api_keys(sdk_config: dict) -> list:
    """환경변수에서 API key 목록 수집."""
    keys = []
    main_env = sdk_config.get("api_key_env", "GEMINI_API_KEY")
    main_key = os.environ.get(main_env)
    if main_key:
        keys.append(main_key)
    for env_name, value in os.environ.items():
        if env_name.startswith("GEMINI_API_KEY_") and value and value not in keys:
            keys.append(value)
    return keys


def _get_models(sdk_config: dict) -> list:
    """사용할 모델 목록 (메인 + 폴백)."""
    main_model = sdk_config.get("model", "gemini-2.5-flash")
    fallback = sdk_config.get("fallback_models", ["gemini-2.0-flash", "gemini-1.5-flash"])
    models = [main_model]
    for m in fallback:
        if m not in models:
            models.append(m)
    return models


def _call_sdk(full_prompt: str, config: dict) -> tuple[str | None, str]:
    """API key + SDK 호출. 429/5xx Exponential Backoff. Returns (result, model)."""
    from google import genai
    from google.genai import types

    sdk_config = config.get("sdk", {})
    timeout = config.get("gemini_timeout", 90)
    api_keys = _get_api_keys(sdk_config)
    models = _get_models(sdk_config)

    if not api_keys:
        return None, ""

    for api_key in api_keys:
        client = genai.Client(api_key=api_key)
        for model_name in models:
            for attempt in range(RETRY_MAX_ATTEMPTS):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            max_output_tokens=sdk_config.get("max_output_tokens", 2048),
                            temperature=sdk_config.get("temperature", 0.3),
                            http_options=types.HttpOptions(timeout=timeout * 1000),
                        ),
                    )
                    text = response.text.strip() if response.text else ""
                    if text:
                        return text, model_name
                except Exception as e:
                    status = getattr(e, "status_code", None) or getattr(e, "code", None)
                    err_str = str(e)
                    is_retryable = (
                        status == 429
                        or (status and int(str(status)) >= 500)
                        or "429" in err_str
                        or "500" in err_str
                        or "503" in err_str
                    )
                    if is_retryable and attempt < RETRY_MAX_ATTEMPTS - 1:
                        delay = _retry_delay(attempt)
                        print(f"[RETRY] {model_name} attempt {attempt+1}, 대기 {delay:.1f}초...", file=sys.stderr)
                        time.sleep(delay)
                        continue
                    break  # non-retryable → next model
    return None, ""


def _call_cli(full_prompt: str, config: dict) -> tuple[str | None, str]:
    """Gemini CLI subprocess 호출."""
    gemini_cmd = config.get("gemini_cmd", "/usr/local/bin/gemini")
    timeout = config.get("gemini_timeout", 90)

    if not Path(gemini_cmd).exists():
        return None, ""

    try:
        result = subprocess.run(
            [gemini_cmd, full_prompt[:10000]],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), "cli"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None, ""


def call_gemini(content: str, prompt: str, config: dict, file_path: str = None) -> tuple[str, str]:
    """Gemini 호출 오케스트레이터: SDK → CLI 폴백.

    Returns: (result_text, model_used)
    """
    sdk_config = config.get("sdk", {})
    sdk_enabled = sdk_config.get("enabled", True)
    fallback_to_cli = sdk_config.get("fallback_to_cli", True)

    # 프롬프트 구성
    if file_path:
        full_prompt = f"{prompt}\n\n파일 경로: {file_path}\n\n파일 내용:\n{content}"
    else:
        full_prompt = f"{prompt}\n\n---\n{content}"

    # SDK 시도
    if sdk_enabled and _sdk_available():
        result, model = _call_sdk(full_prompt, config)
        if result:
            return result, model
        if fallback_to_cli:
            result, model = _call_cli(full_prompt, config)
            if result:
                return f"[FALLBACK] {result}", "cli"
        return "[ERROR] 모든 SDK/CLI 호출 실패", ""

    # CLI 직접 호출
    result, model = _call_cli(full_prompt, config)
    if result:
        return result, model
    return "[ERROR] Gemini CLI 호출 실패", ""
