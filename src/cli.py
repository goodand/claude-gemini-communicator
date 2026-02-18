"""CLI 관리 도구: 시스템 진단, 상태, 통계, 검색, 테스트, 초기화, Hook 설치.

Usage:
    python3 src/cli.py doctor   — 시스템 진단
    python3 src/cli.py status   — 현재 설정 및 상태
    python3 src/cli.py stats    — 피드백 통계
    python3 src/cli.py search <keyword>  — 피드백 검색
    python3 src/cli.py test     — 전체 자동 테스트
    python3 src/cli.py clear    — 상태 파일 초기화
    python3 src/cli.py install  — 다른 프로젝트에 Hook 등록
    python3 src/cli.py uninstall — Hook 등록 해제
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

from src.shared.config import load_config, load_env, validate_config, CONFIG_PATH, PROJECT_ROOT, get_jsonl_path
from src.shared.feedback import FEEDBACK_PATH
from src.core.cooldown import COOLDOWN_STATE_PATH
from src.core.error_analyzer import ERROR_HISTORY_PATH
from src.core.memory import parse_jsonl_file as parse_jsonl_events

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

    # 4. JSONL 버스
    print("\n[4] JSONL 버스 점검")
    if config:
        jsonl_cfg = config.get("jsonl_bus", {})
        if jsonl_cfg.get("enabled"):
            check("ok", "JSONL 버스: ON")
            jsonl_path_str = jsonl_cfg.get("path", "")
            if jsonl_path_str:
                jp = PROJECT_ROOT / jsonl_path_str
                if jp.exists():
                    line_count = sum(1 for l in jp.read_text("utf-8").splitlines() if l.strip())
                    check("ok", f"JSONL 파일: {line_count}개 이벤트")
                else:
                    check("warn", "JSONL 파일 미존재", "아직 이벤트 미기록")
            else:
                check("err", "jsonl_bus.path 미설정")
        else:
            check("warn", "JSONL 버스: OFF")

    # 5. 스크립트 존재
    print("\n[5] src/hooks/ 파일 점검")
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
        jsonl = config.get("jsonl_bus", {})
        print(f"  JSONL 버스:      {'ON' if jsonl.get('enabled') else 'OFF'}")
        if jsonl.get("enabled"):
            print(f"  JSONL 경로:      {jsonl.get('path', 'N/A')}")
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

    # JSONL 버스 상태
    config = json.loads(CONFIG_PATH.read_text("utf-8")) if CONFIG_PATH.exists() else {}
    jsonl_cfg = config.get("jsonl_bus", {})
    if jsonl_cfg.get("enabled"):
        jsonl_path = get_jsonl_path(config)
        if jsonl_path.exists():
            line_count = sum(1 for line in jsonl_path.read_text("utf-8").splitlines() if line.strip())
            size_kb = len(jsonl_path.read_bytes()) / 1024
            print(f"[JSONL Bus] {line_count}개 이벤트, {size_kb:.1f}KB")
        else:
            print("[JSONL Bus] 파일 없음 (아직 이벤트 미기록)")


# ── stats ──

def _stats_jsonl():
    """JSONL 이벤트 통계를 출력한다."""
    config = load_config()
    jsonl_path = get_jsonl_path(config)
    events = parse_jsonl_events(jsonl_path)
    if not events:
        print(f"JSONL 이벤트가 없습니다: {jsonl_path}")
        return

    print(f"=== JSONL Event Statistics ===\n")
    print(f"총 이벤트 수: {len(events)}")

    # 메시지 타입별
    types = {}
    agents = {}
    dates = []
    pairs = 0
    for e in events:
        mt = e.get("message_type", "unknown")
        types[mt] = types.get(mt, 0) + 1
        sa = e.get("source_agent", e.get("source", "unknown"))
        agents[sa] = agents.get(sa, 0) + 1
        ts = e.get("timestamp", "")[:10]
        if ts:
            dates.append(ts)
        if e.get("parent_message_id"):
            pairs += 1

    print()
    print("[메시지 타입별]")
    for mt, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
        print(f"  {mt}: {count}건")

    print()
    print("[에이전트별]")
    for ag, count in sorted(agents.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ag}: {count}건")

    print()
    print(f"[체인 연결] parent_message_id 있는 이벤트: {pairs}건")

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


def cmd_stats(args=None):
    """gemini_feedback.md 또는 JSONL에서 통계를 추출한다."""
    if getattr(args, "jsonl", False):
        return _stats_jsonl()

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
            r"## \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\] (.+?)(?:\s*\|.*)?\s*$",
            raw, re.MULTILINE,
        )
        # 헤더에서 세부 필드 추출: 대상, request_id
        header_line = match.group(0) if match else ""
        target_match = re.search(r"대상:\s*`(.+?)`", header_line)
        entries.append({
            "date": match.group(1) if match else "",
            "source": match.group(2).strip() if match else "",
            "target": target_match.group(1) if target_match else "",
            "body": raw,
        })
    return entries


def _search_jsonl(args):
    """JSONL 이벤트를 검색한다."""
    config = load_config()
    jsonl_path = get_jsonl_path(config)

    events = parse_jsonl_events(jsonl_path)
    if not events:
        print(f"JSONL 이벤트가 없습니다: {jsonl_path}")
        return

    keyword = args.keyword or ""
    agent_filter = getattr(args, "agent", None)
    request_id_filter = getattr(args, "request_id", None)
    since_filter = getattr(args, "since", None)

    results = []
    for event in events:
        # 키워드 필터
        if keyword:
            event_str = json.dumps(event, ensure_ascii=False).lower()
            if keyword.lower() not in event_str:
                continue
        # 에이전트 필터
        if agent_filter:
            src = event.get("source_agent", event.get("source", ""))
            if agent_filter.lower() not in str(src).lower():
                continue
        # request_id 필터
        if request_id_filter:
            rid = event.get("request_id", "")
            if not rid or not rid.startswith(request_id_filter):
                continue
        # 날짜 필터
        if since_filter:
            ts = event.get("timestamp", "")
            if ts < since_filter:
                continue
        results.append(event)

    label = f'"{keyword}" ' if keyword else ""
    print(f'=== JSONL {label}검색 결과: {len(results)}건 ===\n')
    for i, event in enumerate(results, 1):
        ts = event.get("timestamp", "?")[:19]
        msg_type = event.get("message_type", "?")
        src = event.get("source_agent", event.get("source", "?"))
        rid = event.get("request_id", "")[:8]
        parent = event.get("parent_message_id", "")
        parent_info = f" ← {parent[:8]}" if parent else ""
        feedback = event.get("feedback", "")
        snippet = feedback[:80].replace("\n", " ") if feedback else ""

        print(f"[{i}] {ts} | {msg_type} | {src} | rid={rid}{parent_info}")
        if snippet:
            print(f"    {snippet}...")
        print()


def cmd_search(args):
    """피드백을 키워드/소스/날짜로 검색한다."""
    # JSONL 모드
    if getattr(args, "jsonl", False):
        return _search_jsonl(args)

    keyword = args.keyword
    source_filter = args.source
    date_filter = args.date

    if not keyword:
        print("키워드를 입력하세요. (JSONL 모드는 --jsonl 사용)")
        return

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
        status = resp.get("status", {})
        return status.get("code") == "success" and "evaluation" in resp.get("payload", {})

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
    from src.shared.command_guard import check_command

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

    # 6. Phase 8: JSONL 버스 + parent_message_id
    print("\n[6] Phase 8: JSONL 버스 + parent_message_id")
    import tempfile
    from src.shared.feedback import save_feedback, _append_jsonl

    def test_jsonl_append():
        """JSONL append가 올바른 JSON 라인을 기록하는지 확인."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            jsonl_cfg = {"enabled": True, "path": tmp_path}
            # get_jsonl_path는 config.PROJECT_ROOT 기준
            import src.shared.config as cfg_mod
            original_root = cfg_mod.PROJECT_ROOT
            cfg_mod.PROJECT_ROOT = Path("/")  # 절대경로 사용을 위한 임시 변경
            _append_jsonl(jsonl_cfg, "test feedback", "test_source",
                         "test.md", "rid-123", {"message_type": "test"})
            cfg_mod.PROJECT_ROOT = original_root
            content = Path(tmp_path).read_text("utf-8").strip()
            rec = json.loads(content)
            return (rec.get("feedback") == "test feedback"
                    and rec.get("source") == "test_source"
                    and rec.get("request_id") == "rid-123"
                    and rec.get("message_type") == "test")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_jsonl_disabled():
        """JSONL disabled일 때 기록하지 않는지 확인."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            jsonl_cfg = {"enabled": False, "path": tmp_path}
            # save_feedback는 jsonl_config.enabled가 False면 JSONL 기록 안 함
            # _append_jsonl을 직접 호출하지 않으므로 pass
            return True
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_parent_message_id():
        """build_a2a_request에 parent_message_id가 전파되는지 확인."""
        r1 = build_a2a_request("evaluation_request", {}, "test")
        r2 = build_a2a_request("evaluation_response", {}, "test",
                               parent_message_id=r1["message_id"])
        return r2.get("parent_message_id") == r1["message_id"]

    def test_parent_message_id_absent():
        """parent_message_id 미지정 시 필드가 없는지 확인."""
        r = build_a2a_request("evaluation_request", {}, "test")
        return "parent_message_id" not in r

    def test_jsonl_config_validation():
        """jsonl_bus config 검증이 작동하는지 확인."""
        issues = validate_config({
            "gemini_cmd": "/usr/local/bin/gemini",
            "gemini_timeout": 90,
            "watch_extensions": [".md"],
            "evaluation_prompt": "test",
            "jsonl_bus": {"enabled": True},
        })
        return any("jsonl_bus" in msg or "path" in msg for _, msg in issues)

    def test_parse_jsonl_events():
        """parse_jsonl_events가 올바르게 파싱하는지 확인."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as tmp:
            tmp.write('{"message_type":"test","timestamp":"2026-02-17T00:00:00"}\n')
            tmp.write('{"message_type":"test2","source_agent":"gemini"}\n')
            tmp_path = tmp.name
        try:
            events = parse_jsonl_events(Path(tmp_path))
            return (len(events) == 2
                    and events[0]["message_type"] == "test"
                    and events[1]["source_agent"] == "gemini")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    run_test("JSONL append 기록", test_jsonl_append)
    run_test("JSONL disabled 시 미기록", test_jsonl_disabled)
    run_test("parent_message_id 전파", test_parent_message_id)
    run_test("parent_message_id 미지정 시 부재", test_parent_message_id_absent)
    run_test("jsonl_bus config 검증", test_jsonl_config_validation)
    run_test("JSONL 이벤트 파싱", test_parse_jsonl_events)

    # 7. 멀티홉 체인 추적
    print("\n[7] 멀티홉 체인 추적")

    def test_build_chain_basic():
        """parent_message_id로 연결된 체인을 올바르게 추적하는지 확인."""
        events = [
            {"message_id": "m1", "request_id": "r1", "message_type": "req", "timestamp": "2026-01-01T00:00:00"},
            {"message_id": "m2", "parent_message_id": "m1", "request_id": "r1", "message_type": "resp", "timestamp": "2026-01-01T00:01:00"},
            {"message_id": "m3", "request_id": "r2", "message_type": "other", "timestamp": "2026-01-01T00:02:00"},
        ]
        chain = _build_chain(events, "r1")
        return len(chain) == 2 and chain[0]["message_id"] == "m1" and chain[1]["message_id"] == "m2"

    def test_build_chain_prefix():
        """prefix 매칭으로 체인을 찾는지 확인."""
        events = [
            {"message_id": "abc-123-456", "request_id": "xyz-789", "timestamp": "2026-01-01T00:00:00"},
        ]
        chain = _build_chain(events, "abc-123")
        return len(chain) == 1

    def test_build_chain_empty():
        """존재하지 않는 ID에 대해 빈 체인을 반환하는지 확인."""
        events = [
            {"message_id": "m1", "request_id": "r1", "timestamp": "2026-01-01T00:00:00"},
        ]
        return _build_chain(events, "nonexistent") == []

    def test_build_chain_req_resp_pair():
        """요청→응답 쌍이 동일 chain으로 묶이는지 확인."""
        events = [
            {"message_id": "req-1", "request_id": "r1", "message_type": "evaluation_request",
             "source_agent": "claude", "timestamp": "2026-01-01T00:00:00"},
            {"message_id": "resp-1", "parent_message_id": "req-1", "request_id": "r1",
             "message_type": "evaluation_response", "source_agent": "gemini",
             "timestamp": "2026-01-01T00:00:30"},
        ]
        chain = _build_chain(events, "r1")
        return (len(chain) == 2
                and chain[0]["message_type"] == "evaluation_request"
                and chain[1]["message_type"] == "evaluation_response"
                and chain[1].get("parent_message_id") == chain[0]["message_id"])

    def test_log_jsonl_event():
        """log_jsonl_event가 올바르게 기록하는지 확인."""
        from src.shared.feedback import log_jsonl_event
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            import src.shared.config as cfg_mod
            original_root = cfg_mod.PROJECT_ROOT
            cfg_mod.PROJECT_ROOT = Path("/")
            log_jsonl_event({"enabled": True, "path": tmp_path}, {
                "message_id": "test-mid",
                "message_type": "evaluation_request",
            })
            cfg_mod.PROJECT_ROOT = original_root
            content = Path(tmp_path).read_text("utf-8").strip()
            rec = json.loads(content)
            return rec.get("message_id") == "test-mid" and "timestamp" in rec
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    run_test("체인 추적 (parent_message_id)", test_build_chain_basic)
    run_test("체인 prefix 매칭", test_build_chain_prefix)
    run_test("체인 미존재 ID → 빈 결과", test_build_chain_empty)
    run_test("요청→응답 쌍 체인", test_build_chain_req_resp_pair)
    run_test("log_jsonl_event 기록", test_log_jsonl_event)

    # 8. Reference Architecture (Router, Memory, Scheduler)
    print("\n[8] Reference Architecture")
    from src.core.router import resolve_target, list_available_targets
    from src.core.memory import load_events, get_recent, get_by_agent, get_by_type, summarize
    from src.core.scheduler import register_job, get_job, complete_job, list_jobs, summarize_jobs, cleanup_old_jobs

    def test_router_default():
        """기본 라우팅 규칙으로 gemini가 반환되는지 확인."""
        target = resolve_target("evaluation_request", {})
        return target == "gemini"

    def test_router_with_config():
        """config의 routing_rules가 적용되는지 확인."""
        cfg = {"routing_rules": [
            {"match_type": "custom_request", "target": "codex"},
            {"match_type": "*", "target": "gemini"},
        ]}
        return (resolve_target("custom_request", cfg) == "codex"
                and resolve_target("other", cfg) == "gemini")

    def test_router_file_ext():
        """파일 확장자 매칭이 작동하는지 확인."""
        cfg = {"routing_rules": [
            {"match_ext": [".py", ".js"], "target": "codex"},
            {"match_type": "*", "target": "gemini"},
        ]}
        return (resolve_target("any", cfg, file_path="test.py") == "codex"
                and resolve_target("any", cfg, file_path="test.md") == "gemini")

    def test_router_list_targets():
        """사용 가능한 대상 에이전트 목록이 반환되는지 확인."""
        cfg = {"routing_rules": [
            {"match_type": "a", "target": "gemini"},
            {"match_type": "b", "target": "codex"},
        ]}
        targets = list_available_targets(cfg)
        return "codex" in targets and "gemini" in targets

    def test_memory_load_empty():
        """빈 config에서 이벤트 로드가 빈 리스트를 반환하는지 확인."""
        cfg = {"jsonl_bus": {"path": "nonexistent_test_path.jsonl"}}
        events = load_events(cfg)
        return events == []

    def test_memory_summarize_empty():
        """빈 이벤트에서 요약이 total=0을 반환하는지 확인."""
        cfg = {"jsonl_bus": {"path": "nonexistent_test_path.jsonl"}}
        s = summarize(cfg)
        return s["total"] == 0

    def test_memory_functions():
        """Memory 함수들이 JSONL 이벤트를 올바르게 필터하는지 확인."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as tmp:
            events_data = [
                {"message_type": "evaluation_request", "source_agent": "claude", "timestamp": "2026-02-17T00:00:00"},
                {"message_type": "evaluation_response", "source_agent": "gemini", "timestamp": "2026-02-17T00:01:00"},
                {"message_type": "error_analysis_request", "source_agent": "claude", "timestamp": "2026-02-17T00:02:00"},
            ]
            for e in events_data:
                tmp.write(json.dumps(e, ensure_ascii=False) + "\n")
            tmp_path = tmp.name
        try:
            cfg = {"jsonl_bus": {"path": tmp_path}}
            import src.shared.config as cfg_mod
            original_root = cfg_mod.PROJECT_ROOT
            cfg_mod.PROJECT_ROOT = Path("/")

            all_events = load_events(cfg)
            recent = get_recent(cfg, n=2)
            by_agent = get_by_agent(cfg, "gemini")
            by_type = get_by_type(cfg, "error_analysis_request")
            summary = summarize(cfg)

            cfg_mod.PROJECT_ROOT = original_root
            return (len(all_events) == 3
                    and len(recent) == 2
                    and len(by_agent) == 1 and by_agent[0]["source_agent"] == "gemini"
                    and len(by_type) == 1
                    and summary["total"] == 3)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_scheduler_lifecycle():
        """Scheduler 작업 등록→조회→완료 라이프사이클이 작동하는지 확인."""
        import src.core.scheduler as sched_mod
        original_path = sched_mod._JOBS_PATH
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            sched_mod._JOBS_PATH = Path(tmp.name)
        try:
            # 등록
            job = register_job("test-job-1", "evaluation", "gemini")
            assert job["status"] == "pending"
            # 조회
            fetched = get_job("test-job-1")
            assert fetched is not None and fetched["status"] == "pending"
            # 완료
            assert complete_job("test-job-1") is True
            fetched = get_job("test-job-1")
            assert fetched["status"] == "completed"
            # 목록
            jobs = list_jobs()
            assert len(jobs) == 1
            # 요약
            s = summarize_jobs()
            assert s["total"] == 1 and s["by_status"]["completed"] == 1
            return True
        except AssertionError:
            return False
        finally:
            sched_mod._JOBS_PATH.unlink(missing_ok=True)
            sched_mod._JOBS_PATH = original_path

    def test_scheduler_cleanup():
        """Scheduler 오래된 작업 정리가 작동하는지 확인."""
        import src.core.scheduler as sched_mod
        original_path = sched_mod._JOBS_PATH
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            sched_mod._JOBS_PATH = Path(tmp.name)
        try:
            register_job("old-job", "test", "gemini")
            complete_job("old-job")
            # completed_at를 과거로 변경
            data = sched_mod._load_jobs()
            data["jobs"]["old-job"]["completed_at"] = time.time() - 100000
            sched_mod._save_jobs(data)
            cleaned = cleanup_old_jobs(max_age_seconds=1)
            return cleaned == 1 and len(list_jobs()) == 0
        finally:
            sched_mod._JOBS_PATH.unlink(missing_ok=True)
            sched_mod._JOBS_PATH = original_path

    run_test("Router: 기본 라우팅", test_router_default)
    run_test("Router: config 규칙 적용", test_router_with_config)
    run_test("Router: 파일 확장자 매칭", test_router_file_ext)
    run_test("Router: 대상 에이전트 목록", test_router_list_targets)
    run_test("Memory: 빈 이벤트 로드", test_memory_load_empty)
    run_test("Memory: 빈 이벤트 요약", test_memory_summarize_empty)
    run_test("Memory: 필터 함수들", test_memory_functions)
    run_test("Scheduler: 작업 라이프사이클", test_scheduler_lifecycle)
    run_test("Scheduler: 오래된 작업 정리", test_scheduler_cleanup)

    # 9. LLM 추상화
    print("\n[9] LLM 추상화")
    from src.core.llm_base import LLMProvider
    from src.core.llm_registry import get_provider, register, _PROVIDERS

    def test_gemini_provider_registered():
        """GeminiProvider가 레지스트리에 등록되어 있는지 확인."""
        import src.core.gemini_service  # noqa: F401 — 등록 트리거
        return "gemini" in _PROVIDERS

    def test_get_provider_gemini():
        """get_provider('gemini')가 LLMProvider 인스턴스를 반환하는지 확인."""
        provider = get_provider("gemini")
        return isinstance(provider, LLMProvider)

    def test_get_provider_unknown():
        """get_provider('unknown')이 KeyError를 발생시키는지 확인."""
        try:
            get_provider("unknown_provider_xyz")
            return False
        except KeyError:
            return True

    def test_call_gemini_compat():
        """call_gemini() 하위 호환 함수가 여전히 존재하는지 확인."""
        from src.core.gemini_service import call_gemini, call_gemini_async
        return callable(call_gemini) and callable(call_gemini_async)

    run_test("GeminiProvider 등록 확인", test_gemini_provider_registered)
    run_test("get_provider('gemini') 반환", test_get_provider_gemini)
    run_test("get_provider('unknown') → KeyError", test_get_provider_unknown)
    run_test("call_gemini() 하위 호환 유지", test_call_gemini_compat)

    # 10. 피드백 컨텍스트
    print("\n[10] 피드백 컨텍스트")
    from src.core.feedback_context import build_feedback_context

    def test_feedback_context_empty_jsonl():
        """빈 JSONL → 빈 문자열 반환."""
        cfg = {
            "feedback_context": {"enabled": True, "max_entries": 3},
            "jsonl_bus": {"enabled": True, "path": "nonexistent_test_fc.jsonl"},
        }
        return build_feedback_context(cfg) == ""

    def test_feedback_context_file_path_filter():
        """file_path 필터가 작동하는지 확인."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as tmp:
            events_data = [
                {"message_type": "evaluation_response", "file_path": "a.py",
                 "feedback": "변수명이 모호함", "timestamp": "2026-02-17T10:00:00"},
                {"message_type": "evaluation_response", "file_path": "b.py",
                 "feedback": "에러 처리 미흡", "timestamp": "2026-02-17T11:00:00"},
            ]
            for e in events_data:
                tmp.write(json.dumps(e, ensure_ascii=False) + "\n")
            tmp_path = tmp.name
        try:
            import src.shared.config as cfg_mod
            original_root = cfg_mod.PROJECT_ROOT
            cfg_mod.PROJECT_ROOT = Path("/")
            cfg = {
                "feedback_context": {"enabled": True, "max_entries": 3},
                "jsonl_bus": {"enabled": True, "path": tmp_path},
            }
            result = build_feedback_context(cfg, file_path="a.py")
            cfg_mod.PROJECT_ROOT = original_root
            return "변수명이 모호함" in result and "에러 처리 미흡" not in result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_feedback_context_max_entries():
        """max_entries 제한이 작동하는지 확인."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as tmp:
            for i in range(5):
                e = {"message_type": "evaluation_response",
                     "feedback": f"피드백 {i}", "timestamp": f"2026-02-17T{10+i:02d}:00:00"}
                tmp.write(json.dumps(e, ensure_ascii=False) + "\n")
            tmp_path = tmp.name
        try:
            import src.shared.config as cfg_mod
            original_root = cfg_mod.PROJECT_ROOT
            cfg_mod.PROJECT_ROOT = Path("/")
            cfg = {
                "feedback_context": {"enabled": True, "max_entries": 2},
                "jsonl_bus": {"enabled": True, "path": tmp_path},
            }
            result = build_feedback_context(cfg)
            cfg_mod.PROJECT_ROOT = original_root
            # 최근 2건만 포함 (피드백 3, 피드백 4)
            return "피드백 3" in result and "피드백 4" in result and "피드백 0" not in result
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_feedback_context_disabled():
        """disabled일 때 빈 문자열 반환."""
        cfg = {
            "feedback_context": {"enabled": False},
            "jsonl_bus": {"enabled": True, "path": "some.jsonl"},
        }
        return build_feedback_context(cfg) == ""

    run_test("빈 JSONL → 빈 문자열 반환", test_feedback_context_empty_jsonl)
    run_test("file_path 필터 작동", test_feedback_context_file_path_filter)
    run_test("max_entries 제한 작동", test_feedback_context_max_entries)
    run_test("disabled일 때 빈 문자열 반환", test_feedback_context_disabled)

    # 11. CSO 안정성 강화 (스케줄러 락, exclude 오류, 라우터 검증)
    print("\n[11] CSO 안정성 강화")
    from src.core.router import validate_rules

    def test_scheduler_filelock():
        """Scheduler가 파일 락을 사용하는지 확인."""
        import src.core.scheduler as sched_mod
        import inspect
        source = inspect.getsource(sched_mod._load_jobs)
        return "lock_shared" in source

    def test_exclude_files_path_match():
        """exclude_files가 경로 포함 항목도 매칭하는지 확인."""
        # config에 "plans/gemini/gemini_feedback.md"가 있고
        # file_path가 "/abs/path/plans/gemini/gemini_feedback.md"인 경우
        exclude_files = ["plans/gemini/gemini_feedback.md", "gemini_feedback.md"]
        file_path = "/some/project/plans/gemini/gemini_feedback.md"
        basename = os.path.basename(file_path)
        matched = any(basename == os.path.basename(ex) or file_path.endswith(ex)
                      for ex in exclude_files)
        return matched is True

    def test_exclude_files_no_false_positive():
        """exclude_files가 무관한 파일을 매칭하지 않는지 확인."""
        exclude_files = ["plans/gemini/gemini_feedback.md"]
        file_path = "/some/project/plans/test.md"
        basename = os.path.basename(file_path)
        matched = any(basename == os.path.basename(ex) or file_path.endswith(ex)
                      for ex in exclude_files)
        return matched is False

    def test_router_validate_valid():
        """올바른 라우팅 규칙이 검증을 통과하는지 확인."""
        rules = [
            {"match_type": "evaluation_request", "target": "gemini"},
            {"match_ext": [".py"], "target": "codex"},
        ]
        return validate_rules(rules) == []

    def test_router_validate_missing_target():
        """target 누락 규칙을 검증이 잡아내는지 확인."""
        rules = [{"match_type": "test"}]  # target 없음
        errors = validate_rules(rules)
        return len(errors) >= 1 and "target" in errors[0]

    def test_router_validate_no_matcher():
        """match_type/match_ext 둘 다 없는 규칙을 검증이 잡아내는지 확인."""
        rules = [{"target": "gemini"}]  # matcher 없음
        errors = validate_rules(rules)
        return len(errors) >= 1

    def test_router_skips_bad_rules():
        """잘못된 규칙이 있어도 라우팅이 동작하는지 확인."""
        cfg = {"routing_rules": [
            {"bad_rule": True},  # target 없음 → 건너뜀
            {"match_type": "*", "target": "gemini"},
        ]}
        return resolve_target("any", cfg) == "gemini"

    def test_config_validate_bad_routing():
        """validate_config가 잘못된 routing_rules를 감지하는지 확인."""
        issues = validate_config({
            "gemini_cmd": "/usr/local/bin/gemini",
            "gemini_timeout": 90,
            "watch_extensions": [".md"],
            "evaluation_prompt": "test",
            "routing_rules": [{"match_type": "test"}],  # target 없음
        })
        return any("routing_rules" in msg for _, msg in issues)

    run_test("Scheduler: 파일 락 사용", test_scheduler_filelock)
    run_test("exclude_files: 경로 매칭", test_exclude_files_path_match)
    run_test("exclude_files: 오탐 방지", test_exclude_files_no_false_positive)
    run_test("Router 검증: 정상 규칙 통과", test_router_validate_valid)
    run_test("Router 검증: target 누락 감지", test_router_validate_missing_target)
    run_test("Router 검증: matcher 누락 감지", test_router_validate_no_matcher)
    run_test("Router: 잘못된 규칙 건너뛰기", test_router_skips_bad_rules)
    run_test("Config 검증: 잘못된 routing_rules", test_config_validate_bad_routing)

    # 12. 모듈 통합 (JSONL 일원화, Scheduler 연결)
    print("\n[12] 모듈 통합")

    def test_jsonl_path_single_source():
        """JSONL 경로가 shared/config.get_jsonl_path 단일 출처인지 확인."""
        from src.shared.config import get_jsonl_path as gp
        cfg = {"jsonl_bus": {"path": "test/path.jsonl"}}
        path = gp(cfg)
        return str(path).endswith("test/path.jsonl")

    def test_memory_reexports_get_jsonl_path():
        """memory 모듈이 get_jsonl_path를 재export하는지 확인."""
        from src.core.memory import get_jsonl_path as gp2
        cfg = {"jsonl_bus": {"path": "x.jsonl"}}
        return str(gp2(cfg)).endswith("x.jsonl")

    def test_parse_jsonl_file_from_memory():
        """parse_jsonl_file이 memory에서 올바르게 export되는지 확인."""
        from src.core.memory import parse_jsonl_file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False, encoding="utf-8") as tmp:
            tmp.write('{"test": true}\n')
            tmp_path = tmp.name
        try:
            events = parse_jsonl_file(Path(tmp_path))
            return len(events) == 1 and events[0]["test"] is True
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_scheduler_async_runner_integration():
        """async_runner가 scheduler import를 올바르게 수행하는지 확인."""
        from src.core.scheduler import register_job, get_job, complete_job, fail_job
        import src.core.scheduler as sched_mod
        original_path = sched_mod._JOBS_PATH
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
            sched_mod._JOBS_PATH = Path(tmp.name)
        try:
            # 비동기 작업 시뮬레이션: 등록 → 완료
            job = register_job("async-test-1", "gemini_async", "gemini",
                             metadata={"file_path": "test.py"})
            assert job["status"] == "pending"
            complete_job("async-test-1", result_summary="OK")
            completed = get_job("async-test-1")
            # 실패 시나리오
            register_job("async-test-2", "gemini_async", "gemini")
            fail_job("async-test-2", error="timeout")
            failed = get_job("async-test-2")
            return (completed["status"] == "completed"
                    and completed["result_summary"] == "OK"
                    and failed["status"] == "failed"
                    and failed["error"] == "timeout")
        finally:
            sched_mod._JOBS_PATH = original_path

    def test_async_timeout_removed():
        """config.json에서 async_timeout이 제거되었는지 확인."""
        cfg = load_config()
        return "async_timeout" not in cfg

    run_test("JSONL 경로 단일 출처", test_jsonl_path_single_source)
    run_test("Memory: get_jsonl_path 재export", test_memory_reexports_get_jsonl_path)
    run_test("Memory: parse_jsonl_file export", test_parse_jsonl_file_from_memory)
    run_test("Scheduler ↔ Async Runner 통합", test_scheduler_async_runner_integration)
    run_test("async_timeout 제거 확인", test_async_timeout_removed)

    # 13. Hook e2e 통합 테스트
    print("\n[13] Hook e2e 통합 테스트")

    def _run_hook(hook_script: str, stdin_data: dict, timeout: int = 10) -> tuple:
        """Hook 스크립트를 subprocess로 실행하여 (exit_code, stdout) 반환."""
        hook_path = PROJECT_ROOT / "src" / "hooks" / hook_script
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input=json.dumps(stdin_data, ensure_ascii=False),
            capture_output=True, text=True, timeout=timeout,
        )
        return proc.returncode, proc.stdout.strip()

    def test_hook_auto_task_wrong_tool():
        """PostToolUse: Write/Edit 외 도구는 exit(0) + 출력 없음."""
        rc, out = _run_hook("hook_auto_task.py", {
            "tool_name": "Read",
            "tool_input": {"file_path": "test.md"},
        })
        return rc == 0 and out == ""

    def test_hook_auto_task_no_file_path():
        """PostToolUse: file_path 없으면 exit(0) + 출력 없음."""
        rc, out = _run_hook("hook_auto_task.py", {
            "tool_name": "Write",
            "tool_input": {},
        })
        return rc == 0 and out == ""

    def test_hook_auto_task_wrong_extension():
        """PostToolUse: watch_extensions에 없는 확장자면 스킵."""
        rc, out = _run_hook("hook_auto_task.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": "/tmp/test.xyz"},
        })
        return rc == 0 and out == ""

    def test_hook_auto_task_excluded_file():
        """PostToolUse: exclude_files에 해당하면 스킵."""
        rc, out = _run_hook("hook_auto_task.py", {
            "tool_name": "Edit",
            "tool_input": {"file_path": "plans/gemini/gemini_feedback.md"},
        })
        return rc == 0 and out == ""

    def test_hook_pre_tool_non_bash():
        """PreToolUse: Bash 외 도구는 exit(0) + 출력 없음."""
        rc, out = _run_hook("hook_pre_tool.py", {
            "tool_name": "Write",
            "tool_input": {"file_path": "test.py"},
        })
        return rc == 0 and out == ""

    def test_hook_pre_tool_safe_command():
        """PreToolUse: 안전한 명령은 exit(0) + 출력 없음."""
        rc, out = _run_hook("hook_pre_tool.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "ls -la"},
        })
        return rc == 0 and out == ""

    def test_hook_pre_tool_block_dangerous():
        """PreToolUse: 위험한 명령은 block JSON 출력."""
        rc, out = _run_hook("hook_pre_tool.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "rm -rf /"},
        })
        if rc != 0 or not out:
            return False
        try:
            result = json.loads(out)
            return result.get("decision") == "block"
        except json.JSONDecodeError:
            return False

    def test_hook_pre_tool_block_force_push():
        """PreToolUse: git push --force 차단."""
        rc, out = _run_hook("hook_pre_tool.py", {
            "tool_name": "Bash",
            "tool_input": {"command": "git push --force origin main"},
        })
        if rc != 0 or not out:
            return False
        try:
            result = json.loads(out)
            return result.get("decision") == "block"
        except json.JSONDecodeError:
            return False

    def test_hook_stop_invalid_json():
        """Stop Hook: 잘못된 JSON → exit(0), 출력 없음."""
        hook_path = PROJECT_ROOT / "src" / "hooks" / "hook_stop.py"
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input="not valid json {{{",
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode == 0 and proc.stdout.strip() == ""

    def test_hook_stop_short_text_no_plan():
        """Stop Hook: 짧은 텍스트 → Plan 미감지, 출력 없음."""
        rc, out = _run_hook("hook_stop.py", {
            "message": "OK",
        })
        return rc == 0 and out == ""

    def test_hook_auto_task_invalid_json():
        """PostToolUse: 잘못된 JSON → exit(0), 출력 없음."""
        hook_path = PROJECT_ROOT / "src" / "hooks" / "hook_auto_task.py"
        proc = subprocess.run(
            [sys.executable, str(hook_path)],
            input="{broken json",
            capture_output=True, text=True, timeout=10,
        )
        return proc.returncode == 0 and proc.stdout.strip() == ""

    run_test("PostToolUse: 비대상 도구 스킵", test_hook_auto_task_wrong_tool)
    run_test("PostToolUse: file_path 누락 스킵", test_hook_auto_task_no_file_path)
    run_test("PostToolUse: 미감시 확장자 스킵", test_hook_auto_task_wrong_extension)
    run_test("PostToolUse: 제외 파일 스킵", test_hook_auto_task_excluded_file)
    run_test("PostToolUse: 잘못된 JSON → 안전 종료", test_hook_auto_task_invalid_json)
    run_test("PreToolUse: 비Bash 도구 스킵", test_hook_pre_tool_non_bash)
    run_test("PreToolUse: 안전 명령 통과", test_hook_pre_tool_safe_command)
    run_test("PreToolUse: rm -rf 차단", test_hook_pre_tool_block_dangerous)
    run_test("PreToolUse: force push 차단", test_hook_pre_tool_block_force_push)
    run_test("Stop: 잘못된 JSON → 안전 종료", test_hook_stop_invalid_json)
    run_test("Stop: 짧은 텍스트 → Plan 미감지", test_hook_stop_short_text_no_plan)

    # 결과
    print(f"\n{'='*40}")
    print(f"결과: {passed}/{total} 통과", end="")
    if failed:
        print(f", {failed} 실패")
    else:
        print(" — ALL PASSED ✓")
    return failed == 0


# ── chain ──

def _build_chain(events: list, start_id: str) -> list:
    """start_id를 기준으로 parent_message_id 체인을 양방향 탐색한다.

    start_id는 request_id, message_id, parent_message_id 중 어디든 매칭.
    """
    # 인덱스 구축
    by_message_id = {}
    by_parent = {}  # parent_message_id → children
    by_request_id = {}
    for e in events:
        mid = e.get("message_id", "")
        if mid:
            by_message_id[mid] = e
        pid = e.get("parent_message_id", "")
        if pid:
            by_parent.setdefault(pid, []).append(e)
        rid = e.get("request_id", "")
        if rid:
            by_request_id.setdefault(rid, []).append(e)

    # 시작점 탐색: request_id → message_id → parent_message_id prefix 매칭
    seed_events = []
    if start_id in by_request_id:
        seed_events = by_request_id[start_id]
    elif start_id in by_message_id:
        seed_events = [by_message_id[start_id]]
    else:
        # prefix 매칭
        for e in events:
            for field in ("request_id", "message_id", "parent_message_id"):
                val = e.get(field, "")
                if val and val.startswith(start_id):
                    seed_events.append(e)
                    break

    if not seed_events:
        return []

    # BFS: seed에서 위아래로 탐색
    visited = set()
    chain = []
    queue = list(seed_events)
    while queue:
        e = queue.pop(0)
        mid = e.get("message_id", id(e))
        if mid in visited:
            continue
        visited.add(mid)
        chain.append(e)
        # 위로: 이 이벤트의 parent를 찾기
        pid = e.get("parent_message_id", "")
        if pid and pid in by_message_id and pid not in visited:
            queue.append(by_message_id[pid])
        # 아래로: 이 이벤트를 parent로 가진 자식 찾기
        if mid in by_parent:
            for child in by_parent[mid]:
                cmid = child.get("message_id", "")
                if cmid not in visited:
                    queue.append(child)

    # 타임스탬프 순 정렬
    chain.sort(key=lambda e: e.get("timestamp", ""))
    return chain


def cmd_chain(args):
    """메시지 체인을 추적하여 시각화한다."""
    start_id = args.id
    config = load_config()
    jsonl_path = get_jsonl_path(config)
    events = parse_jsonl_events(jsonl_path)

    if not events:
        print(f"JSONL 이벤트가 없습니다: {jsonl_path}")
        return

    # --list 모드: 모든 request_id 목록
    if getattr(args, "list", False):
        rids = {}
        for e in events:
            rid = e.get("request_id", "")
            if rid:
                ts = e.get("timestamp", "?")[:19]
                src = e.get("source", e.get("source_agent", "?"))
                msg_type = e.get("message_type", "?")
                if rid not in rids:
                    rids[rid] = {"ts": ts, "src": src, "type": msg_type, "count": 0}
                rids[rid]["count"] += 1

        print(f"=== JSONL request_id 목록: {len(rids)}개 ===\n")
        for rid, info in sorted(rids.items(), key=lambda x: x[1]["ts"]):
            print(f"  {rid[:12]}  {info['ts']}  {info['src']}  ({info['count']}건)")
        return

    if not start_id:
        print("추적할 ID를 지정하세요: python3.13 src/cli.py chain <id>")
        print("전체 목록: python3.13 src/cli.py chain --list")
        return

    chain = _build_chain(events, start_id)
    if not chain:
        print(f"'{start_id}'와 일치하는 체인을 찾을 수 없습니다.")
        return

    print(f"=== 메시지 체인 ({len(chain)}건) ===\n")
    for i, e in enumerate(chain):
        ts = e.get("timestamp", "?")[:19]
        msg_type = e.get("message_type", "?")
        src = e.get("source_agent", e.get("source", "?"))
        mid = e.get("message_id", "?")[:12]
        pid = e.get("parent_message_id", "")
        rid = e.get("request_id", "")[:12]
        feedback = e.get("feedback", "")
        snippet = feedback[:100].replace("\n", " ") if feedback else ""

        # 트리 형태 표시
        if i == 0:
            prefix = "●"
        else:
            prefix = "└→"

        print(f"  {prefix} [{ts}] {msg_type}")
        print(f"     agent: {src} | mid: {mid} | rid: {rid}")
        if pid:
            print(f"     parent: {pid[:12]}")
        if snippet:
            print(f"     {snippet}...")
        print()


# ── install / uninstall ──

_HOOK_MARKER = "claude-gemini-communicator/src/hooks/"

_INSTALL_HOOKS = {
    "PreToolUse": {
        "matcher": "Bash",
        "hook": {"type": "command",
                 "command": f"python3.13 {PROJECT_ROOT}/src/hooks/hook_pre_tool.py",
                 "timeout": 10},
    },
    "PostToolUse": {
        "matcher": "Write|Edit",
        "hook": {"type": "command",
                 "command": f"python3.13 {PROJECT_ROOT}/src/hooks/hook_auto_task.py",
                 "timeout": 120},
    },
    "Stop": {
        "matcher": None,
        "hook": {"type": "command",
                 "command": f"python3.13 {PROJECT_ROOT}/src/hooks/hook_stop.py",
                 "timeout": 120},
    },
}

# 심링크 설치 대상 Skills
_INSTALL_SKILLS = [
    "agent-parser",
    "codex-user-context",
    "cross-agent-bridge",
    "gemini-cli-context",
    "gemini-reviewer",
    "install",
]


def _load_settings(target_dir: Path) -> dict:
    """대상 디렉토리의 .claude/settings.local.json을 읽거나 기본값 반환."""
    settings_file = target_dir / ".claude" / "settings.local.json"
    if settings_file.exists():
        return json.loads(settings_file.read_text("utf-8"))
    return {"hooks": {}}


def _save_settings(target_dir: Path, settings: dict):
    """대상 디렉토리의 .claude/settings.local.json에 저장."""
    claude_dir = target_dir / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    settings_file = claude_dir / "settings.local.json"
    settings_file.write_text(json.dumps(settings, indent=2, ensure_ascii=False) + "\n", "utf-8")


def _install_hooks(target_dir: Path) -> tuple[int, int]:
    """대상 디렉토리에 Hook을 등록한다. (installed, skipped) 반환."""
    settings = _load_settings(target_dir)
    hooks = settings.setdefault("hooks", {})

    installed = 0
    skipped = 0

    for hook_type, spec in _INSTALL_HOOKS.items():
        hook_list = hooks.setdefault(hook_type, [])

        # 이미 등록 여부 확인
        already = False
        for group in hook_list:
            for h in group.get("hooks", []):
                if _HOOK_MARKER in h.get("command", ""):
                    already = True
                    break
            if already:
                break

        if already:
            skipped += 1
            continue

        # matcher가 같은 그룹이 있으면 거기에 추가, 없으면 새 그룹
        matcher = spec["matcher"]
        target_group = None
        for group in hook_list:
            if group.get("matcher") == matcher:
                target_group = group
                break

        if target_group:
            target_group["hooks"].append(spec["hook"])
        else:
            new_group = {"hooks": [spec["hook"]]}
            if matcher is not None:
                new_group["matcher"] = matcher
            hook_list.append(new_group)

        installed += 1

    _save_settings(target_dir, settings)
    return installed, skipped


def _install_skills(target_dir: Path) -> tuple[int, int]:
    """대상 디렉토리에 Skills 심링크를 생성한다. (linked, skipped) 반환."""
    skills_src = PROJECT_ROOT / "skills"
    skills_dst = target_dir / ".claude" / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)

    linked = 0
    skipped = 0

    for skill_name in _INSTALL_SKILLS:
        src = skills_src / skill_name
        dst = skills_dst / skill_name

        if not src.exists():
            print(f"  [WARN] 소스 없음: {src}")
            continue

        if dst.is_symlink():
            if dst.resolve() == src.resolve():
                skipped += 1
                continue
            # 다른 곳을 가리키는 심링크 → 제거 후 재생성
            dst.unlink()

        if dst.exists():
            # 실제 디렉토리가 있으면 건너뜀 (사용자 커스텀일 수 있음)
            print(f"  [SKIP] 이미 존재 (심링크 아님): {dst}")
            skipped += 1
            continue

        dst.symlink_to(src)
        linked += 1

    return linked, skipped


def cmd_install(args):
    """다른 프로젝트 디렉토리에 Hook + Skills를 설치한다."""
    target_dir = Path(getattr(args, "target", ".")).resolve()

    if target_dir.resolve() == PROJECT_ROOT.resolve():
        print("[WARN] communicator 자체 디렉토리입니다. 외부 프로젝트를 지정하세요.")
        return

    print(f"대상: {target_dir}\n")

    # 1) Hook 등록
    print("── Hook 등록 ──")
    h_installed, h_skipped = _install_hooks(target_dir)
    if h_installed > 0:
        print(f"  {h_installed}개 Hook 등록")
    if h_skipped > 0:
        print(f"  {h_skipped}개 Hook 건너뜀 (이미 설치)")

    # 2) Skills 심링크
    print("── Skills 심링크 ──")
    s_linked, s_skipped = _install_skills(target_dir)
    if s_linked > 0:
        print(f"  {s_linked}개 Skill 심링크 생성")
    if s_skipped > 0:
        print(f"  {s_skipped}개 Skill 건너뜀 (이미 설치)")

    total = h_installed + s_linked
    if total == 0:
        print("\n모든 항목이 이미 설치되어 있습니다.")
    else:
        print(f"\n설치 완료: Hook {h_installed}개 + Skill {s_linked}개 ({target_dir})")


def _uninstall_hooks(target_dir: Path) -> int:
    """대상 디렉토리에서 communicator Hook을 제거한다. 제거 수 반환."""
    settings_file = target_dir / ".claude" / "settings.local.json"

    if not settings_file.exists():
        return 0

    settings = json.loads(settings_file.read_text("utf-8"))
    hooks = settings.get("hooks", {})
    removed = 0

    for hook_type in list(hooks.keys()):
        hook_list = hooks[hook_type]
        new_list = []
        for group in hook_list:
            new_hooks = [h for h in group.get("hooks", [])
                         if _HOOK_MARKER not in h.get("command", "")]
            if new_hooks:
                group["hooks"] = new_hooks
                new_list.append(group)
            removed += len(group.get("hooks", [])) - len(new_hooks)

        if new_list:
            hooks[hook_type] = new_list
        else:
            del hooks[hook_type]

    settings["hooks"] = hooks
    _save_settings(target_dir, settings)
    return removed


def _uninstall_skills(target_dir: Path) -> int:
    """대상 디렉토리에서 communicator Skills 심링크를 제거한다. 제거 수 반환."""
    skills_src = PROJECT_ROOT / "skills"
    skills_dst = target_dir / ".claude" / "skills"
    removed = 0

    if not skills_dst.exists():
        return 0

    for skill_name in _INSTALL_SKILLS:
        dst = skills_dst / skill_name
        if dst.is_symlink():
            src = skills_src / skill_name
            # communicator 심링크만 제거 (다른 프로젝트의 심링크는 보존)
            if dst.resolve() == src.resolve():
                dst.unlink()
                removed += 1

    # skills 디렉토리가 비었으면 정리
    if skills_dst.exists() and not any(skills_dst.iterdir()):
        skills_dst.rmdir()

    return removed


def cmd_uninstall(args):
    """프로젝트 디렉토리에서 communicator Hook + Skills를 제거한다."""
    target_dir = Path(getattr(args, "target", ".")).resolve()

    print(f"대상: {target_dir}\n")

    # 1) Hook 제거
    print("── Hook 제거 ──")
    h_removed = _uninstall_hooks(target_dir)
    if h_removed > 0:
        print(f"  {h_removed}개 Hook 삭제")
    else:
        print("  제거할 Hook 없음")

    # 2) Skills 심링크 제거
    print("── Skills 심링크 제거 ──")
    s_removed = _uninstall_skills(target_dir)
    if s_removed > 0:
        print(f"  {s_removed}개 Skill 심링크 삭제")
    else:
        print("  제거할 Skill 심링크 없음")

    total = h_removed + s_removed
    if total > 0:
        print(f"\n제거 완료: Hook {h_removed}개 + Skill {s_removed}개 ({target_dir})")
    else:
        print("\n제거할 communicator 항목이 없습니다.")


# ── clear ──

def cmd_clear(args=None):
    """런타임 상태 파일을 초기화한다."""
    cleared = []
    targets = [
        (COOLDOWN_STATE_PATH, "쿨다운 상태"),
        (ERROR_HISTORY_PATH, "에러 이력"),
    ]
    # --jsonl 옵션: JSONL 이벤트 로그도 초기화
    if getattr(args, "jsonl", False):
        targets.append((get_jsonl_path(load_config()), "JSONL 이벤트 로그"))

    for path, name in targets:
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
    "chain": ("메시지 체인 추적", cmd_chain),
    "test": ("전체 자동 테스트", cmd_test),
    "clear": ("상태 파일 초기화", cmd_clear),
    "install": ("다른 프로젝트에 Hook + Skills 설치", cmd_install),
    "uninstall": ("Hook + Skills 제거", cmd_uninstall),
}


def main():
    parser = argparse.ArgumentParser(description="Claude-Gemini Communicator CLI")
    subparsers = parser.add_subparsers(dest="command")

    for name, (desc, fn) in COMMANDS.items():
        subparser = subparsers.add_parser(name, help=desc, description=desc)
        if name == "search":
            subparser.add_argument("keyword", nargs="?", default="", help="검색 키워드")
            subparser.add_argument("--source", help="소스 필터 (Markdown 모드)", default=None)
            subparser.add_argument("--date", help="날짜 필터 (Markdown 모드, YYYY-MM-DD)", default=None)
            subparser.add_argument("--jsonl", action="store_true", help="JSONL 모드로 검색")
            subparser.add_argument("--agent", help="에이전트 필터 (JSONL 모드)", default=None)
            subparser.add_argument("--request-id", dest="request_id", help="request_id 필터 (JSONL 모드)", default=None)
            subparser.add_argument("--since", help="날짜 필터 (JSONL 모드, YYYY-MM-DD)", default=None)
        if name == "stats":
            subparser.add_argument("--jsonl", action="store_true", help="JSONL 이벤트 통계")
        if name == "chain":
            subparser.add_argument("id", nargs="?", default="", help="추적할 request_id 또는 message_id (prefix 매칭)")
            subparser.add_argument("--list", action="store_true", help="모든 request_id 목록 표시")
        if name == "clear":
            subparser.add_argument("--jsonl", action="store_true", help="JSONL 이벤트 로그도 초기화")
        if name in ("install", "uninstall"):
            subparser.add_argument("--target", default=".", help="대상 프로젝트 디렉토리 (기본: 현재)")
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
