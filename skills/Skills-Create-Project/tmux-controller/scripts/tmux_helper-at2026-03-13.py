#!/usr/bin/env python3
"""tmux 세션 제어 헬퍼 — 생성/실행/캡처/대기/중지/재시작 통합 래퍼.

사용법:
    python3 tmux_helper.py create myapp
    python3 tmux_helper.py create myapp --socket /tmp/ai.sock
    python3 tmux_helper.py run myapp "python app.py"
    python3 tmux_helper.py capture myapp --lines 100
    python3 tmux_helper.py wait myapp --pattern "ready" --timeout 30
    python3 tmux_helper.py stop myapp
    python3 tmux_helper.py restart myapp "python app.py"
    python3 tmux_helper.py kill myapp
    python3 tmux_helper.py list
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time


# ---------------------------------------------------------------------------
# 글로벌 소켓 경로 (--socket 옵션으로 설정)
# ---------------------------------------------------------------------------
_SOCKET_PATH = None


def run_tmux(args, check=True):
    """tmux 명령을 실행하고 stdout을 반환한다."""
    cmd = ["tmux"]
    if _SOCKET_PATH:
        cmd += ["-S", _SOCKET_PATH]
    cmd += args
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=10,
        )
        if check and result.returncode != 0:
            print(f"[ERROR] tmux {' '.join(args[:3])}: {result.stderr.strip()}", file=sys.stderr)
        return result.stdout.strip()
    except FileNotFoundError:
        print("[ERROR] tmux를 찾을 수 없습니다. 'brew install tmux' 실행.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"[WARN] tmux {' '.join(args[:3])} timed out (10s)", file=sys.stderr)
        return ""


def session_exists(name):
    cmd = ["tmux"]
    if _SOCKET_PATH:
        cmd += ["-S", _SOCKET_PATH]
    cmd += ["has-session", "-t", name]
    result = subprocess.run(cmd, capture_output=True, timeout=5)
    return result.returncode == 0


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_create(args):
    if session_exists(args.session):
        print(f"[INFO] 세션 '{args.session}' 이미 존재합니다.")
        return
    run_tmux(["new-session", "-d", "-s", args.session])
    print(f"[OK] 세션 '{args.session}' 생성 완료.")


def cmd_run(args):
    if not session_exists(args.session):
        print(f"[INFO] 세션 '{args.session}' 없음 → 자동 생성")
        run_tmux(["new-session", "-d", "-s", args.session])
    run_tmux(["send-keys", "-t", args.session, args.command, "Enter"])
    print(f"[OK] '{args.command}' 실행 전송.")


def cmd_capture(args):
    if not session_exists(args.session):
        print(f"[ERROR] 세션 '{args.session}' 없음.", file=sys.stderr)
        sys.exit(1)
    output = run_tmux(["capture-pane", "-t", args.session, "-p", "-S", str(-args.lines)])
    print(output)


def cmd_wait(args):
    """출력에서 패턴이 나타날 때까지 대기. 체크리스트 §5.2 비동기 처리."""
    if not session_exists(args.session):
        print(f"[ERROR] 세션 '{args.session}' 없음.", file=sys.stderr)
        sys.exit(1)

    pattern = re.compile(args.pattern)
    deadline = time.time() + args.timeout
    interval = args.interval

    while time.time() < deadline:
        output = run_tmux(
            ["capture-pane", "-t", args.session, "-p", "-S", str(-args.lines)],
            check=False,
        )
        if pattern.search(output):
            print(f"[OK] 패턴 '{args.pattern}' 발견.", file=sys.stderr)
            # 매칭된 줄 출력
            for line in output.split("\n"):
                if pattern.search(line):
                    print(line)
            sys.exit(0)
        time.sleep(interval)

    print(f"[TIMEOUT] {args.timeout}초 내 패턴 '{args.pattern}' 미발견.", file=sys.stderr)
    # 마지막 캡처 출력
    output = run_tmux(["capture-pane", "-t", args.session, "-p", "-S", str(-args.lines)])
    print(output)
    sys.exit(1)


def cmd_stop(args):
    if not session_exists(args.session):
        print(f"[ERROR] 세션 '{args.session}' 없음.", file=sys.stderr)
        sys.exit(1)
    run_tmux(["send-keys", "-t", args.session, "C-c", ""])
    print(f"[OK] '{args.session}' Ctrl+C 전송.")


def cmd_restart(args):
    if not session_exists(args.session):
        print(f"[INFO] 세션 '{args.session}' 없음 → 자동 생성")
        run_tmux(["new-session", "-d", "-s", args.session])
    run_tmux(["send-keys", "-t", args.session, "C-c", ""])
    time.sleep(1)
    run_tmux(["send-keys", "-t", args.session, args.command, "Enter"])
    print(f"[OK] '{args.session}' 재시작: {args.command}")


def cmd_kill(args):
    if not session_exists(args.session):
        print(f"[INFO] 세션 '{args.session}' 이미 없습니다.")
        return
    run_tmux(["kill-session", "-t", args.session])
    print(f"[OK] 세션 '{args.session}' 종료.")


def cmd_list(_args):
    output = run_tmux(["list-sessions"], check=False)
    if output:
        print(output)
    else:
        print("[INFO] 활성 세션 없음.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="tmux 세션 제어 헬퍼",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--socket", "-S", dest="socket",
                        help="격리 소켓 경로 (예: /tmp/ai.sock)")
    sub = parser.add_subparsers(dest="action", required=True)

    p_create = sub.add_parser("create", help="세션 생성")
    p_create.add_argument("session", help="세션 이름")

    p_run = sub.add_parser("run", help="세션에서 명령 실행")
    p_run.add_argument("session", help="세션 이름")
    p_run.add_argument("command", help="실행할 명령")

    p_capture = sub.add_parser("capture", help="세션 출력 캡처")
    p_capture.add_argument("session", help="세션 이름")
    p_capture.add_argument("--lines", "-l", type=int, default=50,
                           help="캡처 줄 수 (기본: 50)")

    p_wait = sub.add_parser("wait", help="출력에서 패턴 대기")
    p_wait.add_argument("session", help="세션 이름")
    p_wait.add_argument("--pattern", "-p", required=True,
                        help="대기할 정규식 패턴")
    p_wait.add_argument("--timeout", "-t", type=int, default=30,
                        help="최대 대기 시간 초 (기본: 30)")
    p_wait.add_argument("--interval", type=float, default=2.0,
                        help="폴링 간격 초 (기본: 2.0)")
    p_wait.add_argument("--lines", "-l", type=int, default=50,
                        help="캡처 줄 수 (기본: 50)")

    p_stop = sub.add_parser("stop", help="Ctrl+C 전송")
    p_stop.add_argument("session", help="세션 이름")

    p_restart = sub.add_parser("restart", help="Ctrl+C → 재실행")
    p_restart.add_argument("session", help="세션 이름")
    p_restart.add_argument("command", help="재실행할 명령")

    p_kill = sub.add_parser("kill", help="세션 종료")
    p_kill.add_argument("session", help="세션 이름")

    sub.add_parser("list", help="세션 목록")

    args = parser.parse_args()

    # 글로벌 소켓 설정
    global _SOCKET_PATH
    _SOCKET_PATH = args.socket

    actions = {
        "create": cmd_create, "run": cmd_run, "capture": cmd_capture,
        "wait": cmd_wait, "stop": cmd_stop, "restart": cmd_restart,
        "kill": cmd_kill, "list": cmd_list,
    }
    actions[args.action](args)


if __name__ == "__main__":
    main()
