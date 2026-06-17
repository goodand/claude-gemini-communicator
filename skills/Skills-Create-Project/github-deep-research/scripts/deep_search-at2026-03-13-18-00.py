#!/usr/bin/env python3
"""GitHub Deep Search — gh search 통합 래퍼.

gh CLI의 code/issues/prs/repos 검색을 하나의 인터페이스로 통합하고
결과를 markdown 형식으로 출력한다.

사용법:
    python3 deep_search.py --query "langfuse" --scope code --limit 10
    python3 deep_search.py --query "tmux agent" --scope all --output report.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCOPES = ("code", "issues", "prs", "repos", "all")


def run_gh(args: list[str]) -> str:
    """gh CLI 명령을 실행하고 stdout을 반환한다."""
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            print(f"[WARN] gh {' '.join(args[:3])}... failed: {result.stderr.strip()}", file=sys.stderr)
            return ""
        return result.stdout.strip()
    except FileNotFoundError:
        print("[ERROR] gh CLI를 찾을 수 없습니다. 'brew install gh' 후 'gh auth login' 실행.", file=sys.stderr)
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"[WARN] gh {' '.join(args[:3])}... timed out (30s)", file=sys.stderr)
        return ""


def search_scope(scope: str, query: str, limit: int, language: str | None, sort: str | None) -> str:
    """단일 scope에 대해 gh search를 실행하고 결과를 반환한다."""
    cmd = ["search", scope, query, "--limit", str(limit)]
    if language and scope in ("code", "repos"):
        cmd.extend(["--language", language])
    if sort and scope in ("issues", "prs", "repos"):
        cmd.extend(["--sort", sort])
    return run_gh(cmd)


def format_section(scope: str, raw: str) -> str:
    """검색 결과를 markdown 섹션으로 포맷한다."""
    scope_titles = {
        "code": "Code Search",
        "issues": "Issues",
        "prs": "Pull Requests",
        "repos": "Repositories",
    }
    title = scope_titles.get(scope, scope.title())
    if not raw:
        return f"## {title}\n\n결과 없음.\n"

    lines = raw.split("\n")
    formatted = f"## {title}\n\n| # | 결과 |\n|---|------|\n"
    for i, line in enumerate(lines, 1):
        if line.strip():
            # 탭/공백으로 구분된 gh 출력을 정리
            formatted += f"| {i} | {line.strip()} |\n"
    return formatted


def main():
    parser = argparse.ArgumentParser(
        description="GitHub Deep Search — gh search 통합 래퍼",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--query", "-q", required=True, help="검색 쿼리")
    parser.add_argument(
        "--scope", "-s", default="all", choices=SCOPES,
        help="검색 범위: code, issues, prs, repos, all (기본: all)",
    )
    parser.add_argument("--limit", "-l", type=int, default=10, help="결과 수 (기본: 10)")
    parser.add_argument("--language", help="언어 필터 (code, repos에만 적용)")
    parser.add_argument("--sort", help="정렬 기준 (issues/prs/repos에만 적용)")
    parser.add_argument("--output", "-o", help="결과를 파일로 저장 (미지정 시 stdout)")
    args = parser.parse_args()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    header = f"# GitHub Deep Search Report\n\n- **Query**: `{args.query}`\n- **Scope**: {args.scope}\n- **Limit**: {args.limit}\n- **Date**: {now}\n\n"

    scopes = ["code", "issues", "prs", "repos"] if args.scope == "all" else [args.scope]

    sections = []
    for scope in scopes:
        raw = search_scope(scope, args.query, args.limit, args.language, args.sort)
        sections.append(format_section(scope, raw))

    output = header + "\n".join(sections)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"[OK] 결과 저장: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
