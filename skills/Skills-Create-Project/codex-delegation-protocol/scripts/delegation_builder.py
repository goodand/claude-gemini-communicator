#!/usr/bin/env python3
"""codex-delegation-protocol 통합 래퍼.

task-packet을 Codex 위임 메시지로 변환하고 실행 커맨드를 생성한다.

Usage:
    python3 delegation_builder.py compose --packet <packet.json> [--dispatch <dispatch.json>] [--output <msg.md>]
    python3 delegation_builder.py validate --message <msg.md>
    python3 delegation_builder.py command --packet <packet.json> [--worktree <path>] [--model <model>] [--sandbox <mode>]
    python3 delegation_builder.py preview --packet <packet.json>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import sys
from datetime import datetime, timezone, timedelta

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KST = timezone(timedelta(hours=9))

REQUIRED_SECTIONS = ["Mission", "Scope", "Context", "Constraints", "Done Definition"]

FORBIDDEN_PATTERNS = [
    (r"```[\s\S]{500,}```", "코드 블록 500자 초과 — 경로만 전달할 것"),
    (r"(password|secret|api.?key)\s*[:=]", "보안 정보 포함 금지"),
]

DEFAULT_MODEL = "gpt-5.3-codex"
DEFAULT_SANDBOX = "workspace-write"
SANDBOX_OPTIONS = {"read-only", "workspace-write", "danger-full-access"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _load_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _save_text(path, text):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def _err(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# compose: packet → 위임 메시지 조립
# ---------------------------------------------------------------------------

def compose_message(packet, dispatch=None):
    """task-packet에서 5-section 위임 메시지를 조립한다."""
    errors = []

    # 필수 필드 검증
    for field in ("goal", "allowed_paths", "done_definition"):
        if field not in packet:
            errors.append(f"packet에 '{field}' 필드 없음")
    if errors:
        return None, errors

    lines = []

    # --- Mission ---
    lines.append("## Mission")
    lines.append("")
    goal = packet["goal"]
    why = packet.get("why", "")
    lines.append(goal)
    if why:
        lines.append(f"이유: {why}")
    lines.append("")

    # --- Scope ---
    lines.append("## Scope")
    lines.append("")
    lines.append("- allowed_paths:")
    for p in packet["allowed_paths"]:
        lines.append(f"  - {p}")

    forbidden = packet.get("forbidden_paths", [])
    if not forbidden:
        constraints = packet.get("constraints", {})
        forbidden = constraints.get("must_not_modify", [])
    if forbidden:
        lines.append("- forbidden_paths:")
        for p in forbidden:
            lines.append(f"  - {p}")
    lines.append("- 이 범위 밖의 파일은 읽기만 가능")
    lines.append("")

    # dispatch worktree 정보
    if dispatch:
        wt = dispatch.get("worktree_path", "")
        br = dispatch.get("branch", "")
        if wt or br:
            lines.append(f"- worktree: `{wt}` (branch: `{br}`)")
            lines.append("")

    # --- Context ---
    lines.append("## Context")
    lines.append("")
    ctx_files = packet.get("context_files", [])
    if ctx_files:
        for cf in ctx_files:
            if isinstance(cf, dict):
                lines.append(f"- `{cf.get('path', cf)}` — {cf.get('description', '참고 파일')}")
            else:
                lines.append(f"- `{cf}` — 참고 파일")
    else:
        lines.append("- (context_files 없음)")

    handoff = packet.get("handoff_notes", "")
    if handoff:
        lines.append(f"- 참고: {handoff}")
    lines.append("")

    # --- Constraints ---
    lines.append("## Constraints")
    lines.append("")
    constraints = packet.get("constraints", {})
    if constraints.get("must_run_tests"):
        lines.append("- must_run_tests: true")
    else:
        lines.append("- must_run_tests: false")
    if constraints.get("must_not_modify"):
        lines.append(f"- must_not_modify: {constraints['must_not_modify']}")
    if constraints.get("must_not_use_network", True):
        lines.append("- must_not_use_network: true")
    else:
        lines.append("- must_not_use_network: false (네트워크 허용)")

    # non_goals
    non_goals = packet.get("non_goals", [])
    if non_goals:
        lines.append("- non_goals:")
        for ng in non_goals:
            if isinstance(ng, dict):
                lines.append(f"  - [{ng.get('case', '?')}] {ng.get('description', '')}")
            else:
                lines.append(f"  - {ng}")
    lines.append("")

    # --- Done Definition ---
    lines.append("## Done Definition")
    lines.append("")
    done = packet.get("done_definition", [])
    for i, d in enumerate(done, 1):
        lines.append(f"{i}. {d}")

    # required_checks
    checks = packet.get("required_checks", [])
    if checks:
        lines.append("")
        lines.append("검증 커맨드:")
        for c in checks:
            if isinstance(c, dict):
                ctype = c.get("type", "command")
                if ctype == "command":
                    lines.append(f"- `{c.get('command', c.get('value', '?'))}`")
                elif ctype == "file_exists":
                    lines.append(f"- 파일 존재: `{c.get('path', c.get('value', '?'))}`")
                elif ctype == "pattern_match":
                    lines.append(f"- 패턴 매칭: `{c.get('pattern', c.get('value', '?'))}` in `{c.get('path', '?')}`")
            else:
                lines.append(f"- `{c}`")

    lines.append("")
    lines.append("작업 완료 후 각 조건의 충족 여부를 보고할 것.")

    return "\n".join(lines), []


def cmd_compose(args):
    packet = _load_json(args.packet)

    dispatch = None
    if args.dispatch:
        dispatch = _load_json(args.dispatch)

    msg, errors = compose_message(packet, dispatch)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        _save_text(args.output, msg)
        print(f"[OK] 위임 메시지 저장: {args.output}", file=sys.stderr)
    print(msg)


# ---------------------------------------------------------------------------
# validate: 위임 메시지 검증
# ---------------------------------------------------------------------------

def validate_message(text):
    """위임 메시지의 5-section 완전성과 금지 패턴을 검증한다."""
    errors = []
    warnings = []

    # 섹션 존재 확인
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+{re.escape(section)}"
        if not re.search(pattern, text, re.MULTILINE):
            errors.append(f"필수 섹션 누락: '## {section}'")

    # 금지 패턴 검사
    for pat, reason in FORBIDDEN_PATTERNS:
        if re.search(pat, text, re.IGNORECASE):
            errors.append(f"금지 패턴 발견: {reason}")

    # 경고: done definition이 모호한 경우
    done_section = re.search(
        r"## Done Definition\s*\n(.*?)(?=\n## |\Z)",
        text, re.DOTALL
    )
    if done_section:
        done_text = done_section.group(1)
        vague_words = ["잘", "적절히", "깔끔하게", "properly", "nicely", "well"]
        for w in vague_words:
            if w in done_text.lower():
                warnings.append(f"Done Definition에 모호한 표현 '{w}' — 기계 검증 가능한 조건으로 변경 권장")

    # 경고: context에 파일 내용 직접 삽입 의심
    if text.count("```") >= 4:
        warnings.append("코드 블록 4개 이상 — 파일 내용을 직접 삽입한 것은 아닌지 확인")

    return errors, warnings


def cmd_validate(args):
    text = _load_text(args.message)
    errors, warnings = validate_message(text)

    for w in warnings:
        print(f"[WARN] {w}", file=sys.stderr)
    for e in errors:
        print(f"[ERROR] {e}", file=sys.stderr)

    if errors:
        print(f"[FAIL] {len(errors)}개 오류 발견")
        sys.exit(1)
    else:
        status = "PASS" if not warnings else "PASS (경고 있음)"
        print(f"[OK] 위임 메시지 검증 {status}")


# ---------------------------------------------------------------------------
# command: 실행 커맨드 문자열 생성
# ---------------------------------------------------------------------------

def build_command(packet, worktree=None, model=None, sandbox=None):
    """codex exec 커맨드 문자열을 생성한다."""
    model = model or DEFAULT_MODEL
    sandbox = sandbox or DEFAULT_SANDBOX

    if sandbox not in SANDBOX_OPTIONS:
        return None, f"잘못된 sandbox 옵션: {sandbox} (허용: {SANDBOX_OPTIONS})"

    # 프롬프트 조립 (간결 버전)
    msg, errors = compose_message(packet)
    if errors:
        return None, f"프롬프트 조립 실패: {errors}"

    # 커맨드 구성
    parts = ["codex", "exec"]
    parts.extend(["-m", model])
    parts.append("--full-auto")

    if sandbox != "read-only":
        parts.extend(["--sandbox", sandbox])

    # worktree가 있으면 해당 디렉토리에서 실행
    prompt = msg.replace("\n", "\\n")

    # 셸에서 실행할 수 있는 형태로
    cmd_str = " ".join(parts) + " " + shlex.quote(msg)

    if worktree:
        cmd_str = f"cd {shlex.quote(worktree)} && {cmd_str}"

    return cmd_str, None


def cmd_command(args):
    packet = _load_json(args.packet)
    cmd_str, err = build_command(
        packet,
        worktree=args.worktree,
        model=args.model,
        sandbox=args.sandbox,
    )
    if err:
        _err(err)
    print(cmd_str)


# ---------------------------------------------------------------------------
# preview: 위임 메시지 미리보기 (조립 + 검증 + 커맨드)
# ---------------------------------------------------------------------------

def cmd_preview(args):
    packet = _load_json(args.packet)

    dispatch = None
    if args.dispatch:
        dispatch = _load_json(args.dispatch)

    msg, errors = compose_message(packet, dispatch)
    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 60)
    print("DELEGATION MESSAGE PREVIEW")
    print("=" * 60)
    print()
    print(msg)
    print()
    print("=" * 60)
    print("VALIDATION")
    print("=" * 60)

    verrs, vwarns = validate_message(msg)
    for w in vwarns:
        print(f"  [WARN] {w}")
    for e in verrs:
        print(f"  [ERROR] {e}")
    if not verrs and not vwarns:
        print("  [OK] 모든 검증 통과")

    print()
    print("=" * 60)
    print("EXECUTION COMMAND")
    print("=" * 60)

    cmd_str, err = build_command(
        packet,
        worktree=args.worktree,
        model=args.model,
        sandbox=args.sandbox,
    )
    if err:
        print(f"  [ERROR] {err}")
    else:
        print()
        print(cmd_str)

    # 메타 정보
    print()
    print("=" * 60)
    print("META")
    print("=" * 60)
    print(f"  task_id: {packet.get('task_id', '?')}")
    print(f"  title: {packet.get('title', '?')}")
    print(f"  priority: {packet.get('priority', '?')}")
    print(f"  allowed_paths: {len(packet.get('allowed_paths', []))} entries")
    print(f"  context_files: {len(packet.get('context_files', []))} entries")
    print(f"  done_definition: {len(packet.get('done_definition', []))} items")
    print(f"  generated_at: {_now_iso()}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="codex-delegation-protocol 통합 래퍼"
    )
    sub = parser.add_subparsers(dest="command")

    # compose
    p_compose = sub.add_parser("compose", help="packet → 위임 메시지 조립")
    p_compose.add_argument("--packet", required=True, help="task-packet JSON 경로")
    p_compose.add_argument("--dispatch", help="dispatch JSON 경로 (선택)")
    p_compose.add_argument("--output", "-o", help="출력 파일 경로")

    # validate
    p_validate = sub.add_parser("validate", help="위임 메시지 검증")
    p_validate.add_argument("--message", required=True, help="위임 메시지 파일 경로")

    # command
    p_cmd = sub.add_parser("command", help="실행 커맨드 문자열 생성")
    p_cmd.add_argument("--packet", required=True, help="task-packet JSON 경로")
    p_cmd.add_argument("--worktree", help="worktree 경로")
    p_cmd.add_argument("--model", default=DEFAULT_MODEL, help=f"모델 (기본: {DEFAULT_MODEL})")
    p_cmd.add_argument("--sandbox", default=DEFAULT_SANDBOX, help=f"샌드박스 모드 (기본: {DEFAULT_SANDBOX})")

    # preview
    p_preview = sub.add_parser("preview", help="조립 + 검증 + 커맨드 일괄 미리보기")
    p_preview.add_argument("--packet", required=True, help="task-packet JSON 경로")
    p_preview.add_argument("--dispatch", help="dispatch JSON 경로 (선택)")
    p_preview.add_argument("--worktree", help="worktree 경로")
    p_preview.add_argument("--model", default=DEFAULT_MODEL, help=f"모델 (기본: {DEFAULT_MODEL})")
    p_preview.add_argument("--sandbox", default=DEFAULT_SANDBOX, help=f"샌드박스 모드 (기본: {DEFAULT_SANDBOX})")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "compose": cmd_compose,
        "validate": cmd_validate,
        "command": cmd_command,
        "preview": cmd_preview,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
