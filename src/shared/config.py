"""설정 로딩 및 환경변수 관리.

a2a_bridge.py의 load_config() + _load_env()를 분리한 모듈.
"""

import json
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "config.json"
ENV_PATH = PROJECT_ROOT / ".env"


def load_env() -> None:
    """프로젝트 루트의 .env 파일을 환경변수로 로드한다."""
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


def load_config(config_path: Path | None = None) -> dict:
    """config.json에서 설정을 로드한다."""
    path = config_path or CONFIG_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


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

    jsonl = config.get("jsonl_bus")
    if jsonl is not None and isinstance(jsonl, dict):
        jpath = jsonl.get("path")
        if jsonl.get("enabled") and not jpath:
            issues.append(("error", "jsonl_bus.enabled=true이지만 path 미설정"))
        if jpath is not None and not isinstance(jpath, str):
            issues.append(("error", "jsonl_bus.path는 문자열이어야 합니다"))

    guard = config.get("pre_tool_guard")
    if guard is not None and isinstance(guard, dict):
        for i, pat in enumerate(guard.get("custom_block_patterns", [])):
            try:
                re.compile(pat)
            except re.error as e:
                issues.append(("error", f"custom_block_patterns[{i}] 정규식 오류: {e}"))

    return issues
