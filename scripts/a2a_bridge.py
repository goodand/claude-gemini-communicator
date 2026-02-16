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
FEEDBACK_PATH = PROJECT_ROOT / "plans" / "gemini" / "gemini_feedback.md"
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

    FEEDBACK_PATH.parent.mkdir(parents=True, exist_ok=True)
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
