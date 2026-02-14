"""CLI 관리 도구: 시스템 진단, 상태, 통계, 검색, 테스트, 초기화.

Usage:
    python3 scripts/cli.py doctor   — 시스템 진단 (config/환경/Hook 검증)
    python3 scripts/cli.py status   — 현재 설정 및 상태
    python3 scripts/cli.py stats    — 피드백 통계
    python3 scripts/cli.py search <keyword>  — 피드백 검색
    python3 scripts/cli.py test     — 전체 자동 테스트
    python3 scripts/cli.py clear    — 상태 파일 초기화
"""

import json
import os
import re
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


def cmd_doctor():
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

def cmd_status():
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

def cmd_stats():
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


def cmd_search():
    """피드백을 키워드/소스/날짜로 검색합니다."""
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/cli.py search <keyword> [--source <source>] [--date <YYYY-MM-DD>]")
        sys.exit(1)

    keyword = sys.argv[2]
    source_filter = None
    date_filter = None

    # 옵션 파싱
    args = sys.argv[3:]
    i = 0
    while i < len(args):
        if args[i] == "--source" and i + 1 < len(args):
            source_filter = args[i + 1]
            i += 2
        elif args[i] == "--date" and i + 1 < len(args):
            date_filter = args[i + 1]
            i += 2
        else:
            i += 1

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

def cmd_test():
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

def cmd_clear():
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
}


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print("Usage: python3 scripts/cli.py <command>\n")
        print("Commands:")
        for name, (desc, _) in COMMANDS.items():
            print(f"  {name:10s} {desc}")
        sys.exit(1)

    cmd_name = sys.argv[1]
    _, fn = COMMANDS[cmd_name]
    result = fn()

    if cmd_name == "test" and result is False:
        sys.exit(1)


if __name__ == "__main__":
    main()
