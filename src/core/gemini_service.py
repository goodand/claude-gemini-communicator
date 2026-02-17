"""Gemini 호출 서비스 — SDK/CLI 이중화 + 비동기.

a2a_bridge.py의 call_gemini 관련 함수들을 분리한 모듈.
인증 우선순위: API key → OAuth (REST API) → CLI fallback.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from src.shared.config import PROJECT_ROOT, load_env
from src.shared.hook_io import read_file_content
from src.core.llm_base import LLMProvider
from src.core.llm_registry import register

SRC_DIR = PROJECT_ROOT / "src"


def _sdk_available() -> bool:
    """google-genai SDK가 설치되어 있는지 확인한다."""
    try:
        from google import genai  # noqa: F401
        return True
    except ImportError:
        return False


def _build_prompt(content: str, prompt: str, file_path: str | None = None) -> str:
    """SDK/REST 공통 프롬프트를 구성한다."""
    if file_path:
        file_content = read_file_content(file_path)
        return f"{prompt}\n\n파일 경로: {file_path}\n\n파일 내용:\n{file_content}"
    else:
        return f"{prompt}\n\n---\n{content}"


def _get_api_keys(sdk_config: dict) -> list:
    """환경변수에서 사용 가능한 API key 목록을 수집한다."""
    keys = []
    main_env = sdk_config.get("api_key_env", "GEMINI_API_KEY")
    main_key = os.environ.get(main_env)
    if main_key:
        keys.append(main_key)
    for env_name, value in os.environ.items():
        if env_name.startswith("GEMINI_API_KEY_") and value and value not in keys:
            keys.append(value)
    return keys


def _get_fallback_models(sdk_config: dict) -> list:
    """사용할 모델 목록을 반환한다 (메인 모델 + 폴백)."""
    main_model = sdk_config.get("model", "gemini-2.5-flash")
    fallback_models = sdk_config.get("fallback_models", ["gemini-2.0-flash", "gemini-1.5-flash"])
    models = [main_model]
    for m in fallback_models:
        if m not in models:
            models.append(m)
    return models


def _call_gemini_with_api_key(full_prompt: str, config: dict) -> str:
    """API key를 사용하여 google-genai SDK로 호출한다.

    429 Rate Limit 발생 시 다른 키/모델로 자동 전환.
    """
    from google import genai
    from google.genai import types
    from google.genai.errors import ClientError

    sdk_config = config.get("sdk", {})
    timeout = config.get("gemini_timeout", 90)
    api_keys = _get_api_keys(sdk_config)
    models = _get_fallback_models(sdk_config)

    if not api_keys:
        return "[SDK_ERROR] 사용 가능한 API key가 없습니다."

    last_error = None
    for api_key in api_keys:
        client = genai.Client(api_key=api_key)
        for model_name in models:
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
                if not text:
                    continue
                return text
            except ClientError as e:
                last_error = e
                if e.status_code == 429:
                    continue
                raise

    return f"[SDK_ERROR] 모든 API key/모델 조합에서 실패: {last_error}"


def _call_gemini_with_oauth(full_prompt: str, config: dict) -> str:
    """OAuth 자격 증명을 사용하여 Gemini REST API를 직접 호출한다."""
    import httpx
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    sdk_config = config.get("sdk", {})
    model_name = sdk_config.get("model", "gemini-2.0-flash")
    timeout = config.get("gemini_timeout", 90)

    creds_path = Path(
        os.environ.get("GEMINI_OAUTH_CREDS_PATH",
                        sdk_config.get("oauth_creds_path", "~/.gemini/oauth_creds.json"))
    ).expanduser()

    if not creds_path.exists():
        raise RuntimeError("OAuth credentials 파일 없음")

    try:
        with open(creds_path, "r", encoding="utf-8") as f:
            oauth_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        raise RuntimeError("OAuth credentials 로드 실패")

    refresh_token = oauth_data.get("refresh_token")
    if not refresh_token:
        raise RuntimeError("OAuth refresh_token 없음")

    client_id_env = sdk_config.get("oauth_client_id_env", "GEMINI_OAUTH_CLIENT_ID")
    client_secret_env = sdk_config.get("oauth_client_secret_env", "GEMINI_OAUTH_CLIENT_SECRET")
    client_id = os.environ.get(client_id_env, "")
    client_secret = os.environ.get(client_secret_env, "")

    if not client_id or not client_secret:
        raise RuntimeError("OAuth client_id/secret 미설정")

    scopes = oauth_data.get("scope", "").split()
    creds = Credentials(
        token=oauth_data.get("access_token"),
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )

    if creds.expired or not creds.token:
        creds.refresh(Request())

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}
    body = {
        "contents": [{"parts": [{"text": full_prompt}]}],
        "generationConfig": {
            "maxOutputTokens": sdk_config.get("max_output_tokens", 2048),
            "temperature": sdk_config.get("temperature", 0.3),
        },
    }

    resp = httpx.post(url, json=body, headers=headers, timeout=timeout)
    resp.raise_for_status()

    data = resp.json()
    candidates = data.get("candidates", [])
    if not candidates:
        return "[SDK_ERROR] Gemini REST API 응답에 candidates가 없습니다."

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(p.get("text", "") for p in parts).strip()
    if not text:
        return "[SDK_ERROR] Gemini REST API 응답이 비어있습니다."
    return text


def _call_gemini_sdk(content: str, prompt: str, config: dict,
                     file_path: str | None = None) -> str:
    """SDK 또는 REST API를 사용하여 Gemini를 호출한다."""
    sdk_config = config.get("sdk", {})
    full_prompt = _build_prompt(content, prompt, file_path)

    api_key_env = sdk_config.get("api_key_env", "GEMINI_API_KEY")
    api_key = os.environ.get(api_key_env)

    if api_key:
        return _call_gemini_with_api_key(full_prompt, config)
    else:
        return _call_gemini_with_oauth(full_prompt, config)


def _call_gemini_cli(content: str, prompt: str, config: dict,
                     file_path: str | None = None) -> str:
    """Gemini CLI subprocess를 호출한다."""
    gemini_cmd = config.get("gemini_cmd", "/usr/local/bin/gemini")
    timeout = config.get("gemini_timeout", 90)

    if file_path:
        full_prompt = f"{prompt}\n\n파일 경로: {file_path}"
    else:
        full_prompt = f"{prompt}\n\n---\n{content}"

    try:
        result = subprocess.run(
            [gemini_cmd, full_prompt],
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()
            return f"[ERROR] Gemini CLI 호출 실패 (exit code {result.returncode}): {stderr}"

        output = result.stdout.strip()
        if not output:
            return "[ERROR] Gemini CLI 응답이 비어있습니다."
        return output

    except subprocess.TimeoutExpired:
        return f"[ERROR] Gemini CLI 호출 타임아웃 ({timeout}초 초과)"
    except FileNotFoundError:
        return f"[ERROR] Gemini CLI를 찾을 수 없습니다: {gemini_cmd}"
    except Exception as e:
        return f"[ERROR] Gemini CLI 호출 중 예외 발생: {e}"


class GeminiProvider(LLMProvider):
    """Gemini LLM 프로바이더 — SDK/CLI 이중화."""

    def call(self, content: str, prompt: str, config: dict,
             file_path: str | None = None) -> str:
        return call_gemini(content, prompt, config, file_path)

    def call_async(self, content: str, prompt: str, config: dict,
                   file_path: str | None = None,
                   source: str = "Async") -> str:
        return call_gemini_async(content, prompt, config, file_path, source)


# 모듈 로드 시 자동 등록
register("gemini", GeminiProvider)


def call_gemini(content: str, prompt: str, config: dict,
                file_path: str | None = None) -> str:
    """Gemini를 호출하여 평가를 받는다.

    SDK 우선 호출, 실패 시 CLI 폴백.
    """
    sdk_config = config.get("sdk", {})
    sdk_enabled = sdk_config.get("enabled", True)
    fallback_to_cli = sdk_config.get("fallback_to_cli", True)

    if sdk_enabled and _sdk_available():
        try:
            result = _call_gemini_sdk(content, prompt, config, file_path)
            if not result.startswith("[SDK_ERROR]"):
                return result
        except Exception as e:
            result = f"[SDK_ERROR] {e}"

        if fallback_to_cli:
            cli_result = _call_gemini_cli(content, prompt, config, file_path)
            return f"[FALLBACK] SDK 실패 → CLI 사용\n{cli_result}"
        else:
            return result

    return _call_gemini_cli(content, prompt, config, file_path)


def call_gemini_async(content: str, prompt: str, config: dict,
                      file_path: str | None = None,
                      source: str = "Async") -> str:
    """비동기 모드: 별도 프로세스에서 Gemini 호출 (fire-and-forget)."""
    from src.shared.feedback import FEEDBACK_PATH

    args = {
        "content": content,
        "prompt": prompt,
        "config": config,
        "file_path": file_path,
        "source": source,
        "feedback_path": str(FEEDBACK_PATH),
    }

    fd, args_path = tempfile.mkstemp(suffix=".json", prefix="gemini_async_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(args, f, ensure_ascii=False)

    async_runner = SRC_DIR / "async_runner.py"

    subprocess.Popen(
        [sys.executable, str(async_runner), args_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    return "[ASYNC] Gemini 평가가 백그라운드에서 진행 중입니다. 결과는 gemini_feedback.md에 기록됩니다."
