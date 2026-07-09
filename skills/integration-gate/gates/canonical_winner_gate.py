#!/usr/bin/env python3
"""Gate 1 — Canonical Winner: 핵심 skill의 resolver 승자가 repo 정본인지.

통합 판단의 축은 파일 수가 아니라 claim-verifier 생태계다. 핵심 5개
(허브 + 위임/정량화/평가 skill)의 발견 승자가 전부 정본 루트
`repo-skills-createproject`여야 PASS. 하나라도 다른 루트가 이기면
정본 우선순위가 깨진 것이므로 FAIL.

stdlib만. 단독 실행: python3 canonical_winner_gate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS_DIR))

# claim-verifier 허브 + 연결 skill. skill을 평가하는 skill
# (skill-workflow-bridge-eval, agent-tool-benchmark)은 반드시 포함한다.
CORE_SKILLS = [
    "claim-verifier",
    "skill-creation-process",
    "doc-code-sync-checker",
    "skill-workflow-bridge-eval",
    "agent-tool-benchmark",
]
EXPECTED_ROOT = "repo-skills-createproject"


def run() -> dict:
    from resolve_skill import discover
    winners, _ = discover()
    rows, failed = [], []
    for name in CORE_SKILLS:
        rec = winners.get(name)
        root = rec["root"] if rec else None
        ok = root == EXPECTED_ROOT
        rows.append({"skill": name, "winner_root": root, "ok": ok})
        if not ok:
            failed.append(name)
    return {
        "gate": "canonical_winner",
        "status": "PASS" if not failed else "FAIL",
        "summary": (f"core {len(CORE_SKILLS) - len(failed)}/{len(CORE_SKILLS)} "
                    f"winner={EXPECTED_ROOT}"),
        "details": {"expected_root": EXPECTED_ROOT, "results": rows,
                    "failed": failed},
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
