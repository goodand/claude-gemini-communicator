#!/usr/bin/env python3
"""codex-worktree-dispatch 통합 래퍼.

task-packet을 받아 dispatch 상태를 생성·관리한다.
dispatch = mutable runtime 상태 (branch, worktree, status, locked_paths).

Usage:
    python3 dispatch_manager.py new --packet <packet.json> [--agent codex]
    python3 dispatch_manager.py validate <dispatch.json>
    python3 dispatch_manager.py show <dispatch.json>
    python3 dispatch_manager.py status [<dispatch_id>]
    python3 dispatch_manager.py list [--status running]
    python3 dispatch_manager.py check-overlap
    python3 dispatch_manager.py ready <dispatch_id>
    python3 dispatch_manager.py transition <dispatch_id> <new_status> [--reason "..."]
    python3 dispatch_manager.py merge-check <dispatch_id>
    python3 dispatch_manager.py cleanup [--dry-run]
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KST = timezone(timedelta(hours=9))

DISPATCH_DIR = ".codex/dispatch"
PACKET_DIR = ".codex/packets"
WORKTREE_DIR = ".worktrees"

REQUIRED_FIELDS = {
    "dispatch_version", "dispatch_id", "task_id", "packet_path",
    "branch", "worktree_path", "assigned_agent", "status",
    "locked_paths", "history", "created_at", "created_by", "updated_at",
}

OPTIONAL_FIELDS = {
    "owner_model", "status_reason", "depends_on_dispatch_ids",
    "merge_target", "retry_count", "max_retries",
    "tmux_session_hint", "launch_command_hint",
    "session_id", "heartbeat_path", "log_path",
}

# packet 필드를 dispatch에 중복 저장하지 않는다
FORBIDDEN_FIELDS = {
    "goal", "why", "done_definition", "required_checks",
    "deliverables", "constraints", "non_goals", "context_files", "priority",
}

VALID_STATUSES = {
    "queued", "ready", "running", "blocked",
    "failed", "complete", "merged", "abandoned",
}

# 유효 전이 테이블: from → {to, ...}
VALID_TRANSITIONS = {
    "queued":    {"ready", "blocked", "abandoned"},
    "ready":     {"running", "blocked"},
    "running":   {"complete", "failed", "abandoned"},
    "blocked":   {"ready"},
    "failed":    {"running"},
    "complete":  {"merged", "abandoned"},
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def _normalize_path(p):
    """경로 정규화: .. 제거, trailing / 통일."""
    p = os.path.normpath(p)
    if not p.endswith("/") and not os.path.splitext(p)[1]:
        p += "/"
    return p


def _slug_from_title(title):
    """title에서 branch/worktree용 slug 생성."""
    slug = re.sub(r"[^a-zA-Z0-9가-힣\s-]", "", title)
    slug = re.sub(r"\s+", "-", slug.strip()).lower()
    # 한국어 제거 (branch명에 부적합)
    slug = re.sub(r"[가-힣]+", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug[:40] if slug else "task"


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _repo_root():
    """git repo root를 우선 사용하고, 실패하면 현재 작업 디렉토리로 fallback."""
    rc, out = _run_git("rev-parse", "--show-toplevel")
    if rc == 0 and out:
        return out
    return os.getcwd()


def _resolve_repo_path(rel_path):
    """repo root 상대경로를 절대경로로 해석."""
    rel = str(rel_path).rstrip("/")
    return os.path.abspath(os.path.join(_repo_root(), rel))


def _find_dispatch(dispatch_id):
    """dispatch_id로 파일 경로 찾기."""
    if not os.path.isdir(DISPATCH_DIR):
        return None
    for fname in os.listdir(DISPATCH_DIR):
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(DISPATCH_DIR, fname)
        try:
            data = _load_json(fpath)
            if data.get("dispatch_id") == dispatch_id:
                return fpath
        except (json.JSONDecodeError, KeyError):
            continue
    return None


def _load_all_dispatches():
    """모든 dispatch 파일 로드."""
    dispatches = []
    if not os.path.isdir(DISPATCH_DIR):
        return dispatches
    for fname in sorted(os.listdir(DISPATCH_DIR)):
        if not fname.endswith(".json"):
            continue
        try:
            data = _load_json(os.path.join(DISPATCH_DIR, fname))
            dispatches.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return dispatches


def _next_dispatch_id():
    """다음 DISPATCH-#### ID 생성."""
    existing = _load_all_dispatches()
    max_num = 0
    for d in existing:
        did = d.get("dispatch_id", "")
        m = re.match(r"DISPATCH-(\d+)", did)
        if m:
            max_num = max(max_num, int(m.group(1)))
    return f"DISPATCH-{max_num + 1:04d}"


