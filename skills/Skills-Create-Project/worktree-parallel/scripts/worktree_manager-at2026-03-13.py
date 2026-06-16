#!/usr/bin/env python3
"""Git Worktree 병렬 에이전트 관리자 — 생성/상태/검증/정리 통합 래퍼.

사용법:
    python3 worktree_manager.py spawn auth api ui
    python3 worktree_manager.py status
    python3 worktree_manager.py validate [name]
    python3 worktree_manager.py merge-check [name]
    python3 worktree_manager.py cleanup [--force] [--delete-branches]
    python3 worktree_manager.py list
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

WORKTREE_DIR = ".worktrees"
STATUS_DIR = ".agent-status"
REQUIRED_STATUS_FIELDS = {"task_id", "worktree", "branch", "status"}
VALID_STATUSES = {"in_progress", "complete", "failed"}


def run_git(args: list[str], check: bool = True) -> tuple:
    """git 명령 실행. (returncode, stdout) 튜플 반환."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True, text=True, timeout=30,
        )
        if check and result.returncode != 0:
            print(f"[ERROR] git {' '.join(args[:3])}: {result.stderr.strip()}", file=sys.stderr)
        return result.returncode, result.stdout.strip()
    except FileNotFoundError:
        print("[ERROR] git을 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"[WARN] git {' '.join(args[:3])} timed out", file=sys.stderr)
        return -1, ""


def ensure_gitignore():
    gitignore = Path(".gitignore")
    entries = [WORKTREE_DIR + "/", STATUS_DIR + "/"]
    if gitignore.exists():
        content = gitignore.read_text()
    else:
        content = ""
    added = []
    for entry in entries:
        if entry not in content:
            content += f"\n{entry}"
            added.append(entry)
    if added:
        gitignore.write_text(content)
        print(f"[OK] .gitignore에 추가: {', '.join(added)}")


def cmd_spawn(args):
    ensure_gitignore()
    Path(WORKTREE_DIR).mkdir(exist_ok=True)
    Path(STATUS_DIR).mkdir(exist_ok=True)

    _, base_branch = run_git(["branch", "--show-current"])
    base_branch = base_branch or "main"
    created = []
    failed = []
    for name in args.names:
        wt_path = f"{WORKTREE_DIR}/{name}"
        branch = f"feat/{name}"
        if Path(wt_path).exists():
            print(f"[SKIP] '{wt_path}' 이미 존재")
            continue
        rc, _ = run_git(["worktree", "add", wt_path, "-b", branch])
        if rc != 0:
            failed.append(name)
            continue
        # 상태 파일 초기화
        status_file = Path(STATUS_DIR) / f"{name}.json"
        status_file.write_text(json.dumps({
            "task_id": name,
            "worktree": wt_path,
            "branch": branch,
            "status": "in_progress",
            "assigned_to": "",
            "created_at": datetime.now().isoformat(),
        }, ensure_ascii=False, indent=2))
        created.append(name)

    if created:
        print(f"[OK] worktree 생성 완료: {', '.join(created)} (base: {base_branch})")
    if failed:
        print(f"[ERROR] worktree 생성 실패: {', '.join(failed)}", file=sys.stderr)
        sys.exit(1)
    if not created and not failed:
        print("[INFO] 새로 생성된 worktree 없음.")


def cmd_status(_args):
    status_dir = Path(STATUS_DIR)
    if not status_dir.exists():
        print("[INFO] 상태 디렉토리 없음.")
        return

    files = sorted(status_dir.glob("*.json"))
    if not files:
        print("[INFO] 상태 파일 없음.")
        return

    print(f"{'Task':<20} {'Status':<15} {'Branch':<25} {'Created'}")
    print("-" * 80)
    for f in files:
        try:
            data = json.loads(f.read_text())
            print(f"{data.get('task_id', '?'):<20} {data.get('status', '?'):<15} "
                  f"{data.get('branch', '?'):<25} {data.get('created_at', '?')[:16]}")
        except (json.JSONDecodeError, KeyError):
            print(f"{f.stem:<20} [파싱 실패]")


def cmd_list(_args):
    _, output = run_git(["worktree", "list"])
    if output:
        print(output)
    else:
        print("[INFO] worktree 없음.")


def cmd_validate(args):
    """체크리스트 §4 — handoff JSON + worktree 상태 검증."""
    status_dir = Path(STATUS_DIR)
    if not status_dir.exists():
        print("[INFO] 상태 디렉토리 없음.")
        return

    targets = [status_dir / f"{n}.json" for n in args.names] if args.names else list(status_dir.glob("*.json"))
    if not targets:
        print("[INFO] 검증할 상태 파일 없음.")
        return

    errors = 0
    for f in targets:
        if not f.exists():
            print(f"[ERROR] 파일 없음: {f}")
            errors += 1
            continue
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            print(f"[ERROR] {f.name}: JSON 파싱 실패")
            errors += 1
            continue

        # 필수 필드 체크
        missing = REQUIRED_STATUS_FIELDS - set(data.keys())
        if missing:
            print(f"[ERROR] {f.name}: 필수 필드 누락 {missing}")
            errors += 1

        # status 값 체크
        status = data.get("status", "")
        if status not in VALID_STATUSES:
            print(f"[ERROR] {f.name}: 잘못된 status '{status}'")
            errors += 1

        # worktree 경로 존재 체크
        wt_path = Path(data.get("worktree", ""))
        if data.get("status") == "in_progress" and not wt_path.exists():
            print(f"[WARN] {f.name}: in_progress인데 worktree 경로 없음: {wt_path}")

        # branch 존재 체크
        branch = data.get("branch", "")
        if branch:
            rc = subprocess.run(
                ["git", "rev-parse", "--verify", branch],
                capture_output=True, timeout=5,
            ).returncode
            if rc != 0 and data.get("status") == "in_progress":
                print(f"[WARN] {f.name}: branch '{branch}' 없음")

        if missing or status not in VALID_STATUSES:
            continue
        print(f"[OK] {f.name}: {data.get('task_id')} [{status}]")

    if errors:
        print(f"\n[FAIL] {errors}개 오류 발견")
        sys.exit(1)
    print(f"\n[OK] 전체 검증 통과 ({len(targets)}개)")


def cmd_merge_check(args):
    """체크리스트 §9 — merge 전 검증."""
    status_dir = Path(STATUS_DIR)
    if not status_dir.exists():
        print("[INFO] 상태 디렉토리 없음.")
        return

    targets = [status_dir / f"{n}.json" for n in args.names] if args.names else list(status_dir.glob("*.json"))
    if not targets:
        print("[INFO] 검증할 작업 없음.")
        return

    ready = []
    not_ready = []

    for f in targets:
        if not f.exists():
            not_ready.append((f.stem, "상태 파일 없음"))
            continue
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            not_ready.append((f.stem, "JSON 파싱 실패"))
            continue

        task_id = data.get("task_id", f.stem)
        branch = data.get("branch", "")
        status = data.get("status", "")
        reasons = []

        # 1. status가 complete여야 함
        if status != "complete":
            reasons.append(f"status={status} (complete 필요)")

        # 2. worktree가 clean이어야 함
        wt_path = data.get("worktree", "")
        if Path(wt_path).exists():
            rc, out, _ = run_git_raw(["-C", wt_path, "status", "--porcelain"])
            if rc == 0 and out:
                reasons.append(f"dirty ({len(out.splitlines())} uncommitted files)")

        # 3. branch가 main 대비 충돌 없는지 체크
        if branch:
            rc, out, _ = run_git_raw(["merge-tree", "--write-tree", "main", branch])
            if rc != 0:
                reasons.append("merge 충돌 예상")

        if reasons:
            not_ready.append((task_id, "; ".join(reasons)))
        else:
            ready.append(task_id)

    print("Merge 준비도 점검")
    print("=" * 40)
    if ready:
        print(f"\n  v READY ({len(ready)}개):")
        for t in ready:
            print(f"    - {t}")
    if not_ready:
        print(f"\n  x NOT READY ({len(not_ready)}개):")
        for t, reason in not_ready:
            print(f"    - {t}: {reason}")

    if not_ready:
        sys.exit(1)


def run_git_raw(args):
    """returncode, stdout, stderr 직접 반환."""
    try:
        result = subprocess.run(
            ["git"] + args, capture_output=True, text=True, timeout=30,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return -1, "", ""


def cmd_cleanup(args):
    wt_dir = Path(WORKTREE_DIR)
    cleaned = 0

    # 1. 실제 worktree 디렉토리 정리
    if wt_dir.exists():
        worktrees = [d for d in wt_dir.iterdir() if d.is_dir()]
        for wt in worktrees:
            name = wt.name
            force_flag = ["--force"] if args.force else []
            result = subprocess.run(
                ["git", "worktree", "remove", str(wt)] + force_flag,
                capture_output=True, text=True,
            )
            if result.returncode == 0:
                print(f"[OK] worktree 제거: {name}")
                if args.delete_branches:
                    branch = f"feat/{name}"
                    run_git(["branch", "-d", branch], check=False)
                    print(f"[OK] branch 삭제: {branch}")
                # 상태 파일 삭제
                status_file = Path(STATUS_DIR) / f"{name}.json"
                if status_file.exists():
                    status_file.unlink()
                cleaned += 1
            else:
                print(f"[WARN] '{name}' 제거 실패: {result.stderr.strip()}")

    # 2. 고아 상태 파일 정리 (worktree 없는데 상태 파일만 남은 경우)
    status_dir = Path(STATUS_DIR)
    if status_dir.exists():
        for f in status_dir.glob("*.json"):
            wt_path = wt_dir / f.stem
            if not wt_path.exists():
                f.unlink()
                print(f"[OK] 고아 상태 파일 제거: {f.name}")
                if args.delete_branches:
                    branch = f"feat/{f.stem}"
                    run_git(["branch", "-d", branch], check=False)
                cleaned += 1

    if cleaned == 0:
        print("[INFO] 정리할 worktree/상태 파일 없음.")
        return

    run_git(["worktree", "prune"])
    print(f"[OK] 정리 완료 ({cleaned}개).")


def main():
    parser = argparse.ArgumentParser(
        description="Git Worktree 병렬 에이전트 관리자",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="action", required=True)

    p_spawn = sub.add_parser("spawn", help="worktree 생성")
    p_spawn.add_argument("names", nargs="+", help="작업 이름들 (worktree/branch 자동 생성)")

    sub.add_parser("status", help="작업 상태 확인")

    p_validate = sub.add_parser("validate", help="handoff JSON 검증")
    p_validate.add_argument("names", nargs="*", help="검증할 작업 이름 (생략 시 전체)")

    p_merge = sub.add_parser("merge-check", help="merge 준비도 점검")
    p_merge.add_argument("names", nargs="*", help="점검할 작업 이름 (생략 시 전체)")

    sub.add_parser("list", help="git worktree list")

    p_cleanup = sub.add_parser("cleanup", help="worktree 정리")
    p_cleanup.add_argument("--force", action="store_true", help="uncommitted 변경 무시")
    p_cleanup.add_argument("--delete-branches", action="store_true", help="관련 브랜치도 삭제")

    args = parser.parse_args()
    actions = {
        "spawn": cmd_spawn, "status": cmd_status,
        "validate": cmd_validate, "merge-check": cmd_merge_check,
        "list": cmd_list, "cleanup": cmd_cleanup,
    }
    actions[args.action](args)


if __name__ == "__main__":
    main()
