#!/usr/bin/env python3
"""Gate 4 — Policy Sync: 문서가 선언한 발견 정책 = resolver의 실제 동작.

검사 항목:
  stale_excluded           발견 결과(모든 hit)에 `_stale` 경로가 없어야 함
                           (SKILL_DISCOVERY.md·_stale README의 선언)
  stale_readme             external/_stale/README.md 존재 + 격리 정책 서술
  stale_canonicals_present README가 격리했다고 선언한 각 skill의 최신 정본이
                           skills/<name>/SKILL.md 로 실제 존재
  base_root_order          SKILL_DISCOVERY.md §2 표의 우선순위와
                           resolve_skill.BASE_ROOTS 코드 순서 일치

stdlib만. 단독 실행: python3 policy_sync_gate.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS_DIR))

STALE_README = SKILLS_DIR / "external" / "_stale" / "README.md"

# SKILL_DISCOVERY.md §2 표(#2~#8 + 프로젝트 루트)의 코드 대응 순서
EXPECTED_BASE_ORDER = [
    "repo-skills", "repo-skills-createproject", "repo-external",
    "claude-user", "codex-user", "home-skills", "control", "agent",
]


def run() -> dict:
    import resolve_skill
    checks = {}

    # 1) _stale 경로가 발견에서 실제로 제외되는가
    _, all_hits = resolve_skill.discover()
    stale_hits = [h["path"] for h in all_hits if "/_stale/" in h["path"] + "/"]
    checks["stale_excluded"] = {"ok": not stale_hits, "stale_hits": stale_hits}

    # 2) _stale README 존재 + 격리 정책 서술
    readme_ok, quarantined = False, []
    if STALE_README.exists():
        text = STALE_README.read_text(encoding="utf-8")
        readme_ok = ("제외" in text) and ("정본" in text)
        quarantined = [m for m in
                       re.findall(r"(?m)^\|\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*\|", text)
                       if m != "skill"]
    checks["stale_readme"] = {"ok": readme_ok, "path": str(STALE_README)}

    # 3) 격리된 각 skill의 최신 정본이 top-level에 실존
    missing = [n for n in quarantined
               if not (SKILLS_DIR / n / "SKILL.md").exists()]
    checks["stale_canonicals_present"] = {
        "ok": bool(quarantined) and not missing,
        "quarantined": quarantined, "missing_canonicals": missing,
    }

    # 4) 문서의 우선순위 표 = 코드의 BASE_ROOTS 순서
    actual = [label for label, _, _ in resolve_skill.BASE_ROOTS][:len(EXPECTED_BASE_ORDER)]
    checks["base_root_order"] = {
        "ok": actual == EXPECTED_BASE_ORDER,
        "expected": EXPECTED_BASE_ORDER, "actual": actual,
    }

    failed = [k for k, v in checks.items() if not v["ok"]]
    return {
        "gate": "policy_sync",
        "status": "PASS" if not failed else "FAIL",
        "summary": f"{len(checks) - len(failed)}/{len(checks)} checks",
        "details": {"checks": checks, "failed": failed},
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