def _paths_overlap(paths_a, paths_b):
    """두 경로 집합의 prefix-level 겹침 검사."""
    overlaps = []
    norm_a = [_normalize_path(p) for p in paths_a]
    norm_b = [_normalize_path(p) for p in paths_b]
    for a in norm_a:
        for b in norm_b:
            if a.startswith(b) or b.startswith(a):
                overlaps.append((a, b))
    return overlaps


def _run_git(*args):
    """git 명령 실행. (returncode, stdout) 반환."""
    try:
        r = subprocess.run(
            ["git"] + list(args),
            capture_output=True, text=True, timeout=30
        )
        return r.returncode, r.stdout.strip()
    except FileNotFoundError:
        return 1, "git not found"
    except subprocess.TimeoutExpired:
        return 1, "git timeout"


# ---------------------------------------------------------------------------
# Core: new
# ---------------------------------------------------------------------------

def cmd_new(args):
    """packet에서 dispatch scaffold 생성 + worktree + branch 생성."""
    packet_path = args.packet
    if not os.path.isfile(packet_path):
        print(f"[ERROR] packet 파일 없음: {packet_path}", file=sys.stderr)
        sys.exit(1)

    packet = _load_json(packet_path)

    # packet 필수 필드 확인
    for field in ("task_id", "title", "allowed_paths"):
        if field not in packet:
            print(f"[ERROR] packet에 '{field}' 필드 없음", file=sys.stderr)
            sys.exit(1)

    task_id = packet["task_id"]
    title = packet.get("title", task_id)
    slug = _slug_from_title(title)
    agent = args.agent or "codex"

    # 중복 dispatch 확인
    for d in _load_all_dispatches():
        if d.get("task_id") == task_id:
            print(f"[ERROR] 이미 존재하는 dispatch: task_id={task_id} ({d['dispatch_id']})", file=sys.stderr)
            sys.exit(1)

    dispatch_id = _next_dispatch_id()
    branch = packet.get("branch_hint") or f"feat/codex-{slug}"
    wt_path = packet.get("worktree_hint") or f"{WORKTREE_DIR}/{slug}"
    locked_paths = list(packet.get("allowed_paths", []))
    now = _now_iso()

    # depends_on → depends_on_dispatch_ids 매핑
    depends_on_tasks = packet.get("depends_on", [])
    depends_on_dispatch_ids = []
    if depends_on_tasks:
        all_dispatches = _load_all_dispatches()
        for dep_task in depends_on_tasks:
            for d in all_dispatches:
                if d.get("task_id") == dep_task:
                    depends_on_dispatch_ids.append(d["dispatch_id"])
                    break

    # git worktree 생성
    rc, _ = _run_git("worktree", "add", "-b", branch, wt_path)
    if rc != 0:
        # branch가 이미 있으면 -b 없이 시도
        rc2, out2 = _run_git("worktree", "add", wt_path, branch)
        if rc2 != 0:
            print(f"[ERROR] git worktree 생성 실패: {out2}", file=sys.stderr)
            sys.exit(1)

    # worktree 성공 확인 후 dispatch 파일 생성 (orphan 방지)
    dispatch = {
        "dispatch_version": "0.1",
        "dispatch_id": dispatch_id,
        "task_id": task_id,
        "packet_path": packet_path,
        "branch": branch,
        "worktree_path": wt_path,
        "assigned_agent": agent,
        "status": "queued",
        "locked_paths": locked_paths,
        "history": [
            {"from": None, "to": "queued", "at": now, "by": "claude", "reason": "dispatch 생성"}
        ],
        "created_at": now,
        "created_by": "claude",
        "updated_at": now,
    }

    if depends_on_dispatch_ids:
        dispatch["depends_on_dispatch_ids"] = depends_on_dispatch_ids
    if packet.get("parallel_group"):
        dispatch["tmux_session_hint"] = packet["parallel_group"]

    dispatch_file = os.path.join(DISPATCH_DIR, f"{dispatch_id}.json")
    _save_json(dispatch_file, dispatch)
    print(f"[OK] dispatch 생성: {dispatch_file}")
    print(f"     dispatch_id: {dispatch_id}")
    print(f"     branch: {branch}")
    print(f"     worktree: {wt_path}")
    print(f"     locked_paths: {locked_paths}")


