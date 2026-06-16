#!/usr/bin/env python3
"""
Restore plan context after compaction or session resume.

Sources (priority order):
1. git log / git diff — ground truth of recent changes
2. HANDOFF documents — session-level plan state snapshots
3. MEMORY.md — project-level long-term context
4. Session JSONL transcript — compaction summary extraction (expensive, last resort)

Usage:
    python3 context_restore.py --project-root .
    python3 context_restore.py --project-root . --create-handoff
    python3 context_restore.py --project-root . --json
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def run_git(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            ["git"] + args, cwd=cwd, capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def get_git_context(project_root: Path, commit_count: int = 20) -> dict[str, Any]:
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], project_root)
    log_raw = run_git(["log", "--oneline", f"-{commit_count}", "--no-decorate"], project_root)
    diff_stat = run_git(["diff", "HEAD~5..HEAD", "--stat"], project_root)
    status = run_git(["status", "--short"], project_root)
    return {
        "branch": branch,
        "recent_commits": log_raw.splitlines() if log_raw else [],
        "diff_stat_last_5": diff_stat,
        "working_tree_changes": len(status.splitlines()) if status else 0,
    }


def find_handoff_docs(project_root: Path) -> list[dict[str, str]]:
    handoff_files: list[Path] = []
    for pattern in ["**/HANDOFF*", "**/handoff*"]:
        handoff_files.extend(project_root.glob(pattern))
    seen: set[Path] = set()
    unique: list[Path] = []
    for f in handoff_files:
        r = f.resolve()
        if r not in seen and r.is_file():
            seen.add(r)
            unique.append(r)
    unique.sort(key=lambda p: p.name, reverse=True)
    results = []
    for f in unique[:10]:
        try:
            rel = f.relative_to(project_root.resolve())
        except ValueError:
            rel = f
        try:
            preview = "\n".join(f.read_text(encoding="utf-8", errors="replace").splitlines()[:5])
        except Exception:
            preview = "(unreadable)"
        results.append({"path": str(rel), "preview": preview})
    return results


def find_memory_md(project_root: Path) -> dict[str, Any]:
    candidates = [*project_root.glob(".claude/**/MEMORY.md"), project_root / "MEMORY.md"]
    for c in candidates:
        if c.exists() and c.is_file():
            try:
                content = c.read_text(encoding="utf-8", errors="replace")
                return {
                    "path": str(c),
                    "line_count": len(content.splitlines()),
                    "preview": "\n".join(content.splitlines()[:20]),
                }
            except Exception:
                continue
    return {"path": None, "line_count": 0, "preview": ""}


def find_active_plans(project_root: Path) -> list[str]:
    plan_patterns = ["**/PLAN*.md", "**/CHECKLIST*.md", "**/CURRENT_STATE*.md", "**/TASK_*.md", "**/SPEC_*.md"]
    all_plans: list[Path] = []
    for pattern in plan_patterns:
        all_plans.extend(f for f in project_root.glob(pattern) if f.is_file())
    all_plans.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    results = []
    seen: set[Path] = set()
    for f in all_plans:
        r = f.resolve()
        if r in seen:
            continue
        seen.add(r)
        try:
            rel = f.relative_to(project_root.resolve())
        except ValueError:
            rel = f
        results.append(str(rel))
        if len(results) >= 15:
            break
    return results


def find_session_transcript(project_root: Path) -> dict[str, Any] | None:
    all_jsonl: list[Path] = []
    for d in project_root.glob(".claude/projects/*/"):
        all_jsonl.extend(d.glob("*.jsonl"))
    if not all_jsonl:
        return None
    newest = max(all_jsonl, key=lambda p: p.stat().st_mtime)
    size = newest.stat().st_size
    try:
        rel = newest.relative_to(project_root.resolve())
    except ValueError:
        rel = newest
    return {
        "path": str(rel),
        "size_bytes": size,
        "size_mb": round(size / (1024 * 1024), 2),
        "hint": "Use agent-parser skill to extract compaction summary if needed",
    }


def generate_restoration_summary(report: dict[str, Any]) -> str:
    lines: list[str] = [
        "# Context Restoration Summary",
        f"- generated_at: {report.get('timestamp', 'unknown')}",
        f"- difficulty: {report.get('restoration_difficulty', 'unknown')}",
        "",
    ]
    git = report.get("git", {})
    lines.append(f"## 1. Git State (branch: `{git.get('branch', 'unknown')}`)")
    lines.append(f"- Working tree changes: {git.get('working_tree_changes', 0)}")
    commits = git.get("recent_commits", [])
    if commits:
        lines.append("- Recent commits:")
        for c in commits[:10]:
            lines.append(f"  - {c}")
    lines.append("")

    handoffs = report.get("handoff_docs", [])
    lines.append(f"## 2. HANDOFF Documents ({len(handoffs)} found)")
    if handoffs:
        lines.append(f"- **Most recent**: `{handoffs[0]['path']}`")
        preview = handoffs[0]["preview"][:200].replace("\n", " | ")
        lines.append(f"  - Preview: {preview}")
        lines.append("- **Action**: READ this file first to restore plan state")
    else:
        lines.append("- **None found** — reconstruct from git + MEMORY.md")
        lines.append("- **Action**: Run with `--create-handoff` after manual restoration")
    lines.append("")

    memory = report.get("memory_md", {})
    if memory.get("path"):
        lines.append(f"## 3. MEMORY.md ({memory['line_count']} lines)")
        lines.append(f"- Path: `{memory['path']}`")
    else:
        lines.append("## 3. MEMORY.md — not found")
    lines.append("")

    plans = report.get("active_plans", [])
    if plans:
        lines.append(f"## 4. Active Plans/Checklists ({len(plans)} found)")
        for p in plans[:10]:
            lines.append(f"- `{p}`")
    lines.append("")

    transcript = report.get("session_transcript")
    if transcript:
        lines.append("## 5. Session Transcript (last resort)")
        lines.append(f"- Path: `{transcript['path']}` ({transcript['size_mb']} MB)")
        lines.append(f"- {transcript['hint']}")
    lines.append("")

    lines.extend([
        "## Recommended Recovery Order",
        "1. Read the most recent HANDOFF document (if exists)",
        "2. Read MEMORY.md for project-level context",
        "3. Check `git log --oneline -10` for recent work",
        "4. Check active plans/checklists for current phase",
        "5. Report understood state to user for confirmation",
        "6. If no HANDOFF exists, create one after confirmation",
    ])
    return "\n".join(lines)


def create_handoff_stub(project_root: Path, report: dict[str, Any]) -> Path:
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d-%H-%M")
    plans_dirs = [project_root / "plans" / "claude", project_root / "plans", project_root]
    target_dir = next((d for d in plans_dirs if d.exists()), project_root)
    target = target_dir / f"HANDOFF_context_restore_{ts}.md"

    git = report.get("git", {})
    handoffs = report.get("handoff_docs", [])
    plans = report.get("active_plans", [])

    lines = [
        f"# HANDOFF: Context Restore — {ts}",
        f"- created_at: {ts}",
        "- created_by: context_restore.py (auto-generated)",
        "- purpose: compaction/resume 후 복원 앵커",
        "",
        "## 1) 현재 Git 상태",
        f"- branch: `{git.get('branch', 'unknown')}`",
        f"- working tree changes: {git.get('working_tree_changes', 0)}",
    ]
    for c in git.get("recent_commits", [])[:5]:
        lines.append(f"  - {c}")
    lines.append("")
    if handoffs:
        lines.extend(["## 2) 이전 HANDOFF 참조", f"- `{handoffs[0]['path']}`", ""])
    if plans:
        lines.append("## 3) 활성 Plan/Checklist")
        for p in plans[:10]:
            lines.append(f"- `{p}`")
        lines.append("")
    lines.extend([
        "## 4) 복원 시 확인 사항",
        "- [ ] 현재 진행 중인 task는 무엇인가?",
        "- [ ] 다음 단계는 무엇인가?",
        "- [ ] 역할 경계 (CEO/CTO/Codex)는 명확한가?",
        "- [ ] 사용 중인 metric naming 규칙은 어디에 있는가?",
        "",
        "## 5) 수동 보완 필요",
        "- 이 문서는 자동 생성됨 — 사용자가 section 4를 채워야 완전한 HANDOFF가 됨",
    ])
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Restore plan context after compaction or session resume")
    parser.add_argument("--project-root", default=".", help="Project root directory")
    parser.add_argument("--commit-count", type=int, default=20, help="Number of recent commits to show")
    parser.add_argument("--json", action="store_true", help="Emit JSON report")
    parser.add_argument("--create-handoff", action="store_true", help="Create a HANDOFF stub from current state")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if not project_root.exists():
        print(f"[context-restore] error: project root not found: {project_root}", file=sys.stderr)
        return 1

    report: dict[str, Any] = {
        "project_root": str(project_root),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    report["git"] = get_git_context(project_root, args.commit_count)
    report["handoff_docs"] = find_handoff_docs(project_root)
    report["memory_md"] = find_memory_md(project_root)
    report["active_plans"] = find_active_plans(project_root)
    report["session_transcript"] = find_session_transcript(project_root)

    has_handoff = len(report["handoff_docs"]) > 0
    has_memory = report["memory_md"].get("path") is not None
    has_git = len(report["git"].get("recent_commits", [])) > 0

    if has_handoff:
        report["restoration_difficulty"] = "easy"
        report["restoration_hint"] = "HANDOFF exists — read it to restore plan state"
    elif has_memory and has_git:
        report["restoration_difficulty"] = "medium"
        report["restoration_hint"] = "No HANDOFF — reconstruct from MEMORY.md + git log"
    else:
        report["restoration_difficulty"] = "hard"
        report["restoration_hint"] = "No HANDOFF, no MEMORY — rely on git log + session transcript"

    if args.create_handoff:
        handoff_path = create_handoff_stub(project_root, report)
        report["created_handoff"] = str(handoff_path)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(generate_restoration_summary(report))
        if args.create_handoff:
            print(f"\n[context-restore] HANDOFF created: {report['created_handoff']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
