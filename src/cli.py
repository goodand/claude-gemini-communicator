"""CLI 관리 도구: 시스템 진단, 상태, 통계, 검색, 테스트, 초기화.

Usage:
    python3 src/cli.py doctor   — 시스템 진단
    python3 src/cli.py status   — 현재 설정 및 상태
    python3 src/cli.py stats    — 피드백 통계
    python3 src/cli.py search <keyword>  — 피드백 검색
    python3 src/cli.py test     — 전체 자동 테스트
    python3 src/cli.py clear    — 상태 파일 초기화
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

# src/ 패키지 import를 위해 프로젝트 루트를 path에 추가
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from src.shared.config import load_config, load_env, validate_config, CONFIG_PATH, PROJECT_ROOT
from src.shared.feedback import FEEDBACK_PATH
from src.core.cooldown import COOLDOWN_STATE_PATH
from src.core.error_analyzer import ERROR_HISTORY_PATH

SETTINGS_PATH = PROJECT_ROOT / ".claude" / "settings.local.json"
HOOKS_SCRIPTS = {
    "hook_auto_task.py": "PostToolUse Hook",
    "hook_stop.py": "Stop Hook",
    "hook_pre_tool.py": "PreToolUse Hook",
}


# ── doctor ──

def cmd_doctor(args=None):
    """시스템 전체를 진단한다."""
    load_env()
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

    # 1. Config
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

    config = json.loads(CONFIG_PATH.read_text("utf-8")) if CONFIG_PATH.exists() else {}
    gemini_cmd = config.get("gemini_cmd", "/usr/local/bin/gemini")
    if Path(gemini_cmd).exists():
        check("ok", f"Gemini CLI: {gemini_cmd}")
    else:
        check("warn", f"Gemini CLI 없음: {gemini_cmd}", "CLI 폴백 불가")

    if (PROJECT_ROOT / ".env").exists():
        check("ok", ".env 파일 존재")
    else:
        check("warn", ".env 파일 없음")

    # 3. Hook 등록
    print("\n[3] Hook 등록 점검")
    if not SETTINGS_PATH.exists():
        check("err", "settings.local.json", "파일 없음")
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
                    check("warn", f"{hook_type} Hook 미등록", script_name)
        except json.JSONDecodeError:
            check("err", "settings.local.json", "JSON 파싱 실패")

    # 4. 스크립트 존재
    print("\n[4] src/hooks/ 파일 점검")
    hooks_dir = PROJECT_ROOT / "src" / "hooks"
    for script, desc in HOOKS_SCRIPTS.items():
        path = hooks_dir / script
        if path.exists():
            check("ok", f"src/hooks/{script} ({desc})")
        else:
            check("err", f"src/hooks/{script} 없음", desc)

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


# ── status ──

def cmd_status(args=None):
    """현재 시스템 상태를 출력한다."""
    load_env()
    print("=== Claude-Gemini Communicator Status ===\n")

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

    print()
    if COOLDOWN_STATE_PATH.exists():
        state = json.loads(COOLDOWN_STATE_PATH.read_text("utf-8"))
        now = time.time()
        print(f"[Cooldown] {len(state)}개 파일 기록")
        for fp, ts in sorted(state.items(), key=lambda x: x[1], reverse=True)[:5]:
            age = int(now - ts)
            print(f"  {fp}: {age}초 전")
    else:
        print("[Cooldown] 기록 없음")

    print()
    if ERROR_HISTORY_PATH.exists():
        history = json.loads(ERROR_HISTORY_PATH.read_text("utf-8"))
        errors = history.get("errors", {})
        analyzed = sum(1 for e in errors.values() if e.get("analyzed"))
        last = history.get("last_analysis_time", 0)
        last_str = f"{int(time.time() - last)}초 전" if last > 0 else "없음"
        print(f"[Error History] {len(errors)}개 에러, {analyzed}개 분석됨")
        print(f"  마지막 분석: {last_str}")
    else:
        print("[Error History] 기록 없음")

    print()
    if FEEDBACK_PATH.exists():
        content = FEEDBACK_PATH.read_text("utf-8")
        entries = content.count("\n---\n")
        size_kb = len(content.encode("utf-8")) / 1024
        print(f"[Feedback] {entries}개 항목, {size_kb:.1f}KB")
    else:
        print("[Feedback] gemini_feedback.md 없음")


# ── stats ──

def cmd_stats(args=None):
    """gemini_feedback.md에서 통계를 추출한다."""
    print("=== Feedback Statistics ===\n")
    if not FEEDBACK_PATH.exists():
        print("gemini_feedback.md가 없습니다.")
        return

    content = FEEDBACK_PATH.read_text("utf-8")
    if not content.strip():
        print("피드백이 비어있습니다.")
        return

    entries = content.split("\n---\n")
    entries = [e.strip() for e in entries if e.strip()]

    sources = {}
    dates = []
    for entry in entries:
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
        day_counts = {}
        for d in dates:
            day_counts[d] = day_counts.get(d, 0) + 1
        print("[일별]")
        for day, count in sorted(day_counts.items())[-7:]:
            bar = "█" * count
            print(f"  {day}: {bar} ({count})")


# ── search ──

def parse_feedback_entries(content: str) -> list:
    """gemini_feedback.md를 항목별로 파싱한다."""
    raw_entries = content.split("\n---\n")
    entries = []
    for raw in raw_entries:
        raw = raw.strip()
        if not raw:
            continue
        match = re.search(
            r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.+?)(?:\s*\|\s*대상:\s*`(.+?)`)?$",
            raw, re.MULTILINE,
        )
        entries.append({
            "date": match.group(1) if match else "",
            "source": match.group(2).strip() if match else "",
            "target": match.group(3) if match and match.group(3) else "",
            "body": raw,
        })
    return entries


def cmd_search(args):
    """피드백을 키워드/소스/날짜로 검색한다."""
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
        if keyword.lower() not in entry["body"].lower():
            continue
        if source_filter and source_filter.lower() not in entry["source"].lower():
            continue
        if date_filter and not entry["date"].startswith(date_filter):
            continue
        results.append(entry)

    print(f'=== "{keyword}" 검색 결과: {len(results)}건 ===\n')
    for i, entry in enumerate(results, 1):
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


# ── test ──

def cmd_test(args=None):
    """전체 시스템 자동 테스트를 실행한다."""
    load_env()
    print("=== System Test Suite ===\n")
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

    # 1. Config
    print("[1] Config 검증")

    def test_config_load():
        c = load_config()
        return isinstance(c, dict) and "gemini_timeout" in c

    def test_config_required_fields():
        c = load_config()
        required = ["gemini_cmd", "gemini_timeout", "watch_extensions", "evaluation_prompt", "sdk"]
        return all(k in c for k in required)

    run_test("config.json 로드", test_config_load)
    run_test("필수 필드 존재", test_config_required_fields)

    # 2. 에러 감지
    print("\n[2] 에러 감지 함수")
    from src.core.error_analyzer import normalize_error_text, hash_error, classify_error_severity

    def test_normalize_error():
        result = normalize_error_text("File /usr/local/lib/python3.13/test.py, line 42")
        return "<PATH>" in result and "line <N>" in result

    def test_hash_error():
        h1 = hash_error("TypeError: foo at /path/a.py line 1")
        h2 = hash_error("TypeError: foo at /different/b.py line 99")
        return h1 == h2

    def test_classify_severity():
        return (classify_error_severity("PermissionError: access denied") == "critical"
                and classify_error_severity("ImportError: no module") == "high"
                and classify_error_severity("TypeError: bad arg") == "medium"
                and classify_error_severity("SyntaxError: invalid") == "low")

    run_test("에러 텍스트 정규화", test_normalize_error)
    run_test("동일 에러 해시 일치", test_hash_error)
    run_test("심각도 분류", test_classify_severity)

    # 3. A2A 프로토콜
    print("\n[3] A2A 프로토콜")
    from src.core.a2a_protocol import (
        build_a2a_request, parse_a2a_response, a2a_response_to_markdown,
    )

    def test_a2a_request():
        req = build_a2a_request("evaluation_request", {"text": "hello"}, "test")
        return req.get("a2a_version") == "1.0" and "request_id" in req

    def test_a2a_parse_valid():
        resp = parse_a2a_response('{"evaluation":{"score":"good"},"summary":"ok"}')
        return resp.get("status") == "success" and "evaluation" in resp.get("payload", {})

    def test_a2a_parse_raw():
        resp = parse_a2a_response("그냥 텍스트 응답")
        return "raw_text" in resp.get("payload", {})

    def test_a2a_to_markdown():
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
    run_test("A2A raw text 폴백", test_a2a_parse_raw)
    run_test("A2A → 마크다운 변환", test_a2a_to_markdown)

    # 4. PreToolUse Guard
    print("\n[4] PreToolUse Guard")
    from src.hooks.hook_pre_tool import check_command

    def _check(cmd, expected_severity):
        result = check_command(cmd, load_config())
        if expected_severity is None:
            return result is None
        return result is not None and result["severity"] == expected_severity

    run_test("Block: rm -rf", lambda: _check("rm -rf /tmp/data", "block"))
    run_test("Block: git push --force", lambda: _check("git push --force origin main", "block"))
    run_test("Block: git reset --hard", lambda: _check("git reset --hard HEAD~3", "block"))
    run_test("Allow: 안전한 명령", lambda: _check("ls -la", None) and _check("git status", None))
    run_test("오탐 방지: echo 안의 rm -rf", lambda: _check('echo "rm -rf is dangerous"', None))

    # 5. Config 검증 함수
    print("\n[5] Config 검증 함수")

    def test_validate_valid():
        issues = validate_config(load_config())
        errors = [i for i in issues if i[0] == "error"]
        return len(errors) == 0

    def test_validate_missing_field():
        issues = validate_config({"sdk": {}})
        errors = [i for i in issues if i[0] == "error"]
        return len(errors) >= 3

    run_test("현재 config 유효성", test_validate_valid)
    run_test("필수 필드 누락 감지", test_validate_missing_field)

    # 결과
    print(f"\n{'='*40}")
    print(f"결과: {passed}/{total} 통과", end="")
    if failed:
        print(f", {failed} 실패")
    else:
        print(" — ALL PASSED ✓")
    return failed == 0


# ── clear ──

def cmd_clear(args=None):
    """런타임 상태 파일을 초기화한다."""
    cleared = []
    for path, name in [
        (COOLDOWN_STATE_PATH, "쿨다운 상태"),
        (ERROR_HISTORY_PATH, "에러 이력"),
    ]:
        if path.exists():
            path.unlink()
            cleared.append(name)

    if cleared:
        print(f"초기화 완료: {', '.join(cleared)}")
    else:
        print("초기화할 파일이 없습니다.")


# ── main ──

COMMANDS = {
    "doctor": ("시스템 진단", cmd_doctor),
    "status": ("시스템 상태 확인", cmd_status),
    "stats": ("피드백 통계", cmd_stats),
    "search": ("피드백 검색", cmd_search),
    "test": ("전체 자동 테스트", cmd_test),
    "clear": ("상태 파일 초기화", cmd_clear),
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
