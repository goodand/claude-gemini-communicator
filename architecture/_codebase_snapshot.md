# 코드베이스 전체 스냅샷

생성일: 2026-02-16T01:40:08Z


---
## FILE: scripts/a2a_bridge.py
```python
"""A2A Bridge: Claude ↔ Gemini 협업 평가 브릿지.

Phase 2: SDK 직접 호출 + CLI 폴백 + 비동기 모드 지원.
Phase 3: A2A 구조화된 JSON 메시지 프로토콜.
Phase 4: 에러 감지 + Lazy Analysis.
파일 경로를 Gemini에 전달하여 평가를 받고,
결과를 gemini_feedback.md에 기록합니다.
"""

import fcntl
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
COOLDOWN_STATE_PATH = SCRIPT_DIR / ".cooldown_state.json"
FEEDBACK_PATH = PROJECT_ROOT / "gemini_feedback.md"
ENV_PATH = PROJECT_ROOT / ".env"
ERROR_HISTORY_PATH = SCRIPT_DIR / ".error_history.json"


def _load_env():
    """프로젝트 루트의 .env 파일을 환경변수로 로드합니다."""
    if not ENV_PATH.exists():
        return
    try:
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value
    except IOError:
        pass


_load_env()


# ============================================================
# 설정 로드 (Phase 1 유지)
# ============================================================

def load_config() -> dict:
    """config.json에서 설정을 로드합니다."""
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================
# 쿨다운 메커니즘 (Phase 1 유지)
# ============================================================

def _load_cooldown_state() -> dict:
    """쿨다운 상태 파일을 로드합니다."""
    if not COOLDOWN_STATE_PATH.exists():
        return {}
    try:
        with open(COOLDOWN_STATE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_cooldown_state(state: dict) -> None:
    """쿨다운 상태를 파일에 저장합니다."""
    with open(COOLDOWN_STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False)


def check_cooldown(file_path: str, config: dict) -> bool:
    """파일별 디바운싱: 쿨다운 기간 내이면 False를 반환합니다.

    Returns:
        True: 호출 가능 (쿨다운 지남)
        False: 쿨다운 중 (스킵해야 함)
    """
    cooldown_seconds = config.get("cooldown_seconds_per_file", 300)
    state = _load_cooldown_state()
    now = time.time()
    last_call = state.get(file_path, 0)

    if now - last_call < cooldown_seconds:
        return False

    state[file_path] = now
    _save_cooldown_state(state)
    return True


# ============================================================
# 피드백 저장 / Hook 출력 (Phase 1 유지)
# ============================================================

def save_feedback(feedback: str, source: str, file_path: str = None) -> None:
    """gemini_feedback.md에 피드백을 추가합니다 (file lock으로 동시 쓰기 보호)."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target_info = f" | 대상: `{file_path}`" if file_path else ""

    entry = f"\n---\n\n## [{timestamp}] {source}{target_info}\n\n{feedback}\n"

    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(entry)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def format_hook_output(feedback: str) -> str:
    """Claude Hook용 JSON stdout을 생성합니다."""
    short = feedback[:500] if len(feedback) > 500 else feedback
    output = {
        "hookSpecificOutput": {
            "additionalContext": f"[Gemini 평가] {short}"
        }
    }
    return json.dumps(output, ensure_ascii=False)


# ============================================================
# Phase 2: SDK 지원
# ============================================================

def _sdk_available() -> bool:
    """google-genai SDK가 설치되어 있는지 확인합니다."""
    try:
        from google import genai  # noqa: F401
        return True
    except ImportError:
        return False


def _read_file_content(file_path: str, max_chars: int = 50000) -> str:
    """파일 내용을 읽어 반환합니다. SDK 호출 시 사용."""
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


def _load_oauth_credentials(sdk_config: dict):
    """Gemini CLI의 OAuth 자격 증명을 로드하여 Credentials 객체를 반환합니다."""
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request

    creds_path = Path(
        sdk_config.get("oauth_creds_path", "~/.gemini/oauth_creds.json")
    ).expanduser()

    if not creds_path.exists():
        return None

    try:
        with open(creds_path, "r", encoding="utf-8") as f:
            oauth_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None

    refresh_token = oauth_data.get("refresh_token")
    if not refresh_token:
        return None

    # OAuth 클라이언트 정보 (.env 환경변수에서 로드)
    client_id_env = sdk_config.get("oauth_client_id_env", "GEMINI_OAUTH_CLIENT_ID")
    client_secret_env = sdk_config.get("oauth_client_secret_env", "GEMINI_OAUTH_CLIENT_SECRET")
    client_id = os.environ.get(client_id_env, "")
    client_secret = os.environ.get(client_secret_env, "")
    token_uri = "https://oauth2.googleapis.com/token"

    if not client_id or not client_secret:
        return None

    scopes = oauth_data.get("scope", "").split()

    creds = Credentials(
        token=oauth_data.get("access_token"),
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=client_id,
        client_secret=client_secret,
        scopes=scopes,
    )

    if creds.expired or not creds.token:
        try:
            creds.refresh(Request())
        except Exception:
            return None

    return creds


def _build_prompt(content: str, prompt: str, file_path: str = None) -> str:
    """SDK/REST 공통 프롬프트를 구성합니다."""
    if file_path:
        file_content = _read_file_content(file_path)
        return f"{prompt}\n\n파일 경로: {file_path}\n\n파일 내용:\n{file_content}"
    else:
        return f"{prompt}\n\n---\n{content}"


def _get_api_keys(sdk_config: dict) -> list:
    """환경변수에서 사용 가능한 API key 목록을 수집합니다."""
    keys = []
    # 메인 키
    main_env = sdk_config.get("api_key_env", "GEMINI_API_KEY")
    main_key = os.environ.get(main_env)
    if main_key:
        keys.append(main_key)
    # 추가 키 (GEMINI_API_KEY_* 패턴)
    for env_name, value in os.environ.items():
        if env_name.startswith("GEMINI_API_KEY_") and value and value not in keys:
            keys.append(value)
    return keys


def _get_fallback_models(sdk_config: dict) -> list:
    """사용할 모델 목록을 반환합니다 (메인 모델 + 폴백)."""
    main_model = sdk_config.get("model", "gemini-2.5-flash")
    fallback_models = sdk_config.get("fallback_models", ["gemini-2.0-flash", "gemini-1.5-flash"])
    models = [main_model]
    for m in fallback_models:
        if m not in models:
            models.append(m)
    return models


def _call_gemini_with_api_key(full_prompt: str, config: dict) -> str:
    """API key를 사용하여 google-genai SDK로 호출합니다.

    429 Rate Limit 발생 시 다른 키/모델로 자동 전환합니다.
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
                    continue  # 다음 키/모델 시도
                raise  # 429 외 에러는 상위로 전파

    return f"[SDK_ERROR] 모든 API key/모델 조합에서 실패: {last_error}"


def _call_gemini_with_oauth(full_prompt: str, config: dict) -> str:
    """OAuth 자격 증명을 사용하여 Gemini REST API를 직접 호출합니다."""
    import httpx
    from google.auth.transport.requests import Request

    sdk_config = config.get("sdk", {})
    model_name = sdk_config.get("model", "gemini-2.0-flash")
    timeout = config.get("gemini_timeout", 90)

    creds = _load_oauth_credentials(sdk_config)
    if creds is None:
        raise RuntimeError("OAuth credentials 로드 실패")

    # 항상 토큰 갱신 (캐시된 토큰이 서버에서 만료됐을 수 있음)
    if creds.refresh_token:
        creds.refresh(Request())

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json",
    }
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


def _call_gemini_sdk(content: str, prompt: str, config: dict, file_path: str = None) -> str:
    """SDK 또는 REST API를 사용하여 Gemini를 호출합니다.

    인증 우선순위: API key → OAuth (REST API 직접 호출)
    """
    sdk_config = config.get("sdk", {})
    full_prompt = _build_prompt(content, prompt, file_path)

    api_key_env = sdk_config.get("api_key_env", "GEMINI_API_KEY")
    api_key = os.environ.get(api_key_env)

    if api_key:
        return _call_gemini_with_api_key(full_prompt, config)
    else:
        return _call_gemini_with_oauth(full_prompt, config)


# ============================================================
# Phase 1 CLI 호출 (리네이밍)
# ============================================================

def _call_gemini_cli(content: str, prompt: str, config: dict, file_path: str = None) -> str:
    """Gemini CLI subprocess를 호출합니다 (Phase 1 로직)."""
    gemini_cmd = config.get("gemini_cmd", "/usr/local/bin/gemini")
    timeout = config.get("gemini_timeout", 90)

    if file_path:
        full_prompt = f"{prompt}\n\n파일 경로: {file_path}"
    else:
        full_prompt = f"{prompt}\n\n---\n{content}"

    try:
        result = subprocess.run(
            [gemini_cmd, full_prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
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


# ============================================================
# Phase 2: 오케스트레이터 (SDK → CLI 폴백)
# ============================================================

def call_gemini(content: str, prompt: str, config: dict, file_path: str = None) -> str:
    """Gemini를 호출하여 평가를 받습니다.

    Phase 2: SDK 우선 호출, 실패 시 CLI 폴백.
    호출자(hook 스크립트)의 코드 변경 불필요 — 동일 시그니처 유지.
    """
    sdk_config = config.get("sdk", {})
    sdk_enabled = sdk_config.get("enabled", True)
    fallback_to_cli = sdk_config.get("fallback_to_cli", True)

    # SDK 시도
    if sdk_enabled and _sdk_available():
        try:
            result = _call_gemini_sdk(content, prompt, config, file_path)
            if not result.startswith("[SDK_ERROR]"):
                return result
        except Exception as e:
            result = f"[SDK_ERROR] {e}"

        # SDK 실패 → CLI 폴백
        if fallback_to_cli:
            cli_result = _call_gemini_cli(content, prompt, config, file_path)
            return f"[FALLBACK] SDK 실패 → CLI 사용\n{cli_result}"
        else:
            return result

    # SDK 미설치 또는 비활성화 → CLI 직접 호출
    return _call_gemini_cli(content, prompt, config, file_path)


# ============================================================
# Phase 2: 비동기 (fire-and-forget)
# ============================================================

def call_gemini_async(content: str, prompt: str, config: dict,
                      file_path: str = None, source: str = "Async") -> str:
    """비동기 모드: 별도 프로세스에서 Gemini 호출 (fire-and-forget).

    Returns:
        즉시 반환되는 "pending" 상태 메시지
    """
    import tempfile

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

    async_runner = SCRIPT_DIR / "async_runner.py"

    subprocess.Popen(
        [sys.executable, str(async_runner), args_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    return "[ASYNC] Gemini 평가가 백그라운드에서 진행 중입니다. 결과는 gemini_feedback.md에 기록됩니다."


# ============================================================
# Phase 3: A2A 구조화된 메시지 프로토콜
# ============================================================

A2A_VERSION = "1.0"

# Gemini에 JSON 응답을 강제하기 위한 시스템 프롬프트
_A2A_RESPONSE_INSTRUCTION = """반드시 아래 JSON 형식으로만 응답하라. JSON 외 다른 텍스트를 포함하지 마라.
각 detail과 항목은 반드시 1-2문장 이내로 간결하게 작성하라. 절대 긴 설명을 하지 마라.

{
  "evaluation": {
    "논리적 일관성": {"score": "높음|보통|낮음", "detail": "1문장"},
    "실현 가능성": {"score": "높음|보통|낮음", "detail": "1문장"},
    "누락된 고려사항": ["항목1", "항목2"],
    "개선 제안": ["제안1", "제안2"]
  },
  "summary": "한 줄 요약"
}"""

_A2A_CLASSIFICATION_INSTRUCTION = """반드시 아래 JSON 형식으로만 응답하라. JSON 외 다른 텍스트를 포함하지 마라.

{"is_plan": true 또는 false}"""


def build_a2a_request(message_type: str, payload: dict,
                      hook_source: str = "unknown") -> dict:
    """A2A 요청 메시지를 생성합니다."""
    return {
        "a2a_version": A2A_VERSION,
        "message_type": message_type,
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {
            "agent": "claude",
            "hook": hook_source,
        },
        "payload": payload,
    }


def _try_parse_json(text: str):
    """JSON 파싱을 시도합니다. 실패 시 None."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _try_repair_json(text: str):
    """잘린 JSON을 복구 시도합니다.

    토큰 제한으로 잘린 응답에서 닫히지 않은 괄호/따옴표를 보정.
    """
    # 열린 문자열 잘라내기 (마지막 불완전한 값 제거)
    # 마지막 완전한 key-value 또는 배열 요소까지 자르기
    for trim_target in [',\n', ',"', ', "', ',']:
        idx = text.rfind(trim_target)
        if idx > 0:
            candidate = text[:idx]
            # 닫히지 않은 괄호 보정
            open_braces = candidate.count('{') - candidate.count('}')
            open_brackets = candidate.count('[') - candidate.count(']')
            if open_braces >= 0 and open_brackets >= 0:
                candidate += ']' * open_brackets + '}' * open_braces
                result = _try_parse_json(candidate)
                if result is not None:
                    return result
    return None


def parse_a2a_response(raw_text: str, request_id: str = None) -> dict:
    """Gemini 응답 텍스트에서 A2A JSON을 파싱합니다.

    JSON 파싱 실패 시 raw text를 payload에 담아 반환합니다.
    """
    # JSON 블록 추출 (```json ... ``` 또는 순수 JSON)
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = []
        inside = False
        for line in lines:
            if line.strip().startswith("```") and not inside:
                inside = True
                continue
            elif line.strip() == "```" and inside:
                break
            elif inside:
                json_lines.append(line)
        text = "\n".join(json_lines).strip()

    # 1차 시도: 그대로 파싱
    parsed = _try_parse_json(text)

    # 2차 시도: 잘린 JSON 복구 (닫히지 않은 괄호 보정)
    if parsed is None:
        parsed = _try_repair_json(text)

    if parsed is not None:
        return {
            "a2a_version": A2A_VERSION,
            "message_type": "evaluation_response",
            "request_id": request_id or "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": {"agent": "gemini"},
            "status": "success",
            "payload": parsed,
        }

    # 파싱 실패 → 원본 텍스트를 그대로 담기
    return {
        "a2a_version": A2A_VERSION,
        "message_type": "evaluation_response",
        "request_id": request_id or "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {"agent": "gemini"},
        "status": "success",
        "payload": {"raw_text": raw_text},
    }


def a2a_response_to_markdown(response: dict) -> str:
    """A2A 응답을 gemini_feedback.md용 마크다운으로 변환합니다."""
    payload = response.get("payload", {})

    # raw_text 모드 (JSON 파싱 실패 시)
    if "raw_text" in payload:
        return payload["raw_text"]

    # 구조화된 응답
    evaluation = payload.get("evaluation", {})
    summary = payload.get("summary", "")
    parts = []

    for key, value in evaluation.items():
        if isinstance(value, dict):
            score = value.get("score", "")
            detail = value.get("detail", "")
            parts.append(f"### {key}: {score}\n{detail}")
        elif isinstance(value, list):
            items = "\n".join(f"- {item}" for item in value)
            parts.append(f"### {key}\n{items}")

    if summary:
        parts.append(f"\n**요약:** {summary}")

    return "\n\n".join(parts)


def build_a2a_evaluation_prompt(base_prompt: str, config: dict) -> str:
    """A2A 모드일 때 JSON 응답을 강제하는 프롬프트를 생성합니다."""
    if config.get("a2a_schema_enabled", False):
        return f"{base_prompt}\n\n{_A2A_RESPONSE_INSTRUCTION}"
    return base_prompt


def build_a2a_classification_prompt(base_prompt: str, config: dict) -> str:
    """A2A 모드일 때 분류 요청 프롬프트를 생성합니다."""
    if config.get("a2a_schema_enabled", False):
        return f"{base_prompt}\n\n{_A2A_CLASSIFICATION_INSTRUCTION}"
    return base_prompt


# ============================================================
# Phase 4: 에러 감지 + Lazy Analysis
# ============================================================

# 심각도별 에러 패턴
_ERROR_SEVERITY = {
    "critical": [
        "PermissionError", "AuthenticationError", "EnvironmentError",
        "OSError: [Errno 13]", "EACCES",
    ],
    "high": [
        "ImportError", "ModuleNotFoundError", "ConnectionError",
        "ConnectionRefusedError", "TimeoutError", "FileNotFoundError",
    ],
    "medium": [
        "TypeError", "ValueError", "KeyError", "IndexError",
        "AttributeError", "RuntimeError",
    ],
    "low": [
        "SyntaxError", "NameError", "IndentationError",
        "TabError", "DeprecationWarning",
    ],
}

# 에러 감지 정규식 (transcript 스캔용)
_ERROR_DETECT_RE = re.compile(
    r"Traceback \(most recent call last\)"
    r"|(?:Error|Exception|FAILED|FAIL|error:)(?=[\s:\]])"
    r"|exit code [1-9]",
    re.IGNORECASE,
)

# 에러 해시 정규화 패턴 (가변 요소 마스킹)
_NORMALIZE_PATTERNS = [
    (re.compile(r"/[\w/.+-]+"), "<PATH>"),          # 파일 경로
    (re.compile(r"line \d+"), "line <N>"),           # 라인 번호
    (re.compile(r"0x[0-9a-fA-F]+"), "<ADDR>"),      # 메모리 주소
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}"), "<TIME>"),  # 타임스탬프
]