# ---------------------------------------------------------------------------
# Core: validate
# ---------------------------------------------------------------------------

def validate_dispatch(data):
    """Dispatch JSON 검증. (errors, warnings) 반환."""
    errors = []
    warnings = []

    # 1. 금지 필드 체크
    for f in FORBIDDEN_FIELDS:
        if f in data:
            errors.append(f"금지 필드 포함: '{f}' — packet 내용을 dispatch에 중복 저장하지 않는다")

    # 2. 필수 필드 체크
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        errors.append(f"필수 필드 누락: {sorted(missing)}")

    # 3. status 유효성
    if "status" in data and data["status"] not in VALID_STATUSES:
        errors.append(f"잘못된 status '{data['status']}' — 허용: {sorted(VALID_STATUSES)}")

    # 4. locked_paths 비어있지 않은지 + path traversal 방지
    if "locked_paths" in data:
        lp = data["locked_paths"]
        if not isinstance(lp, list) or len(lp) == 0:
            errors.append("locked_paths는 1개 이상 필요")
        elif isinstance(lp, list):
            for i, p in enumerate(lp):
                ps = str(p)
                if ".." in ps:
                    errors.append(f"locked_paths[{i}]: path traversal 금지 ('..') — '{p}'")
                if ps.startswith("/"):
                    errors.append(f"locked_paths[{i}]: 절대경로 금지 — repo root 상대경로 사용")
                resolved = _resolve_repo_path(_normalize_path(ps))
                if os.path.lexists(resolved) and os.path.islink(resolved):
                    errors.append(f"locked_paths[{i}]: symlink 금지 — 실제 경로를 사용할 것 — '{p}'")

            if "packet_path" in data and os.path.isfile(data["packet_path"]):
                try:
                    packet = _load_json(data["packet_path"])
                except json.JSONDecodeError:
                    warnings.append(f"packet_path JSON 파싱 실패: {data['packet_path']}")
                else:
                    allowed_raw = packet.get("allowed_paths", [])
                    if isinstance(allowed_raw, list):
                        allowed_paths = {_normalize_path(str(p)) for p in allowed_raw}
                        for i, p in enumerate(lp):
                            ps = _normalize_path(str(p))
                            if ps not in allowed_paths:
                                errors.append(
                                    f"locked_paths[{i}]: packet allowed_paths 범위 밖 — '{p}'"
                                )

    # 5. history 유효성
    if "history" in data:
        h = data["history"]
        if not isinstance(h, list) or len(h) == 0:
            errors.append("history는 최소 1개 이상")

    # 6. dispatch_id 형식
    if "dispatch_id" in data:
        did = data["dispatch_id"]
        if not isinstance(did, str) or not did.strip():
            errors.append("dispatch_id가 비어있다")

    # 7. task_id 존재
    if "task_id" in data:
        tid = data["task_id"]
        if not isinstance(tid, str) or not tid.strip():
            errors.append("task_id가 비어있다")

    # 8. packet_path 존재 확인
    if "packet_path" in data:
        pp = data["packet_path"]
        if pp and not os.path.isfile(pp):
            warnings.append(f"packet_path 파일 없음: {pp}")

    # 9. branch 비어있지 않은지
    if "branch" in data:
        if not str(data["branch"]).strip():
            errors.append("branch가 비어있다")

    # 10. worktree_path 비어있지 않은지
    if "worktree_path" in data:
        if not str(data["worktree_path"]).strip():
            errors.append("worktree_path가 비어있다")

    # 11. assigned_agent 비어있지 않은지
    if "assigned_agent" in data:
        if not str(data["assigned_agent"]).strip():
            errors.append("assigned_agent가 비어있다")

    # 12. retry_count 유효성
    if "retry_count" in data:
        rc = data["retry_count"]
        if not isinstance(rc, int) or rc < 0:
            errors.append("retry_count는 0 이상 정수")

    return errors, warnings


