#!/usr/bin/env python3
"""Git Worktree 병렬 에이전트 환경 검증 — git 설치, worktree 건강, 브랜치 규칙, 파일 겹침 점검.

사용법:
    python3 worktree_verify.py                    # 전체 검증
    python3 worktree_verify.py --check-overlap    # 파일 겹침 감지
    python3 worktree_verify.py --cleanup-stale    # stale worktree 표시
    python3 worktree_verify.py --cleanup-stale --force  # 실제 정리
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

WORKTREE_DIR = ".worktrees"
STATUS_DIR = ".agent-status"
BRANCH_PREFIX = "feat/"

# 체크리스트 §1.1 — handoff JSON 필수 필드
REQUIRED_STATUS_FIELDS = {"task_id", "worktree", "branch", "status"}
VALID_STATUSES = {"in_progress", "complete", "failed"}


def run(cmd, timeout=15):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timeout"


def check_git_installed():
    """체크리스트 §1.1 — git 설치 + 버전."""
    rc, out, err = run(["git", "--version"])
    if rc == -1:
        return False, "git 미설치"
    if rc != 0:
        return False, f"git --version 실패: {err}"
    match = re.search(r"(\d+\.\d+\.\d+)", out)
    version = match.group(1) if match else out
    return True, f"git {version}"


def check_gitignore():
    """체크리스트 §1.2 — .gitignore 안전성."""
    gitignore = Path(".gitignore")
    if not gitignore.exists():
        return False, ".gitignore 없음"
    content = gitignore.read_text()
    missing = []
    for entry in [WORKTREE_DIR + "/", STATUS_DIR + "/"]:
        if entry not in content:
            missing.append(entry)
    if missing:
        return False, f".gitignore에 누락: {', '.join(missing)}"
    return True, ".gitignore OK"


def check_branch_naming():
    """체크리스트 §1.1 — 브랜치 naming 규칙 (feat/ 접두사)."""
    rc, out, _ = run(["git", "worktree", "list", "--porcelain"])
    if rc != 0 or not out:
        return True, "활성 worktree 없음 (검증 스킵)"

    violations = []
    current_wt = None
    for line in out.split("\n"):
        if line.startswith("worktree "):
            current_wt = line.split(" ", 1)[1]
        elif line.startswith("branch refs/heads/"):
            branch = line.replace("branch refs/heads/", "")
            # main worktree는 제외
            if current_wt and WORKTREE_DIR in current_wt:
                if not branch.startswith(BRANCH_PREFIX):
                    violations.append(f"{branch} ({current_wt})")

    if violations:
        return False, f"브랜치 규칙 위반 ('{BRANCH_PREFIX}' 접두사 필요): {', '.join(violations)}"
    return True, "브랜치 naming OK"


def check_status_files():
    """체크리스트 §2.4 / §4 — .agent-status JSON 유효성."""
    status_dir = Path(STATUS_DIR)
    if not status_dir.exists():
        return True, ".agent-status/ 없음 (정상 — 아직 작업 없음)"

    files = list(status_dir.glob("*.json"))
    if not files:
        return True, ".agent-status/ 비어있음"

    errors = []
    for f in files:
        try:
            data = json.loads(f.read_text())
        except json.JSONDecodeError:
            errors.append(f"{f.name}: JSON 파싱 실패")
            continue

        missing = REQUIRED_STATUS_FIELDS - set(data.keys())
        if missing:
            errors.append(f"{f.name}: 필수 필드 누락 {missing}")

        status = data.get("status", "")
        if status and status not in VALID_STATUSES:
            errors.append(f"{f.name}: 잘못된 status '{status}' (허용: {VALID_STATUSES})")

    if errors:
        return False, "상태 파일 오류: " + "; ".join(errors)
    return True, f"상태 파일 OK ({len(files)}개)"


def get_worktree_info():
    """현재 worktree 목록 파싱."""
    rc, out, _ = run(["git", "worktree", "list", "--porcelain"])
    if rc != 0 or not out:
        return []

    worktrees = []
    current = {}
    for line in out.split("\n"):
        if line.startswith("worktree "):
            if current:
                worktrees.append(current)
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch refs/heads/"):
            current["branch"] = line.replace("branch refs/heads/", "")
        elif line == "bare":
            current["bare"] = True
        elif line == "detached":
            current["detached"] = True
        elif line == "":
            pass
    if current:
        worktrees.append(current)
    return worktrees


def check_dirty_worktrees():
    """체크리스트 §1.2 — dirty worktree 감지."""
    worktrees = get_worktree_info()
    sub_wts = [wt for wt in worktrees if WORKTREE_DIR in wt.get("path", "")]
    if not sub_wts:
        return True, "sub worktree 없음"

    dirty = []
    for wt in sub_wts:
        rc, out, _ = run(["git", "-C", wt["path"], "status", "--porcelain"])
        if rc == 0 and out:
            dirty.append(f"{wt.get('branch', '?')} ({len(out.splitlines())} files)")

    if dirty:
        return False, f"dirty worktree: {'; '.join(dirty)}"
    return True, f"clean worktree ({len(sub_wts)}개)"


def check_file_overlap():
    """체크리스트 §1.2 — 여러 worktree에서 같은 파일 수정 시 충돌 경고."""
    worktrees = get_worktree_info()
    sub_wts = [wt for wt in worktrees if WORKTREE_DIR in wt.get("path", "")]
    if len(sub_wts) < 2:
        return True, "2개 미만 worktree — 겹침 불가"

    # 각 worktree에서 변경된 파일 수집
    changes = {}
    for wt in sub_wts:
        branch = wt.get("branch", "unknown")
        rc, out, _ = run(["git", "-C", wt["path"], "diff", "--name-only", "main"])
        if rc == 0 and out:
            for f in out.splitlines():
                changes.setdefault(f, []).append(branch)

    overlaps = {f: branches for f, branches in changes.items() if len(branches) > 1}
    if overlaps:
        details = [f"{f} → {', '.join(bs)}" for f, bs in overlaps.items()]
        return False, f"파일 겹침 감지: {'; '.join(details)}"
    return True, "파일 겹침 없음"


def check_stale_worktrees():
    """체크리스트 §1.2 — 상태 파일이 complete/failed인데 worktree가 남아있는 경우."""
    status_dir = Path(STATUS_DIR)
    if not status_dir.exists():
        return []

    stale = []
    for f in status_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, KeyError):
            continue
        if data.get("status") in ("complete", "failed"):
            wt_path = Path(data.get("worktree", ""))
            if wt_path.exists():
                stale.append({
                    "task_id": data.get("task_id", f.stem),
                    "worktree": str(wt_path),
                    "branch": data.get("branch", "?"),
                    "status": data.get("status"),
                })
    return stale


def cleanup_stale(force=False):
    """완료/실패 상태인 worktree 정리."""
    stale = check_stale_worktrees()
    if not stale:
        print("[OK] stale worktree 없음", file=sys.stderr)
        return 0

    for s in stale:
        label = f"{s['task_id']} ({s['branch']}, {s['status']})"
        if force:
            force_flag = ["--force"] if s["status"] == "failed" else []
            run(["git", "worktree", "remove", s["worktree"]] + force_flag)
            print(f"  x 제거: {label}", file=sys.stderr)
        else:
            print(f"  ! stale: {label} (--force로 정리)", file=sys.stderr)

    return len(stale)


def main():
    parser = argparse.ArgumentParser(description="Git Worktree 환경 검증")
    parser.add_argument("--check-overlap", action="store_true",
                        help="worktree 간 파일 겹침 검사")
    parser.add_argument("--cleanup-stale", action="store_true",
                        help="complete/failed worktree 표시")
    parser.add_argument("--force", action="store_true",
                        help="--cleanup-stale과 함께: 실제 제거")
    args = parser.parse_args()

    print("Git Worktree 환경 검증")
    print("=" * 40)

    errors = 0

    # 1. git 설치
    ok, msg = check_git_installed()
    print(f"{'  v' if ok else '  x'} git: {msg}")
    if not ok:
        print(f"\n결과: ERROR=1")
        sys.exit(1)

    # 2. .gitignore
    ok, msg = check_gitignore()
    print(f"{'  v' if ok else '  x'} gitignore: {msg}")
    if not ok:
        errors += 1

    # 3. 브랜치 naming
    ok, msg = check_branch_naming()
    print(f"{'  v' if ok else '  !'} naming: {msg}")

    # 4. 상태 파일 유효성
    ok, msg = check_status_files()
    print(f"{'  v' if ok else '  x'} status: {msg}")
    if not ok:
        errors += 1

    # 5. dirty worktree
    ok, msg = check_dirty_worktrees()
    print(f"{'  v' if ok else '  !'} dirty: {msg}")

    # 6. 파일 겹침 (선택)
    if args.check_overlap:
        ok, msg = check_file_overlap()
        print(f"{'  v' if ok else '  !'} overlap: {msg}")

    # 7. stale 정리
    if args.cleanup_stale:
        stale = check_stale_worktrees()
        print(f"\nstale worktree {'정리' if args.force else '미리보기'}:")
        if stale:
            count = cleanup_stale(args.force)
            print(f"  stale {count}개 {'정리됨' if args.force else '발견'}")
        else:
            print("  없음")

    print(f"\n{'=' * 40}")
    print(f"검증 {'PASSED' if errors == 0 else 'FAILED'}")
    sys.exit(errors)


if __name__ == "__main__":
    main()
