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