def cmd_validate(args):
    """dispatch JSON 검증."""
    data = _load_json(args.file)
    errors, warnings = validate_dispatch(data)

    name = os.path.basename(args.file)
    for w in warnings:
        print(f"[WARN] {name}: {w}")
    for e in errors:
        print(f"[ERROR] {name}: {e}")

    if errors:
        sys.exit(1)
    else:
        print(f"[OK] {name}: 검증 통과")


# ---------------------------------------------------------------------------
# Core: show
# ---------------------------------------------------------------------------

def cmd_show(args):
    """dispatch 요약 출력."""
    data = _load_json(args.file)
    print(f"Dispatch: {data.get('dispatch_id', '?')} → Task: {data.get('task_id', '?')}")
    print(f"Status: {data.get('status', '?')}")

    agent = data.get("assigned_agent", "")
    model = data.get("owner_model", "")
    agent_str = f"{agent}" + (f" ({model})" if model else "")
    print(f"Agent: {agent_str}")

    print(f"Branch: {data.get('branch', '?')}")
    print(f"Worktree: {data.get('worktree_path', '?')}")
    print(f"Locked paths: {data.get('locked_paths', [])}")

    deps = data.get("depends_on_dispatch_ids", [])
    if deps:
        print(f"Depends on: {deps}")

    reason = data.get("status_reason", "")
    if reason:
        print(f"Reason: {reason}")

    history = data.get("history", [])
    if history:
        last = history[-1]
        print(f"Last transition: {last.get('from')} → {last.get('to')} at {last.get('at', '?')}")

    created_by = str(data.get("created_by", "")).strip()
    created_at = data.get("created_at", "?")
    if created_by:
        print(f"Created: {created_at} by {created_by}")
    else:
        print(f"Created: {created_at}")


# ---------------------------------------------------------------------------
# Core: status / list
# ---------------------------------------------------------------------------

def cmd_status(args):
    """단일 dispatch 또는 전체 상태 출력."""
    if args.dispatch_id:
        fpath = _find_dispatch(args.dispatch_id)
        if not fpath:
            print(f"[ERROR] dispatch 없음: {args.dispatch_id}", file=sys.stderr)
            sys.exit(1)
        data = _load_json(fpath)
        print(f"{data['dispatch_id']}  {data['status']:10s}  {data.get('branch', '?'):30s}  {data.get('assigned_agent', '?')}")
    else:
        dispatches = _load_all_dispatches()
        if not dispatches:
            print("[INFO] 활성 dispatch 없음")
            return
        for d in dispatches:
            print(f"{d['dispatch_id']}  {d['status']:10s}  {d.get('branch', '?'):30s}  {d.get('assigned_agent', '?')}")


def cmd_list(args):
    """dispatch 목록 (필터 가능)."""
    dispatches = _load_all_dispatches()
    if args.status:
        dispatches = [d for d in dispatches if d.get("status") == args.status]
    if not dispatches:
        print("[INFO] 조건에 맞는 dispatch 없음")
        return
    for d in dispatches:
        print(f"{d['dispatch_id']}  {d['status']:10s}  task={d.get('task_id', '?')}  branch={d.get('branch', '?')}")


