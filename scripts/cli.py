"""CLI 관리 도구: 시스템 상태 확인, 통계, 테스트, 초기화.

Usage:
    python3 scripts/cli.py status   — 현재 설정 및 상태
    python3 scripts/cli.py stats    — 피드백 통계
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
    "status": ("시스템 상태 확인", cmd_status),
    "stats": ("피드백 통계", cmd_stats),
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
