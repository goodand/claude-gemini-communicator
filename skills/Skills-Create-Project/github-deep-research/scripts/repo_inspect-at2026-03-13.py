#!/usr/bin/env python3
"""GitHub Repo Inspector — repo 검증에 필요한 증거를 한 번에 수집한다.

사용법:
    python3 repo_inspect.py owner/repo
    python3 repo_inspect.py owner/repo --output report.md
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime


def run_gh(args: list[str], timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            ["gh"] + args,
            capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            return ""
        return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def inspect_repo(repo: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sections = [f"# Repo Inspection: {repo}\n\n- **Date**: {now}\n"]

    # 1. 기본 정보
    info = run_gh(["repo", "view", repo, "--json",
                   "description,stargazerCount,forkCount,primaryLanguage,license,updatedAt,openIssues"])
    if info:
        try:
            d = json.loads(info)
            sections.append("## 기본 정보\n")
            sections.append(f"- **Description**: {d.get('description', 'N/A')}")
            sections.append(f"- **Stars**: {d.get('stargazerCount', '?')}")
            sections.append(f"- **Forks**: {d.get('forkCount', '?')}")
            lang = d.get('primaryLanguage', {})
            sections.append(f"- **Language**: {lang.get('name', '?') if lang else '?'}")
            lic = d.get('license', {})
            sections.append(f"- **License**: {lic.get('name', '?') if lic else '?'}")
            sections.append(f"- **Updated**: {d.get('updatedAt', '?')[:10]}")
            issues = d.get('openIssues', {})
            sections.append(f"- **Open Issues**: {issues.get('totalCount', '?') if isinstance(issues, dict) else '?'}")
            sections.append("")
        except json.JSONDecodeError:
            sections.append(f"```\n{info}\n```\n")

    # 2. 파일 트리 (top-level)
    tree = run_gh(["api", f"repos/{repo}/contents/", "--jq", ".[].name"])
    if tree:
        sections.append("## 파일 트리 (top-level)\n")
        sections.append("```")
        sections.append(tree)
        sections.append("```\n")

    # 3. README 앞부분
    readme = run_gh(["api", f"repos/{repo}/readme", "--jq", ".content"], timeout=10)
    if readme:
        import base64
        try:
            decoded = base64.b64decode(readme).decode("utf-8", errors="replace")
            preview = "\n".join(decoded.split("\n")[:30])
            sections.append("## README (처음 30줄)\n")
            sections.append(f"```\n{preview}\n```\n")
        except Exception:
            pass

    # 4. 최근 이슈 5개
    issues = run_gh(["search", "issues", "", f"--repo={repo}", "--limit", "5", "--sort", "updated"])
    if issues:
        sections.append("## 최근 이슈\n")
        for line in issues.split("\n")[:5]:
            if line.strip():
                sections.append(f"- {line.strip()}")
        sections.append("")

    # 5. 최근 커밋 5개
    commits = run_gh(["api", f"repos/{repo}/commits?per_page=5",
                      "--jq", '.[] | "- " + .commit.message[:80] + " (" + .commit.author.date[:10] + ")"'])
    if commits:
        sections.append("## 최근 커밋\n")
        sections.append(commits)
        sections.append("")

    return "\n".join(sections)


def main():
    parser = argparse.ArgumentParser(description="GitHub Repo Inspector")
    parser.add_argument("repo", help="owner/repo 형식")
    parser.add_argument("--output", "-o", help="결과를 파일로 저장")
    args = parser.parse_args()

    output = inspect_repo(args.repo)

    if args.output:
        from pathlib import Path
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"[OK] 저장: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