# ---------------------------------------------------------------------------
# Core: check-overlap
# ---------------------------------------------------------------------------

def cmd_check_overlap(args):
    """활성 dispatch 전체의 locked_paths 겹침 검사."""
    dispatches = _load_all_dispatches()
    active = [d for d in dispatches if d.get("status") in ("queued", "ready", "running", "blocked")]

    if len(active) < 2:
        print("[OK] 활성 dispatch 2개 미만 — 겹침 검사 불필요")
        return

    found = False
    for i in range(len(active)):
        for j in range(i + 1, len(active)):
            a, b = active[i], active[j]
            overlaps = _paths_overlap(
                a.get("locked_paths", []),
                b.get("locked_paths", [])
            )
            if overlaps:
                found = True
                print(f"[OVERLAP] {a['dispatch_id']} ↔ {b['dispatch_id']}")
                for pa, pb in overlaps:
                    print(f"  {pa}  ↔  {pb}")

    if not found:
        print("[OK] 활성 dispatch 간 경로 겹침 없음")
    else:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Core: ready
# ---------------------------------------------------------------------------

def cmd_ready(args):
    """의존성 완료 + 경로 점유 확인 → queued → ready 전이."""
    fpath = _find_dispatch(args.dispatch_id)
    if not fpath:
        print(f"[ERROR] dispatch 없음: {args.dispatch_id}", file=sys.stderr)
        sys.exit(1)

    data = _load_json(fpath)

    if data["status"] not in ("queued", "blocked"):
        print(f"[ERROR] ready 전이 불가: 현재 status={data['status']} (queued 또는 blocked만 가능)", file=sys.stderr)
        sys.exit(1)

    # 의존성 확인
    deps = data.get("depends_on_dispatch_ids", [])
    all_dispatches = _load_all_dispatches()
    for dep_id in deps:
        dep = next((d for d in all_dispatches if d.get("dispatch_id") == dep_id), None)
        if not dep:
            print(f"[ERROR] 의존성 dispatch 없음: {dep_id}", file=sys.stderr)
            sys.exit(1)
        if dep["status"] not in ("complete", "merged"):
            print(f"[BLOCKED] 의존성 미완료: {dep_id} (status={dep['status']})")
            # queued → blocked 전이
            if data["status"] == "queued":
                _do_transition(data, "blocked", f"의존성 {dep_id} 미완료")
                _save_json(fpath, data)
            sys.exit(1)

    # 경로 점유 확인
    active = [d for d in all_dispatches
              if d.get("dispatch_id") != data["dispatch_id"]
              and d.get("status") in ("ready", "running")]
    for other in active:
        overlaps = _paths_overlap(data.get("locked_paths", []), other.get("locked_paths", []))
        if overlaps:
            print(f"[BLOCKED] 경로 점유 충돌: {other['dispatch_id']}")
            for pa, pb in overlaps:
                print(f"  {pa}  ↔  {pb}")
            if data["status"] == "queued":
                _do_transition(data, "blocked", f"경로 충돌: {other['dispatch_id']}")
                _save_json(fpath, data)
            sys.exit(1)

    # 전이
    _do_transition(data, "ready", "의존성 완료, 경로 점유 없음")
    _save_json(fpath, data)
    print(f"[OK] {data['dispatch_id']}: queued → ready")


# ---------------------------------------------------------------------------
# Core: transition
# ---------------------------------------------------------------------------

def _do_transition(data, new_status, reason=""):
    """상태 전이 수행 (유효성 검증 포함)."""
    old_status = data["status"]

    valid_targets = VALID_TRANSITIONS.get(old_status, set())
    if new_status not in valid_targets:
        raise ValueError(
            f"잘못된 전이: {old_status} → {new_status} "
            f"(허용: {sorted(valid_targets)})"
        )

    # retry_count 검사를 상태 변경 전에 수행 — 초과 시 객체 오염 방지
    if old_status == "failed" and new_status == "running":
        next_retry = data.get("retry_count", 0) + 1
        max_r = data.get("max_retries", 3)
        if next_retry > max_r:
            raise ValueError(f"최대 재시도 횟수 초과: {next_retry} > {max_r}")

    now = _now_iso()
    data["status"] = new_status
    data["status_reason"] = reason
    data["updated_at"] = now
    data["history"].append({
        "from": old_status,
        "to": new_status,
        "at": now,
        "by": "claude",
        "reason": reason,
    })

    # retry_count 증가 (검사 통과 후)
    if old_status == "failed" and new_status == "running":
        data["retry_count"] = data.get("retry_count", 0) + 1


