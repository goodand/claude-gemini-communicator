"""에러 감지 + Lazy Analysis.

a2a_bridge.py의 에러 관련 함수들을 분리한 모듈.
transcript 스캔 → 패턴 매칭 → 심각도 분류 → 임계값 도달 시 Gemini 분석.
"""

import fcntl
import hashlib
import json
import os
import re
import time
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ERROR_HISTORY_PATH = PROJECT_ROOT / ".error_history.json"

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

# 에러 감지 정규식
_ERROR_DETECT_RE = re.compile(
    r"Traceback \(most recent call last\)"
    r"|(?:Error|Exception|FAILED|FAIL|error:)(?=[\s:\]])"
    r"|exit code [1-9]",
    re.IGNORECASE,
)

# 에러 해시 정규화 패턴 (가변 요소 마스킹)
_NORMALIZE_PATTERNS = [
    (re.compile(r"/[\w/.+-]+"), "<PATH>"),
    (re.compile(r"line \d+"), "line <N>"),
    (re.compile(r"0x[0-9a-fA-F]+"), "<ADDR>"),
    (re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}"), "<TIME>"),
]


def _load_error_history() -> dict:
    """에러 이력 파일을 로드한다."""
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
    """에러 이력 파일을 저장한다."""
    with open(ERROR_HISTORY_PATH, "w", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(history, f, ensure_ascii=False, indent=2)
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def normalize_error_text(error_text: str) -> str:
    """에러 텍스트에서 가변 요소를 마스킹하여 정규화한다."""
    normalized = error_text
    for pattern, replacement in _NORMALIZE_PATTERNS:
        normalized = pattern.sub(replacement, normalized)
    return normalized


def hash_error(error_text: str) -> str:
    """정규화된 에러 텍스트의 해시를 생성한다."""
    normalized = normalize_error_text(error_text)
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()[:12]


def classify_error_severity(error_text: str) -> str:
    """에러 텍스트의 심각도를 분류한다."""
    for severity, patterns in _ERROR_SEVERITY.items():
        if any(p in error_text for p in patterns):
            return severity
    return "medium"


def scan_transcript_for_errors(transcript_path: str, tail_lines: int = 50) -> list:
    """Transcript JSONL 파일의 마지막 N줄에서 에러를 스캔한다."""
    if not transcript_path or not os.path.exists(transcript_path):
        return []

    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except IOError:
        return []

    recent_lines = lines[-tail_lines:] if len(lines) > tail_lines else lines

    errors = []
    seen_hashes = set()

    for line in recent_lines:
        try:
            entry = json.loads(line.strip())
        except json.JSONDecodeError:
            continue

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
    """에러 목록을 이력에 기록하고, Lazy Analysis 조건 충족 시 Gemini 분석을 실행한다."""
    if not errors:
        return None

    # 지연 import — 순환 의존 방지
    from src.core.gemini_service import call_gemini
    from src.shared.feedback import save_feedback

    error_config = config.get("error_detection", {})
    thresholds = error_config.get("thresholds", {"critical": 1, "high": 1, "medium": 2, "low": 3})
    global_cooldown = error_config.get("global_cooldown_seconds", 60)
    error_prompt = error_config.get(
        "error_prompt",
        "다음 에러를 분석하고 원인과 수정 방법을 간결하게 한국어로 제안해주세요.",
    )
    prefix = error_config.get("feedback_prefix", "[SYSTEM ADVISORY: Gemini Error Analysis]")

    history = _load_error_history()

    now = time.time()
    if now - history.get("last_analysis_time", 0) < global_cooldown:
        return None

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

    combined = "\n\n---\n\n".join(errors_to_analyze[:3])
    full_prompt = f"{error_prompt}\n\n{combined}"

    feedback = call_gemini(content="", prompt=full_prompt, config=config)

    history = _load_error_history()
    history["last_analysis_time"] = time.time()
    for error_text in errors_to_analyze:
        error_hash = hash_error(error_text)
        if error_hash in history["errors"]:
            history["errors"][error_hash]["analyzed"] = True
    _save_error_history(history)

    request_id = str(uuid.uuid4())
    prefixed_feedback = f"{prefix}\n\n{feedback}"
    save_feedback(prefixed_feedback, source="Error Analysis (Stop Hook)",
                  request_id=request_id)

    return prefixed_feedback
