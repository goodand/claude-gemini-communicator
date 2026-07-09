#!/usr/bin/env python3
"""Integration Gate — feat→main 통합 판정 집계기 (4 subflow).

독립 runner다 — agent-tool-benchmark에 넣지 않는다(그건 메트릭 정의용이고,
평가 skill은 이 runner의 결과를 소비만 한다).

판정:
  PASS               4 gate 전부 PASS
  PASS_WITH_WARNING  FAIL 없음 + WARN 있음 (예: 미러/사본 클래스 충돌)
  FAIL               하나라도 FAIL (핵심 winner 불일치 · repo 내부 중복 ·
                     catalog drift · 문서-동작 불일치)

종료코드: PASS·PASS_WITH_WARNING=0, FAIL=1 (CI 게이트용).

사용 (repo 루트에서):
    python3 skills/integration-gate/run_integration_gate.py [--json]

리포트: skills/integration-gate/reports/integration_gate_report.{json,md}
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
GATES = [
    "canonical_winner_gate",
    "conflict_gate",
    "catalog_drift_gate",
    "policy_sync_gate",
]


def _load_gate(name: str):
    spec = importlib.util.spec_from_file_location(name, HERE / "gates" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git_head() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], cwd=HERE,
            capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def run_all() -> dict:
    results = []
    for name in GATES:
        try:
            results.append(_load_gate(name).run())
        except Exception as e:  # gate 크래시도 FAIL로 집계 (CI 안전)
            results.append({"gate": name.removesuffix("_gate"), "status": "FAIL",
                            "summary": f"gate crashed: {e}", "details": {}})
    statuses = {r["status"] for r in results}
    if "FAIL" in statuses:
        verdict = "FAIL"
    elif "WARN" in statuses:
        verdict = "PASS_WITH_WARNING"
    else:
        verdict = "PASS"
    return {
        "verdict": verdict,
        "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "head": _git_head(),
        "gates": results,
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# Integration Gate Report",
        "",
        f"- verdict: **{report['verdict']}**",
        f"- generated: {report['generated']}",
        f"- HEAD: `{report['head']}`",
        "",
        "| gate | status | summary |",
        "|---|---|---|",
    ]
    for g in report["gates"]:
        lines.append(f"| {g['gate']} | {g['status']} | {g['summary']} |")
    conflict = next((g for g in report["gates"] if g["gate"] == "conflict"), None)
    if conflict and conflict["details"].get("class_counts"):
        lines += ["", "## Conflict classes", "",
                  "| class | count | 판정 |", "|---|---|---|"]
        for cls, n in sorted(conflict["details"]["class_counts"].items()):
            j = "FAIL" if cls == "REPO_INTERNAL" else "WARN"
            lines.append(f"| {cls} | {n} | {j} |")
        lines += ["",
                  "충돌 수는 환경(보이는 발견 루트)에 따라 변하므로 개수가 아니라 "
                  "클래스로 판정한다. FAIL은 `REPO_INTERNAL`(정본 루트 내 중복)뿐이다."]
    winner = next((g for g in report["gates"] if g["gate"] == "canonical_winner"), None)
    if winner:
        lines += ["", "## Core skill winners", "",
                  "| skill | winner root | ok |", "|---|---|---|"]
        for r in winner["details"].get("results", []):
            lines.append(f"| {r['skill']} | {r['winner_root']} | {'✅' if r['ok'] else '❌'} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="integration gate runner")
    ap.add_argument("--json", action="store_true", help="JSON을 stdout으로")
    args = ap.parse_args(argv)

    report = run_all()

    reports_dir = HERE / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "integration_gate_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = to_markdown(report)
    (reports_dir / "integration_gate_report.md").write_text(md, encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else md)
    return 0 if report["verdict"] in ("PASS", "PASS_WITH_WARNING") else 1


if __name__ == "__main__":
    raise SystemExit(main())