def cmd_transition(args):
    """수동 상태 전이."""
    fpath = _find_dispatch(args.dispatch_id)
    if not fpath:
        print(f"[ERROR] dispatch 없음: {args.dispatch_id}", file=sys.stderr)
        sys.exit(1)

    data = _load_json(fpath)
    old = data["status"]

    try:
        _do_transition(data, args.new_status, args.reason or "")
    except ValueError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    _save_json(fpath, data)
    print(f"[OK] {data['dispatch_id']}: {old} → {args.new_status}")


# ---------------------------------------------------------------------------
# Core: merge-check
# ---------------------------------------------------------------------------

def cmd_merge_check(args):
    """merge 가능 여부 판정."""
    fpath = _find_dispatch(args.dispatch_id)
    if not fpath:
        print(f"[ERROR] dispatch 없음: {args.dispatch_id}", file=sys.stderr)
        sys.exit(1)

    data = _load_json(fpath)
    checks = []
    all_pass = True

    # 1. status = complete
    if data["status"] == "complete":
        checks.append(("status=complete", True))
    else:
        checks.append(("status=complete", False, f"현재 status={data['status']}"))
        all_pass = False

    # 2. branch 존재
    branch = data.get("branch", "")
    rc, _ = _run_git("rev-parse", "--verify", branch)
    if rc == 0:
        checks.append(("branch 존재", True))
    else:
        checks.append(("branch 존재", False, f"branch '{branch}' 없음"))
        all_pass = False

    # 3. worktree 존재
    wt = data.get("worktree_path", "")
    if os.path.isdir(wt):
        checks.append(("worktree 존재", True))
    else:
        checks.append(("worktree 존재", False, f"worktree '{wt}' 없음"))
        all_pass = False

    # 4. worktree clean (uncommitted changes)
    if os.path.isdir(wt):
        rc, out = _run_git("-C", wt, "status", "--porcelain")
        if rc == 0 and not out:
            checks.append(("worktree clean", True))
        else:
            checks.append(("worktree clean", False, "uncommitted changes 있음"))
            all_pass = False

    # 5. merge conflict 예측
    merge_target = data.get("merge_target", "main")
    if branch:
        rc, _ = _run_git("merge-tree", merge_target, branch)
        # merge-tree는 충돌 시 exit 1
        if rc == 0:
            checks.append(("merge conflict 없음", True))
        else:
            checks.append(("merge conflict 없음", False, f"{merge_target}와 충돌 가능"))
            all_pass = False

    # 결과 출력
    for check in checks:
        name = check[0]
        passed = check[1]
        if passed:
            print(f"  [PASS] {name}")
        else:
            reason = check[2] if len(check) > 2 else ""
            print(f"  [FAIL] {name}: {reason}")

    if all_pass:
        print(f"\n[OK] {data['dispatch_id']}: merge 가능")
    else:
        print(f"\n[FAIL] {data['dispatch_id']}: merge 불가")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Core: cleanup
# ---------------------------------------------------------------------------

