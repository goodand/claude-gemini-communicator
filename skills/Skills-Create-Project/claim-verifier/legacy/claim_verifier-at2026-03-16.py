#!/usr/bin/env python3
"""claim-verifier scaffold.

Usage:
    python3 claim_verifier.py extract --input <file>
    python3 claim_verifier.py verify --claims <claims.json> --repo <path>
    python3 claim_verifier.py report --results <results.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def cmd_extract(args):
    payload = {
        "status": "scaffold",
        "command": "extract",
        "input": args.input,
        "claims": [],
        "message": "TODO: claim 추출 로직 구현",
        "generated_at": _now_iso(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_verify(args):
    payload = {
        "status": "scaffold",
        "command": "verify",
        "claims": args.claims,
        "repo": args.repo,
        "results": [],
        "message": "TODO: 파일/라인 증거 수집 및 판정 로직 구현",
        "verified_at": _now_iso(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_report(args):
    payload = {
        "status": "scaffold",
        "command": "report",
        "results": args.results,
        "message": "TODO: claim별 true/false/partial/unverifiable 보고서 생성",
        "reported_at": _now_iso(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="claim-verifier scaffold")
    sub = parser.add_subparsers(dest="command")

    p_extract = sub.add_parser("extract", help="claim 목록 추출")
    p_extract.add_argument("--input", required=True, help="원본 텍스트/문서 파일")

    p_verify = sub.add_parser("verify", help="claim 증거 검증")
    p_verify.add_argument("--claims", required=True, help="claim 목록 JSON")
    p_verify.add_argument("--repo", required=True, help="검증 대상 repo 경로")

    p_report = sub.add_parser("report", help="검증 결과 보고")
    p_report.add_argument("--results", required=True, help="검증 결과 JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "extract": cmd_extract,
        "verify": cmd_verify,
        "report": cmd_report,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
