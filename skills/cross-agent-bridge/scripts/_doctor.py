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
    feedback_path = project_root / "plans" / "gemini" / "gemini_feedback.md"
    if feedback_path.exists():
        content = feedback_path.read_text("utf-8")
        entries = content.count("\n---\n")
        size_kb = len(content.encode("utf-8")) / 1024
        check("ok", f"plans/gemini/gemini_feedback.md: {entries}개 항목, {size_kb:.1f}KB")
    else:
        check("warn", "plans/gemini/gemini_feedback.md 없음")

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