def cmd_cleanup(args):
    """orphan dispatch/worktree 탐지·정리."""
    dispatches = _load_all_dispatches()
    dry_run = args.dry_run
    cleaned = 0

    for d in dispatches:
        dispatch_id = d.get("dispatch_id", "?")
        wt = d.get("worktree_path", "")
        branch = d.get("branch", "")
        status = d.get("status", "")

        # 완료/병합/폐기된 dispatch의 worktree 정리
        if status in ("merged", "abandoned"):
            if wt and os.path.isdir(wt):
                if dry_run:
                    print(f"[DRY-RUN] worktree 삭제 대상: {wt} ({dispatch_id}, status={status})")
                else:
                    rc, out = _run_git("worktree", "remove", "--force", wt)
                    if rc == 0:
                        print(f"[CLEANED] worktree 삭제: {wt} ({dispatch_id})")
                        cleaned += 1
                    else:
                        print(f"[WARN] worktree 삭제 실패: {wt} — {out}")

        # orphan: dispatch 파일은 있지만 worktree가 없고, 활성 상태
        if status in ("queued", "ready", "running", "blocked"):
            if wt and not os.path.isdir(wt):
                print(f"[ORPHAN] dispatch={dispatch_id}, worktree 없음: {wt}")

    # orphan worktree: worktree는 있지만 dispatch가 없음
    if os.path.isdir(WORKTREE_DIR):
        dispatch_wts = {d.get("worktree_path", "") for d in dispatches}
        for entry in os.listdir(WORKTREE_DIR):
            wt_path = os.path.join(WORKTREE_DIR, entry)
            if os.path.isdir(wt_path) and wt_path not in dispatch_wts:
                if dry_run:
                    print(f"[DRY-RUN] orphan worktree: {wt_path} (dispatch 없음)")
                else:
                    rc, out = _run_git("worktree", "remove", "--force", wt_path)
                    if rc == 0:
                        print(f"[CLEANED] orphan worktree 삭제: {wt_path}")
                        cleaned += 1
                    else:
                        print(f"[WARN] orphan worktree 삭제 실패: {wt_path} — {out}")

    if cleaned > 0:
        print(f"\n[OK] {cleaned}개 정리 완료")
    elif not dry_run:
        print("[OK] 정리할 항목 없음")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="codex-worktree-dispatch 통합 래퍼",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    # new
    p_new = sub.add_parser("new", help="packet에서 dispatch + worktree 생성")
    p_new.add_argument("--packet", required=True, help="task-packet JSON 경로")
    p_new.add_argument("--agent", default="codex", help="배정 agent (기본: codex)")

    # validate
    p_val = sub.add_parser("validate", help="dispatch JSON 검증")
    p_val.add_argument("file", help="dispatch JSON 파일")

    # show
    p_show = sub.add_parser("show", help="dispatch 요약 출력")
    p_show.add_argument("file", help="dispatch JSON 파일")

    # status
    p_stat = sub.add_parser("status", help="dispatch 상태 조회")
    p_stat.add_argument("dispatch_id", nargs="?", help="dispatch ID (생략 시 전체)")

    # list
    p_list = sub.add_parser("list", help="dispatch 목록")
    p_list.add_argument("--status", help="status 필터")

    # check-overlap
    sub.add_parser("check-overlap", help="활성 dispatch 경로 겹침 검사")

    # ready
    p_ready = sub.add_parser("ready", help="queued → ready 전이 (의존성+경로 확인)")
    p_ready.add_argument("dispatch_id", help="dispatch ID")

    # transition
    p_trans = sub.add_parser("transition", help="수동 상태 전이")
    p_trans.add_argument("dispatch_id", help="dispatch ID")
    p_trans.add_argument("new_status", help="새 상태")
    p_trans.add_argument("--reason", default="", help="전이 사유")

    # merge-check
    p_merge = sub.add_parser("merge-check", help="merge 가능 여부 판정")
    p_merge.add_argument("dispatch_id", help="dispatch ID")

    # cleanup
    p_clean = sub.add_parser("cleanup", help="orphan dispatch/worktree 정리")
    p_clean.add_argument("--dry-run", action="store_true", help="실제 삭제 없이 대상만 출력")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "new": cmd_new,
        "validate": cmd_validate,
        "show": cmd_show,
        "status": cmd_status,
        "list": cmd_list,
        "check-overlap": cmd_check_overlap,
        "ready": cmd_ready,
        "transition": cmd_transition,
        "merge-check": cmd_merge_check,
        "cleanup": cmd_cleanup,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
