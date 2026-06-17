#!/usr/bin/env python3
"""Audit Python files for safe static-diagnostic fix patterns.

Usage:
    python3 diagnostic_audit.py audit --target <file.py>
"""

from __future__ import annotations

import argparse
import ast
import json
import py_compile
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path


KST = timezone(timedelta(hours=9))


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _err(message: str) -> None:
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(1)


@dataclass
class Finding:
    category: str
    name: str
    line: int | None
    evidence: str
    recommendation: str

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "name": self.name,
            "line": self.line,
            "evidence": self.evidence,
            "recommendation": self.recommendation,
        }


class UsageCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.used_names: set[str] = set()

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            self.used_names.add(node.id)
        self.generic_visit(node)


def collect_imported_names(tree: ast.AST) -> list[tuple[str, int]]:
    imported: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.append((alias.asname or alias.name.split(".")[0], node.lineno))
        elif isinstance(node, ast.ImportFrom):
            if node.module == "__future__":
                continue
            for alias in node.names:
                if alias.name == "*":
                    continue
                imported.append((alias.asname or alias.name, node.lineno))
    return imported


def collect_assigned_names(tree: ast.AST) -> list[tuple[str, int]]:
    assigned: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                assigned.extend(_extract_target_names(target, node.lineno))
        elif isinstance(node, ast.AnnAssign):
            assigned.extend(_extract_target_names(node.target, node.lineno))
    return assigned


def _extract_target_names(target: ast.AST, lineno: int) -> list[tuple[str, int]]:
    if isinstance(target, ast.Name):
        return [(target.id, lineno)]
    if isinstance(target, (ast.Tuple, ast.List)):
        items: list[tuple[str, int]] = []
        for elt in target.elts:
            items.extend(_extract_target_names(elt, lineno))
        return items
    return []


def detect_unused_imports(tree: ast.AST) -> list[Finding]:
    imported = collect_imported_names(tree)
    used = UsageCollector()
    used.visit(tree)
    findings: list[Finding] = []
    for name, lineno in imported:
        if name.startswith("_"):
            continue
        if name not in used.used_names:
            findings.append(
                Finding(
                    category="unused_import",
                    name=name,
                    line=lineno,
                    evidence=f"imported name `{name}` is never loaded",
                    recommendation="remove the import or justify the alias name explicitly",
                )
            )
    return findings


def detect_unused_assignments(tree: ast.AST) -> list[Finding]:
    assigned = collect_assigned_names(tree)
    used = UsageCollector()
    used.visit(tree)
    counter = Counter(name for name, _ in assigned)
    findings: list[Finding] = []
    for name, lineno in assigned:
        if name.startswith("_"):
            continue
        if name not in used.used_names and counter[name] >= 1:
            findings.append(
                Finding(
                    category="unused_variable",
                    name=name,
                    line=lineno,
                    evidence=f"assigned name `{name}` is never loaded",
                    recommendation="remove it or rename to `_` if intentionally unused",
                )
            )
            counter[name] = 0
    return findings


def detect_loader_guard(text: str, tree: ast.AST) -> list[Finding]:
    if "spec_from_file_location" not in text or "exec_module" not in text:
        return []

    guard_found = "spec.loader is None" in text or "spec is None or spec.loader is None" in text
    if guard_found:
        return []

    line = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "exec_module":
            line = node.lineno
            break

    return [
        Finding(
            category="optional_loader_guard_missing",
            name="spec.loader",
            line=line,
            evidence="dynamic import executes module without an explicit `spec.loader is None` guard",
            recommendation="add `if spec is None or spec.loader is None` before `exec_module`",
        )
    ]


def run_runtime_gate(target: Path) -> dict[str, object]:
    try:
        py_compile.compile(str(target), doraise=True)
        return {"ok": True, "tool": "py_compile", "message": "py_compile passed"}
    except py_compile.PyCompileError as exc:
        return {"ok": False, "tool": "py_compile", "message": str(exc)}


def audit_target(target: Path) -> dict[str, object]:
    if not target.is_file():
        _err(f"target file이 없습니다: {target}")

    text = target.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text, filename=str(target))
    except SyntaxError as exc:
        payload = {
            "status": "syntax_error",
            "generated_at": _now_iso(),
            "target": str(target),
            "runtime_gate": {"ok": False, "tool": "ast.parse", "message": str(exc)},
            "finding_count": 0,
            "findings": [],
        }
        return payload

    runtime_gate = run_runtime_gate(target)
    findings: list[Finding] = []
    findings.extend(detect_unused_imports(tree))
    findings.extend(detect_unused_assignments(tree))
    findings.extend(detect_loader_guard(text, tree))

    return {
        "status": "ok" if runtime_gate["ok"] else "runtime_gate_failed",
        "generated_at": _now_iso(),
        "target": str(target),
        "runtime_gate": runtime_gate,
        "finding_count": len(findings),
        "findings": [finding.to_dict() for finding in findings],
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# python-static-diagnostic-fixer audit summary",
        "",
        f"- generated_at: `{payload['generated_at']}`",
        f"- target: `{payload['target']}`",
        f"- status: `{payload['status']}`",
        f"- runtime_gate_ok: `{payload['runtime_gate']['ok']}`",
        f"- finding_count: `{payload['finding_count']}`",
        "",
        "## Runtime Gate",
        "",
        f"- tool: `{payload['runtime_gate']['tool']}`",
        f"- message: {payload['runtime_gate']['message']}",
        "",
        "## Findings",
        "",
    ]

    if not payload["findings"]:
        lines.append("- no static findings")
        return "\n".join(lines) + "\n"

    for finding in payload["findings"]:
        lines.extend(
            [
                f"- `{finding['category']}` / `{finding['name']}`",
                f"  - line: `{finding['line']}`",
                f"  - evidence: {finding['evidence']}",
                f"  - recommendation: {finding['recommendation']}",
            ]
        )

    return "\n".join(lines) + "\n"


def cmd_audit(args: argparse.Namespace) -> int:
    target = Path(args.target)
    payload = audit_target(target)

    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[INFO] JSON report written: {args.output_json}", file=sys.stderr)
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))

    if args.output_md:
        Path(args.output_md).write_text(render_markdown(payload), encoding="utf-8")
        print(f"[INFO] Markdown report written: {args.output_md}", file=sys.stderr)

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit Python files for safe static-diagnostic fix patterns.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Audit one Python file for runtime gate and safe-fix candidates.")
    audit_parser.add_argument("--target", required=True, help="Path to Python file.")
    audit_parser.add_argument("--output-json", help="Optional output path for JSON report.")
    audit_parser.add_argument("--output-md", help="Optional output path for Markdown report.")
    audit_parser.set_defaults(func=cmd_audit)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
