#!/usr/bin/env python3
"""Gate 2 — Conflict: 이름 충돌을 클래스로 분류, repo 내부 canonical 중복만 FAIL.

충돌 '개수'는 환경에 따라 달라진다 — 2026-07-09 실측에서 Desktop 프로젝트
루트가 TCC에 막힌 세션은 7건, 보이는 세션은 약 55건이 관측됐다(추가분은
전부 미러↔원소유repo / 정본↔프로젝트사본). 따라서 이 gate는 개수가 아니라
충돌에 참여한 root의 클래스로 판정한다.

FAIL 클래스 (정본이 모호해지는 유일한 경우):
  REPO_INTERNAL            같은 이름이 정본 루트(repo-skills,
                           repo-skills-createproject) 두 곳 이상에 존재

WARN 클래스 (설계상 존재하거나 무해한 사본):
  EXTERNAL_MIRROR_DUP      external/ 미러 버킷 두 곳에 같은 이름
  EXTERNAL_VS_USER_GLOBAL  미러 ↔ 사용자 전역(~/.claude, ~/.codex, ~/skills)
  MIRROR_VS_ORIGIN_REPO    미러 ↔ 원 소유 프로젝트 repo (external은 미러,
                           출처가 정본이므로 이름이 겹치는 게 정상)
  CANONICAL_VS_PROJECT_COPY 정본 ↔ 다른 프로젝트에 배포/복사된 사본
  OTHER_NON_CANONICAL      그 외 (user-global ↔ 프로젝트 등)

stdlib만. 단독 실행: python3 conflict_gate.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS_DIR))

CANONICAL_ROOTS = {"repo-skills", "repo-skills-createproject"}
USER_GLOBAL_ROOTS = {"claude-user", "codex-user", "home-skills"}
FAIL_CLASSES = {"REPO_INTERNAL"}


def classify(root_labels: list[str]) -> str:
    canon = [r for r in root_labels if r in CANONICAL_ROOTS]
    if len(canon) >= 2:
        return "REPO_INTERNAL"
    ext = [r for r in root_labels if r == "repo-external"]
    if len(ext) >= 2:
        return "EXTERNAL_MIRROR_DUP"
    has_user = any(r in USER_GLOBAL_ROOTS for r in root_labels)
    has_proj = any(r.startswith("proj:") for r in root_labels)
    if ext and has_user and not has_proj:
        return "EXTERNAL_VS_USER_GLOBAL"
    if ext and has_proj:
        return "MIRROR_VS_ORIGIN_REPO"
    if canon and has_proj:
        return "CANONICAL_VS_PROJECT_COPY"
    return "OTHER_NON_CANONICAL"


def run() -> dict:
    from resolve_skill import discover
    _, all_hits = discover()
    by_name: dict[str, list] = {}
    for h in all_hits:
        hits = by_name.setdefault(h["name"], [])
        if h["real"] not in {x["real"] for x in hits}:
            hits.append(h)
    conflicts = []
    for name, hits in sorted(by_name.items()):
        if len(hits) < 2:
            continue
        cls = classify([h["root"] for h in hits])
        conflicts.append({
            "name": name, "class": cls,
            "hits": [{"root": h["root"], "path": h["path"]} for h in hits],
        })
    class_counts = Counter(c["class"] for c in conflicts)
    failing = [c for c in conflicts if c["class"] in FAIL_CLASSES]
    if failing:
        status = "FAIL"
    elif conflicts:
        status = "WARN"
    else:
        status = "PASS"
    return {
        "gate": "conflict",
        "status": status,
        "summary": (f"{len(conflicts)} conflicts, "
                    f"REPO_INTERNAL={class_counts.get('REPO_INTERNAL', 0)}"),
        "details": {"class_counts": dict(class_counts),
                    "failing": failing, "conflicts": conflicts},
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