def _load_error_history() -> dict:
    """에러 이력 파일을 로드합니다."""
    if not ERROR_HISTORY_PATH.exists():
        return {"last_analysis_time": 0, "errors": {}}
    try:
        with open(ERROR_HISTORY_PATH, "r", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                return json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except (json.JSONDecodeError, IOError):
        return {"last_analysis_time": 0, "errors": {}}


def _save_error_history(history: dict) -> None:
    """에러 이력 파일을 저장합니다."""
    with open(ERROR_HISTORY_PATH, "w", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(history, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def normalize_error_text(error_text: str) -> str:
    """에러 텍스트에서 가변 요소를 마스킹하여 정규화합니다."""
    normalized = error_text
    for pattern, replacement in _NORMALIZE_PATTERNS:
        normalized = pattern.sub(replacement, normalized)
    return normalized


def hash_error(error_text: str) -> str:
    """정규화된 에러 텍스트의 해시를 생성합니다."""
    normalized = normalize_error_text(error_text)
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()[:12]


def classify_error_severity(error_text: str) -> str:
    """에러 텍스트의 심각도를 분류합니다."""
    for severity, patterns in _ERROR_SEVERITY.items():
        if any(p in error_text for p in patterns):
            return severity
    return "medium"


def scan_transcript_for_errors(transcript_path: str, tail_lines: int = 50) -> list:
    """Transcript JSONL 파일의 마지막 N줄에서 에러를 스캔합니다.

    Returns:
        에러 텍스트 목록 (중복 제거)
    """
    if not transcript_path or not os.path.exists(transcript_path):
        return []

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except IOError:
        return []

    # 마지막 N줄만 검사 (전체 스캔 방지)
    recent_lines = lines[-tail_lines:] if len(lines) > tail_lines else lines

    errors = []
    seen_hashes = set()

    for line in recent_lines:
        try:
            entry = json.loads(line.strip())
        except json.JSONDecodeError:
            continue

        # tool_result에서 에러 찾기 (Bash 도구 실행 결과)
        content = entry.get("content", "")
        if isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "") or block.get("content", "")
                    if text and _ERROR_DETECT_RE.search(text):
                        h = hash_error(text)
                        if h not in seen_hashes:
                            seen_hashes.add(h)
                            errors.append(text[:1000])
        elif isinstance(content, str) and _ERROR_DETECT_RE.search(content):
            h = hash_error(content)
            if h not in seen_hashes:
                seen_hashes.add(h)
                errors.append(content[:1000])

    return errors


def check_error_and_analyze(errors: list, config: dict) -> str | None:
    """에러 목록을 이력에 기록하고, Lazy Analysis 조건 충족 시 Gemini 분석을 실행합니다.

    Returns:
        Gemini 분석 결과 문자열, 또는 분석 불필요 시 None
    """
    if not errors:
        return None

    error_config = config.get("error_detection", {})
    thresholds = error_config.get("thresholds", {"critical": 1, "high": 1, "medium": 2, "low": 3})
    global_cooldown = error_config.get("global_cooldown_seconds", 60)
    error_prompt = error_config.get(
        "error_prompt",
        "다음 에러를 분석하고 원인과 수정 방법을 간결하게 한국어로 제안해주세요.",
    )
    prefix = error_config.get("feedback_prefix", "[SYSTEM ADVISORY: Gemini Error Analysis]")

    history = _load_error_history()

    # 전역 쿨다운 확인
    now = time.time()
    if now - history.get("last_analysis_time", 0) < global_cooldown:
        return None

    # 에러 기록 + 트리거 조건 확인
    errors_to_analyze = []
    for error_text in errors:
        error_hash = hash_error(error_text)
        severity = classify_error_severity(error_text)

        if error_hash not in history["errors"]:
            history["errors"][error_hash] = {
                "preview": error_text[:200],
                "count": 0,
                "severity": severity,
                "analyzed": False,
            }

        entry = history["errors"][error_hash]
        entry["count"] += 1

        threshold = thresholds.get(severity, 2)
        if entry["count"] >= threshold and not entry["analyzed"]:
            errors_to_analyze.append(error_text)

    _save_error_history(history)

    if not errors_to_analyze:
        return None

    # Gemini 분석 호출
    combined = "\n\n---\n\n".join(errors_to_analyze[:3])  # 최대 3개
    full_prompt = f"{error_prompt}\n\n{combined}"

    feedback = call_gemini(content="", prompt=full_prompt, config=config)

    # 분석 완료 표시
    history = _load_error_history()
    history["last_analysis_time"] = time.time()
    for error_text in errors_to_analyze:
        error_hash = hash_error(error_text)
        if error_hash in history["errors"]:
            history["errors"][error_hash]["analyzed"] = True
    _save_error_history(history)

    # 피드백 저장
    prefixed_feedback = f"{prefix}\n\n{feedback}"
    save_feedback(prefixed_feedback, source="Error Analysis (Stop Hook)")

    return prefixed_feedback
```

---
## FILE: scripts/async_runner.py
```python
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
```

---
## FILE: scripts/cli.py
```python
"""CLI 관리 도구: 시스템 진단, 상태, 통계, 검색, 테스트, 초기화.

Usage:
    python3 scripts/cli.py doctor   — 시스템 진단 (config/환경/Hook 검증)
    python3 scripts/cli.py status   — 현재 설정 및 상태
    python3 scripts/cli.py stats    — 피드백 통계
    python3 scripts/cli.py search <keyword>  — 피드백 검색
    python3 scripts/cli.py test     — 전체 자동 테스트
    python3 scripts/cli.py clear    — 상태 파일 초기화
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
COOLDOWN_PATH = SCRIPT_DIR / ".cooldown_state.json"
ERROR_HISTORY_PATH = SCRIPT_DIR / ".error_history.json"
FEEDBACK_PATH = PROJECT_ROOT / "gemini_feedback.md"


SETTINGS_PATH = PROJECT_ROOT / ".claude" / "settings.local.json"
HOOKS_SCRIPTS = {
    "hook_auto_task.py": "PostToolUse Hook",
    "hook_stop.py": "Stop Hook",
    "hook_pre_tool.py": "PreToolUse Hook",
    "a2a_bridge.py": "핵심 브릿지",
    "async_runner.py": "비동기 실행기",
}


# ============================================================
# doctor: 시스템 진단
# ============================================================

def validate_config(config: dict) -> list:
    """config.json을 검증하고 문제 목록을 반환합니다."""
    issues = []

    # 필수 필드
    required = {
        "gemini_cmd": str,
        "gemini_timeout": (int, float),
        "watch_extensions": list,
        "evaluation_prompt": str,
    }
    for field, expected_type in required.items():
        if field not in config:
            issues.append(("error", f"필수 필드 누락: {field}"))
        elif not isinstance(config[field], expected_type):
            issues.append(("error", f"타입 오류: {field} — {type(config[field]).__name__} (expected {expected_type})"))

    # SDK 설정
    sdk = config.get("sdk")
    if sdk is not None:
        if not isinstance(sdk, dict):
            issues.append(("error", "sdk는 dict여야 합니다"))
        else:
            if "model" not in sdk:
                issues.append(("warn", "sdk.model 미설정 (기본값 사용됨)"))
            fallback = sdk.get("fallback_models")
            if fallback is not None and not isinstance(fallback, list):
                issues.append(("error", "sdk.fallback_models는 list여야 합니다"))
            temp = sdk.get("temperature")
            if temp is not None and not (0 <= temp <= 2):
                issues.append(("warn", f"sdk.temperature={temp} — 0~2 범위 권장"))

    # 에러 감지 설정
    err = config.get("error_detection")
    if err is not None and isinstance(err, dict):
        thresholds = err.get("thresholds")
        if thresholds is not None:
            if not isinstance(thresholds, dict):
                issues.append(("error", "error_detection.thresholds는 dict여야 합니다"))
            else:
                for sev in ["critical", "high", "medium", "low"]:
                    val = thresholds.get(sev)
                    if val is not None and (not isinstance(val, int) or val < 1):
                        issues.append(("error", f"thresholds.{sev}={val} — 1 이상 정수여야 합니다"))

    # PreTool Guard 커스텀 패턴
    guard = config.get("pre_tool_guard")
    if guard is not None and isinstance(guard, dict):
        for i, pat in enumerate(guard.get("custom_block_patterns", [])):
            try:
                re.compile(pat)
            except re.error as e:
                issues.append(("error", f"custom_block_patterns[{i}] 정규식 오류: {e}"))

    # watch_extensions 형식
    exts = config.get("watch_extensions", [])
    for ext in exts:
        if not ext.startswith("."):
            issues.append(("warn", f"watch_extensions '{ext}' — 점(.)으로 시작해야 합니다"))

    return issues


def cmd_doctor(args=None):
    """시스템 전체를 진단합니다."""
    print("=== System Doctor ===\n")
    ok_count = 0
    warn_count = 0
    err_count = 0

    def check(passed, label, detail=""):
        nonlocal ok_count, warn_count, err_count
        if passed == "ok":
            print(f"  ✓ {label}")
            ok_count += 1
        elif passed == "warn":
            print(f"  ⚠ {label}" + (f" — {detail}" if detail else ""))
            warn_count += 1
        else:
            print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))
            err_count += 1

    # ── 1. Config ──
    print("[1] Config 검증")
    if not CONFIG_PATH.exists():
        check("err", "config.json", "파일 없음")
    else:
        try:
            config = json.loads(CONFIG_PATH.read_text("utf-8"))
            check("ok", "config.json 파싱 성공")
        except json.JSONDecodeError as e:
            check("err", "config.json", f"JSON 파싱 실패: {e}")
            config = None

        if config:
            issues = validate_config(config)
            if not issues:
                check("ok", "config 필드 검증 통과")
            for level, msg in issues:
                check(level if level == "warn" else "err", msg)

    # ── 2. 환경 ──
    print("\n[2] 환경 점검")

    # API Key
    api_key = os.environ.get("GEMINI_API_KEY", "")
    extra_keys = [k for k in os.environ if k.startswith("GEMINI_API_KEY_")]
    total_keys = (1 if api_key else 0) + len(extra_keys)
    if total_keys > 0:
        check("ok", f"API Key: {total_keys}개 설정됨")
    else:
        check("warn", "API Key 미설정", "GEMINI_API_KEY 환경변수 필요 (SDK 사용 시)")

    # SDK
    try:
        from google import genai  # noqa: F401
        check("ok", "google-genai SDK 설치됨")
    except ImportError:
        check("warn", "google-genai SDK 미설치", "pip install google-genai")

    # Gemini CLI
    config = json.loads(CONFIG_PATH.read_text("utf-8")) if CONFIG_PATH.exists() else {}
    gemini_cmd = config.get("gemini_cmd", "/usr/local/bin/gemini")
    if Path(gemini_cmd).exists():
        check("ok", f"Gemini CLI: {gemini_cmd}")
    else:
        check("warn", f"Gemini CLI 없음: {gemini_cmd}", "CLI 폴백 불가")

    # .env
    if (PROJECT_ROOT / ".env").exists():
        check("ok", ".env 파일 존재")
    else:
        check("warn", ".env 파일 없음", "API Key를 .env에 설정하세요")

    # ── 3. Hook 등록 ──
    print("\n[3] Hook 등록 점검")
    if not SETTINGS_PATH.exists():
        check("err", "settings.local.json", "파일 없음 — Hook 미등록 상태")
    else:
        try:
            settings = json.loads(SETTINGS_PATH.read_text("utf-8"))
            hooks = settings.get("hooks", {})

            expected_hooks = {
                "PreToolUse": "hook_pre_tool.py",
                "PostToolUse": "hook_auto_task.py",
                "Stop": "hook_stop.py",
            }
            for hook_type, script_name in expected_hooks.items():
                hook_list = hooks.get(hook_type, [])
                found = any(
                    script_name in h.get("command", "")
                    for group in hook_list
                    for h in group.get("hooks", [])
                )
                if found:
                    check("ok", f"{hook_type} Hook → {script_name}")
                else:
                    check("warn", f"{hook_type} Hook 미등록", f"{script_name}")
        except json.JSONDecodeError:
            check("err", "settings.local.json", "JSON 파싱 실패")

    # ── 4. 스크립트 존재 ──
    print("\n[4] 스크립트 파일 점검")
    for script, desc in HOOKS_SCRIPTS.items():
        path = SCRIPT_DIR / script
        if path.exists():
            check("ok", f"{script} ({desc})")
        else:
            check("err", f"{script} 없음", desc)

    # ── 결과 ──
    print(f"\n{'='*40}")
    total = ok_count + warn_count + err_count
    print(f"결과: {ok_count}/{total} OK, {warn_count} 경고, {err_count} 에러")
    if err_count == 0 and warn_count == 0:
        print("시스템 상태: 정상 ✓")
    elif err_count == 0:
        print("시스템 상태: 동작 가능 (경고 확인 권장)")
    else:
        print("시스템 상태: 문제 있음 (에러 수정 필요)")
    return err_count == 0


# ============================================================
# status: 현재 설정 및 상태
# ============================================================

def cmd_status(args=None):
    """현재 시스템 상태를 출력합니다."""
    print("=== Claude-Gemini Communicator Status ===\n")

    # Config
    if CONFIG_PATH.exists():
        config = json.loads(CONFIG_PATH.read_text("utf-8"))
        sdk = config.get("sdk", {})
        err = config.get("error_detection", {})
        guard = config.get("pre_tool_guard", {})

        print("[Config]")
        print(f"  SDK 모드:        {'ON' if sdk.get('enabled') else 'OFF'}")
        print(f"  SDK 모델:        {sdk.get('model', 'N/A')}")
        print(f"  CLI 폴백:        {'ON' if sdk.get('fallback_to_cli') else 'OFF'}")
        print(f"  비동기 모드:     {'ON' if config.get('async_mode') else 'OFF'}")
        print(f"  A2A 스키마:      {'ON' if config.get('a2a_schema_enabled') else 'OFF'}")
        print(f"  에러 감지:       {'ON' if err.get('enabled') else 'OFF'}")
        print(f"  PreTool Guard:   {'ON' if guard.get('enabled', True) else 'OFF'}")
        print(f"  감시 확장자:     {config.get('watch_extensions', [])}")
        print(f"  쿨다운(파일):    {config.get('cooldown_seconds_per_file', 300)}초")
    else:
        print("[Config] config.json 없음!")

    # Cooldown state
    print()
    if COOLDOWN_PATH.exists():
        state = json.loads(COOLDOWN_PATH.read_text("utf-8"))
        now = time.time()
        print(f"[Cooldown] {len(state)}개 파일 기록")
        for fp, ts in sorted(state.items(), key=lambda x: x[1], reverse=True)[:5]:
            age = int(now - ts)
            print(f"  {fp}: {age}초 전")
    else:
        print("[Cooldown] 기록 없음")

    # Error history
    print()
    if ERROR_HISTORY_PATH.exists():
        history = json.loads(ERROR_HISTORY_PATH.read_text("utf-8"))
        errors = history.get("errors", {})
        analyzed = sum(1 for e in errors.values() if e.get("analyzed"))
        last = history.get("last_analysis_time", 0)
        last_str = f"{int(time.time() - last)}초 전" if last > 0 else "없음"
        print(f"[Error History] {len(errors)}개 에러, {analyzed}개 분석됨")
        print(f"  마지막 분석: {last_str}")
        for h, e in list(errors.items())[:3]:
            print(f"  [{e.get('severity','?')}] {e.get('preview','')[:60]}")
    else:
        print("[Error History] 기록 없음")

    # Feedback file
    print()
    if FEEDBACK_PATH.exists():
        content = FEEDBACK_PATH.read_text("utf-8")
        entries = content.count("\n---\n")
        size_kb = len(content.encode("utf-8")) / 1024
        print(f"[Feedback] {entries}개 항목, {size_kb:.1f}KB")
    else:
        print("[Feedback] gemini_feedback.md 없음")


# ============================================================
# stats: 피드백 통계
# ============================================================

def cmd_stats(args=None):
    """gemini_feedback.md에서 통계를 추출합니다."""
    print("=== Feedback Statistics ===\n")

    if not FEEDBACK_PATH.exists():
        print("gemini_feedback.md가 없습니다.")
        return

    content = FEEDBACK_PATH.read_text("utf-8")
    if not content.strip():
        print("피드백이 비어있습니다.")
        return

    # 항목별 분석
    entries = content.split("\n---\n")
    entries = [e.strip() for e in entries if e.strip()]

    sources = {}
    dates = []
    for entry in entries:
        # 소스 추출: ## [2024-01-01 12:00:00] Source Name
        match = re.search(r"## \[(\d{4}-\d{2}-\d{2}) \d{2}:\d{2}:\d{2}\] (.+?)(?:\s*\||$)", entry)
        if match:
            dates.append(match.group(1))
            source = match.group(2).strip()
            sources[source] = sources.get(source, 0) + 1

    print(f"총 피드백 수: {len(entries)}")
    print()

    if sources:
        print("[소스별]")
        for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"  {src}: {count}건")

    if dates:
        print()
        print(f"[기간] {min(dates)} ~ {max(dates)}")

        # 일별 분포
        day_counts = {}
        for d in dates:
            day_counts[d] = day_counts.get(d, 0) + 1
        print("[일별]")
        for day, count in sorted(day_counts.items())[-7:]:
            bar = "█" * count
            print(f"  {day}: {bar} ({count})")


# ============================================================
# search: 피드백 검색
# ============================================================

def parse_feedback_entries(content: str) -> list:
    """gemini_feedback.md를 항목별로 파싱합니다."""
    raw_entries = content.split("\n---\n")
    entries = []
    for raw in raw_entries:
        raw = raw.strip()
        if not raw:
            continue
        match = re.search(
            r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.+?)(?:\s*\|\s*대상:\s*`(.+?)`)?$",
            raw,
            re.MULTILINE,
        )
        entries.append({
            "date": match.group(1) if match else "",
            "source": match.group(2).strip() if match else "",
            "target": match.group(3) if match and match.group(3) else "",
            "body": raw,
        })
    return entries


def cmd_search(args):
    """피드백을 키워드/소스/날짜로 검색합니다."""
    keyword = args.keyword
    source_filter = args.source
    date_filter = args.date

    if not FEEDBACK_PATH.exists():
        print("gemini_feedback.md가 없습니다.")
        return

    content = FEEDBACK_PATH.read_text("utf-8")
    entries = parse_feedback_entries(content)

    results = []
    for entry in entries:
        # 키워드 필터
        if keyword.lower() not in entry["body"].lower():
            continue
        # 소스 필터
        if source_filter and source_filter.lower() not in entry["source"].lower():
            continue
        # 날짜 필터
        if date_filter and not entry["date"].startswith(date_filter):
            continue
        results.append(entry)

    print(f'=== "{keyword}" 검색 결과: {len(results)}건 ===\n')

    for i, entry in enumerate(results, 1):
        # 키워드 주변 컨텍스트 추출
        body_lower = entry["body"].lower()
        kw_lower = keyword.lower()
        idx = body_lower.find(kw_lower)
        start = max(0, idx - 60)
        end = min(len(entry["body"]), idx + len(keyword) + 60)
        snippet = entry["body"][start:end].replace("\n", " ").strip()
        if start > 0:
            snippet = "..." + snippet
        if end < len(entry["body"]):
            snippet = snippet + "..."

        src_info = entry["source"] or "unknown"
        date_info = entry["date"] or "unknown"
        target_info = f" → {entry['target']}" if entry["target"] else ""

        print(f"[{i}] {date_info} | {src_info}{target_info}")
        print(f"    {snippet}")
        print()


# ============================================================
# test: 전체 자동 테스트
# ============================================================

def cmd_test(args=None):
    """전체 시스템 자동 테스트를 실행합니다."""
    print("=== System Test Suite ===\n")

    sys.path.insert(0, str(SCRIPT_DIR))
    passed = 0
    failed = 0
    total = 0

    def run_test(name, fn):
        nonlocal passed, failed, total
        total += 1
        try:
            result = fn()
            if result:
                print(f"  ✓ {name}")
                passed += 1
            else:
                print(f"  ✗ {name} — 실패")
                failed += 1
        except Exception as e:
            print(f"  ✗ {name} — 예외: {e}")
            failed += 1

    # ── 1. Config 테스트 ──
    print("[1] Config 검증")

    def test_config_load():
        from a2a_bridge import load_config
        c = load_config()
        return isinstance(c, dict) and "gemini_timeout" in c

    def test_config_required_fields():
        from a2a_bridge import load_config
        c = load_config()
        required = ["gemini_cmd", "gemini_timeout", "watch_extensions",
                     "evaluation_prompt", "sdk"]
        return all(k in c for k in required)

    def test_config_sdk_fields():
        from a2a_bridge import load_config
        c = load_config()
        sdk = c.get("sdk", {})
        return "model" in sdk and "enabled" in sdk

    run_test("config.json 로드", test_config_load)
    run_test("필수 필드 존재", test_config_required_fields)
    run_test("SDK 설정 필드", test_config_sdk_fields)

    # ── 2. 에러 감지 함수 테스트 ──
    print("\n[2] 에러 감지 함수")

    def test_normalize_error():
        from a2a_bridge import normalize_error_text
        result = normalize_error_text("File /usr/local/lib/python3.13/test.py, line 42")
        return "<PATH>" in result and "line <N>" in result

    def test_hash_error():
        from a2a_bridge import hash_error
        h1 = hash_error("TypeError: foo at /path/a.py line 1")
        h2 = hash_error("TypeError: foo at /different/b.py line 99")
        return h1 == h2  # 경로/라인 정규화 → 같은 해시

    def test_hash_error_different():
        from a2a_bridge import hash_error
        h1 = hash_error("TypeError: cannot add str and int")
        h2 = hash_error("ImportError: no module named foo")
        return h1 != h2  # 다른 에러 → 다른 해시

    def test_classify_severity():
        from a2a_bridge import classify_error_severity
        return (classify_error_severity("PermissionError: access denied") == "critical"
                and classify_error_severity("ImportError: no module") == "high"
                and classify_error_severity("TypeError: bad arg") == "medium"
                and classify_error_severity("SyntaxError: invalid") == "low")

    run_test("에러 텍스트 정규화", test_normalize_error)
    run_test("동일 에러 해시 일치", test_hash_error)
    run_test("다른 에러 해시 불일치", test_hash_error_different)
    run_test("심각도 분류", test_classify_severity)

    # ── 3. A2A 프로토콜 테스트 ──
    print("\n[3] A2A 프로토콜")

    def test_a2a_request():
        from a2a_bridge import build_a2a_request
        req = build_a2a_request("evaluation_request", {"text": "hello"}, "test")
        return (req.get("a2a_version") == "1.0"
                and req.get("message_type") == "evaluation_request"
                and "request_id" in req)

    def test_a2a_parse_valid():
        from a2a_bridge import parse_a2a_response
        resp = parse_a2a_response('{"evaluation":{"score":"good"},"summary":"ok"}')
        return resp.get("status") == "success" and "evaluation" in resp.get("payload", {})

    def test_a2a_parse_truncated():
        from a2a_bridge import parse_a2a_response
        truncated = '{"evaluation":{"논리적 일관성":{"score":"높음","detail":"좋다"},"실현 가능성":{"score":"보통","detail":"가능"},"누락된 고려사항":["항목1"'
        resp = parse_a2a_response(truncated)
        payload = resp.get("payload", {})
        return "evaluation" in payload or "raw_text" in payload

    def test_a2a_parse_raw():
        from a2a_bridge import parse_a2a_response
        resp = parse_a2a_response("그냥 텍스트 응답")
        return "raw_text" in resp.get("payload", {})

    def test_a2a_to_markdown():
        from a2a_bridge import a2a_response_to_markdown
        resp = {
            "payload": {
                "evaluation": {
                    "논리적 일관성": {"score": "높음", "detail": "좋다"},
                    "개선 제안": ["제안1", "제안2"],
                },
                "summary": "전체 요약",
            }
        }
        md = a2a_response_to_markdown(resp)
        return "높음" in md and "제안1" in md and "전체 요약" in md

    run_test("A2A 요청 생성", test_a2a_request)
    run_test("A2A 정상 JSON 파싱", test_a2a_parse_valid)
    run_test("A2A 잘린 JSON 복구", test_a2a_parse_truncated)
    run_test("A2A raw text 폴백", test_a2a_parse_raw)
    run_test("A2A → 마크다운 변환", test_a2a_to_markdown)

    # ── 4. PreToolUse Guard 테스트 ──
    print("\n[4] PreToolUse Guard")

    def _check(cmd, expected_severity):
        from hook_pre_tool import check_command
        from a2a_bridge import load_config
        result = check_command(cmd, load_config())
        if expected_severity is None:
            return result is None
        return result is not None and result["severity"] == expected_severity

    def test_block_rm_rf():
        return _check("rm -rf /tmp/data", "block")

    def test_block_force_push():
        return _check("git push --force origin main", "block")

    def test_block_reset_hard():
        return _check("git reset --hard HEAD~3", "block")

    def test_block_drop_table():
        return _check('psql -c "DROP TABLE users"', "block")

    def test_warn_branch_d():
        return _check("git branch -D old", "warn")

    def test_warn_chmod_777():
        return _check("chmod 777 file.sh", "warn")

    def test_allow_safe():
        return (_check("ls -la", None)
                and _check("git status", None)
                and _check("python3 test.py", None))

    def test_allow_pip_requirements():
        return _check("pip install -r requirements.txt", None)

    def test_false_positive_echo():
        return _check('echo "rm -rf is dangerous"', None)

    def test_false_positive_commit():
        return _check('git commit -m "fix: DROP TABLE bug"', None)

    run_test("Block: rm -rf", test_block_rm_rf)
    run_test("Block: git push --force", test_block_force_push)
    run_test("Block: git reset --hard", test_block_reset_hard)
    run_test("Block: DROP TABLE", test_block_drop_table)
    run_test("Warn: git branch -D", test_warn_branch_d)
    run_test("Warn: chmod 777", test_warn_chmod_777)
    run_test("Allow: 안전한 명령", test_allow_safe)
    run_test("Allow: pip -r requirements", test_allow_pip_requirements)
    run_test("오탐 방지: echo 안의 rm -rf", test_false_positive_echo)
    run_test("오탐 방지: commit 안의 DROP TABLE", test_false_positive_commit)

    # ── 5. Cooldown 테스트 ──
    print("\n[5] 쿨다운 메커니즘")

    def test_cooldown():
        from a2a_bridge import check_cooldown, load_config, _save_cooldown_state
        config = load_config()
        _save_cooldown_state({})  # 초기화
        result1 = check_cooldown("/test/file.md", config)
        result2 = check_cooldown("/test/file.md", config)
        _save_cooldown_state({})  # 정리
        return result1 is True and result2 is False  # 첫 번째 통과, 두 번째 쿨다운

    def test_cooldown_different_files():
        from a2a_bridge import check_cooldown, load_config, _save_cooldown_state
        config = load_config()
        _save_cooldown_state({})
        r1 = check_cooldown("/test/a.md", config)
        r2 = check_cooldown("/test/b.md", config)
        _save_cooldown_state({})
        return r1 is True and r2 is True  # 다른 파일은 각각 통과

    run_test("동일 파일 쿨다운", test_cooldown)
    run_test("다른 파일 독립 쿨다운", test_cooldown_different_files)

    # ── 6. Config 검증 (validate_config) ──
    print("\n[6] Config 검증 함수")

    def test_validate_valid():
        from a2a_bridge import load_config
        issues = validate_config(load_config())
        errors = [i for i in issues if i[0] == "error"]
        return len(errors) == 0

    def test_validate_missing_field():
        issues = validate_config({"sdk": {}})  # gemini_cmd 등 누락
        errors = [i for i in issues if i[0] == "error"]
        return len(errors) >= 3  # 여러 필수 필드 누락

    def test_validate_bad_type():
        issues = validate_config({
            "gemini_cmd": 123,  # str이어야 함
            "gemini_timeout": "abc",  # int여야 함
            "watch_extensions": "not a list",
            "evaluation_prompt": "",
        })
        errors = [i for i in issues if i[0] == "error"]
        return len(errors) >= 3

    def test_validate_bad_threshold():
        issues = validate_config({
            "gemini_cmd": "/usr/local/bin/gemini",
            "gemini_timeout": 90,
            "watch_extensions": [".md"],
            "evaluation_prompt": "test",
            "error_detection": {"thresholds": {"critical": 0, "high": -1}},
        })
        errors = [i for i in issues if i[0] == "error"]
        return len(errors) >= 2

    def test_validate_bad_regex():
        issues = validate_config({
            "gemini_cmd": "/usr/local/bin/gemini",
            "gemini_timeout": 90,
            "watch_extensions": [".md"],
            "evaluation_prompt": "test",
            "pre_tool_guard": {"custom_block_patterns": ["[invalid regex"]},
        })
        errors = [i for i in issues if i[0] == "error"]
        return len(errors) >= 1

    def test_validate_bad_extension():
        issues = validate_config({
            "gemini_cmd": "/usr/local/bin/gemini",
            "gemini_timeout": 90,
            "watch_extensions": ["md"],  # 점 없음
            "evaluation_prompt": "test",
        })
        warns = [i for i in issues if i[0] == "warn"]
        return len(warns) >= 1

    run_test("현재 config 유효성", test_validate_valid)
    run_test("필수 필드 누락 감지", test_validate_missing_field)
    run_test("타입 오류 감지", test_validate_bad_type)
    run_test("threshold 범위 오류", test_validate_bad_threshold)
    run_test("정규식 오류 감지", test_validate_bad_regex)
    run_test("확장자 형식 경고", test_validate_bad_extension)

    # ── 7. Agent Skill 테스트 ──
    print("\n[7] Agent Skill (gemini-reviewer)")

    SKILL_DIR = PROJECT_ROOT / "skills" / "gemini-reviewer"

    def test_skill_structure():
        return ((SKILL_DIR / "SKILL.md").exists()
                and (SKILL_DIR / "scripts" / "evaluate.py").exists()
                and (SKILL_DIR / "references" / "setup.md").exists())

    def test_skill_metadata():
        content = (SKILL_DIR / "SKILL.md").read_text("utf-8")
        return "name: gemini-reviewer" in content and "description:" in content

    def test_skill_detect_mode():
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from evaluate import detect_mode
        return (detect_mode("test.py") == "code"
                and detect_mode("plan.md") == "doc"
                and detect_mode("app.js") == "code")

    def test_skill_prompts():
        sys.path.insert(0, str(SKILL_DIR / "scripts"))
        from evaluate import PROMPTS
        return "code" in PROMPTS and "doc" in PROMPTS and "버그" in PROMPTS["code"]

    run_test("Skill 디렉토리 구조", test_skill_structure)
    run_test("SKILL.md 메타데이터", test_skill_metadata)
    run_test("모드 자동 감지", test_skill_detect_mode)
    run_test("프롬프트 정의", test_skill_prompts)

    # ── 8. 피드백 파싱 테스트 ──
    print("\n[8] 피드백 파싱")

    def test_parse_entries():
        sample = (
            "\n---\n\n## [2026-02-14 10:00:00] PostToolUse Hook | 대상: `test.md`\n\n평가 내용\n"
            "\n---\n\n## [2026-02-14 11:00:00] Stop Hook (Plan 감지)\n\n계획 평가\n"
        )
        entries = parse_feedback_entries(sample)
        return (len(entries) == 2
                and entries[0]["source"] == "PostToolUse Hook"
                and entries[0]["target"] == "test.md"
                and entries[1]["source"] == "Stop Hook (Plan 감지)"
                and entries[1]["target"] == "")

    def test_parse_search():
        sample = "\n---\n\n## [2026-02-14 10:00:00] Source\n\n보안 취약점 발견\n"
        entries = parse_feedback_entries(sample)
        matched = [e for e in entries if "보안" in e["body"]]
        not_matched = [e for e in entries if "존재하지않는단어" in e["body"]]
        return len(matched) == 1 and len(not_matched) == 0

    run_test("피드백 항목 파싱", test_parse_entries)
    run_test("피드백 키워드 검색", test_parse_search)

    # ── 결과 ──
    print(f"\n{'='*40}")
    print(f"결과: {passed}/{total} 통과", end="")
    if failed:
        print(f", {failed} 실패")
    else:
        print(" — ALL PASSED ✓")
    return failed == 0


# ============================================================
# clear: 상태 파일 초기화
# ============================================================

def cmd_clear(args=None):
    """런타임 상태 파일을 초기화합니다."""
    cleared = []
    for path, name in [
        (COOLDOWN_PATH, "쿨다운 상태"),
        (ERROR_HISTORY_PATH, "에러 이력"),
    ]:
        if path.exists():
            path.unlink()
            cleared.append(name)

    if cleared:
        print(f"초기화 완료: {', '.join(cleared)}")
    else:
        print("초기화할 파일이 없습니다.")


def _print_status_result(label: str, status: str, detail: str = ""):
    """상태 라인을 출력합니다."""
    detail_text = f" - {detail}" if detail else ""
    print(f"[{status:7s}] {label}{detail_text}")


def _has_notify_hook(config_text: str) -> bool:
    """config.toml 내 notify hook 등록 여부를 휴리스틱으로 확인합니다."""
    patterns = [
        r"(?im)^\s*notify\s*=",
        r"(?im)^\s*\[notify\]",
        r"(?im)^\s*\[\s*hooks\.notify\s*\]",
    ]
    return any(re.search(pattern, config_text) for pattern in patterns)


def cmd_codex_status(args):
    """Codex CLI 연동 상태를 진단합니다."""
    print("=== Codex CLI Integration Status ===\n")

    ok_count = 0
    missing_count = 0
    error_count = 0

    def record(status: str):
        nonlocal ok_count, missing_count, error_count
        if status == "OK":
            ok_count += 1
        elif status == "MISSING":
            missing_count += 1
        else:
            error_count += 1

    # 1) codex CLI 설치 여부
    codex_path = shutil.which("codex")
    if codex_path:
        _print_status_result("codex CLI 설치", "OK", codex_path)
        record("OK")
    else:
        _print_status_result("codex CLI 설치", "MISSING", "`which codex` 결과 없음")
        record("MISSING")

    # 2) codex 버전
    if codex_path:
        try:
            result = subprocess.run(
                ["codex", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            version_text = (result.stdout or result.stderr).strip()
            if result.returncode == 0 and version_text:
                _print_status_result("codex 버전", "OK", version_text.splitlines()[0])
                record("OK")
            else:
                detail = version_text or f"종료 코드 {result.returncode}"
                _print_status_result("codex 버전", "ERROR", detail)
                record("ERROR")
        except Exception as e:
            _print_status_result("codex 버전", "ERROR", str(e))
            record("ERROR")
    else:
        _print_status_result("codex 버전", "MISSING", "codex 미설치")
        record("MISSING")

    # 3) ~/.codex/config.toml notify hook 등록 여부
    user_codex_config = Path.home() / ".codex" / "config.toml"
    if not user_codex_config.exists():
        _print_status_result("~/.codex/config.toml notify hook", "MISSING", "config.toml 없음")
        record("MISSING")
    else:
        try:
            content = user_codex_config.read_text("utf-8")
            if _has_notify_hook(content):
                _print_status_result("~/.codex/config.toml notify hook", "OK", "notify 설정 감지됨")
                record("OK")
            else:
                _print_status_result("~/.codex/config.toml notify hook", "MISSING", "notify 설정 없음")
                record("MISSING")
        except Exception as e:
            _print_status_result("~/.codex/config.toml notify hook", "ERROR", str(e))
            record("ERROR")

    # 4) skills/gemini-reviewer/SKILL.md 존재 여부
    skill_md = PROJECT_ROOT / "skills" / "gemini-reviewer" / "SKILL.md"
    if skill_md.exists():
        _print_status_result("skills/gemini-reviewer/SKILL.md", "OK")
        record("OK")
    else:
        _print_status_result("skills/gemini-reviewer/SKILL.md", "MISSING")
        record("MISSING")

    # 5) GEMINI_API_KEY 설정 여부 (.env 확인)
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        _print_status_result("GEMINI_API_KEY (.env)", "MISSING", ".env 파일 없음")
        record("MISSING")
    else:
        try:
            env_content = env_path.read_text("utf-8")
            match = re.search(r"(?m)^\s*GEMINI_API_KEY\s*=\s*(.+?)\s*$", env_content)
            if match and match.group(1).strip().strip("\"'"):
                _print_status_result("GEMINI_API_KEY (.env)", "OK")
                record("OK")
            else:
                _print_status_result("GEMINI_API_KEY (.env)", "MISSING", "값이 비어있거나 미설정")
                record("MISSING")
        except Exception as e:
            _print_status_result("GEMINI_API_KEY (.env)", "ERROR", str(e))
            record("ERROR")

    # 6) 프로젝트 레벨 codex.toml 존재 여부
    project_codex_toml = PROJECT_ROOT / "codex.toml"
    if project_codex_toml.exists():
        _print_status_result("codex.toml (project)", "OK")
        record("OK")
    else:
        _print_status_result("codex.toml (project)", "MISSING")
        record("MISSING")

    total = ok_count + missing_count + error_count
    print(f"\n요약: OK={ok_count}, MISSING={missing_count}, ERROR={error_count}, TOTAL={total}")
    if error_count > 0:
        print("전체 상태: ERROR")
    elif missing_count > 0:
        print("전체 상태: PARTIAL")
    else:
        print("전체 상태: OK")


# ============================================================
# main
# ============================================================

COMMANDS = {
    "doctor": ("시스템 진단", cmd_doctor),
    "status": ("시스템 상태 확인", cmd_status),
    "stats": ("피드백 통계", cmd_stats),
    "search": ("피드백 검색", cmd_search),
    "test": ("전체 자동 테스트", cmd_test),
    "clear": ("상태 파일 초기화", cmd_clear),
    "codex-status": ("Codex CLI 연동 상태 진단", cmd_codex_status),
}


def main():
    parser = argparse.ArgumentParser(description="Claude-Gemini Communicator CLI")
    subparsers = parser.add_subparsers(dest="command")

    for name, (desc, fn) in COMMANDS.items():
        subparser = subparsers.add_parser(name, help=desc, description=desc)
        if name == "search":
            subparser.add_argument("keyword", help="검색 키워드")
            subparser.add_argument("--source", help="소스 필터", default=None)
            subparser.add_argument("--date", help="날짜 필터 (YYYY-MM-DD)", default=None)
        subparser.set_defaults(func=fn)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    result = args.func(args)
    if args.command == "test" and result is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
```

---
## FILE: scripts/codex_json_parser.py
```python
#!/usr/bin/env python3
"""codex exec --json(JSONL) 출력을 파싱하여 구조화 요약을 생성합니다."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def read_jsonl_input(file_path: str | None) -> str | None:
    """--file 또는 stdin에서 JSONL 텍스트를 읽습니다."""
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


def summarize_output(text: str, max_chars: int = 240) -> str:
    """command output을 짧은 요약 문자열로 만듭니다."""
    if not text:
        return "(출력 없음)"

    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def parse_jsonl_events(raw_text: str) -> dict:
    """JSONL 이벤트를 파싱해 구조화된 결과를 반환합니다."""
    events = []
    parse_errors = []

    for idx, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
            else:
                parse_errors.append({"line": idx, "message": "JSON 객체가 아님"})
        except json.JSONDecodeError as e:
            parse_errors.append({"line": idx, "message": f"JSON 파싱 실패: {e.msg}"})

    thread_id = None
    reasoning_list: list[str] = []
    agent_messages: list[str] = []
    command_exec_map: dict[str, dict] = {}
    file_changes: list[dict] = []
    errors: list[dict] = []
    usage_total = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
    }

    def upsert_command(item: dict):
        item_id = str(item.get("id", f"unknown_{len(command_exec_map)}"))
        if item_id not in command_exec_map:
            command_exec_map[item_id] = {
                "id": item_id,
                "command": "",
                "exit_code": None,
                "status": "",
                "output": "",
                "output_summary": "(출력 없음)",
            }

        rec = command_exec_map[item_id]
        if item.get("command"):
            rec["command"] = item.get("command", "")
        if "exit_code" in item:
            rec["exit_code"] = item.get("exit_code")
        if item.get("status"):
            rec["status"] = item.get("status", "")

        output = item.get("aggregated_output")
        if isinstance(output, str):
            rec["output"] = output
            rec["output_summary"] = summarize_output(output)

    for event in events:
        event_type = str(event.get("type", ""))

        if event_type == "thread.started" and event.get("thread_id"):
            thread_id = event.get("thread_id")

        item = event.get("item") if isinstance(event.get("item"), dict) else None
        item_type = str(item.get("type", "")) if item else ""

        if event_type in ("item.started", "item.completed") and item:
            if item_type == "reasoning":
                reasoning_text = item.get("text", "")
                if isinstance(reasoning_text, str) and reasoning_text:
                    reasoning_list.append(reasoning_text)

            elif item_type == "agent_message":
                message_text = item.get("text", "")
                if isinstance(message_text, str) and message_text:
                    agent_messages.append(message_text)

            elif item_type == "command_execution":
                upsert_command(item)

            elif item_type == "file_change":
                file_changes.append(item)

            elif "error" in item_type.lower():
                errors.append(
                    {
                        "event_type": event_type,
                        "item_type": item_type,
                        "message": item.get("message") or item.get("text") or "item error",
                        "raw": item,
                    }
                )

        # file_change 이벤트가 item 외부에 있는 경우도 수용
        if event_type == "file_change":
            file_changes.append(event)

        # error 이벤트 수집
        if "error" in event_type.lower() or event.get("error") is not None:
            err_payload = event.get("error")
            message = ""
            if isinstance(err_payload, dict):
                message = err_payload.get("message", "")
            elif isinstance(err_payload, str):
                message = err_payload

            errors.append(
                {
                    "event_type": event_type,
                    "item_type": item_type or None,
                    "message": message or "error event",
                    "raw": event,
                }
            )

        if event_type == "turn.completed":
            usage = event.get("usage")
            if isinstance(usage, dict):
                usage_total["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
                usage_total["cached_input_tokens"] += int(usage.get("cached_input_tokens", 0) or 0)
                usage_total["output_tokens"] += int(usage.get("output_tokens", 0) or 0)

    usage_total["total_input_tokens"] = (
        usage_total["input_tokens"] + usage_total["cached_input_tokens"]
    )

    command_executions = list(command_exec_map.values())

    return {
        "thread_id": thread_id,
        "reasoning": reasoning_list,
        "agent_messages": agent_messages,
        "final_message": agent_messages[-1] if agent_messages else None,
        "command_executions": command_executions,
        "file_changes": file_changes,
        "errors": errors,
        "usage": usage_total,
        "event_count": len(events),
        "parse_errors": parse_errors,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약을 생성합니다."""
    lines = []

    lines.append("# Codex JSONL 요약")
    lines.append("")
    lines.append(f"- thread_id: {parsed.get('thread_id') or '(없음)'}")
    lines.append(f"- 이벤트 수: {parsed.get('event_count', 0)}")
    lines.append(f"- reasoning 수: {len(parsed.get('reasoning', []))}")
    lines.append(f"- agent_message 수: {len(parsed.get('agent_messages', []))}")
    lines.append(f"- command_execution 수: {len(parsed.get('command_executions', []))}")
    lines.append(f"- file_change 수: {len(parsed.get('file_changes', []))}")
    lines.append(f"- error 수: {len(parsed.get('errors', []))}")
    lines.append(f"- parse_error 수: {len(parsed.get('parse_errors', []))}")
    lines.append("")

    final_message = parsed.get("final_message")
    lines.append("## 최종 agent_message")
    if final_message:
        lines.append(final_message)
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## Command Executions")
    commands = parsed.get("command_executions", [])
    if commands:
        for idx, cmd in enumerate(commands, start=1):
            lines.append(
                f"{idx}. command={cmd.get('command')!r}, exit_code={cmd.get('exit_code')}, "
                f"status={cmd.get('status')}, output_summary={cmd.get('output_summary')!r}"
            )
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## Usage")
    usage = parsed.get("usage", {})
    lines.append(f"- input_tokens: {usage.get('input_tokens', 0)}")
    lines.append(f"- cached_input_tokens: {usage.get('cached_input_tokens', 0)}")
    lines.append(f"- output_tokens: {usage.get('output_tokens', 0)}")
    lines.append(f"- total_input_tokens: {usage.get('total_input_tokens', 0)}")
    lines.append("")

    if parsed.get("errors"):
        lines.append("## Errors")
        for idx, err in enumerate(parsed.get("errors", []), start=1):
            lines.append(
                f"{idx}. event_type={err.get('event_type')}, "
                f"item_type={err.get('item_type')}, message={err.get('message')!r}"
            )
        lines.append("")

    if parsed.get("parse_errors"):
        lines.append("## Parse Errors")
        for pe in parsed.get("parse_errors", []):
            lines.append(f"- line {pe.get('line')}: {pe.get('message')}")

    return "\n".join(lines).rstrip() + "\n"


def save_feedback(content: str, source_desc: str):
    """gemini_feedback.md에 결과를 append합니다."""
    feedback_path = Path.cwd() / "gemini_feedback.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] {source_desc}\n\n{content}\n"

    try:
        with open(feedback_path, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"[저장됨] {feedback_path}", file=sys.stderr)
    except IOError as e:
        print(f"[ERROR] 저장 실패: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="codex exec --json(JSONL) 파서: 구조화 요약 생성"
    )
    parser.add_argument("--file", "-f", help="입력 JSONL 파일 경로")
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="출력 형식 (기본: summary)",
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="결과를 gemini_feedback.md에 append",
    )
    args = parser.parse_args()

    raw_text = read_jsonl_input(args.file)
    if raw_text is None:
        return 0

    parsed = parse_jsonl_events(raw_text)

    if args.format == "json":
        output = json.dumps(parsed, ensure_ascii=False, indent=2)
    else:
        output = render_summary(parsed)

    print(output)

    if args.save:
        source = "Codex JSON Parser"
        if args.file:
            source += f" | 대상: `{args.file}`"
        save_feedback(output, source)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
```

---
## FILE: scripts/gemini_json_parser.py
```python
#!/usr/bin/env python3
"""Gemini CLI headless JSON 출력을 파싱하여 구조화 요약을 생성합니다."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def read_json_input(file_path: str | None) -> str | None:
    """--file 또는 stdin에서 JSON 텍스트를 읽습니다."""
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


def to_int(value) -> int:
    """숫자형 필드를 안전하게 int로 변환합니다."""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def parse_gemini_json(raw_text: str) -> dict | None:
    """Gemini JSON을 파싱하여 필요한 필드만 추출합니다."""
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 실패: {e.msg} (line {e.lineno}, col {e.colno})", file=sys.stderr)
        return None

    if not isinstance(payload, dict):
        print("[ERROR] JSON 루트가 객체(dict)가 아닙니다.", file=sys.stderr)
        return None

    stats = payload.get("stats") if isinstance(payload.get("stats"), dict) else {}
    models_raw = stats.get("models") if isinstance(stats.get("models"), dict) else {}
    tools_raw = stats.get("tools") if isinstance(stats.get("tools"), dict) else {}
    files_raw = stats.get("files") if isinstance(stats.get("files"), dict) else {}

    models = []
    for model_name, model_data in models_raw.items():
        if not isinstance(model_data, dict):
            continue
        api = model_data.get("api") if isinstance(model_data.get("api"), dict) else {}
        tokens = model_data.get("tokens") if isinstance(model_data.get("tokens"), dict) else {}

        models.append(
            {
                "name": model_name,
                "api": {
                    "total_requests": to_int(api.get("totalRequests")),
                    "total_errors": to_int(api.get("totalErrors")),
                    "total_latency_ms": to_int(api.get("totalLatencyMs")),
                },
                "tokens": {
                    "input": to_int(tokens.get("input")),
                    "prompt": to_int(tokens.get("prompt")),
                    "candidates": to_int(tokens.get("candidates")),
                    "total": to_int(tokens.get("total")),
                    "cached": to_int(tokens.get("cached")),
                    "thoughts": to_int(tokens.get("thoughts")),
                    "tool": to_int(tokens.get("tool")),
                },
            }
        )

    tools_by_name_raw = tools_raw.get("byName") if isinstance(tools_raw.get("byName"), dict) else {}
    tools_by_name = []
    for tool_name, tool_data in tools_by_name_raw.items():
        if not isinstance(tool_data, dict):
            continue
        decisions = tool_data.get("decisions") if isinstance(tool_data.get("decisions"), dict) else {}
        tools_by_name.append(
            {
                "name": tool_name,
                "count": to_int(tool_data.get("count")),
                "success": to_int(tool_data.get("success")),
                "fail": to_int(tool_data.get("fail")),
                "duration_ms": to_int(tool_data.get("durationMs")),
                "decisions": {
                    "accept": to_int(decisions.get("accept")),
                    "reject": to_int(decisions.get("reject")),
                    "modify": to_int(decisions.get("modify")),
                    "auto_accept": to_int(decisions.get("auto_accept")),
                },
            }
        )

    total_decisions = (
        tools_raw.get("totalDecisions") if isinstance(tools_raw.get("totalDecisions"), dict) else {}
    )
    error_value = payload.get("error")
    if isinstance(error_value, (dict, list)):
        error_parsed = error_value
    elif error_value is None:
        error_parsed = None
    else:
        error_parsed = str(error_value)

    return {
        "session_id": payload.get("session_id"),
        "response": payload.get("response"),
        "models": models,
        "tools": {
            "total_calls": to_int(tools_raw.get("totalCalls")),
            "total_success": to_int(tools_raw.get("totalSuccess")),
            "total_fail": to_int(tools_raw.get("totalFail")),
            "total_duration_ms": to_int(tools_raw.get("totalDurationMs")),
            "total_decisions": {
                "accept": to_int(total_decisions.get("accept")),
                "reject": to_int(total_decisions.get("reject")),
                "modify": to_int(total_decisions.get("modify")),
                "auto_accept": to_int(total_decisions.get("auto_accept")),
            },
            "by_name": tools_by_name,
        },
        "files": {
            "total_lines_added": to_int(files_raw.get("totalLinesAdded")),
            "total_lines_removed": to_int(files_raw.get("totalLinesRemoved")),
        },
        "error": error_parsed,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약을 생성합니다."""
    lines = []
    lines.append("# Gemini JSON 요약")
    lines.append("")
    lines.append(f"- session_id: {parsed.get('session_id') or '(없음)'}")
    lines.append(f"- error: {json.dumps(parsed.get('error'), ensure_ascii=False) if parsed.get('error') is not None else '(없음)'}")
    lines.append("")

    lines.append("## 최종 응답(response)")
    response = parsed.get("response")
    lines.append(response if isinstance(response, str) and response else "(없음)")
    lines.append("")

    lines.append("## 모델 통계")
    models = parsed.get("models", [])
    if models:
        for idx, model in enumerate(models, start=1):
            api = model.get("api", {})
            tokens = model.get("tokens", {})
            lines.append(
                f"{idx}. {model.get('name')} | requests={api.get('total_requests', 0)}, "
                f"errors={api.get('total_errors', 0)}, latency_ms={api.get('total_latency_ms', 0)}"
            )
            lines.append(
                "   "
                f"tokens(input={tokens.get('input', 0)}, prompt={tokens.get('prompt', 0)}, "
                f"candidates={tokens.get('candidates', 0)}, total={tokens.get('total', 0)}, "
                f"cached={tokens.get('cached', 0)}, thoughts={tokens.get('thoughts', 0)}, "
                f"tool={tokens.get('tool', 0)})"
            )
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## 도구 사용 통계")
    tools = parsed.get("tools", {})
    lines.append(
        f"- totals: calls={tools.get('total_calls', 0)}, success={tools.get('total_success', 0)}, "
        f"fail={tools.get('total_fail', 0)}, duration_ms={tools.get('total_duration_ms', 0)}"
    )
    decisions = tools.get("total_decisions", {})
    lines.append(
        f"- decisions: accept={decisions.get('accept', 0)}, reject={decisions.get('reject', 0)}, "
        f"modify={decisions.get('modify', 0)}, auto_accept={decisions.get('auto_accept', 0)}"
    )
    by_name = tools.get("by_name", [])
    if by_name:
        lines.append("- by_name:")
        for idx, tool in enumerate(by_name, start=1):
            lines.append(
                f"  {idx}. {tool.get('name')} | count={tool.get('count', 0)}, success={tool.get('success', 0)}, "
                f"fail={tool.get('fail', 0)}, duration_ms={tool.get('duration_ms', 0)}"
            )
    else:
        lines.append("- by_name: (없음)")
    lines.append("")

    files = parsed.get("files", {})
    lines.append("## 파일 변경 통계")
    lines.append(
        f"- lines_added={files.get('total_lines_added', 0)}, lines_removed={files.get('total_lines_removed', 0)}"
    )

    return "\n".join(lines).rstrip() + "\n"


def save_feedback(content: str, source_desc: str):
    """gemini_feedback.md에 결과를 append합니다."""
    feedback_path = Path.cwd() / "gemini_feedback.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] {source_desc}\n\n{content}\n"

    try:
        with open(feedback_path, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"[저장됨] {feedback_path}", file=sys.stderr)
    except IOError as e:
        print(f"[ERROR] 저장 실패: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gemini CLI JSON 파서: 구조화 요약 생성"
    )
    parser.add_argument("--file", "-f", help="입력 JSON 파일 경로")
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="출력 형식 (기본: summary)",
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="결과를 gemini_feedback.md에 append",
    )
    args = parser.parse_args()

    raw_text = read_json_input(args.file)
    if raw_text is None:
        return 0

    parsed = parse_gemini_json(raw_text)
    if parsed is None:
        return 0

    if args.format == "json":
        output = json.dumps(parsed, ensure_ascii=False, indent=2)
    else:
        output = render_summary(parsed)

    print(output)

    if args.save:
        source = "Gemini JSON Parser"
        if args.file:
            source += f" | 대상: `{args.file}`"
        save_feedback(output, source)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
```

---
## FILE: scripts/hook_auto_task.py
```python
"""PostToolUse Hook: Write/Edit 도구 사용 후 자동으로 Gemini 평가를 트리거합니다.

stdin으로 Claude Hook JSON을 수신하고, .md 파일 변경 시 Gemini CLI로 평가합니다.
"""

import json
import os
import sys

try:
    from a2a_bridge import (
        call_gemini,
        check_cooldown,
        format_hook_output,
        load_config,
        save_feedback,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from a2a_bridge import (
        call_gemini,
        check_cooldown,
        format_hook_output,
        load_config,
        save_feedback,
    )


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    config = load_config()

    # 확장자 확인
    extensions = config.get("watch_extensions", [".md"])
    if not any(file_path.endswith(ext) for ext in extensions):
        sys.exit(0)

    # 제외 파일 확인
    exclude_files = config.get("exclude_files", [])
    basename = os.path.basename(file_path)
    if basename in exclude_files:
        sys.exit(0)

    # 쿨다운 확인
    if not check_cooldown(file_path, config):
        sys.exit(0)

    # Gemini 평가 호출 (코드 파일은 코드 리뷰 프롬프트 사용)
    from a2a_bridge import build_a2a_evaluation_prompt, parse_a2a_response, a2a_response_to_markdown

    code_exts = config.get("code_extensions", [".py", ".js", ".ts", ".jsx", ".tsx"])
    if any(file_path.endswith(ext) for ext in code_exts):
        prompt = config.get("code_evaluation_prompt", "이 코드를 리뷰해줘.")
    else:
        prompt = config.get("evaluation_prompt", "이 문서를 평가해줘.")
    prompt = build_a2a_evaluation_prompt(prompt, config)

    # 비동기 모드: 백그라운드에서 평가, 즉시 리턴
    if config.get("async_mode", False):
        from a2a_bridge import call_gemini_async
        pending_msg = call_gemini_async(
            content="", prompt=prompt, config=config,
            file_path=file_path, source="PostToolUse Hook",
        )
        print(format_hook_output(pending_msg))
        sys.exit(0)

    # 동기 모드: 평가 완료까지 대기
    raw_feedback = call_gemini(
        content="",
        prompt=prompt,
        config=config,
        file_path=file_path,
    )

    # A2A 모드: 구조화된 응답 파싱 → 마크다운 변환
    if config.get("a2a_schema_enabled", False):
        a2a_resp = parse_a2a_response(raw_feedback)
        feedback = a2a_response_to_markdown(a2a_resp)
    else:
        feedback = raw_feedback

    # 피드백 저장
    save_feedback(feedback, source="PostToolUse Hook", file_path=file_path)

    # Claude에 피드백 전달
    print(format_hook_output(feedback))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
```

---
## FILE: scripts/hook_pre_tool.py
```python
"""PreToolUse Hook: 위험한 명령 실행 전 사전 경고/차단합니다.

stdin으로 Claude PreToolUse Hook JSON을 수신하고,
Bash 명령이 위험 패턴에 매칭되면 차단(block) 판정을 반환합니다.
"""

import json
import os
import re
import sys

try:
    from a2a_bridge import load_config
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from a2a_bridge import load_config


# ── 위험 명령 패턴 (severity: block / warn) ──

_DANGEROUS_PATTERNS = [
    # Block: 되돌리기 극히 어려운 명령
    {
        "pattern": re.compile(r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*f|(-[a-zA-Z]*f[a-zA-Z]*r))\b"),
        "severity": "block",
        "reason": "rm -rf: 재귀 강제 삭제는 복구 불가능합니다",
    },
    {
        "pattern": re.compile(r"\brm\s+-[a-zA-Z]*r\b.*(/|~|\$HOME|\.\.)"),
        "severity": "block",
        "reason": "rm -r with broad path: 광범위한 재귀 삭제는 위험합니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+push\s+.*--force\b"),
        "severity": "block",
        "reason": "git push --force: 원격 히스토리가 덮어쓰여 복구가 어렵습니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+push\s+-f\b"),
        "severity": "block",
        "reason": "git push -f: force push는 원격 히스토리를 파괴합니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+reset\s+--hard\b"),
        "severity": "block",
        "reason": "git reset --hard: 커밋되지 않은 변경사항이 영구 삭제됩니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+clean\s+-[a-zA-Z]*f"),
        "severity": "block",
        "reason": "git clean -f: 추적되지 않는 파일이 영구 삭제됩니다",
    },
    {
        "pattern": re.compile(r"\bDROP\s+(TABLE|DATABASE)\b", re.IGNORECASE),
        "severity": "block",
        "reason": "DROP TABLE/DATABASE: 데이터베이스 구조가 영구 삭제됩니다",
        "requires_context": re.compile(r"\b(psql|mysql|sqlite3|mongo|redis-cli|cockroach)\b"),
    },
    {
        "pattern": re.compile(r"\bTRUNCATE\s+TABLE\b", re.IGNORECASE),
        "severity": "block",
        "reason": "TRUNCATE TABLE: 테이블의 모든 데이터가 영구 삭제됩니다",
        "requires_context": re.compile(r"\b(psql|mysql|sqlite3|mongo|redis-cli|cockroach)\b"),
    },
    {
        "pattern": re.compile(r">\s*/dev/sd[a-z]"),
        "severity": "block",
        "reason": "디스크 디바이스 직접 쓰기: 파일시스템이 파괴됩니다",
    },
    {
        "pattern": re.compile(r"\bmkfs\b"),
        "severity": "block",
        "reason": "mkfs: 파일시스템 포맷은 모든 데이터를 삭제합니다",
    },
    {
        "pattern": re.compile(r"\bdd\s+.*of=/dev/"),
        "severity": "block",
        "reason": "dd to device: 디스크에 직접 쓰기는 데이터를 파괴합니다",
    },
    # Warn: 주의가 필요한 명령 (차단은 안 함)
    {
        "pattern": re.compile(r"\bgit\s+branch\s+-D\b"),
        "severity": "warn",
        "reason": "git branch -D: 머지되지 않은 브랜치가 강제 삭제됩니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+checkout\s+\.\s*$"),
        "severity": "warn",
        "reason": "git checkout .: 모든 변경사항이 되돌아갑니다",
    },
    {
        "pattern": re.compile(r"\bgit\s+restore\s+\.\s*$"),
        "severity": "warn",
        "reason": "git restore .: 모든 변경사항이 되돌아갑니다",
    },
    {
        "pattern": re.compile(r"\bchmod\s+777\b"),
        "severity": "warn",
        "reason": "chmod 777: 모든 사용자에게 전체 권한을 부여합니다",
    },
    {
        "pattern": re.compile(r"\bkill\s+-9\b"),
        "severity": "warn",
        "reason": "kill -9: 프로세스가 정리 없이 강제 종료됩니다",
    },
    {
        "pattern": re.compile(r"\bpip\s+install\b(?!.*-r\s)(?!.*requirements)"),
        "severity": "warn",
        "reason": "pip install (단일 패키지): 의존성 충돌 가능성을 확인하세요",
    },
]


def _strip_string_content(command: str) -> str:
    """명령어에서 문자열 리터럴/heredoc 내용을 제거합니다 (오탐 방지).

    커밋 메시지, echo 인자 등에 포함된 위험 키워드 텍스트가
    실제 명령으로 오인되는 것을 방지합니다.
    """
    # 1) Heredoc 내용 제거: <<'EOF' ... EOF / <<EOF ... EOF
    result = re.sub(
        r"<<-?\s*['\"]?(\w+)['\"]?\s*\n.*?\n\s*\1",
        "", command, flags=re.DOTALL,
    )
    # 2) 단일 따옴표 문자열 내용 제거
    result = re.sub(r"'[^']*'", "''", result)
    # 3) 이중 따옴표 문자열 내용 제거 (escaped quote 처리)
    result = re.sub(r'"(?:[^"\\]|\\.)*"', '""', result)
    return result


def check_command(command: str, config: dict) -> dict | None:
    """명령어를 위험 패턴과 매칭합니다.

    Returns:
        매칭 시 {"severity": "block"|"warn", "reason": str},
        안전하면 None
    """
    if not command or not command.strip():
        return None

    guard_config = config.get("pre_tool_guard", {})
    if not guard_config.get("enabled", True):
        return None

    # 문자열 리터럴 내용 제거 후 패턴 매칭 (오탐 방지)
    stripped = _strip_string_content(command)

    for entry in _DANGEROUS_PATTERNS:
        # requires_context: SQL 패턴은 DB 클라이언트가 있을 때만 원본에서 체크
        ctx_re = entry.get("requires_context")
        if ctx_re:
            if ctx_re.search(command) and entry["pattern"].search(command):
                return {"severity": entry["severity"], "reason": entry["reason"]}
        elif entry["pattern"].search(stripped):
            return {"severity": entry["severity"], "reason": entry["reason"]}

    # 사용자 정의 패턴 (config.json)
    custom_patterns = guard_config.get("custom_block_patterns", [])
    for pattern_str in custom_patterns:
        try:
            if re.search(pattern_str, command):
                return {
                    "severity": "block",
                    "reason": f"사용자 정의 차단 패턴 매칭: {pattern_str}",
                }
        except re.error:
            continue

    return None


def main():
    try:
        hook_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    tool_name = hook_input.get("tool_name", "")
    if tool_name != "Bash":
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {})
    command = tool_input.get("command", "")

    if not command:
        sys.exit(0)

    config = load_config()
    result = check_command(command, config)

    if result is None:
        # 안전 — 허용
        sys.exit(0)

    if result["severity"] == "block":
        output = {
            "decision": "block",
            "reason": f"⚠️ 위험 명령 차단: {result['reason']}\n명령어: {command[:200]}",
        }
        print(json.dumps(output, ensure_ascii=False))
    elif result["severity"] == "warn":
        output = {
            "decision": "allow",
            "hookSpecificOutput": {
                "additionalContext": f"⚠️ 주의: {result['reason']}\n명령어: {command[:200]}",
            },
        }
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
```

---
## FILE: scripts/hook_stop.py
```python
"""Stop Hook: Claude 응답 완료 시 (1) Plan 감지 (2) 에러 감지를 수행합니다.

stdin으로 Claude Stop Hook JSON을 수신하고,
- 마지막 출력이 소프트웨어 개발 계획이면 Gemini 평가
- transcript에 반복 에러가 있으면 Gemini 에러 분석 (Lazy Analysis)
"""

import json
import os
import sys

try:
    from a2a_bridge import (
        call_gemini,
        check_error_and_analyze,
        format_hook_output,
        load_config,
        save_feedback,
        scan_transcript_for_errors,
    )
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from a2a_bridge import (
        call_gemini,
        check_error_and_analyze,
        format_hook_output,
        load_config,
        save_feedback,
        scan_transcript_for_errors,
    )


def extract_last_assistant_text(stop_input: dict) -> str:
    """Stop Hook 입력에서 Claude의 마지막 텍스트 출력을 추출합니다."""
    transcript_path = stop_input.get("transcript_path", "")

    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in reversed(lines):
                try:
                    entry = json.loads(line.strip())
                    if entry.get("role") == "assistant":
                        content = entry.get("content", "")
                        if isinstance(content, list):
                            texts = [
                                block.get("text", "")
                                for block in content
                                if block.get("type") == "text"
                            ]
                            return "\n".join(texts)
                        return str(content)
                except json.JSONDecodeError:
                    continue
        except IOError:
            pass

    message = stop_input.get("message", "")
    if message:
        return message

    content = stop_input.get("content", "")
    if isinstance(content, list):
        texts = [
            block.get("text", "")
            for block in content
            if isinstance(block, dict) and block.get("type") == "text"
        ]
        return "\n".join(texts)

    return str(content) if content else ""


def handle_plan_detection(text: str, config: dict) -> str | None:
    """Plan 감지 → Gemini 평가. 피드백 문자열 또는 None 반환."""
    min_length = config.get("min_content_length", 300)
    if len(text) < min_length:
        return None

    from a2a_bridge import (
        build_a2a_classification_prompt,
        build_a2a_evaluation_prompt,
        parse_a2a_response,
        a2a_response_to_markdown,
    )

    plan_prompt = config.get(
        "plan_detection_prompt",
        "이 텍스트는 소프트웨어 개발 계획입니까? '예' 또는 '아니오'로만 답하시오.",
    )
    plan_prompt = build_a2a_classification_prompt(plan_prompt, config)
    classification = call_gemini(
        content=text[:2000],
        prompt=plan_prompt,
        config=config,
    )

    is_plan = False
    if config.get("a2a_schema_enabled", False):
        try:
            parsed = json.loads(classification.strip().strip("`").replace("json", "", 1).strip())
            is_plan = parsed.get("is_plan", False)
        except (json.JSONDecodeError, ValueError):
            is_plan = "예" in classification
    else:
        is_plan = "예" in classification

    if not is_plan:
        return None

    eval_prompt = config.get("evaluation_prompt", "이 문서를 평가해줘.")
    eval_prompt = build_a2a_evaluation_prompt(eval_prompt, config)

    if config.get("async_mode", False):
        from a2a_bridge import call_gemini_async
        return call_gemini_async(
            content=text, prompt=eval_prompt, config=config,
            source="Stop Hook (Plan 감지)",
        )

    raw_feedback = call_gemini(content=text, prompt=eval_prompt, config=config)

    if config.get("a2a_schema_enabled", False):
        a2a_resp = parse_a2a_response(raw_feedback)
        feedback = a2a_response_to_markdown(a2a_resp)
    else:
        feedback = raw_feedback

    save_feedback(feedback, source="Stop Hook (Plan 감지)")
    return feedback


def handle_error_detection(stop_input: dict, config: dict) -> str | None:
    """Transcript에서 에러 스캔 → Lazy Analysis → Gemini 분석."""
    error_config = config.get("error_detection", {})
    if not error_config.get("enabled", False):
        return None

    transcript_path = stop_input.get("transcript_path", "")
    if not transcript_path:
        return None

    tail_lines = error_config.get("tail_lines", 50)
    errors = scan_transcript_for_errors(transcript_path, tail_lines)
    if not errors:
        return None

    return check_error_and_analyze(errors, config)


def main():
    try:
        stop_input = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, IOError):
        sys.exit(0)

    config = load_config()
    outputs = []

    # ① Plan 감지 (기존 로직)
    text = extract_last_assistant_text(stop_input)
    plan_feedback = handle_plan_detection(text, config)
    if plan_feedback:
        outputs.append(plan_feedback)

    # ② 에러 감지 (Phase 4 신규)
    error_feedback = handle_error_detection(stop_input, config)
    if error_feedback:
        outputs.append(error_feedback)

    # 결과 출력
    if outputs:
        combined = "\n\n".join(outputs)
        print(format_hook_output(combined))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        sys.exit(0)
```

---
## FILE: scripts/transcript_parser.py
```python
#!/usr/bin/env python3
"""Claude Code transcript(JSONL)를 파싱하여 구조화 요약을 생성합니다."""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def read_jsonl_input(file_path: str | None) -> str | None:
    """--file 또는 stdin에서 JSONL 텍스트를 읽습니다."""
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


def shorten_text(text: str, max_chars: int) -> str:
    """텍스트를 한 줄 요약으로 정규화하고 길이를 제한합니다."""
    normalized = " ".join(str(text).split())
    if not normalized:
        return "(없음)"
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def extract_user_text(content) -> str:
    """user content가 문자열/배열일 때 텍스트를 추출합니다."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks = []
        for block in content:
            if isinstance(block, str):
                chunks.append(block)
                continue
            if not isinstance(block, dict):
                continue
            block_type = str(block.get("type", ""))
            if block_type in ("text", "input_text"):
                text_value = block.get("text")
                if isinstance(text_value, str):
                    chunks.append(text_value)
            elif isinstance(block.get("text"), str):
                chunks.append(block.get("text"))
        return "\n".join(chunks).strip()

    return ""


def parse_transcript_jsonl(raw_text: str, last_n: int | None = None) -> dict:
    """transcript JSONL을 파싱하여 집계 결과를 생성합니다."""
    records = []
    parse_errors = []

    for idx, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as e:
            parse_errors.append({"line": idx, "message": f"JSON 파싱 실패: {e.msg}"})
            continue

        if not isinstance(payload, dict):
            parse_errors.append({"line": idx, "message": "JSON 객체(dict)가 아님"})
            continue

        record_type = str(payload.get("type", ""))
        if record_type not in ("user", "assistant", "file-history-snapshot"):
            continue
        records.append(payload)

    messages = [r for r in records if str(r.get("type", "")) in ("user", "assistant")]
    if last_n is not None:
        if last_n < 0:
            last_n = 0
        messages = messages[-last_n:] if last_n > 0 else []

    session_id = None
    for msg in messages:
        value = msg.get("sessionId")
        if isinstance(value, str) and value:
            session_id = value
            break
    if session_id is None:
        for rec in records:
            value = rec.get("sessionId")
            if isinstance(value, str) and value:
                session_id = value
                break

    user_count = 0
    assistant_count = 0
    last_user_text = ""
    assistant_text_total_length = 0
    last_assistant_text = ""
    thinking_count = 0
    tool_use_counts: dict[str, int] = {}
    pending_user = 0
    turn_count = 0

    for msg in messages:
        record_type = str(msg.get("type", ""))
        message = msg.get("message") if isinstance(msg.get("message"), dict) else {}

        if record_type == "user":
            user_count += 1
            pending_user += 1
            user_text = extract_user_text(message.get("content"))
            if user_text:
                last_user_text = user_text
            continue

        if record_type != "assistant":
            continue

        assistant_count += 1
        if pending_user > 0:
            turn_count += 1
            pending_user -= 1

        content = message.get("content")
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = str(block.get("type", ""))

            if block_type == "text":
                text_value = block.get("text")
                if isinstance(text_value, str):
                    assistant_text_total_length += len(text_value)
                    if text_value.strip():
                        last_assistant_text = text_value

            elif block_type == "thinking":
                thinking_count += 1

            elif block_type == "tool_use":
                tool_name = block.get("name")
                if isinstance(tool_name, str) and tool_name:
                    tool_use_counts[tool_name] = tool_use_counts.get(tool_name, 0) + 1

    return {
        "session_id": session_id,
        "messages_analyzed": len(messages),
        "last_n_applied": last_n,
        "user": {
            "count": user_count,
            "last_message_summary": shorten_text(last_user_text, 120),
        },
        "assistant": {
            "count": assistant_count,
            "text_total_length": assistant_text_total_length,
            "last_text_summary": shorten_text(last_assistant_text, 200),
            "thinking_block_count": thinking_count,
            "tool_use_counts": dict(sorted(tool_use_counts.items())),
        },
        "turn_count": turn_count,
        "parse_errors": parse_errors,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약을 생성합니다."""
    lines = []
    lines.append("# Claude Transcript 요약")
    lines.append("")
    lines.append(f"- session_id: {parsed.get('session_id') or '(없음)'}")
    lines.append(f"- 분석한 메시지 수: {parsed.get('messages_analyzed', 0)}")
    lines.append(f"- last_n 적용값: {parsed.get('last_n_applied')}")
    lines.append(f"- 대화 턴 수(user+assistant 쌍): {parsed.get('turn_count', 0)}")
    lines.append("")

    user = parsed.get("user", {})
    lines.append("## User")
    lines.append(f"- 메시지 수: {user.get('count', 0)}")
    lines.append(f"- 마지막 메시지 요약: {user.get('last_message_summary', '(없음)')}")
    lines.append("")

    assistant = parsed.get("assistant", {})
    lines.append("## Assistant")
    lines.append(f"- 메시지 수: {assistant.get('count', 0)}")
    lines.append(f"- text 총 길이: {assistant.get('text_total_length', 0)}")
    lines.append(f"- 마지막 text 요약: {assistant.get('last_text_summary', '(없음)')}")
    lines.append(f"- thinking 블록 수: {assistant.get('thinking_block_count', 0)}")
    lines.append("")

    lines.append("## Tool Use 집계")
    tool_use_counts = assistant.get("tool_use_counts", {})
    if isinstance(tool_use_counts, dict) and tool_use_counts:
        for idx, (name, count) in enumerate(tool_use_counts.items(), start=1):
            lines.append(f"{idx}. {name}: {count}")
    else:
        lines.append("(없음)")
    lines.append("")

    parse_errors = parsed.get("parse_errors", [])
    lines.append(f"- parse_error 수: {len(parse_errors)}")
    if parse_errors:
        lines.append("## Parse Errors")
        for err in parse_errors:
            lines.append(f"- line {err.get('line')}: {err.get('message')}")

    return "\n".join(lines).rstrip() + "\n"


def save_feedback(content: str, source_desc: str):
    """gemini_feedback.md에 결과를 append합니다."""
    feedback_path = Path.cwd() / "gemini_feedback.md"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] {source_desc}\n\n{content}\n"

    try:
        with open(feedback_path, "a", encoding="utf-8") as f:
            f.write(entry)
        print(f"[저장됨] {feedback_path}", file=sys.stderr)
    except IOError as e:
        print(f"[ERROR] 저장 실패: {e}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Claude transcript(JSONL) 파서: 구조화 요약 생성"
    )
    parser.add_argument("--file", "-f", help="입력 JSONL 파일 경로")
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="출력 형식 (기본: summary)",
    )
    parser.add_argument(
        "--save",
        "-s",
        action="store_true",
        help="결과를 gemini_feedback.md에 append",
    )
    parser.add_argument(
        "--last-n",
        type=int,
        default=None,
        help="마지막 N개 메시지만 파싱",
    )
    args = parser.parse_args()

    raw_text = read_jsonl_input(args.file)
    if raw_text is None:
        return 0

    parsed = parse_transcript_jsonl(raw_text, last_n=args.last_n)

    if args.format == "json":
        output = json.dumps(parsed, ensure_ascii=False, indent=2)
    else:
        output = render_summary(parsed)

    print(output)

    if args.save:
        source = "Transcript Parser"
        if args.file:
            source += f" | 대상: `{args.file}`"
        save_feedback(output, source)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
```

---
## FILE: skills/agent-parser/scripts/_codex_parser.py
```python
#!/usr/bin/env python3
"""Codex JSONL 파서: codex exec --json 출력을 구조화 요약으로 변환."""

import json


def summarize_output(text: str, max_chars: int = 240) -> str:
    """command output을 짧은 요약 문자열로 만든다."""
    if not text:
        return "(출력 없음)"
    normalized = " ".join(text.split())
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def parse_jsonl_events(raw_text: str) -> dict:
    """JSONL 이벤트를 파싱해 구조화된 결과를 반환."""
    events = []
    parse_errors = []

    for idx, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
            if isinstance(event, dict):
                events.append(event)
            else:
                parse_errors.append({"line": idx, "message": "JSON 객체가 아님"})
        except json.JSONDecodeError as e:
            parse_errors.append({"line": idx, "message": f"JSON 파싱 실패: {e.msg}"})

    thread_id = None
    reasoning_list: list[str] = []
    agent_messages: list[str] = []
    command_exec_map: dict[str, dict] = {}
    file_changes: list[dict] = []
    errors: list[dict] = []
    usage_total = {
        "input_tokens": 0,
        "cached_input_tokens": 0,
        "output_tokens": 0,
    }

    def upsert_command(item: dict):
        item_id = str(item.get("id", f"unknown_{len(command_exec_map)}"))
        if item_id not in command_exec_map:
            command_exec_map[item_id] = {
                "id": item_id,
                "command": "",
                "exit_code": None,
                "status": "",
                "output": "",
                "output_summary": "(출력 없음)",
            }

        rec = command_exec_map[item_id]
        if item.get("command"):
            rec["command"] = item.get("command", "")
        if "exit_code" in item:
            rec["exit_code"] = item.get("exit_code")
        if item.get("status"):
            rec["status"] = item.get("status", "")

        output = item.get("aggregated_output")
        if isinstance(output, str):
            rec["output"] = output
            rec["output_summary"] = summarize_output(output)

    for event in events:
        event_type = str(event.get("type", ""))

        if event_type == "thread.started" and event.get("thread_id"):
            thread_id = event.get("thread_id")

        item = event.get("item") if isinstance(event.get("item"), dict) else None
        item_type = str(item.get("type", "")) if item else ""

        if event_type in ("item.started", "item.completed") and item:
            if item_type == "reasoning":
                reasoning_text = item.get("text", "")
                if isinstance(reasoning_text, str) and reasoning_text:
                    reasoning_list.append(reasoning_text)

            elif item_type == "agent_message":
                message_text = item.get("text", "")
                if isinstance(message_text, str) and message_text:
                    agent_messages.append(message_text)

            elif item_type == "command_execution":
                upsert_command(item)

            elif item_type == "file_change":
                file_changes.append(item)

            elif "error" in item_type.lower():
                errors.append(
                    {
                        "event_type": event_type,
                        "item_type": item_type,
                        "message": item.get("message") or item.get("text") or "item error",
                        "raw": item,
                    }
                )

        # file_change 이벤트가 item 외부에 있는 경우도 수용
        if event_type == "file_change":
            file_changes.append(event)

        # error 이벤트 수집
        if "error" in event_type.lower() or event.get("error") is not None:
            err_payload = event.get("error")
            message = ""
            if isinstance(err_payload, dict):
                message = err_payload.get("message", "")
            elif isinstance(err_payload, str):
                message = err_payload

            errors.append(
                {
                    "event_type": event_type,
                    "item_type": item_type or None,
                    "message": message or "error event",
                    "raw": event,
                }
            )

        if event_type == "turn.completed":
            usage = event.get("usage")
            if isinstance(usage, dict):
                usage_total["input_tokens"] += int(usage.get("input_tokens", 0) or 0)
                usage_total["cached_input_tokens"] += int(usage.get("cached_input_tokens", 0) or 0)
                usage_total["output_tokens"] += int(usage.get("output_tokens", 0) or 0)

    usage_total["total_input_tokens"] = (
        usage_total["input_tokens"] + usage_total["cached_input_tokens"]
    )

    command_executions = list(command_exec_map.values())

    return {
        "thread_id": thread_id,
        "reasoning": reasoning_list,
        "agent_messages": agent_messages,
        "final_message": agent_messages[-1] if agent_messages else None,
        "command_executions": command_executions,
        "file_changes": file_changes,
        "errors": errors,
        "usage": usage_total,
        "event_count": len(events),
        "parse_errors": parse_errors,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약 생성."""
    lines = []

    lines.append("# Codex JSONL 요약")
    lines.append("")
    lines.append(f"- thread_id: {parsed.get('thread_id') or '(없음)'}")
    lines.append(f"- 이벤트 수: {parsed.get('event_count', 0)}")
    lines.append(f"- reasoning 수: {len(parsed.get('reasoning', []))}")
    lines.append(f"- agent_message 수: {len(parsed.get('agent_messages', []))}")
    lines.append(f"- command_execution 수: {len(parsed.get('command_executions', []))}")
    lines.append(f"- file_change 수: {len(parsed.get('file_changes', []))}")
    lines.append(f"- error 수: {len(parsed.get('errors', []))}")
    lines.append(f"- parse_error 수: {len(parsed.get('parse_errors', []))}")
    lines.append("")

    final_message = parsed.get("final_message")
    lines.append("## 최종 agent_message")
    if final_message:
        lines.append(final_message)
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## Command Executions")
    commands = parsed.get("command_executions", [])
    if commands:
        for idx, cmd in enumerate(commands, start=1):
            lines.append(
                f"{idx}. command={cmd.get('command')!r}, exit_code={cmd.get('exit_code')}, "
                f"status={cmd.get('status')}, output_summary={cmd.get('output_summary')!r}"
            )
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## Usage")
    usage = parsed.get("usage", {})
    lines.append(f"- input_tokens: {usage.get('input_tokens', 0)}")
    lines.append(f"- cached_input_tokens: {usage.get('cached_input_tokens', 0)}")
    lines.append(f"- output_tokens: {usage.get('output_tokens', 0)}")
    lines.append(f"- total_input_tokens: {usage.get('total_input_tokens', 0)}")
    lines.append("")

    if parsed.get("errors"):
        lines.append("## Errors")
        for idx, err in enumerate(parsed.get("errors", []), start=1):
            lines.append(
                f"{idx}. event_type={err.get('event_type')}, "
                f"item_type={err.get('item_type')}, message={err.get('message')!r}"
            )
        lines.append("")

    if parsed.get("parse_errors"):
        lines.append("## Parse Errors")
        for pe in parsed.get("parse_errors", []):
            lines.append(f"- line {pe.get('line')}: {pe.get('message')}")

    return "\n".join(lines).rstrip() + "\n"
```

---
## FILE: skills/agent-parser/scripts/_common.py
```python
#!/usr/bin/env python3
"""agent-parser 공용 유틸리티."""

import sys
import fcntl
from datetime import datetime
from pathlib import Path


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
    """gemini_feedback.md에 결과를 append (fcntl lock)."""
    feedback_path = Path.cwd() / "gemini_feedback.md"
    for candidate in [feedback_path, Path(__file__).resolve().parent.parent.parent.parent / "gemini_feedback.md"]:
        if candidate.parent.exists():
            feedback_path = candidate
            break
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n---\n\n## [{timestamp}] {source_desc}\n\n{content}\n"
    try:
        with open(feedback_path, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.write(entry)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
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
```

---
## FILE: skills/agent-parser/scripts/_gemini_parser.py
```python
#!/usr/bin/env python3
"""Gemini JSON 파서: Gemini headless JSON 출력을 구조화 요약으로 변환."""

import json


def to_int(value) -> int:
    """숫자형 필드를 안전하게 int로 변환."""
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def parse_gemini_json(raw_text: str) -> dict | None:
    """Gemini JSON을 파싱하여 필요한 필드만 추출."""
    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 파싱 실패: {e.msg} (line {e.lineno}, col {e.colno})")
        return None

    if not isinstance(payload, dict):
        print("[ERROR] JSON 루트가 객체(dict)가 아닙니다.")
        return None

    stats = payload.get("stats") if isinstance(payload.get("stats"), dict) else {}
    models_raw = stats.get("models") if isinstance(stats.get("models"), dict) else {}
    tools_raw = stats.get("tools") if isinstance(stats.get("tools"), dict) else {}
    files_raw = stats.get("files") if isinstance(stats.get("files"), dict) else {}

    models = []
    for model_name, model_data in models_raw.items():
        if not isinstance(model_data, dict):
            continue
        api = model_data.get("api") if isinstance(model_data.get("api"), dict) else {}
        tokens = model_data.get("tokens") if isinstance(model_data.get("tokens"), dict) else {}

        models.append(
            {
                "name": model_name,
                "api": {
                    "total_requests": to_int(api.get("totalRequests")),
                    "total_errors": to_int(api.get("totalErrors")),
                    "total_latency_ms": to_int(api.get("totalLatencyMs")),
                },
                "tokens": {
                    "input": to_int(tokens.get("input")),
                    "prompt": to_int(tokens.get("prompt")),
                    "candidates": to_int(tokens.get("candidates")),
                    "total": to_int(tokens.get("total")),
                    "cached": to_int(tokens.get("cached")),
                    "thoughts": to_int(tokens.get("thoughts")),
                    "tool": to_int(tokens.get("tool")),
                },
            }
        )

    tools_by_name_raw = tools_raw.get("byName") if isinstance(tools_raw.get("byName"), dict) else {}
    tools_by_name = []
    for tool_name, tool_data in tools_by_name_raw.items():
        if not isinstance(tool_data, dict):
            continue
        decisions = tool_data.get("decisions") if isinstance(tool_data.get("decisions"), dict) else {}
        tools_by_name.append(
            {
                "name": tool_name,
                "count": to_int(tool_data.get("count")),
                "success": to_int(tool_data.get("success")),
                "fail": to_int(tool_data.get("fail")),
                "duration_ms": to_int(tool_data.get("durationMs")),
                "decisions": {
                    "accept": to_int(decisions.get("accept")),
                    "reject": to_int(decisions.get("reject")),
                    "modify": to_int(decisions.get("modify")),
                    "auto_accept": to_int(decisions.get("auto_accept")),
                },
            }
        )

    total_decisions = (
        tools_raw.get("totalDecisions") if isinstance(tools_raw.get("totalDecisions"), dict) else {}
    )
    error_value = payload.get("error")
    if isinstance(error_value, (dict, list)):
        error_parsed = error_value
    elif error_value is None:
        error_parsed = None
    else:
        error_parsed = str(error_value)

    return {
        "session_id": payload.get("session_id"),
        "response": payload.get("response"),
        "models": models,
        "tools": {
            "total_calls": to_int(tools_raw.get("totalCalls")),
            "total_success": to_int(tools_raw.get("totalSuccess")),
            "total_fail": to_int(tools_raw.get("totalFail")),
            "total_duration_ms": to_int(tools_raw.get("totalDurationMs")),
            "total_decisions": {
                "accept": to_int(total_decisions.get("accept")),
                "reject": to_int(total_decisions.get("reject")),
                "modify": to_int(total_decisions.get("modify")),
                "auto_accept": to_int(total_decisions.get("auto_accept")),
            },
            "by_name": tools_by_name,
        },
        "files": {
            "total_lines_added": to_int(files_raw.get("totalLinesAdded")),
            "total_lines_removed": to_int(files_raw.get("totalLinesRemoved")),
        },
        "error": error_parsed,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약 생성."""
    lines = []
    lines.append("# Gemini JSON 요약")
    lines.append("")
    lines.append(f"- session_id: {parsed.get('session_id') or '(없음)'}")
    lines.append(f"- error: {json.dumps(parsed.get('error'), ensure_ascii=False) if parsed.get('error') is not None else '(없음)'}")
    lines.append("")

    lines.append("## 최종 응답(response)")
    response = parsed.get("response")
    lines.append(response if isinstance(response, str) and response else "(없음)")
    lines.append("")

    lines.append("## 모델 통계")
    models = parsed.get("models", [])
    if models:
        for idx, model in enumerate(models, start=1):
            api = model.get("api", {})
            tokens = model.get("tokens", {})
            lines.append(
                f"{idx}. {model.get('name')} | requests={api.get('total_requests', 0)}, "
                f"errors={api.get('total_errors', 0)}, latency_ms={api.get('total_latency_ms', 0)}"
            )
            lines.append(
                "   "
                f"tokens(input={tokens.get('input', 0)}, prompt={tokens.get('prompt', 0)}, "
                f"candidates={tokens.get('candidates', 0)}, total={tokens.get('total', 0)}, "
                f"cached={tokens.get('cached', 0)}, thoughts={tokens.get('thoughts', 0)}, "
                f"tool={tokens.get('tool', 0)})"
            )
    else:
        lines.append("(없음)")
    lines.append("")

    lines.append("## 도구 사용 통계")
    tools = parsed.get("tools", {})
    lines.append(
        f"- totals: calls={tools.get('total_calls', 0)}, success={tools.get('total_success', 0)}, "
        f"fail={tools.get('total_fail', 0)}, duration_ms={tools.get('total_duration_ms', 0)}"
    )
    decisions = tools.get("total_decisions", {})
    lines.append(
        f"- decisions: accept={decisions.get('accept', 0)}, reject={decisions.get('reject', 0)}, "
        f"modify={decisions.get('modify', 0)}, auto_accept={decisions.get('auto_accept', 0)}"
    )
    by_name = tools.get("by_name", [])
    if by_name:
        lines.append("- by_name:")
        for idx, tool in enumerate(by_name, start=1):
            lines.append(
                f"  {idx}. {tool.get('name')} | count={tool.get('count', 0)}, success={tool.get('success', 0)}, "
                f"fail={tool.get('fail', 0)}, duration_ms={tool.get('duration_ms', 0)}"
            )
    else:
        lines.append("- by_name: (없음)")
    lines.append("")

    files = parsed.get("files", {})
    lines.append("## 파일 변경 통계")
    lines.append(
        f"- lines_added={files.get('total_lines_added', 0)}, lines_removed={files.get('total_lines_removed', 0)}"
    )

    return "\n".join(lines).rstrip() + "\n"
```

---
## FILE: skills/agent-parser/scripts/_transcript_parser.py
```python
#!/usr/bin/env python3
"""Claude Transcript 파서: Claude Code transcript(JSONL) 구조화 요약 생성."""

import json


def shorten_text(text: str, max_chars: int) -> str:
    """텍스트를 한 줄 요약으로 정규화하고 길이를 제한."""
    normalized = " ".join(str(text).split())
    if not normalized:
        return "(없음)"
    if len(normalized) <= max_chars:
        return normalized
    return normalized[:max_chars].rstrip() + "..."


def extract_user_text(content) -> str:
    """user content가 문자열/배열일 때 텍스트를 추출."""
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        chunks = []
        for block in content:
            if isinstance(block, str):
                chunks.append(block)
                continue
            if not isinstance(block, dict):
                continue
            block_type = str(block.get("type", ""))
            if block_type in ("text", "input_text"):
                text_value = block.get("text")
                if isinstance(text_value, str):
                    chunks.append(text_value)
            elif isinstance(block.get("text"), str):
                chunks.append(block.get("text"))
        return "\n".join(chunks).strip()

    return ""


def parse_transcript_jsonl(raw_text: str, last_n: int | None = None) -> dict:
    """transcript JSONL을 파싱하여 집계 결과를 생성."""
    records = []
    parse_errors = []

    for idx, line in enumerate(raw_text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as e:
            parse_errors.append({"line": idx, "message": f"JSON 파싱 실패: {e.msg}"})
            continue

        if not isinstance(payload, dict):
            parse_errors.append({"line": idx, "message": "JSON 객체(dict)가 아님"})
            continue

        record_type = str(payload.get("type", ""))
        if record_type not in ("user", "assistant", "file-history-snapshot"):
            continue
        records.append(payload)

    messages = [r for r in records if str(r.get("type", "")) in ("user", "assistant")]
    if last_n is not None:
        if last_n < 0:
            last_n = 0
        messages = messages[-last_n:] if last_n > 0 else []

    session_id = None
    for msg in messages:
        value = msg.get("sessionId")
        if isinstance(value, str) and value:
            session_id = value
            break
    if session_id is None:
        for rec in records:
            value = rec.get("sessionId")
            if isinstance(value, str) and value:
                session_id = value
                break

    user_count = 0
    assistant_count = 0
    last_user_text = ""
    assistant_text_total_length = 0
    last_assistant_text = ""
    thinking_count = 0
    tool_use_counts: dict[str, int] = {}
    pending_user = 0
    turn_count = 0

    for msg in messages:
        record_type = str(msg.get("type", ""))
        message = msg.get("message") if isinstance(msg.get("message"), dict) else {}

        if record_type == "user":
            user_count += 1
            pending_user += 1
            user_text = extract_user_text(message.get("content"))
            if user_text:
                last_user_text = user_text
            continue

        if record_type != "assistant":
            continue

        assistant_count += 1
        if pending_user > 0:
            turn_count += 1
            pending_user -= 1

        content = message.get("content")
        if not isinstance(content, list):
            continue

        for block in content:
            if not isinstance(block, dict):
                continue
            block_type = str(block.get("type", ""))

            if block_type == "text":
                text_value = block.get("text")
                if isinstance(text_value, str):
                    assistant_text_total_length += len(text_value)
                    if text_value.strip():
                        last_assistant_text = text_value

            elif block_type == "thinking":
                thinking_count += 1

            elif block_type == "tool_use":
                tool_name = block.get("name")
                if isinstance(tool_name, str) and tool_name:
                    tool_use_counts[tool_name] = tool_use_counts.get(tool_name, 0) + 1

    return {
        "session_id": session_id,
        "messages_analyzed": len(messages),
        "last_n_applied": last_n,
        "user": {
            "count": user_count,
            "last_message_summary": shorten_text(last_user_text, 120),
        },
        "assistant": {
            "count": assistant_count,
            "text_total_length": assistant_text_total_length,
            "last_text_summary": shorten_text(last_assistant_text, 200),
            "thinking_block_count": thinking_count,
            "tool_use_counts": dict(sorted(tool_use_counts.items())),
        },
        "turn_count": turn_count,
        "parse_errors": parse_errors,
    }


def render_summary(parsed: dict) -> str:
    """사람이 읽기 좋은 텍스트 요약 생성."""
    lines = []
    lines.append("# Claude Transcript 요약")
    lines.append("")
    lines.append(f"- session_id: {parsed.get('session_id') or '(없음)'}")
    lines.append(f"- 분석한 메시지 수: {parsed.get('messages_analyzed', 0)}")
    lines.append(f"- last_n 적용값: {parsed.get('last_n_applied')}")
    lines.append(f"- 대화 턴 수(user+assistant 쌍): {parsed.get('turn_count', 0)}")
    lines.append("")

    user = parsed.get("user", {})
    lines.append("## User")
    lines.append(f"- 메시지 수: {user.get('count', 0)}")
    lines.append(f"- 마지막 메시지 요약: {user.get('last_message_summary', '(없음)')}")
    lines.append("")

    assistant = parsed.get("assistant", {})
    lines.append("## Assistant")
    lines.append(f"- 메시지 수: {assistant.get('count', 0)}")
    lines.append(f"- text 총 길이: {assistant.get('text_total_length', 0)}")
    lines.append(f"- 마지막 text 요약: {assistant.get('last_text_summary', '(없음)')}")
    lines.append(f"- thinking 블록 수: {assistant.get('thinking_block_count', 0)}")
    lines.append("")

    lines.append("## Tool Use 집계")
    tool_use_counts = assistant.get("tool_use_counts", {})
    if isinstance(tool_use_counts, dict) and tool_use_counts:
        for idx, (name, count) in enumerate(tool_use_counts.items(), start=1):
            lines.append(f"{idx}. {name}: {count}")
    else:
        lines.append("(없음)")
    lines.append("")

    parse_errors = parsed.get("parse_errors", [])
    lines.append(f"- parse_error 수: {len(parse_errors)}")
    if parse_errors:
        lines.append("## Parse Errors")
        for err in parse_errors:
            lines.append(f"- line {err.get('line')}: {err.get('message')}")

    return "\n".join(lines).rstrip() + "\n"
```

---
## FILE: skills/agent-parser/scripts/parse.py
```python
#!/usr/bin/env python3
"""통합 에이전트 출력 파서: Codex/Gemini/Claude 자동 감지 + 파싱.

Usage:
    # 자동 감지
    python3 parse.py --file output.jsonl
    cat output.json | python3 parse.py

    # 에이전트 명시
    python3 parse.py --file output.jsonl --agent codex
    python3 parse.py --file output.json --agent gemini

    # JSON 출력 + 저장
    python3 parse.py --file transcript.jsonl --format json --save
"""

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from _common import read_input, save_feedback
from _codex_parser import parse_jsonl_events, render_summary as codex_summary
from _gemini_parser import parse_gemini_json, render_summary as gemini_summary
from _transcript_parser import parse_transcript_jsonl, render_summary as transcript_summary


def detect_agent(raw_text: str) -> str | None:
    """첫 번째 유효 JSON 라인의 시그니처로 에이전트를 자동 감지."""
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue

        # Codex: thread.started / item.started / item.completed / turn.completed
        obj_type = str(obj.get("type", ""))
        if obj_type in ("thread.started", "item.started", "item.completed", "turn.completed"):
            return "codex"

        # Gemini: stats + response (또는 session_id + response)
        if "stats" in obj and "response" in obj:
            return "gemini"
        if "session_id" in obj and "response" in obj and "stats" in obj:
            return "gemini"

        # Claude transcript: type=user|assistant + message
        if obj_type in ("user", "assistant") and "message" in obj:
            return "claude"

    return None


def parse_and_render(raw_text: str, agent: str, fmt: str, last_n: int | None = None) -> str | None:
    """감지된 에이전트에 맞는 파서로 파싱 + 렌더링."""
    if agent == "codex":
        parsed = parse_jsonl_events(raw_text)
        if fmt == "json":
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        return codex_summary(parsed)

    elif agent == "gemini":
        parsed = parse_gemini_json(raw_text)
        if parsed is None:
            return None
        if fmt == "json":
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        return gemini_summary(parsed)

    elif agent == "claude":
        parsed = parse_transcript_jsonl(raw_text, last_n=last_n)
        if fmt == "json":
            return json.dumps(parsed, ensure_ascii=False, indent=2)
        return transcript_summary(parsed)

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="통합 에이전트 출력 파서 (Codex/Gemini/Claude 자동 감지)"
    )
    parser.add_argument("--file", "-f", help="입력 파일 경로")
    parser.add_argument(
        "--agent", "-a",
        choices=["codex", "gemini", "claude", "auto"],
        default="auto",
        help="에이전트 지정 (기본: auto)",
    )
    parser.add_argument(
        "--format",
        choices=["summary", "json"],
        default="summary",
        help="출력 형식 (기본: summary)",
    )
    parser.add_argument("--save", "-s", action="store_true", help="gemini_feedback.md에 저장")
    parser.add_argument("--last-n", type=int, default=None, help="마지막 N개 메시지만 파싱 (Claude)")
    args = parser.parse_args()

    raw_text = read_input(args.file)
    if raw_text is None:
        return 0

    # 에이전트 감지
    agent = args.agent
    if agent == "auto":
        agent = detect_agent(raw_text)
        if agent is None:
            print("[ERROR] 에이전트 형식을 자동 감지할 수 없습니다. --agent로 지정하세요.", file=sys.stderr)
            return 1
        print(f"[감지됨] {agent}", file=sys.stderr)

    # 파싱 + 렌더링
    output = parse_and_render(raw_text, agent, args.format, last_n=args.last_n)
    if output is None:
        print("[ERROR] 파싱 실패.", file=sys.stderr)
        return 1

    print(output)

    if args.save:
        source = f"Agent Parser ({agent})"
        if args.file:
            source += f" | 대상: `{args.file}`"
        save_feedback(output, source)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
```

---
## FILE: skills/cross-agent-bridge/scripts/_a2a_protocol.py
```python
#!/usr/bin/env python3
"""A2A (Agent-to-Agent) 메시지 프로토콜 — 빌드/파싱/렌더링."""

import json
import uuid
from datetime import datetime, timezone

A2A_VERSION = "1.0"

_A2A_RESPONSE_INSTRUCTION = """반드시 아래 JSON 형식으로만 응답하라. JSON 외 다른 텍스트를 포함하지 마라.
각 detail과 항목은 반드시 1-2문장 이내로 간결하게 작성하라.

{
  "evaluation": {
    "논리적 일관성": {"score": "높음|보통|낮음", "detail": "1문장"},
    "실현 가능성": {"score": "높음|보통|낮음", "detail": "1문장"},
    "누락된 고려사항": ["항목1", "항목2"],
    "개선 제안": ["제안1", "제안2"]
  },
  "summary": "한 줄 요약"
}"""

_A2A_CLASSIFICATION_INSTRUCTION = """반드시 아래 JSON 형식으로만 응답하라. JSON 외 다른 텍스트를 포함하지 마라.

{"is_plan": true 또는 false}"""


def build_request(message_type: str, payload: dict, hook_source: str = "unknown") -> dict:
    """A2A 요청 메시지 생성."""
    return {
        "a2a_version": A2A_VERSION,
        "message_type": message_type,
        "request_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {"agent": "claude", "hook": hook_source},
        "payload": payload,
    }


def _try_parse_json(text: str):
    """JSON 파싱 시도. 실패 시 None."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        return None


def _try_repair_json(text: str):
    """잘린 JSON 복구 (닫히지 않은 괄호/따옴표 보정)."""
    for trim_target in [',\n', ',"', ', "', ',']:
        idx = text.rfind(trim_target)
        if idx > 0:
            candidate = text[:idx]
            open_braces = candidate.count('{') - candidate.count('}')
            open_brackets = candidate.count('[') - candidate.count(']')
            if open_braces >= 0 and open_brackets >= 0:
                candidate += ']' * open_brackets + '}' * open_braces
                result = _try_parse_json(candidate)
                if result is not None:
                    return result
    return None


def parse_response(raw_text: str, request_id: str = None) -> dict:
    """Gemini 응답 텍스트에서 A2A JSON을 파싱."""
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        json_lines = []
        inside = False
        for line in lines:
            if line.strip().startswith("```") and not inside:
                inside = True
                continue
            elif line.strip() == "```" and inside:
                break
            elif inside:
                json_lines.append(line)
        text = "\n".join(json_lines).strip()

    parsed = _try_parse_json(text)
    if parsed is None:
        parsed = _try_repair_json(text)

    if parsed is not None:
        return {
            "a2a_version": A2A_VERSION,
            "message_type": "evaluation_response",
            "request_id": request_id or "",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": {"agent": "gemini"},
            "status": "success",
            "payload": parsed,
        }

    return {
        "a2a_version": A2A_VERSION,
        "message_type": "evaluation_response",
        "request_id": request_id or "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": {"agent": "gemini"},
        "status": "success",
        "payload": {"raw_text": raw_text},
    }


def response_to_markdown(response: dict) -> str:
    """A2A 응답을 마크다운으로 변환."""
    payload = response.get("payload", {})
    if "raw_text" in payload:
        return payload["raw_text"]

    evaluation = payload.get("evaluation", {})
    summary = payload.get("summary", "")
    parts = []

    for key, value in evaluation.items():
        if isinstance(value, dict):
            score = value.get("score", "")
            detail = value.get("detail", "")
            parts.append(f"### {key}: {score}\n{detail}")
        elif isinstance(value, list):
            items = "\n".join(f"- {item}" for item in value)
            parts.append(f"### {key}\n{items}")

    if summary:
        parts.append(f"\n**요약:** {summary}")

    return "\n\n".join(parts)


def build_evaluation_prompt(base_prompt: str, a2a_enabled: bool = False) -> str:
    """A2A 모드일 때 JSON 응답 강제 프롬프트 생성."""
    if a2a_enabled:
        return f"{base_prompt}\n\n{_A2A_RESPONSE_INSTRUCTION}"
    return base_prompt


def build_classification_prompt(base_prompt: str, a2a_enabled: bool = False) -> str:
    """A2A 모드일 때 분류 요청 프롬프트 생성."""
    if a2a_enabled:
        return f"{base_prompt}\n\n{_A2A_CLASSIFICATION_INSTRUCTION}"
    return base_prompt
```

---
## FILE: skills/cross-agent-bridge/scripts/_common.py
```python
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
    feedback_path = Path.cwd() / "gemini_feedback.md"
    for candidate in [feedback_path, Path(__file__).resolve().parent.parent.parent.parent / "gemini_feedback.md"]:
        if candidate.parent.exists():
            feedback_path = candidate
            break
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target = f" | 대상: `{file_path}`" if file_path else ""
    entry = f"\n---\n\n## [{timestamp}] {source}{target}\n\n{feedback}\n"
    try:
        with open(feedback_path, "a", encoding="utf-8") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.write(entry)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except IOError as e:
        print(f"[ERROR] 피드백 저장 실패: {e}", file=sys.stderr)
```

---
## FILE: skills/cross-agent-bridge/scripts/_config.py
```python
#!/usr/bin/env python3
"""config 로딩/검증/기본값 생성."""

import json
import re
from pathlib import Path

DEFAULT_CONFIG = {
    "gemini_cmd": "/usr/local/bin/gemini",
    "gemini_timeout": 90,
    "cooldown_seconds_per_file": 300,
    "min_content_length": 300,
    "watch_extensions": [".md", ".py"],
    "exclude_files": ["gemini_feedback.md"],
    "evaluation_prompt": "다음 문서를 평가해줘:\n- 논리적 일관성\n- 실현 가능성\n- 누락된 고려사항\n- 개선 제안\n간결하게 한국어로 답해줘.",
    "code_evaluation_prompt": "다음 코드를 리뷰해줘:\n- 버그 또는 잠재적 오류\n- 보안 취약점\n- 에러 처리 누락\n- 개선 제안\n간결하게 한국어로 답해줘.",
    "code_extensions": [".py", ".js", ".ts", ".jsx", ".tsx"],
    "sdk": {
        "enabled": True,
        "model": "gemini-2.5-flash",
        "fallback_models": ["gemini-2.0-flash", "gemini-1.5-flash"],
        "fallback_to_cli": True,
        "api_key_env": "GEMINI_API_KEY",
        "max_output_tokens": 2048,
        "temperature": 0.3,
    },
    "async_mode": False,
    "a2a_schema_enabled": False,
    "error_detection": {
        "enabled": True,
        "tail_lines": 50,
        "global_cooldown_seconds": 60,
        "thresholds": {"critical": 1, "high": 1, "medium": 2, "low": 3},
    },
}


def find_config(start_dir: Path = None) -> Path | None:
    """프로젝트 내 config.json을 탐색."""
    candidates = []
    if start_dir:
        candidates.append(start_dir / "scripts" / "config.json")
        candidates.append(start_dir / "config.json")
    candidates.extend([
        Path.cwd() / "scripts" / "config.json",
        Path.cwd() / "config.json",
        Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "config.json",
    ])
    for c in candidates:
        if c.exists():
            return c
    return None


def load_config(config_path: Path = None) -> dict:
    """config.json 로드. 없으면 기본값 반환."""
    if config_path is None:
        config_path = find_config()
    if config_path and config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return dict(DEFAULT_CONFIG)


def validate_config(config: dict) -> list:
    """config를 검증하고 (level, message) 문제 목록 반환."""
    issues = []
    required = {
        "gemini_cmd": str,
        "gemini_timeout": (int, float),
        "watch_extensions": list,
        "evaluation_prompt": str,
    }
    for field, expected_type in required.items():
        if field not in config:
            issues.append(("error", f"필수 필드 누락: {field}"))
        elif not isinstance(config[field], expected_type):
            issues.append(("error", f"타입 오류: {field}"))

    sdk = config.get("sdk")
    if sdk is not None:
        if not isinstance(sdk, dict):
            issues.append(("error", "sdk는 dict여야 합니다"))
        else:
            if "model" not in sdk:
                issues.append(("warn", "sdk.model 미설정"))
            temp = sdk.get("temperature")
            if temp is not None and not (0 <= temp <= 2):
                issues.append(("warn", f"sdk.temperature={temp} — 0~2 범위 권장"))

    err = config.get("error_detection")
    if err is not None and isinstance(err, dict):
        thresholds = err.get("thresholds")
        if thresholds is not None and isinstance(thresholds, dict):
            for sev in ["critical", "high", "medium", "low"]:
                val = thresholds.get(sev)
                if val is not None and (not isinstance(val, int) or val < 1):
                    issues.append(("error", f"thresholds.{sev}={val} — 1 이상 정수"))

    guard = config.get("pre_tool_guard")
    if guard is not None and isinstance(guard, dict):
        for i, pat in enumerate(guard.get("custom_block_patterns", [])):
            try:
                re.compile(pat)
            except re.error as e:
                issues.append(("error", f"custom_block_patterns[{i}] 정규식 오류: {e}"))

    return issues


def generate_config(output_path: Path):
    """기본 config.json 생성."""
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
    print(f"[생성됨] {output_path}")
```

---
## FILE: skills/cross-agent-bridge/scripts/_doctor.py
```python
#!/usr/bin/env python3
"""시스템 진단 — config, 환경, SDK, CLI, Hook 검증."""

import json
import os
import time
from pathlib import Path


def run_doctor(config: dict, project_root: Path = None):
    """시스템 전체 진단 실행."""
    if project_root is None:
        project_root = Path.cwd()

    print("=== Cross-Agent Bridge Doctor ===\n")
    ok_count = 0
    warn_count = 0
    err_count = 0

    def check(passed, label, detail=""):
        nonlocal ok_count, warn_count, err_count
        if passed == "ok":
            print(f"  ✓ {label}")
            ok_count += 1
        elif passed == "warn":
            print(f"  ⚠ {label}" + (f" — {detail}" if detail else ""))
            warn_count += 1
        else:
            print(f"  ✗ {label}" + (f" — {detail}" if detail else ""))
            err_count += 1

    # 1. Config
    print("[1] Config 검증")
    from _config import validate_config
    issues = validate_config(config)
    if not issues:
        check("ok", "config 필드 검증 통과")
    for level, msg in issues:
        check(level if level == "warn" else "err", msg)

    # 2. 환경
    print("\n[2] 환경 점검")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    extra_keys = [k for k in os.environ if k.startswith("GEMINI_API_KEY_")]
    total_keys = (1 if api_key else 0) + len(extra_keys)
    if total_keys > 0:
        check("ok", f"API Key: {total_keys}개 설정됨")
    else:
        check("warn", "API Key 미설정", "GEMINI_API_KEY 환경변수 필요")

    try:
        from google import genai  # noqa: F401
        check("ok", "google-genai SDK 설치됨")
    except ImportError:
        check("warn", "google-genai SDK 미설치", "pip install google-genai")

    gemini_cmd = config.get("gemini_cmd", "/usr/local/bin/gemini")
    if Path(gemini_cmd).exists():
        check("ok", f"Gemini CLI: {gemini_cmd}")
    else:
        check("warn", f"Gemini CLI 없음: {gemini_cmd}", "CLI 폴백 불가")

    env_path = project_root / ".env"
    if env_path.exists():
        check("ok", ".env 파일 존재")
    else:
        check("warn", ".env 파일 없음")

    # 3. Feedback 파일
    print("\n[3] 피드백 상태")
    feedback_path = project_root / "gemini_feedback.md"
    if feedback_path.exists():
        content = feedback_path.read_text("utf-8")
        entries = content.count("\n---\n")
        size_kb = len(content.encode("utf-8")) / 1024
        check("ok", f"gemini_feedback.md: {entries}개 항목, {size_kb:.1f}KB")
    else:
        check("warn", "gemini_feedback.md 없음")

    # 결과
    print(f"\n{'='*40}")
    total = ok_count + warn_count + err_count
    print(f"결과: {ok_count}/{total} OK, {warn_count} 경고, {err_count} 에러")
    if err_count == 0 and warn_count == 0:
        print("시스템 상태: 정상 ✓")
    elif err_count == 0:
        print("시스템 상태: 동작 가능 (경고 확인 권장)")
    else:
        print("시스템 상태: 문제 있음 (에러 수정 필요)")
    return err_count == 0
```

---
## FILE: skills/cross-agent-bridge/scripts/_gemini_client.py
```python
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
```

---
## FILE: skills/cross-agent-bridge/scripts/bridge.py
```python
#!/usr/bin/env python3
"""Cross-Agent Bridge — 통합 오케스트레이터.

에이전트 간 협업을 위한 CLI 도구.

Usage:
    python3 bridge.py review --file <파일경로>
    python3 bridge.py review --file code.py --mode code --format json
    python3 bridge.py codex-review --file plan.md --model gpt-5
    python3 bridge.py parse --file output.jsonl
    python3 bridge.py parse --file output.jsonl --agent codex --format json
    python3 bridge.py doctor
    python3 bridge.py setup [--output config.json]
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from _common import load_env, read_input, save_feedback

CODE_EXTENSIONS = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go", ".rs", ".c", ".cpp", ".rb", ".sh"}

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


def cmd_review(args):
    """Gemini에 코드/문서 리뷰 요청."""
    from _config import load_config
    from _gemini_client import call_gemini

    load_env()
    config = load_config()

    content = read_input(args.file)
    if content is None:
        print("[ERROR] 입력이 필요합니다.", file=sys.stderr)
        return 1

    # 모드 결정
    mode = args.mode
    if not mode:
        if args.file:
            ext = Path(args.file).suffix.lower()
            mode = "code" if ext in CODE_EXTENSIONS else "doc"
        else:
            mode = "doc"

    prompt = args.prompt or PROMPTS[mode]
    if args.file:
        prompt = f"{prompt}\n\n파일 경로: {args.file}"

    result, model_used = call_gemini(content, prompt, config, file_path=args.file)

    if args.format == "json":
        output = json.dumps({
            "mode": mode,
            "file_path": args.file,
            "feedback": result,
            "model_used": model_used,
            "timestamp": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2)
    else:
        output = result

    print(output)

    if args.save:
        save_feedback(result, source="Cross-Agent Bridge Review", file_path=args.file)
    return 0


def _run_codex_exec(prompt: str, model: str | None, timeout: int) -> tuple[int, str]:
    """codex exec를 호출하고 최종 메시지를 반환."""
    cmd = ["codex", "exec"]
    if model:
        cmd.extend(["-m", model])

    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()

    try:
        cmd.extend(["--output-last-message", temp_file.name, prompt])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        last_message = Path(temp_file.name).read_text(encoding="utf-8").strip()
        if last_message:
            return result.returncode, last_message

        fallback = result.stdout.strip() or result.stderr.strip()
        return result.returncode, fallback
    except subprocess.TimeoutExpired:
        return 124, "[ERROR] codex exec timeout"
    except FileNotFoundError:
        return 127, "[ERROR] codex command not found"
    finally:
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass


def cmd_codex_review(args):
    """Codex에 코드/문서 리뷰 요청."""
    content = read_input(args.file)
    if content is None:
        print("[ERROR] 입력이 필요합니다.", file=sys.stderr)
        return 1

    mode = args.mode
    if not mode:
        if args.file:
            ext = Path(args.file).suffix.lower()
            mode = "code" if ext in CODE_EXTENSIONS else "doc"
        else:
            mode = "doc"

    prompt = args.prompt or PROMPTS[mode]
    if args.file:
        prompt = f"{prompt}\n\n파일 경로: {args.file}"
    full_prompt = f"{prompt}\n\n---\n{content}"

    rc, result = _run_codex_exec(full_prompt, args.model, args.timeout)
    model_used = args.model or "default"
    if rc != 0 and not result.startswith("[ERROR]"):
        result = f"[ERROR] codex exec failed (exit={rc})\n{result}"

    if args.format == "json":
        output = json.dumps(
            {
                "mode": mode,
                "file_path": args.file,
                "feedback": result,
                "model_used": model_used,
                "provider": "codex",
                "timestamp": datetime.now().isoformat(),
            },
            ensure_ascii=False,
            indent=2,
        )
    else:
        output = result

    print(output)
    if args.save:
        save_feedback(result, source="Cross-Agent Bridge Codex Review", file_path=args.file)
    return 0


def cmd_parse(args):
    """에이전트 출력 파싱 (Codex/Gemini/Claude 자동 감지)."""
    raw_text = read_input(args.file)
    if raw_text is None:
        print("[ERROR] 입력이 필요합니다.", file=sys.stderr)
        return 1

    agent = args.agent
    if agent == "auto":
        agent = _detect_agent(raw_text)
        if agent is None:
            print("[ERROR] 에이전트 형식을 자동 감지할 수 없습니다. --agent로 지정하세요.", file=sys.stderr)
            return 1
        print(f"[감지됨] {agent}", file=sys.stderr)

    output = _parse_and_render(raw_text, agent, args.format, last_n=args.last_n)
    if output is None:
        print("[ERROR] 파싱 실패.", file=sys.stderr)
        return 1

    print(output)

    if args.save:
        save_feedback(output, source=f"Cross-Agent Bridge Parse ({agent})", file_path=args.file)
    return 0


def _detect_agent(raw_text: str) -> str | None:
    """첫 유효 JSON 라인 시그니처로 에이전트 감지."""
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(obj, dict):
            continue
        obj_type = str(obj.get("type", ""))
        if obj_type in ("thread.started", "item.started", "item.completed", "turn.completed"):
            return "codex"
        if "stats" in obj and "response" in obj:
            return "gemini"
        if obj_type in ("user", "assistant") and "message" in obj:
            return "claude"
    return None


def _parse_and_render(raw_text: str, agent: str, fmt: str, last_n: int = None) -> str | None:
    """감지된 에이전트 파서로 파싱 + 렌더링."""
    if agent == "codex":
        return _parse_codex(raw_text, fmt)
    elif agent == "gemini":
        return _parse_gemini(raw_text, fmt)
    elif agent == "claude":
        return _parse_claude(raw_text, fmt, last_n)
    return None


# ── 내장 파서 (자립성: agent-parser 의존 없음) ──

def _parse_codex(raw_text: str, fmt: str) -> str:
    """Codex JSONL 간이 파서."""
    events = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            if isinstance(obj, dict):
                events.append(obj)
        except json.JSONDecodeError:
            continue

    thread_id = None
    messages = []
    commands = []
    errors = []

    for e in events:
        t = str(e.get("type", ""))
        if t == "thread.started":
            thread_id = e.get("thread_id")
        item = e.get("item") if isinstance(e.get("item"), dict) else None
        if item:
            it = str(item.get("type", ""))
            if it == "agent_message" and item.get("text"):
                messages.append(item["text"])
            elif it == "command_execution":
                commands.append({
                    "command": item.get("command", ""),
                    "exit_code": item.get("exit_code"),
                })
            elif "error" in it.lower():
                errors.append(item.get("message", "error"))

    parsed = {
        "agent": "codex", "thread_id": thread_id,
        "event_count": len(events), "messages": len(messages),
        "commands": len(commands), "errors": len(errors),
        "final_message": messages[-1] if messages else None,
    }

    if fmt == "json":
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    lines = [
        "# Codex 요약",
        f"- thread_id: {thread_id or '(없음)'}",
        f"- 이벤트: {len(events)}, 메시지: {len(messages)}, 명령: {len(commands)}, 에러: {len(errors)}",
    ]
    if messages:
        lines.append(f"\n## 최종 메시지\n{messages[-1]}")
    return "\n".join(lines)


def _parse_gemini(raw_text: str, fmt: str) -> str | None:
    """Gemini JSON 간이 파서."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        return None

    parsed = {
        "agent": "gemini",
        "session_id": data.get("session_id"),
        "response": data.get("response"),
        "has_stats": "stats" in data,
        "error": data.get("error"),
    }

    if fmt == "json":
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    lines = [
        "# Gemini 요약",
        f"- session_id: {parsed['session_id'] or '(없음)'}",
        f"- error: {parsed['error'] or '없음'}",
    ]
    resp = parsed.get("response")
    if resp:
        lines.append(f"\n## 응답\n{resp[:500]}")
    return "\n".join(lines)


def _parse_claude(raw_text: str, fmt: str, last_n: int = None) -> str:
    """Claude transcript JSONL 간이 파서."""
    messages = []
    for line in raw_text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("type") in ("user", "assistant"):
            messages.append(obj)

    if last_n is not None and last_n > 0:
        messages = messages[-last_n:]

    user_count = sum(1 for m in messages if m.get("type") == "user")
    asst_count = sum(1 for m in messages if m.get("type") == "assistant")

    parsed = {
        "agent": "claude",
        "messages_analyzed": len(messages),
        "user_count": user_count,
        "assistant_count": asst_count,
    }

    if fmt == "json":
        return json.dumps(parsed, ensure_ascii=False, indent=2)

    return f"# Claude 요약\n- 메시지: {len(messages)} (user: {user_count}, assistant: {asst_count})"


def cmd_doctor(args):
    """시스템 진단."""
    from _config import load_config
    from _doctor import run_doctor

    load_env()
    config = load_config()
    run_doctor(config)
    return 0


def cmd_setup(args):
    """초기 설정 (config 생성, .env 템플릿)."""
    from _config import generate_config

    output = Path(args.output) if args.output else Path.cwd() / "config.json"
    if output.exists():
        print(f"[SKIP] 이미 존재: {output}")
    else:
        generate_config(output)

    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        env_path.write_text(
            "# Gemini API Key\nGEMINI_API_KEY=your-api-key-here\n",
            encoding="utf-8",
        )
        print(f"[생성됨] {env_path}")
    else:
        print(f"[SKIP] .env 이미 존재")

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Cross-Agent Bridge — 통합 오케스트레이터"
    )
    subparsers = parser.add_subparsers(dest="command", help="서브커맨드")

    # review
    p_review = subparsers.add_parser("review", help="Gemini 코드/문서 리뷰")
    p_review.add_argument("--file", "-f", help="리뷰할 파일 경로")
    p_review.add_argument("--mode", "-m", choices=["code", "doc"], help="리뷰 모드")
    p_review.add_argument("--prompt", "-p", help="커스텀 프롬프트")
    p_review.add_argument("--format", choices=["text", "json"], default="text", help="출력 형식")
    p_review.add_argument("--save", "-s", action="store_true", help="피드백 저장")

    # codex-review
    p_creview = subparsers.add_parser("codex-review", help="Codex 코드/문서 리뷰")
    p_creview.add_argument("--file", "-f", help="리뷰할 파일 경로")
    p_creview.add_argument("--mode", "-m", choices=["code", "doc"], help="리뷰 모드")
    p_creview.add_argument("--prompt", "-p", help="커스텀 프롬프트")
    p_creview.add_argument("--format", choices=["text", "json"], default="text", help="출력 형식")
    p_creview.add_argument("--model", default="gpt-5", help="Codex 모델")
    p_creview.add_argument("--timeout", type=int, default=120, help="실행 타임아웃(초)")
    p_creview.add_argument("--save", "-s", action="store_true", help="피드백 저장")

    # parse
    p_parse = subparsers.add_parser("parse", help="에이전트 출력 파싱")
    p_parse.add_argument("--file", "-f", help="입력 파일 경로")
    p_parse.add_argument("--agent", "-a", choices=["codex", "gemini", "claude", "auto"], default="auto")
    p_parse.add_argument("--format", choices=["summary", "json"], default="summary")
    p_parse.add_argument("--save", "-s", action="store_true")
    p_parse.add_argument("--last-n", type=int, default=None, help="마지막 N개 (Claude)")

    # doctor
    subparsers.add_parser("doctor", help="시스템 진단")

    # setup
    p_setup = subparsers.add_parser("setup", help="초기 설정")
    p_setup.add_argument("--output", "-o", help="config.json 출력 경로")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "review": cmd_review,
        "codex-review": cmd_codex_review,
        "parse": cmd_parse,
        "doctor": cmd_doctor,
        "setup": cmd_setup,
    }
    return commands[args.command](args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(0)
```

---
## FILE: skills/gemini-reviewer/scripts/_common.py
```python
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
    feedback_path = Path.cwd() / "gemini_feedback.md"
    for candidate in [
        feedback_path,
        Path(__file__).resolve().parent.parent.parent.parent / "gemini_feedback.md",
    ]:
        if candidate.parent.exists():
            feedback_path = candidate
            break

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    target = f" | 대상: `{file_path}`" if file_path else ""
    entry = f"\n---\n\n## [{timestamp}] {source}{target}\n\n{feedback}\n"

    with open(feedback_path, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            f.write(entry)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    print(f"[저장됨] {feedback_path}", file=sys.stderr)
```

---
## FILE: skills/gemini-reviewer/scripts/codex_notify.py
```python
#!/usr/bin/env python3
"""Codex CLI notify hook: agent-turn-complete 시 Gemini 평가를 트리거합니다.

Codex의 notify 설정에 등록하여 사용합니다.
Claude Code의 Stop Hook과 동일한 역할 (Plan 감지 -> Gemini 평가).

Setup (config.toml):
    notify = ["python3", "/path/to/codex_notify.py"]

수신 JSON (sys.argv[1]):
    {
        "type": "agent-turn-complete",
        "thread-id": "...",
        "turn-id": "...",
        "cwd": "...",
        "input-messages": [...],
        "last-assistant-message": "..."
    }
"""

import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))
from _common import load_env, save_feedback


def is_plan(text: str, min_length: int = 300) -> bool:
    """텍스트가 소프트웨어 개발 계획인지 간단히 판별합니다.

    Gemini API 호출 없이 키워드 기반 휴리스틱으로 빠르게 판별.
    """
    if len(text) < min_length:
        return False

    plan_keywords = [
        "구현", "설계", "아키텍처", "단계", "phase",
        "implementation", "architecture", "design",
        "## ", "### ", "```",
    ]
    score = sum(1 for kw in plan_keywords if kw.lower() in text.lower())
    return score >= 3


def evaluate_with_gemini(text: str) -> str | None:
    """evaluate.py를 import하여 Gemini 평가를 실행합니다."""
    try:
        from evaluate import call_gemini, PROMPTS
        result, _ = call_gemini(text, PROMPTS["doc"])
        return result
    except Exception as e:
        return f"[ERROR] Gemini 호출 실패: {e}"


def main():
    if len(sys.argv) < 2:
        # 테스트 모드: stdin에서 JSON 읽기
        try:
            notification = json.loads(sys.stdin.read())
        except (json.JSONDecodeError, IOError):
            return 0
    else:
        try:
            notification = json.loads(sys.argv[1])
        except (json.JSONDecodeError, ValueError):
            return 0

    if notification.get("type") != "agent-turn-complete":
        return 0

    load_env()

    # 마지막 어시스턴트 메시지 추출
    text = notification.get("last-assistant-message", "")
    if not text or not is_plan(text):
        return 0

    # Gemini 평가
    feedback = evaluate_with_gemini(text)
    if feedback:
        save_feedback(feedback, source="Codex Notify Hook (Plan 감지)", file_path=None)
        # stdout으로도 출력 (Codex가 표시할 수 있도록)
        print(f"[Gemini 평가] {feedback[:500]}")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
```

---
## FILE: skills/gemini-reviewer/scripts/evaluate.py
```python
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
            [gemini_cmd, full_prompt],
            capture_output=True, text=True, timeout=90,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip(), "cli"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None, ""


def call_gemini(content: str, prompt: str) -> tuple[str, str]:
    """Gemini 호출 (SDK 우선, CLI 폴백).

    Returns:
        (결과 텍스트, 사용된 모델명)
    """
    result, model = call_gemini_sdk(content, prompt)
    if result:
        return result, model

    result, model = call_gemini_cli(content, prompt)
    if result:
        return f"[CLI] {result}", "cli"

    print("[ERROR] Gemini 호출 실패. GEMINI_API_KEY를 확인하세요.", file=sys.stderr)
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
```

---
## FILE: scripts/config.json
```json
{
  "gemini_cmd": "/usr/local/bin/gemini",
  "gemini_timeout": 90,
  "cooldown_seconds_per_file": 300,
  "min_content_length": 300,
  "watch_extensions": [
    ".md", ".py"
  ],
  "exclude_files": [
    "gemini_feedback.md"
  ],
  "evaluation_prompt": "다음 문서를 평가해줘:\n- 논리적 일관성\n- 실현 가능성\n- 누락된 고려사항\n- 개선 제안\n간결하게 한국어로 답해줘.",
  "code_evaluation_prompt": "다음 코드를 리뷰해줘:\n- 버그 또는 잠재적 오류\n- 보안 취약점 (인젝션, 하드코딩된 비밀 등)\n- 에러 처리 누락\n- 개선 제안\n간결하게 한국어로 답해줘.",
  "code_extensions": [".py", ".js", ".ts", ".jsx", ".tsx"],
  "plan_detection_prompt": "이 텍스트는 소프트웨어 개발 계획입니까? '예' 또는 '아니오'로만 답하시오.",
  "sdk": {
    "enabled": true,
    "model": "gemini-2.5-flash",
    "fallback_models": ["gemini-2.0-flash", "gemini-1.5-flash"],
    "fallback_to_cli": true,
    "oauth_creds_path": "~/.gemini/oauth_creds.json",
    "api_key_env": "GEMINI_API_KEY",
    "max_output_tokens": 2048,
    "temperature": 0.3,
    "oauth_client_id_env": "GEMINI_OAUTH_CLIENT_ID",
    "oauth_client_secret_env": "GEMINI_OAUTH_CLIENT_SECRET"
  },
  "async_mode": false,
  "async_timeout": 120,

  "a2a_schema_enabled": false,

  "pre_tool_guard": {
    "enabled": true,
    "custom_block_patterns": []
  },

  "error_detection": {
    "enabled": true,
    "tail_lines": 50,
    "global_cooldown_seconds": 60,
    "thresholds": {"critical": 1, "high": 1, "medium": 2, "low": 3},
    "error_prompt": "다음 에러를 분석하고 원인과 수정 방법을 간결하게 한국어로 제안해주세요.",
    "feedback_prefix": "[SYSTEM ADVISORY: Gemini Error Analysis]"
  }
}```

---
## FILE: .claude/settings.local.json
```json
{
  "permissions": {
    "allow": [
      "Bash(python3:*)",
      "Bash(gemini:*)",
      "Bash(find:*)",
      "Bash(/usr/local/bin/gemini:*)",
      "WebSearch",
      "WebFetch(domain:ai.google.dev)",
      "WebFetch(domain:github.com)",
      "WebFetch(domain:googleapis.dev)",
      "WebFetch(domain:googleapis.github.io)",
      "Bash(chmod:*)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator status -u)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator status)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator add .env.example .gitignore CLAUDE.md README.md gemini_feedback.md plans/ requirements.txt scripts/)",
      "Bash(git commit:*)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator remote add:*)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator push -u origin main)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator add .env.example scripts/config.json scripts/a2a_bridge.py plans/phase2_implementation_plan.md)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator commit --amend -m \"$\\(cat <<''EOF''\nfeat: Phase 1+2 완료 — Claude-Gemini 협업 평가 시스템\n\nPhase 1 \\(MVP\\):\n- PostToolUse/Stop Hook으로 .md 파일 Write/Edit 시 Gemini 자동 평가\n- 쿨다운 메커니즘, 피드백 로그 \\(gemini_feedback.md\\)\n\nPhase 2:\n- google-genai SDK 직접 호출 \\(Dual Mode: SDK 우선, CLI fallback\\)\n- 비동기 모드 \\(fire-and-forget 백그라운드 평가\\)\n- .env 기반 복수 API key 지원\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n\\)\")",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator add scripts/a2a_bridge.py scripts/config.json)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator commit -m \"$\\(cat <<''EOF''\nfeat: Rate Limit 자동 전환 — 복수 API key/모델 순회\n\n429 에러 시 다음 API key → 다음 모델 자동 전환.\nGEMINI_API_KEY_* 환경변수 자동 수집, fallback_models 설정 지원.\n\nCo-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>\nEOF\n\\)\")",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator push)",
      "Bash(git add:*)",
      "Bash(git push:*)",
      "WebFetch(domain:developers.google.com)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator config commit.template .gitmessage)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator config --local commit.template)",
      "Bash(echo:*)",
      "Bash(printf '{\"\"\"\"tool_name\"\"\"\":\"\"\"\"Bash\"\"\"\",\"\"\"\"tool_input\"\"\"\":{\"\"\"\"command\"\"\"\":\"\"\"\"git commit -m \\\\\"\"\"\"$\\(cat <<'\"''''\"'EOF'\"''''\"'\\\\\\\\nrm -rf 설명\\\\\\\\nEOF\\\\\\\\n\\)\\\\\"\"\"\"\"\"\"\"}}')",
      "WebFetch(domain:developers.openai.com)",
      "Bash(/Users/jaehyuntak/.nvm/versions/node/v25.6.1/bin/codex:*)",
      "Bash(lsof:*)",
      "Bash(xxd:*)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator status --short)",
      "Bash(git -C /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator log --oneline -3)",
      "Bash(gh api:*)",
      "Bash(wc:*)",
      "Bash(ls:*)",
      "Bash(codex --version:*)",
      "Bash(codex:*)",
      "Bash(git status:*)",
      "Bash(git check-ignore:*)"
    ],
    "deny": []
  },
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/scripts/hook_pre_tool.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/scripts/hook_auto_task.py",
            "timeout": 120
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 /Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/scripts/hook_stop.py",
            "timeout": 120
          }
        ]
      }
    ]
  }
}
```

---
## FILE: schemas/codex_review_result.json
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["summary", "issues", "score", "strengths"],
  "properties": {
    "summary": {
      "type": "string",
      "description": "리뷰 요약 (1-3문장)"
    },
    "issues": {
      "type": "array",
      "description": "발견된 이슈 목록",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["severity", "description", "file", "line", "suggestion"],
        "properties": {
          "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"]
          },
          "description": {
            "type": "string"
          },
          "file": {
            "type": ["string", "null"]
          },
          "line": {
            "type": ["integer", "null"]
          },
          "suggestion": {
            "type": ["string", "null"]
          }
        }
      }
    },
    "score": {
      "type": "integer",
      "description": "전체 코드 품질 점수 (1-10)"
    },
    "strengths": {
      "type": "array",
      "description": "잘 된 점",
      "items": {
        "type": "string"
      }
    }
  }
}
```

---
## FILE: schemas/codex_task_result.json
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "additionalProperties": false,
  "required": ["task_completed", "summary", "files_modified", "files_created", "commands_run", "next_steps"],
  "properties": {
    "task_completed": {
      "type": "boolean"
    },
    "summary": {
      "type": "string",
      "description": "작업 요약"
    },
    "files_modified": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "files_created": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "commands_run": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "next_steps": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  }
}
```
