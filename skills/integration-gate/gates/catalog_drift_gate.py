#!/usr/bin/env python3
"""Gate 3 — Catalog Drift: 층2(catalog) ↔ 층3(resolver) 정합성.

catalog(skills.json)의 각 SKILL-* 항목이 resolver 발견 승자와 같은 정본을
가리키는지 형제 모듈 catalog_resolver_audit에 위임해 검사한다.
드리프트(PATH_MISSING / NOT_DISCOVERED / NOT_WINNER / NAME_MISMATCH)가
하나라도 있으면 FAIL.

stdlib만. 단독 실행: python3 catalog_drift_gate.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SKILLS_DIR))


def run() -> dict:
    from catalog_resolver_audit import audit, DEFAULT_CATALOG
    rows = audit(DEFAULT_CATALOG)
    drift = [r for r in rows if r["status"] != "OK"]
    return {
        "gate": "catalog_drift",
        "status": "PASS" if not drift else "FAIL",
        "summary": f"OK {len(rows) - len(drift)}/{len(rows)}, drift {len(drift)}",
        "details": {"total": len(rows), "drift": drift},
    }


if __name__ == "__main__":
    print(json.dumps(run(), ensure_ascii=False, indent=2))
