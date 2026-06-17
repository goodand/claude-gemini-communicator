#!/usr/bin/env python3
"""Codebase Progress Scanner — TODO/git/milestone/delta 통합 스캐너.

사용법:
    python3 scan_progress.py --path .
    python3 scan_progress.py --mode todos --path src/
    python3 scan_progress.py --mode milestone --milestone plans/milestone.md --path .
    python3 scan_progress.py --mode delta --since "1 week ago" --path .
    python3 scan_progress.py --mode full --path . --output progress.md
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(cmd: List[str], timeout: int = 30) -> str:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def find_files(path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """재귀적으로 소스 파일 목록 반환. .git, node_modules 등 제외."""
    skip = {".git", "node_modules", "__pycache__", ".venv", "venv", ".worktrees"}
    result = []
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in skip]
        for f in files:
            if extensions:
                if not any(f.endswith(e) for e in extensions):
                    continue
            result.append(os.path.join(root, f))
    return result


# ---------------------------------------------------------------------------
# Mode: todos
# ---------------------------------------------------------------------------

def scan_todos(path: str) -> List[Dict[str, str]]:
    """TODO/FIXME/HACK/XXX 패턴을 소스 파일에서 추출."""
    pattern = re.compile(r"#\s*(TODO|FIXME|HACK|XXX)\b[:\s]*(.*)", re.IGNORECASE)
    exts = [".py", ".js", ".ts", ".jsx", ".tsx", ".go", ".rs", ".java", ".rb", ".sh", ".sql"]
    todos = []
    for fp in find_files(path, exts):
        try:
            with open(fp, encoding="utf-8", errors="replace") as fh:
                for i, line in enumerate(fh, 1):
                    m = pattern.search(line)
                    if m:
                        todos.append({
                            "file": os.path.relpath(fp, path),
                            "line": str(i),
                            "tag": m.group(1).upper(),
                            "text": m.group(2).strip(),
                        })
        except OSError:
            continue
    return todos


def format_todos(todos: List[Dict[str, str]]) -> str:
    if not todos:
        return "TODO/FIXME 항목 없음.\n"
    lines = [f"## TODOs / FIXMEs ({len(todos)}개)\n"]
    for t in todos:
        lines.append(f"- `{t['file']}:{t['line']}` **{t['tag']}**: {t['text']}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Mode: git-stats
# ---------------------------------------------------------------------------

def scan_git_stats(path: str, since: Optional[str] = None) -> str:
    args = ["git", "-C", path, "log", "--oneline"]
    if since:
        args += ["--since", since]
    log = run(args)
    commit_count = len(log.strip().split("\n")) if log.strip() else 0

    diff_args = ["git", "-C", path, "diff", "--stat"]
    if since:
        diff_args = ["git", "-C", path, "log", "--stat", "--since", since, "--oneline"]
    diff_stat = run(diff_args)

    lines = ["## Git 활동\n"]
    lines.append(f"- **커밋 수**: {commit_count}")
    if diff_stat:
        # 마지막 줄에 summary가 있을 수 있음
        last = diff_stat.strip().split("\n")[-1]
        if "changed" in last:
            lines.append(f"- **변경 요약**: {last.strip()}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Mode: milestone
# ---------------------------------------------------------------------------

def scan_milestone(path: str, milestone_file: str) -> str:
    """마일스톤 파일의 체크리스트 항목을 코드에서 키워드 검색으로 대조."""
    try:
        content = Path(milestone_file).read_text(encoding="utf-8")
    except OSError:
        return f"마일스톤 파일을 읽을 수 없음: {milestone_file}\n"

    # - [ ] 또는 - [x] 패턴 추출
    items = re.findall(r"-\s*\[([ xX])\]\s*(.*)", content)
    if not items:
        return "마일스톤 파일에서 체크리스트 항목을 찾을 수 없음.\n"

    lines = [f"## 마일스톤 대비 진행률\n"]
    done = 0
    total = len(items)

    for checked, text in items:
        is_done = checked.lower() == "x"
        # 코드에서 키워드 확인 (간단한 grep)
        keyword = text.strip().split()[0] if text.strip() else ""
        code_found = False
        if keyword and len(keyword) > 2:
            result = run(["grep", "-rl", keyword, path, "--include=*.py",
                          "--include=*.js", "--include=*.ts"], timeout=10)
            code_found = bool(result)

        if is_done:
            done += 1
            marker = "v"
        elif code_found:
            done += 1
            marker = "v (코드 발견)"
        else:
            marker = "x"

        lines.append(f"- [{marker}] {text.strip()}")

    pct = int(done / total * 100) if total else 0
    lines.append(f"\n**Progress**: {done}/{total} ({pct}%)")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Mode: delta
# ---------------------------------------------------------------------------

def scan_delta(path: str, since: str) -> str:
    """이전 시점 대비 변경 요약."""
    # 새 파일
    added = run(["git", "-C", path, "log", "--diff-filter=A", "--name-only",
                 "--pretty=format:", "--since", since])
    modified = run(["git", "-C", path, "log", "--diff-filter=M", "--name-only",
                    "--pretty=format:", "--since", since])
    deleted = run(["git", "-C", path, "log", "--diff-filter=D", "--name-only",
                   "--pretty=format:", "--since", since])

    added_files = [f for f in added.split("\n") if f.strip()] if added else []
    mod_files = [f for f in modified.split("\n") if f.strip()] if modified else []
    del_files = [f for f in deleted.split("\n") if f.strip()] if deleted else []

    lines = [f"## Delta (since {since})\n"]
    lines.append(f"- **추가**: {len(set(added_files))}개 파일")
    lines.append(f"- **수정**: {len(set(mod_files))}개 파일")
    lines.append(f"- **삭제**: {len(set(del_files))}개 파일")

    if added_files:
        lines.append("\n### 추가된 파일")
        for f in sorted(set(added_files))[:20]:
            lines.append(f"  - {f}")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Mode: full
# ---------------------------------------------------------------------------

def scan_full(path: str, since: Optional[str] = None,
              milestone_file: Optional[str] = None) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sections = [f"# Progress Report — {now}\n"]

    # 파일 통계
    all_files = find_files(path)
    sections.append(f"## Overview\n\n- **총 파일 수**: {len(all_files)}\n")

    # TODOs
    todos = scan_todos(path)
    sections.append(format_todos(todos))

    # Git
    sections.append(scan_git_stats(path, since))

    # Milestone
    if milestone_file:
        sections.append(scan_milestone(path, milestone_file))

    # Delta
    if since:
        sections.append(scan_delta(path, since))

    return "\n".join(sections)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_output(output: str) -> int:
    """결과물 검증. 최소 섹션이 있는지 확인."""
    warnings = []
    if "## " not in output:
        warnings.append("섹션 헤딩(##)이 없음")
    if len(output.strip()) < 50:
        warnings.append("출력이 너무 짧음 (50자 미만)")

    if warnings:
        for w in warnings:
            print(f"[WARN] {w}", file=sys.stderr)
        return 1
    print("[OK] 검증 통과", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Codebase Progress Scanner — TODO/git/milestone/delta 통합 스캐너"
    )
    parser.add_argument("--path", default=".", help="스캔 대상 디렉토리 (기본: .)")
    parser.add_argument("--mode", default="full",
                        choices=["todos", "git-stats", "milestone", "delta", "full"],
                        help="스캔 모드 (기본: full)")
    parser.add_argument("--since", help="git delta/stats 기준 시점 (예: '1 week ago')")
    parser.add_argument("--milestone", help="마일스톤 체크리스트 파일 경로")
    parser.add_argument("--output", "-o", help="결과를 파일로 저장")
    args = parser.parse_args()

    path = os.path.abspath(args.path)

    if args.mode == "todos":
        result = format_todos(scan_todos(path))
    elif args.mode == "git-stats":
        result = scan_git_stats(path, args.since)
    elif args.mode == "milestone":
        if not args.milestone:
            print("[ERROR] --milestone 옵션이 필요합니다.", file=sys.stderr)
            sys.exit(1)
        result = scan_milestone(path, args.milestone)
    elif args.mode == "delta":
        if not args.since:
            print("[ERROR] --since 옵션이 필요합니다.", file=sys.stderr)
            sys.exit(1)
        result = scan_delta(path, args.since)
    else:
        result = scan_full(path, args.since, args.milestone)

    # Verify
    exit_code = verify_output(result)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"[OK] 저장: {args.output}", file=sys.stderr)
    else:
        print(result)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
