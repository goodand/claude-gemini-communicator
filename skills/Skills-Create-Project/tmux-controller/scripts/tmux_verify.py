#!/usr/bin/env python3
"""tmux 환경 검증 — tmux 설치, 버전, 소켓 상태, 세션 건강 체크.

사용법:
    python3 tmux_verify.py                    # 전체 검증
    python3 tmux_verify.py --socket /tmp/ai.sock  # 특정 소켓 검증
    python3 tmux_verify.py --cleanup-stale    # stale 세션 정리 (dry-run)
    python3 tmux_verify.py --cleanup-stale --force  # 실제 정리
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime


def run(cmd, timeout=10):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timeout"


def check_tmux_installed():
    """tmux 설치 여부 + 버전 확인."""
    rc, out, err = run(["tmux", "-V"])
    if rc == -1:
        return False, "tmux 미설치. 'brew install tmux' 또는 'apt install tmux' 실행 필요"
    if rc != 0:
        return False, f"tmux -V 실패: {err}"
    # 버전 파싱 (예: "tmux 3.4")
    match = re.search(r"(\d+\.\d+)", out)
    version = match.group(1) if match else out
    min_version = 2.6
    try:
        if float(version) < min_version:
            return False, f"tmux {version} — 최소 {min_version} 이상 필요"
    except ValueError:
        pass
    return True, f"tmux {version}"


def check_socket(socket_path=None):
    """tmux 소켓 상태 확인."""
    if socket_path:
        if not os.path.exists(socket_path):
            return False, f"소켓 없음: {socket_path}"
        rc, out, _ = run(["tmux", "-S", socket_path, "list-sessions"])
        if rc == 0:
            count = len(out.strip().split("\n")) if out.strip() else 0
            return True, f"소켓 활성 ({count}개 세션): {socket_path}"
        return False, f"소켓 존재하지만 서버 응답 없음: {socket_path}"

    # 기본 소켓
    rc, out, _ = run(["tmux", "list-sessions"])
    if rc == 0:
        count = len(out.strip().split("\n")) if out.strip() else 0
        return True, f"기본 소켓 활성 ({count}개 세션)"
    return True, "기본 소켓: 활성 세션 없음 (정상)"


def check_sessions(socket_path=None):
    """세션 목록 + 건강 상태 확인."""
    cmd = ["tmux"]
    if socket_path:
        cmd += ["-S", socket_path]
    cmd += ["list-sessions", "-F", "#{session_name}\t#{session_windows}\t#{session_created}\t#{session_attached}"]

    rc, out, _ = run(cmd)
    if rc != 0 or not out.strip():
        return []

    sessions = []
    now = datetime.now().timestamp()
    for line in out.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        name, windows, created_ts, attached = parts
        try:
            age_hours = (now - float(created_ts)) / 3600
        except ValueError:
            age_hours = 0

        status = "active"
        if attached == "0" and age_hours > 24:
            status = "stale"
        elif attached == "0":
            status = "detached"

        sessions.append({
            "name": name,
            "windows": windows,
            "age_hours": round(age_hours, 1),
            "attached": attached != "0",
            "status": status,
        })
    return sessions


def cleanup_stale(socket_path=None, force=False):
    """24시간 이상 미접속 세션 정리."""
    sessions = check_sessions(socket_path)
    stale = [s for s in sessions if s["status"] == "stale"]

    if not stale:
        print("[OK] stale 세션 없음", file=sys.stderr)
        return 0

    for s in stale:
        label = f"{s['name']} ({s['age_hours']}h, {s['windows']}창)"
        if force:
            cmd = ["tmux"]
            if socket_path:
                cmd += ["-S", socket_path]
            cmd += ["kill-session", "-t", s["name"]]
            run(cmd)
            print(f"  x 종료: {label}", file=sys.stderr)
        else:
            print(f"  ! stale: {label} (--force로 정리)", file=sys.stderr)

    return len(stale)


def main():
    parser = argparse.ArgumentParser(description="tmux 환경 검증")
    parser.add_argument("--socket", "-S", help="검증할 tmux 소켓 경로")
    parser.add_argument("--cleanup-stale", action="store_true",
                        help="24시간 이상 미접속 stale 세션 표시")
    parser.add_argument("--force", action="store_true",
                        help="--cleanup-stale과 함께: 실제로 종료")
    args = parser.parse_args()

    print("tmux 환경 검증")
    print("=" * 40)

    errors = 0

    # 1. 설치 확인
    ok, msg = check_tmux_installed()
    print(f"{'  v' if ok else '  x'} 설치: {msg}")
    if not ok:
        errors += 1
        print(f"\n결과: ERROR={errors}")
        sys.exit(1)

    # 2. 소켓 확인
    ok, msg = check_socket(args.socket)
    print(f"{'  v' if ok else '  !'} 소켓: {msg}")

    # 3. 세션 건강 체크
    sessions = check_sessions(args.socket)
    if sessions:
        print(f"\n세션 목록 ({len(sessions)}개):")
        for s in sessions:
            icon = {"active": "v", "detached": "-", "stale": "!"}[s["status"]]
            att = "접속중" if s["attached"] else "미접속"
            print(f"  {icon} {s['name']}: {s['windows']}창, {s['age_hours']}h, {att} [{s['status']}]")
    else:
        print("\n  활성 세션 없음")

    # 4. stale 정리
    if args.cleanup_stale:
        print(f"\nstale 세션 정리 {'(실행)' if args.force else '(미리보기)'}:")
        stale_count = cleanup_stale(args.socket, args.force)
        if stale_count:
            print(f"  stale {stale_count}개 {'정리됨' if args.force else '발견'}")

    print(f"\n{'=' * 40}")
    print(f"검증 {'PASSED' if errors == 0 else 'FAILED'}")
    sys.exit(errors)


if __name__ == "__main__":
    main()
