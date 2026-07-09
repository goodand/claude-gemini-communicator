#!/usr/bin/env python3
"""doc-code-sync-checker scaffold.

v0.1은 문서 1개와 코드 1개를 비교하는 pairwise smoke-test checker다.
`normalize`는 별도 CLI가 아니라 compare 내부 단계로 남겨둔 상태다.

Usage:
    python3 doc_code_sync.py extract-doc --doc <file>
    python3 doc_code_sync.py extract-code --script <file>
    python3 doc_code_sync.py compare --doc-rules <json> --code-rules <json>
    python3 doc_code_sync.py report --results <results.json>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta

KST = timezone(timedelta(hours=9))


def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def cmd_extract_doc(args):
    payload = {
        "status": "scaffold",
        "scope": "pairwise_smoke_test",
        "command": "extract-doc",
        "doc": args.doc,
        "rules": [],
        "message": "TODO: 표/목록/규칙 문장 파싱 구현",
        "generated_at": _now_iso(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_extract_code(args):
    payload = {
        "status": "scaffold",
        "scope": "pairwise_smoke_test",
        "command": "extract-code",
        "script": args.script,
        "rules": [],
        "message": "TODO: validate/상수/전이 dict 추출 구현",
        "generated_at": _now_iso(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_compare(args):
    payload = {
        "status": "scaffold",
        "scope": "pairwise_smoke_test",
        "command": "compare",
        "doc_rules": args.doc_rules,
        "code_rules": args.code_rules,
        "normalization": {
            "mode": "internal_compare_stage",
            "implemented": False,
        },
        "missing_in_code": [],
        "missing_in_doc": [],
        "mismatch": [],
        "message": "TODO: rule-set 비교 로직 구현",
        "compared_at": _now_iso(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_report(args):
    payload = {
        "status": "scaffold",
        "scope": "pairwise_smoke_test",
        "command": "report",
        "results": args.results,
        "message": "TODO: drift 보고서 생성",
        "reported_at": _now_iso(),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        description="doc-code-sync-checker scaffold (v0.1 pairwise smoke-test)"
    )
    sub = parser.add_subparsers(dest="command")

    p_doc = sub.add_parser("extract-doc", help="문서 규칙 추출")
    p_doc.add_argument("--doc", required=True, help="reference 문서 경로")

    p_code = sub.add_parser("extract-code", help="코드 규칙 추출")
    p_code.add_argument("--script", required=True, help="validate 포함 스크립트 경로")

    p_compare = sub.add_parser("compare", help="문서/코드 규칙 비교")
    p_compare.add_argument("--doc-rules", required=True, help="문서 규칙 JSON")
    p_compare.add_argument("--code-rules", required=True, help="코드 규칙 JSON")

    p_report = sub.add_parser("report", help="비교 결과 보고")
    p_report.add_argument("--results", required=True, help="비교 결과 JSON")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "extract-doc": cmd_extract_doc,
        "extract-code": cmd_extract_code,
        "compare": cmd_compare,
        "report": cmd_report,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
