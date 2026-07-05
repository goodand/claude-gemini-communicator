#!/usr/bin/env python3
"""Skill resolver — SKILL_DISCOVERY.md의 발견 규칙 구현.

여러 루트(레포 skills/, external/, ~/.claude, ~/.codex, ~/skills, /control,
/agent, <project>/control)를 우선순위대로 스캔해 skill을 찾는다. 같은 이름이
여러 루트에 있으면 우선순위가 높은(먼저 스캔된) 것을 채택한다.

stdlib만 사용. Claude Code / Codex CLI / Gemini CLI 공용.

사용:
    python3 resolve_skill.py list [--json]
    python3 resolve_skill.py find <name>
    python3 resolve_skill.py path <name>
    python3 resolve_skill.py conflicts [--json]

환경변수:
    SKILLS_ROOT             최우선 루트(들), 콜론 구분
    SKILL_DISCOVERY_EXTRA   추가 루트(들), 콜론 구분 (뒤에 append)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

HOME = Path.home()
REPO = Path(__file__).resolve().parent.parent  # <repo>/skills/resolve_skill.py → <repo>

# 프로젝트들이 모여있는 베이스 (이 PC 관례).
# $SKILL_PROJECTS_BASE로 오버라이드 가능.
PROJECTS_BASE = Path(os.environ.get(
    "SKILL_PROJECTS_BASE",
    "/Users/jaehyuntak/Desktop/Project_____현재_진행중인"))

# 알려진 프로젝트 (skills/ + control/ 관례를 따르는 곳).
# 각 프로젝트는 <proj>/skills, <proj>/.claude/skills, <proj>/control을 스캔한다.
KNOWN_PROJECTS = ["my-image-parser", "narrative-ai", "vscode-markdown-review-surface",
                  "my-second-identity"]


def _project_roots():
    roots = []
    for proj in KNOWN_PROJECTS:
        base = PROJECTS_BASE / proj
        roots.append((f"proj:{proj}:skills", base / "skills", 1))
        roots.append((f"proj:{proj}:claude", base / ".claude" / "skills", 2))
        roots.append((f"proj:{proj}:control", base / "control", 3))
    return roots


# 우선순위 순 발견 루트. (label, path, recursive_depth)
# depth=1: 루트 바로 아래 각 디렉토리가 skill 후보
# depth=2: 루트/<bucket>/<skill> 형태
BASE_ROOTS = [
    ("repo-skills", REPO / "skills", 1),
    ("repo-skills-createproject", REPO / "skills" / "Skills-Create-Project", 1),
    ("repo-external", REPO / "skills" / "external", 2),
    ("claude-user", HOME / ".claude" / "skills", 1),
    ("codex-user", HOME / ".codex" / "skills", 1),
    ("home-skills", HOME / "skills", 1),
    ("control", Path("/Users/jaehyuntak/control"), 3),
    ("agent", Path("/Users/jaehyuntak/agent"), 3),
] + _project_roots()


def _extra_roots():
    roots = []
    for env, prepend in (("SKILLS_ROOT", True), ("SKILL_DISCOVERY_EXTRA", False)):
        val = os.environ.get(env, "")
        for p in filter(None, (x.strip() for x in val.split(":"))):
            roots.append(("env:" + env, Path(p), 3, prepend))
    return roots


def _iter_skill_dirs(root: Path, max_depth: int):
    """root 아래에서 SKILL.md를 가진 디렉토리를 max_depth까지 찾는다."""
    if not root.exists():
        return
    root_str = str(root)
    for dirpath, dirnames, filenames in os.walk(root_str, followlinks=True):
        rel = os.path.relpath(dirpath, root_str)
        depth = 0 if rel == "." else len(rel.split(os.sep))
        if depth > max_depth:
            dirnames[:] = []
            continue
        # _stale: 구버전 스냅샷 격리 디렉토리는 발견에서 제외
        if os.sep + "_stale" + os.sep in dirpath + os.sep:
            dirnames[:] = []
            continue
        if "SKILL.md" in filenames:
            yield Path(dirpath)
            dirnames[:] = []  # skill 내부는 더 내려가지 않음


def discover():
    """우선순위 순으로 skill을 수집. 반환: (winners, all_hits).

    winners: name -> record (우선순위 승자)
    all_hits: 모든 발견(중복 포함) 리스트
    """
    roots = []
    for lbl, p, d, prepend in _extra_roots():
        (roots.insert(0, (lbl, p, d)) if prepend else roots.append((lbl, p, d)))
    roots = [r for r in roots] + [(l, p, d) for (l, p, d) in BASE_ROOTS]

    winners: dict[str, dict] = {}
    all_hits: list[dict] = []
    seen_real = set()
    for label, root, depth in roots:
        for sdir in _iter_skill_dirs(root, depth):
            real = str(sdir.resolve())
            name = sdir.name
            rec = {"name": name, "path": str(sdir), "real": real,
                   "root": label, "skill_md": str(sdir / "SKILL.md")}
            all_hits.append(rec)
            # 같은 실제 경로(심링크)면 중복으로 세지 않음
            if real in seen_real:
                continue
            seen_real.add(real)
            if name not in winners:
                winners[name] = rec
    return winners, all_hits


def cmd_list(args):
    winners, _ = discover()
    if args.json:
        print(json.dumps(list(winners.values()), ensure_ascii=False, indent=2))
        return 0
    w = max((len(n) for n in winners), default=4)
    print(f"{'name':<{w}}  root")
    for name in sorted(winners):
        print(f"{name:<{w}}  {winners[name]['root']}")
    print(f"\ntotal: {len(winners)} skills")
    return 0


def cmd_find(args):
    winners, _ = discover()
    rec = winners.get(args.name)
    if not rec:
        print(f"not found: {args.name}", file=sys.stderr)
        return 1
    print(json.dumps(rec, ensure_ascii=False, indent=2))
    return 0


def cmd_path(args):
    winners, _ = discover()
    rec = winners.get(args.name)
    if not rec:
        print(f"not found: {args.name}", file=sys.stderr)
        return 1
    print(rec["skill_md"])
    return 0


def cmd_conflicts(args):
    _, all_hits = discover()
    by_name: dict[str, list] = {}
    for h in all_hits:
        by_name.setdefault(h["name"], [])
        if h["real"] not in {x["real"] for x in by_name[h["name"]]}:
            by_name[h["name"]].append(h)
    conflicts = {n: v for n, v in by_name.items() if len(v) > 1}
    if args.json:
        print(json.dumps(conflicts, ensure_ascii=False, indent=2))
        return 0
    if not conflicts:
        print("no name conflicts (distinct real paths per name)")
        return 0
    for name, hits in sorted(conflicts.items()):
        print(f"{name}:")
        for h in hits:
            print(f"  [{h['root']}] {h['path']}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="skill resolver")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("list"); p.add_argument("--json", action="store_true")
    p = sub.add_parser("find"); p.add_argument("name")
    p = sub.add_parser("path"); p.add_argument("name")
    p = sub.add_parser("conflicts"); p.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    return {"list": cmd_list, "find": cmd_find,
            "path": cmd_path, "conflicts": cmd_conflicts}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
