#!/usr/bin/env python3
"""codex-tmux-orchestrator 통합 래퍼.

ready dispatch를 받아 Codex CLI를 worktree에서 실행하고 런타임을 추적한다.

Usage:
    python3 orchestrator.py launch --dispatch <dispatch.json> --packet <packet.json> [--model <model>] [--sandbox <mode>]
    python3 orchestrator.py status [--dispatch-id <id>] [--all]
    python3 orchestrator.py restart --dispatch-id <id>
    python3 orchestrator.py kill --dispatch-id <id>
    python3 orchestrator.py cleanup [--dry-run]
    python3 orchestrator.py capture --dispatch-id <id> [--lines <n>]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KST = timezone(timedelta(hours=9))

RUNTIME_DIR = ".codex/runtime"
LOG_DIR = ".codex/logs"
HEARTBEAT_DIR = ".codex/heartbeats"

DEFAULT_MODEL = "gpt-5.3-codex"
DEFAULT_SANDBOX = "workspace-write"
DEFAULT_SOCKET = "/tmp/ai-orch.sock"
SANDBOX_OPTIONS = {"read-only", "workspace-write", "danger-full-access"}

RUNTIME_VERSION = "0.1"

# 상태
VALID_STATUSES = {
    "planned", "launching", "running", "waiting_input",
    "completed", "failed", "stale", "killed", "abandoned", "archived",
}

VALID_TRANSITIONS = {
    "planned": {"launching"},
    "launching": {"running", "failed"},
    "running": {"waiting_input", "completed", "failed", "stale", "killed"},
    "waiting_input": {"running", "failed", "stale", "killed"},
    "stale": {"launching", "killed", "abandoned"},
    "failed": {"launching", "abandoned", "archived"},
    "completed": {"archived"},
    "killed": {"launching", "abandoned", "archived"},
    "abandoned": {"archived"},
    "archived": set(),
}

# Marker protocol
MARKER_START = "__CODEX_ORCH_START__"
MARKER_HEARTBEAT = "__CODEX_ORCH_HEARTBEAT__"
MARKER_DONE = "__CODEX_ORCH_DONE__"
MARKER_FAIL = "__CODEX_ORCH_FAIL__"

# Heartbeat timeout (seconds)
SHORT_TIMEOUT = 90
LONG_TIMEOUT = 300

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def _now_ts():
    return datetime.now(KST)


def _gen_id(prefix="RT"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _err(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def _warn(msg):
    print(f"[WARN] {msg}", file=sys.stderr)


def _info(msg):
    print(f"[INFO] {msg}", file=sys.stderr)


# ---------------------------------------------------------------------------
# tmux primitives (재사용)
# ---------------------------------------------------------------------------

def _tmux(args, socket=DEFAULT_SOCKET, check=True, timeout=10):
    cmd = ["tmux", "-S", socket] + args
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        if check and r.returncode != 0:
            return None, r.stderr.strip()
        return r.stdout.strip(), None
    except FileNotFoundError:
        return None, "tmux를 찾을 수 없음 — brew install tmux"
    except subprocess.TimeoutExpired:
        return None, f"tmux {' '.join(args[:2])} timeout ({timeout}s)"


def _session_exists(name, socket=DEFAULT_SOCKET):
    cmd = ["tmux", "-S", socket, "has-session", "-t", name]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _tmux_capture(name, lines=100, socket=DEFAULT_SOCKET):
    out, err = _tmux(
        ["capture-pane", "-t", name, "-p", "-S", f"-{lines}"],
        socket=socket, check=False
    )
    return out or "", err


# ---------------------------------------------------------------------------
# Session name convention
# ---------------------------------------------------------------------------

def _session_name(dispatch_id):
    """dispatch_id에서 deterministic session name 생성."""
    return f"codex-{dispatch_id}"


# ---------------------------------------------------------------------------
# Preflight: 12항목 사전 검증
# ---------------------------------------------------------------------------

def preflight(packet_path, dispatch_path):
    """launch 전 사전 검증. (errors: list, packet: dict, dispatch: dict) 반환."""
    errors = []

    # 1. packet 파일 존재
    if not os.path.isfile(packet_path):
        errors.append(f"packet 파일 없음: {packet_path}")
        return errors, None, None

    # 2. dispatch 파일 존재
    if not os.path.isfile(dispatch_path):
        errors.append(f"dispatch 파일 없음: {dispatch_path}")
        return errors, None, None

    packet = _load_json(packet_path)
    dispatch = _load_json(dispatch_path)

    # 3. dispatch status = ready
    status = dispatch.get("status", "")
    if status != "ready":
        errors.append(f"dispatch status가 'ready'가 아님: '{status}'")

    # 4. worktree 경로 존재
    wt = dispatch.get("worktree_path", "")
    if not wt:
        errors.append("dispatch에 worktree_path 없음")
    elif not os.path.isdir(wt):
        errors.append(f"worktree 디렉토리 없음: {wt}")
    else:
        # 5. git repo 확인
        git_dir = os.path.join(wt, ".git")
        if not os.path.exists(git_dir):
            errors.append(f"worktree가 git repo가 아님: {wt}")

        # 6. branch 일치 확인
        expected_branch = dispatch.get("branch", "")
        if expected_branch and os.path.isdir(wt):
            try:
                r = subprocess.run(
                    ["git", "-C", wt, "branch", "--show-current"],
                    capture_output=True, text=True, timeout=5
                )
                actual_branch = r.stdout.strip()
                if actual_branch != expected_branch:
                    errors.append(f"branch 불일치: expected='{expected_branch}', actual='{actual_branch}'")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                errors.append("git branch 확인 실패")

    # 7. packet revision 기록 (경고만)
    # (revision mismatch는 dispatch가 관리하므로 여기서는 기록)

    # 8. log path collision 확인
    dispatch_id = dispatch.get("dispatch_id", "unknown")
    # attempt 번호는 launch 시 동적 결정

    # 9. active runtime collision 확인
    rt_path = os.path.join(RUNTIME_DIR, f"{dispatch_id}.json")
    if os.path.isfile(rt_path):
        try:
            existing = _load_json(rt_path)
            existing_status = existing.get("runtime_status", "")
            if existing_status in ("planned", "launching", "running", "waiting_input"):
                errors.append(f"active runtime 존재: {rt_path} (status={existing_status})")
        except (json.JSONDecodeError, KeyError):
            _warn(f"runtime 파일 파싱 실패: {rt_path}")

    # 10. (lock conflict — dispatch 레벨에서 검증)

    # 11. codex CLI 존재 확인
    codex_check = subprocess.run(
        ["which", "codex"], capture_output=True, text=True
    )
    if codex_check.returncode != 0:
        errors.append("codex CLI를 찾을 수 없음 — npm install -g @openai/codex")

    # 12. session name collision
    sname = _session_name(dispatch_id)
    if _session_exists(sname):
        errors.append(f"tmux session 이름 충돌: {sname}")

    return errors, packet, dispatch


# ---------------------------------------------------------------------------
# launch: dispatch → tmux session → Codex CLI
# ---------------------------------------------------------------------------

def cmd_launch(args):
    errors, packet, dispatch = preflight(args.packet, args.dispatch)

    if errors:
        for e in errors:
            print(f"[PREFLIGHT FAIL] {e}", file=sys.stderr)
        sys.exit(1)

    dispatch_id = dispatch["dispatch_id"]
    task_id = dispatch.get("task_id", "unknown")
    wt = dispatch["worktree_path"]
    branch = dispatch.get("branch", "unknown")
    sname = _session_name(dispatch_id)
    socket = args.socket or DEFAULT_SOCKET
    model = args.model or DEFAULT_MODEL
    sandbox = args.sandbox or DEFAULT_SANDBOX

    if sandbox not in SANDBOX_OPTIONS:
        _err(f"잘못된 sandbox: {sandbox}")

    # attempt 번호 결정
    attempt = 1
    rt_path = os.path.join(RUNTIME_DIR, f"{dispatch_id}.json")
    if os.path.isfile(rt_path):
        try:
            existing = _load_json(rt_path)
            attempt = existing.get("attempt_number", 0) + 1
        except (json.JSONDecodeError, KeyError):
            pass

    log_path = os.path.join(LOG_DIR, f"{dispatch_id}-attempt-{attempt:03d}.log")
    hb_path = os.path.join(HEARTBEAT_DIR, f"{dispatch_id}.json")

    # 디렉토리 생성
    for d in (RUNTIME_DIR, LOG_DIR, HEARTBEAT_DIR):
        os.makedirs(d, exist_ok=True)

    # delegation message 조립 (간결 버전)
    goal = packet.get("goal", "")
    done_def = packet.get("done_definition", [])
    allowed = packet.get("allowed_paths", [])
    context_files = packet.get("context_files", [])

    prompt_parts = [
        f"## Mission\n{goal}",
        f"\n## Scope\n- allowed_paths: {', '.join(allowed)}",
    ]
    if context_files:
        ctx_lines = "\n".join(f"- {cf}" for cf in context_files)
        prompt_parts.append(f"\n## Context\n{ctx_lines}")
    if done_def:
        done_lines = "\n".join(f"{i}. {d}" for i, d in enumerate(done_def, 1))
        prompt_parts.append(f"\n## Done Definition\n{done_lines}")

    prompt = "\n".join(prompt_parts)

    # Codex 실행 커맨드
    codex_parts = ["codex", "exec", "-m", model, "--full-auto"]
    if sandbox != "read-only":
        codex_parts.extend(["--sandbox", sandbox])

    # start marker echo → codex exec → done/fail marker
    start_marker = f"{MARKER_START}:{dispatch_id}:{attempt}:{_now_iso()}"

    # 셸 커맨드 조립
    codex_cmd = " ".join(codex_parts) + f" '{prompt}'"
    shell_cmd = (
        f"cd {wt} && "
        f"echo '{start_marker}' && "
        f"{codex_cmd} 2>&1 | tee -a {os.path.abspath(log_path)} ; "
        f"echo '{MARKER_DONE}:{dispatch_id}:{attempt}:'$?':{_now_iso()}'"
    )

    # runtime record 생성 (planned)
    runtime = {
        "runtime_version": RUNTIME_VERSION,
        "task_id": task_id,
        "dispatch_id": dispatch_id,
        "packet_revision": packet.get("revision", 1),
        "branch": branch,
        "worktree_path": wt,
        "session_name": sname,
        "socket_name": socket,
        "launch_command": codex_cmd,
        "attempt_number": attempt,
        "runtime_status": "launching",
        "started_at": _now_iso(),
        "last_seen_at": _now_iso(),
        "completed_at": None,
        "exit_code": None,
        "exit_reason": None,
        "log_path": log_path,
        "heartbeat_path": hb_path,
        "marker_protocol_version": "v1",
        "restart_count": max(0, attempt - 1),
        "previous_attempts": [],
        "notes": "",
    }
    _save_json(rt_path, runtime)

    # heartbeat 초기화
    hb = {
        "dispatch_id": dispatch_id,
        "attempt_number": attempt,
        "session_name": sname,
        "last_seen_at": _now_iso(),
        "last_marker": start_marker,
        "pid_or_identity": f"tmux-{sname}",
        "status_hint": "launching",
    }
    _save_json(hb_path, hb)

    # tmux session 생성
    _, err = _tmux(["new-session", "-d", "-s", sname, "-x", "200", "-y", "50"], socket=socket)
    if err:
        runtime["runtime_status"] = "failed"
        runtime["exit_reason"] = f"tmux session 생성 실패: {err}"
        _save_json(rt_path, runtime)
        _err(f"tmux session 생성 실패: {err}")

    # 커맨드 전송
    _tmux(["send-keys", "-t", sname, shell_cmd, "Enter"], socket=socket)

    # 짧은 대기 후 세션 존재 확인
    time.sleep(1)
    if not _session_exists(sname, socket):
        runtime["runtime_status"] = "failed"
        runtime["exit_reason"] = "session이 즉시 종료됨"
        _save_json(rt_path, runtime)
        _err("session이 launch 직후 종료됨")

    # launching → running
    runtime["runtime_status"] = "running"
    runtime["last_seen_at"] = _now_iso()
    _save_json(rt_path, runtime)

    hb["status_hint"] = "running"
    hb["last_seen_at"] = _now_iso()
    _save_json(hb_path, hb)

    print(json.dumps({
        "result": "launched",
        "dispatch_id": dispatch_id,
        "session_name": sname,
        "socket": socket,
        "attempt": attempt,
        "log_path": log_path,
        "runtime_path": rt_path,
    }, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# status: 런타임 상태 조회
# ---------------------------------------------------------------------------

def _check_runtime_health(rt, socket=DEFAULT_SOCKET):
    """runtime record의 실제 건강 상태를 판정한다."""
    sname = rt.get("session_name", "")
    status = rt.get("runtime_status", "unknown")

    # 이미 종료 상태이면 그대로
    if status in ("completed", "failed", "killed", "abandoned", "archived"):
        return status, ""

    # tmux session 존재 확인
    alive = _session_exists(sname, socket) if sname else False

    if not alive:
        # 세션이 없으면 log에서 DONE/FAIL marker 확인
        log_path = rt.get("log_path", "")
        if log_path and os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            if MARKER_DONE in content:
                return "completed", "종료 marker 발견"
            if MARKER_FAIL in content:
                return "failed", "실패 marker 발견"
        return "failed", "tmux session 없음"

    # 세션 존재 + heartbeat timeout 체크
    hb_path = rt.get("heartbeat_path", "")
    if hb_path and os.path.isfile(hb_path):
        try:
            hb = _load_json(hb_path)
            last_str = hb.get("last_seen_at", "")
            if last_str:
                last_dt = datetime.fromisoformat(last_str)
                age = (_now_ts() - last_dt).total_seconds()
                if age > LONG_TIMEOUT:
                    return "stale", f"heartbeat {int(age)}s 초과"
        except (json.JSONDecodeError, ValueError):
            pass

    return status, "세션 활성"


def cmd_status(args):
    socket = args.socket or DEFAULT_SOCKET

    if args.dispatch_id:
        rt_path = os.path.join(RUNTIME_DIR, f"{args.dispatch_id}.json")
        if not os.path.isfile(rt_path):
            _err(f"runtime 없음: {rt_path}")
        rt = _load_json(rt_path)
        health, reason = _check_runtime_health(rt, socket)

        # 상태 갱신
        if health != rt.get("runtime_status"):
            rt["runtime_status"] = health
            rt["last_seen_at"] = _now_iso()
            _save_json(rt_path, rt)

        # 마지막 출력 캡처
        last_output = ""
        sname = rt.get("session_name", "")
        if _session_exists(sname, socket):
            captured, _ = _tmux_capture(sname, lines=5, socket=socket)
            last_output = captured

        print(json.dumps({
            "dispatch_id": args.dispatch_id,
            "task_id": rt.get("task_id", "?"),
            "runtime_status": health,
            "reason": reason,
            "session_name": sname,
            "attempt": rt.get("attempt_number", 0),
            "started_at": rt.get("started_at", "?"),
            "last_seen_at": rt.get("last_seen_at", "?"),
            "log_path": rt.get("log_path", ""),
            "last_output": last_output,
        }, indent=2, ensure_ascii=False))
        return

    # --all: 전체 runtime 목록
    if not os.path.isdir(RUNTIME_DIR):
        print("[]")
        return

    results = []
    for f in sorted(os.listdir(RUNTIME_DIR)):
        if not f.endswith(".json"):
            continue
        rt_path = os.path.join(RUNTIME_DIR, f)
        try:
            rt = _load_json(rt_path)
            health, reason = _check_runtime_health(rt, socket)
            results.append({
                "dispatch_id": rt.get("dispatch_id", "?"),
                "task_id": rt.get("task_id", "?"),
                "runtime_status": health,
                "session_name": rt.get("session_name", ""),
                "attempt": rt.get("attempt_number", 0),
                "started_at": rt.get("started_at", "?"),
            })
        except (json.JSONDecodeError, KeyError):
            results.append({"file": f, "error": "파싱 실패"})

    print(json.dumps(results, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# restart: failed/stale → 재시작
# ---------------------------------------------------------------------------

def cmd_restart(args):
    socket = args.socket or DEFAULT_SOCKET
    dispatch_id = args.dispatch_id
    rt_path = os.path.join(RUNTIME_DIR, f"{dispatch_id}.json")

    if not os.path.isfile(rt_path):
        _err(f"runtime 없음: {rt_path}")

    rt = _load_json(rt_path)
    status = rt.get("runtime_status", "")

    if status not in ("failed", "stale", "killed"):
        _err(f"restart 불가: 현재 status='{status}' (failed/stale/killed만 가능)")

    # 기존 세션 kill (남아있으면)
    sname = rt.get("session_name", "")
    if sname and _session_exists(sname, socket):
        _tmux(["kill-session", "-t", sname], socket=socket, check=False)

    # previous attempt 기록
    prev = rt.get("previous_attempts", [])
    prev.append({
        "attempt": rt.get("attempt_number", 0),
        "status": status,
        "started_at": rt.get("started_at", "?"),
        "ended_at": _now_iso(),
    })

    # 새 attempt
    new_attempt = rt.get("attempt_number", 0) + 1
    log_path = os.path.join(LOG_DIR, f"{dispatch_id}-attempt-{new_attempt:03d}.log")

    rt["attempt_number"] = new_attempt
    rt["runtime_status"] = "launching"
    rt["started_at"] = _now_iso()
    rt["last_seen_at"] = _now_iso()
    rt["completed_at"] = None
    rt["exit_code"] = None
    rt["exit_reason"] = None
    rt["log_path"] = log_path
    rt["restart_count"] = max(0, new_attempt - 1)
    rt["previous_attempts"] = prev
    _save_json(rt_path, rt)

    # 새 session 생성 + 커맨드 전송
    wt = rt.get("worktree_path", ".")
    codex_cmd = rt.get("launch_command", "")
    start_marker = f"{MARKER_START}:{dispatch_id}:{new_attempt}:{_now_iso()}"

    shell_cmd = (
        f"cd {wt} && "
        f"echo '{start_marker}' && "
        f"{codex_cmd} 2>&1 | tee -a {os.path.abspath(log_path)} ; "
        f"echo '{MARKER_DONE}:{dispatch_id}:{new_attempt}:'$?':{_now_iso()}'"
    )

    _, err = _tmux(["new-session", "-d", "-s", sname, "-x", "200", "-y", "50"], socket=socket)
    if err:
        rt["runtime_status"] = "failed"
        rt["exit_reason"] = f"restart tmux 실패: {err}"
        _save_json(rt_path, rt)
        _err(f"tmux session 재생성 실패: {err}")

    _tmux(["send-keys", "-t", sname, shell_cmd, "Enter"], socket=socket)

    time.sleep(1)
    rt["runtime_status"] = "running"
    rt["last_seen_at"] = _now_iso()
    _save_json(rt_path, rt)

    # heartbeat 갱신
    hb_path = rt.get("heartbeat_path", "")
    if hb_path:
        hb = {
            "dispatch_id": dispatch_id,
            "attempt_number": new_attempt,
            "session_name": sname,
            "last_seen_at": _now_iso(),
            "last_marker": start_marker,
            "pid_or_identity": f"tmux-{sname}",
            "status_hint": "running",
        }
        _save_json(hb_path, hb)

    print(json.dumps({
        "result": "restarted",
        "dispatch_id": dispatch_id,
        "attempt": new_attempt,
        "session_name": sname,
        "log_path": log_path,
    }, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# kill: 세션 종료
# ---------------------------------------------------------------------------

def cmd_kill(args):
    socket = args.socket or DEFAULT_SOCKET
    dispatch_id = args.dispatch_id
    rt_path = os.path.join(RUNTIME_DIR, f"{dispatch_id}.json")

    if not os.path.isfile(rt_path):
        _err(f"runtime 없음: {rt_path}")

    rt = _load_json(rt_path)
    sname = rt.get("session_name", "")

    if sname and _session_exists(sname, socket):
        _tmux(["kill-session", "-t", sname], socket=socket, check=False)
        _info(f"session '{sname}' killed")
    else:
        _warn(f"session '{sname}' 이미 없음")

    rt["runtime_status"] = "killed"
    rt["completed_at"] = _now_iso()
    rt["exit_reason"] = "operator kill"
    rt["last_seen_at"] = _now_iso()
    _save_json(rt_path, rt)

    print(json.dumps({
        "result": "killed",
        "dispatch_id": dispatch_id,
        "session_name": sname,
    }, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# cleanup: stale/orphan 정리
# ---------------------------------------------------------------------------

def cmd_cleanup(args):
    socket = args.socket or DEFAULT_SOCKET
    dry_run = args.dry_run

    if not os.path.isdir(RUNTIME_DIR):
        print("runtime 디렉토리 없음 — 정리할 대상 없음")
        return

    cleaned = []
    for f in sorted(os.listdir(RUNTIME_DIR)):
        if not f.endswith(".json"):
            continue
        rt_path = os.path.join(RUNTIME_DIR, f)
        try:
            rt = _load_json(rt_path)
        except (json.JSONDecodeError, KeyError):
            continue

        health, reason = _check_runtime_health(rt, socket)
        dispatch_id = rt.get("dispatch_id", "?")
        sname = rt.get("session_name", "")

        if health == "stale":
            if dry_run:
                cleaned.append({"dispatch_id": dispatch_id, "action": "would kill+mark stale", "reason": reason})
            else:
                if sname and _session_exists(sname, socket):
                    _tmux(["kill-session", "-t", sname], socket=socket, check=False)
                rt["runtime_status"] = "killed"
                rt["exit_reason"] = f"cleanup: {reason}"
                rt["completed_at"] = _now_iso()
                _save_json(rt_path, rt)
                cleaned.append({"dispatch_id": dispatch_id, "action": "killed", "reason": reason})

        elif health == "failed" and sname and _session_exists(sname, socket):
            # orphan: runtime은 failed인데 session이 살아있음
            if dry_run:
                cleaned.append({"dispatch_id": dispatch_id, "action": "would kill orphan session"})
            else:
                _tmux(["kill-session", "-t", sname], socket=socket, check=False)
                cleaned.append({"dispatch_id": dispatch_id, "action": "killed orphan session"})

    # tmux orphan session 검사 (registry에 없는 codex-* 세션)
    known_sessions = set()
    for f in os.listdir(RUNTIME_DIR):
        if f.endswith(".json"):
            try:
                rt = _load_json(os.path.join(RUNTIME_DIR, f))
                known_sessions.add(rt.get("session_name", ""))
            except (json.JSONDecodeError, KeyError):
                pass

    out, _ = _tmux(["list-sessions", "-F", "#{session_name}"], socket=socket, check=False)
    if out:
        for line in out.strip().split("\n"):
            sname = line.strip()
            if sname.startswith("codex-") and sname not in known_sessions:
                if dry_run:
                    cleaned.append({"session": sname, "action": "would kill unregistered session"})
                else:
                    _tmux(["kill-session", "-t", sname], socket=socket, check=False)
                    cleaned.append({"session": sname, "action": "killed unregistered session"})

    if cleaned:
        print(json.dumps(cleaned, indent=2, ensure_ascii=False))
    else:
        print("정리할 대상 없음")


# ---------------------------------------------------------------------------
# capture: 세션 출력 캡처
# ---------------------------------------------------------------------------

def cmd_capture(args):
    socket = args.socket or DEFAULT_SOCKET
    dispatch_id = args.dispatch_id
    rt_path = os.path.join(RUNTIME_DIR, f"{dispatch_id}.json")

    if not os.path.isfile(rt_path):
        _err(f"runtime 없음: {rt_path}")

    rt = _load_json(rt_path)
    sname = rt.get("session_name", "")

    if not sname or not _session_exists(sname, socket):
        # log fallback
        log_path = rt.get("log_path", "")
        if log_path and os.path.isfile(log_path):
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            tail = lines[-(args.lines or 100):]
            print("".join(tail))
        else:
            _err(f"session '{sname}' 없고 log도 없음")
        return

    captured, err = _tmux_capture(sname, lines=args.lines or 100, socket=socket)
    if err:
        _warn(f"캡처 오류: {err}")
    print(captured)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="codex-tmux-orchestrator 통합 래퍼"
    )
    parser.add_argument("--socket", default=DEFAULT_SOCKET, help=f"tmux socket (기본: {DEFAULT_SOCKET})")
    sub = parser.add_subparsers(dest="command")

    # launch
    p_launch = sub.add_parser("launch", help="dispatch → tmux session → Codex CLI 실행")
    p_launch.add_argument("--dispatch", required=True, help="dispatch JSON 경로")
    p_launch.add_argument("--packet", required=True, help="task-packet JSON 경로")
    p_launch.add_argument("--model", default=DEFAULT_MODEL, help=f"모델 (기본: {DEFAULT_MODEL})")
    p_launch.add_argument("--sandbox", default=DEFAULT_SANDBOX, help=f"샌드박스 (기본: {DEFAULT_SANDBOX})")

    # status
    p_status = sub.add_parser("status", help="런타임 상태 조회")
    p_status.add_argument("--dispatch-id", help="특정 dispatch ID")
    p_status.add_argument("--all", action="store_true", help="전체 목록")

    # restart
    p_restart = sub.add_parser("restart", help="failed/stale 세션 재시작")
    p_restart.add_argument("--dispatch-id", required=True, help="dispatch ID")

    # kill
    p_kill = sub.add_parser("kill", help="세션 종료")
    p_kill.add_argument("--dispatch-id", required=True, help="dispatch ID")

    # cleanup
    p_cleanup = sub.add_parser("cleanup", help="stale/orphan 정리")
    p_cleanup.add_argument("--dry-run", action="store_true", help="실제 정리 없이 대상만 표시")

    # capture
    p_capture = sub.add_parser("capture", help="세션 출력 캡처")
    p_capture.add_argument("--dispatch-id", required=True, help="dispatch ID")
    p_capture.add_argument("--lines", type=int, default=100, help="캡처 줄 수 (기본: 100)")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "launch": cmd_launch,
        "status": cmd_status,
        "restart": cmd_restart,
        "kill": cmd_kill,
        "cleanup": cmd_cleanup,
        "capture": cmd_capture,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
