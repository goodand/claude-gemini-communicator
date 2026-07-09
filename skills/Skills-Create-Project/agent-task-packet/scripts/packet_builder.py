#!/usr/bin/env python3
"""Agent Task Packet 관리자 — 생성/검증/렌더링/조회 통합 래퍼.

사용법:
    python3 packet_builder.py new --task-id TASK-0001 --title "인증 모듈 구현"
    python3 packet_builder.py validate .codex/packets/TASK-0001.json
    python3 packet_builder.py show .codex/packets/TASK-0001.json [--raw]
    python3 packet_builder.py render-prompt .codex/packets/TASK-0001.json
    python3 packet_builder.py list [--dir .codex/packets]
    python3 packet_builder.py check-paths .codex/packets/TASK-0001.json .codex/packets/TASK-0002.json
    python3 packet_builder.py update-revision .codex/packets/TASK-0001.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Packet Schema Definition
# ---------------------------------------------------------------------------

PACKET_VERSION = "0.1"

REQUIRED_FIELDS = {
    "packet_version", "task_id", "title", "goal", "why",
    "allowed_paths", "context_files", "priority",
    "constraints", "done_definition", "required_checks", "deliverables",
    "revision", "created_at", "created_by", "updated_at",
}

OPTIONAL_FIELDS = {
    "forbidden_paths", "depends_on", "parallel_group",
    "non_goals", "handoff_notes",
    "branch_hint", "worktree_hint", "launch_hint",
    "trace_id", "parent_task_id",
    # 운영 안전 필드 — extended가 아니라 core optional.
    # timeout 없는 worker는 무한 실행 위험, stop_conditions 없으면 범위 초과 방지 불가.
    "timeout_minutes", "stop_conditions",
}

# v0.2 Extended Profile 후보 필드 — core를 깨지 않는 opt-in 메타데이터.
# consumer는 이 필드를 무시해도 정상 동작해야 한다.
EXTENDED_FIELDS = {
    "packet_profile",       # "standard" | "extended"
    "repo_root", "source_of_truth", "env_requirements",
    "failure_guide", "report_format",
}

# 설명용 메타 블록 — 템플릿에서 사용하는 주석 필드. validate 시 무시.
META_FIELDS = {"$schema_notes"}

# Runtime/dispatch 상태 — packet에 절대 넣지 않는다 (immutable 원칙)
FORBIDDEN_FIELDS = {
    # runtime/session/process
    "status", "session_name", "session_id", "pid",
    "heartbeat", "heartbeat_path", "retry_count", "last_heartbeat",
    "current_status", "log_path",
    # dispatch ownership
    "worktree_path", "branch", "locked_paths", "assigned_agent",
    "dispatch_id", "dispatch_version",
}

# done_definition 호환성: v0.1에서 string[]로 유지한다.
# object-array 전환은 proposal-only 상태이며, 필요 시 extended profile에서 별도로 검토.
# 이 주석은 P2 (Consumer Compatibility Lock) 결정 기록이다.

VALID_PRIORITIES = {"critical", "high", "medium", "low"}

NON_GOAL_CASES = {"state", "type", "scope", "performance:null", "performance:over", "performance:under"}

VALID_CHECK_TYPES = {"command", "file_exists", "pattern_match"}


def _now_iso():
    return datetime.now().astimezone().isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# State Milestone: Dispatch Status Transition (ToolSandbox 3-Milestone AND)
# ---------------------------------------------------------------------------

DISPATCH_STATUSES = {
    "queued", "ready", "running", "complete",
    "failed", "merged", "blocked", "abandoned",
}

DISPATCH_TRANSITIONS = {
    "queued":    {"ready", "blocked", "abandoned"},
    "ready":     {"running", "blocked"},
    "running":   {"complete", "failed", "abandoned"},
    "blocked":   {"ready"},
    "failed":    {"running"},          # retry
    "complete":  {"merged", "abandoned"},
    "merged":    set(),                # terminal
    "abandoned": set(),                # terminal
}

TERMINAL_STATUSES = {"merged", "abandoned"}

# dispatch에 넣지 않는 필드 — packet 계약 내용 중복 금지
DISPATCH_FORBIDDEN_FIELDS = {
    "goal", "why", "done_definition", "required_checks",
    "deliverables", "constraints", "non_goals", "context_files", "priority",
}


def validate_dispatch_transition(from_status, to_status):
    """dispatch status 전이가 유효한지 검사.

    Returns: (valid: bool, reason: str)
    """
    if from_status not in DISPATCH_STATUSES:
        return False, f"알 수 없는 from_status: '{from_status}'"
    if to_status not in DISPATCH_STATUSES:
        return False, f"알 수 없는 to_status: '{to_status}'"
    if from_status in TERMINAL_STATUSES:
        return False, f"terminal status '{from_status}'에서는 전이 불가"
    if to_status not in DISPATCH_TRANSITIONS.get(from_status, set()):
        allowed = sorted(DISPATCH_TRANSITIONS[from_status])
        return False, f"'{from_status}' → '{to_status}' 전이 불가. 허용: {allowed}"
    return True, ""


def validate_dispatch(data):
    """Dispatch JSON 검증. (errors, warnings) 반환.

    State Milestone: history의 모든 전이가 유효 전이 집합에 속하는지,
    마지막 history.to와 current status가 일치하는지 검사한다.
    """
    errors = []
    warnings = []

    # 1. 필수 필드 체크
    required = {
        "dispatch_version", "dispatch_id", "task_id", "packet_path",
        "branch", "worktree_path", "assigned_agent", "status",
        "locked_paths", "history", "created_at", "created_by", "updated_at",
    }
    missing = required - set(data.keys())
    if missing:
        errors.append(f"필수 필드 누락: {sorted(missing)}")

    # 2. status 유효성
    status = data.get("status")
    if status and status not in DISPATCH_STATUSES:
        errors.append(f"알 수 없는 status: '{status}'")

    # 3. history 전이 검증
    history = data.get("history", [])
    for i, entry in enumerate(history):
        if not isinstance(entry, dict):
            errors.append(f"history[{i}]: dict가 아님")
            continue
        from_s = entry.get("from")
        to_s = entry.get("to")
        if from_s is None and i == 0:
            # 첫 항목은 from=null 허용 (초기 생성)
            if to_s and to_s not in DISPATCH_STATUSES:
                errors.append(f"history[{i}]: 알 수 없는 to_status '{to_s}'")
            continue
        if from_s is not None and to_s is not None:
            valid, reason = validate_dispatch_transition(from_s, to_s)
            if not valid:
                errors.append(f"history[{i}]: {reason}")

    # 4. history 연속성: 마지막 to == current status
    if history and status:
        last_to = history[-1].get("to") if isinstance(history[-1], dict) else None
        if last_to and last_to != status:
            errors.append(
                f"history 마지막 to='{last_to}'와 현재 status='{status}'가 불일치"
            )

    # 5. 금지 필드 — packet 계약 중복 저장 금지
    for f in DISPATCH_FORBIDDEN_FIELDS:
        if f in data:
            errors.append(
                f"금지 필드 포함: '{f}'"
                " — dispatch는 packet 계약 내용을 중복 소유하지 않는다"
            )

    return errors, warnings


def _normalize_path(p):
    """경로 정규화: symlink, .., 중복 slash 제거 → repo root 상대경로."""
    return os.path.normpath(p)


def _done_ref_to_index(ref):
    """D-1 형식 done_ref를 0-based index로 변환한다."""
    if not isinstance(ref, str):
        return None
    match = re.fullmatch(r"D-(\d+)", ref.strip())
    if not match:
        return None
    return int(match.group(1)) - 1


# ---------------------------------------------------------------------------
# Response Milestone Coverage (ToolSandbox 3-Milestone AND 대응)
# ---------------------------------------------------------------------------

def response_coverage(data):
    """done_definition의 required_checks + deliverables 커버리지 계산.

    ToolSandbox Response milestone 대응: done_definition의 몇 %가
    required_checks 또는 deliverables의 done_ref / done_index로 machine-verifiable한지 측정.

    Returns: float (0.0 ~ 1.0). done_definition이 비어있으면 0.0.
    """
    defs = data.get("done_definition", [])
    if not defs:
        return 0.0
    n = len(defs)
    covered = set()
    for check in data.get("required_checks", []):
        idx = None
        if isinstance(check, dict):
            if "done_ref" in check:
                idx = _done_ref_to_index(check.get("done_ref"))
            elif "done_index" in check:
                idx = check.get("done_index")
        if isinstance(idx, int) and 0 <= idx < n:
            covered.add(idx)
    for d in data.get("deliverables", []):
        idx = None
        if isinstance(d, dict):
            if "done_ref" in d:
                idx = _done_ref_to_index(d.get("done_ref"))
            elif "done_index" in d:
                idx = d.get("done_index")
        if isinstance(idx, int) and 0 <= idx < n:
            covered.add(idx)
    return len(covered) / n


# ---------------------------------------------------------------------------
# Scaffold (new)
# ---------------------------------------------------------------------------

def make_scaffold(task_id, title, profile="standard"):
    """필수 필드를 빠짐없이 채운 scaffold packet 생성.

    profile="standard" → core only
    profile="extended" → core + extended fields 포함

    packet_version은 항상 "0.1"이다 (core schema version).
    standard/extended 구분은 packet_profile 필드로만 한다.
    version을 "0.2"로 올리는 것은 breaking schema change를 암시하므로 사용하지 않는다.
    """
    now = _now_iso()
    packet = {
        "packet_version": PACKET_VERSION,
        "packet_profile": profile,
        "task_id": task_id,
        "title": title,
        "goal": "",
        "why": "",
        "allowed_paths": [],
        "forbidden_paths": [],
        "context_files": [],
        "depends_on": [],
        "parallel_group": None,
        "priority": "medium",
        "constraints": {
            "must_not_modify": [],
            "must_run_tests": False,
            "must_not_use_network": True,
            "notes": "",
        },
        "non_goals": [],
        "done_definition": [],
        "required_checks": [],
        "deliverables": [],
        "handoff_notes": "",
        "branch_hint": f"feat/codex-{task_id.lower()}",
        "worktree_hint": f".worktrees/{task_id.lower()}",
        "launch_hint": None,
        "trace_id": None,
        "parent_task_id": None,
        "timeout_minutes": None,
        "stop_conditions": [],
        "revision": 1,
        "created_at": now,
        "created_by": "",
        "updated_at": now,
    }
    if profile == "extended":
        packet["repo_root"] = "."
        packet["source_of_truth"] = ""
        packet["env_requirements"] = {}
        packet["failure_guide"] = ""
        packet["report_format"] = ""
    return packet


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def _detect_profile(data):
    """packet_profile 필드로만 profile 판별. implicit detection 없음.

    packet_profile이 없으면 standard. extended 필드가 있어도
    packet_profile: "extended"가 없으면 standard로 판별한다.
    """
    explicit = data.get("packet_profile")
    if explicit in ("standard", "extended"):
        return explicit
    return "standard"


def validate_packet(data, profile=None):
    """Packet JSON 검증. (errors, warnings) 반환.

    profile=None → packet_profile 필드로 판별 (없으면 standard)
    profile="standard" → core only (extended 필드 존재 시 에러)
    profile="extended" → extended 필드 타입도 검증
    """
    errors = []
    warnings = []
    effective_profile = profile or _detect_profile(data)

    # 1. 금지 필드 체크 — runtime/dispatch 소유 필드
    for f in FORBIDDEN_FIELDS:
        if f in data:
            errors.append(f"금지 필드 포함: '{f}' — packet은 runtime/dispatch 상태를 담지 않는다")

    # 1.5. Standard profile strict boundary — extended-only 필드 금지
    if effective_profile == "standard":
        extended_only = EXTENDED_FIELDS - {"packet_profile"}
        found = sorted(f for f in extended_only if f in data)
        if found:
            errors.append(
                f"standard profile에 extended 필드 존재: {found}"
                " — packet_profile을 'extended'로 설정하거나 필드를 제거해야 한다"
            )

    # 2. 필수 필드 체크
    missing = REQUIRED_FIELDS - set(data.keys())
    if missing:
        errors.append(f"필수 필드 누락: {sorted(missing)}")

    # 2.5. 알 수 없는 필드 경고 (extended/meta 필드는 허용)
    known = REQUIRED_FIELDS | OPTIONAL_FIELDS | EXTENDED_FIELDS | META_FIELDS | FORBIDDEN_FIELDS
    unknown = set(data.keys()) - known
    if unknown:
        warnings.append(f"알 수 없는 필드: {sorted(unknown)} — extended candidate이면 EXTENDED_FIELDS에 등록 필요")

    # 2.6. Extended field 타입 검증 (profile=extended일 때만)
    if effective_profile == "extended":
        if "packet_profile" in data and data["packet_profile"] not in ("standard", "extended"):
            errors.append(f"잘못된 packet_profile '{data['packet_profile']}' — 허용: standard, extended")
        if "repo_root" in data and not isinstance(data["repo_root"], str):
            errors.append("repo_root는 문자열")
        if "source_of_truth" in data and not isinstance(data["source_of_truth"], str):
            errors.append("source_of_truth는 문자열")
        if "env_requirements" in data and not isinstance(data["env_requirements"], (dict, type(None))):
            errors.append("env_requirements는 object 또는 null")
        if "failure_guide" in data and not isinstance(data["failure_guide"], str):
            errors.append("failure_guide는 문자열")
        if "report_format" in data and not isinstance(data["report_format"], str):
            errors.append("report_format는 문자열")

    # 2.7. Core optional 타입 검증 — profile 무관하게 항상 검사
    if "timeout_minutes" in data:
        tm = data["timeout_minutes"]
        if tm is not None and not isinstance(tm, int):
            errors.append("timeout_minutes는 정수 또는 null")
    if "stop_conditions" in data and not isinstance(data["stop_conditions"], list):
        errors.append("stop_conditions는 string[]")

    # 3. 필드별 세부 검증

    # packet_version — 항상 "0.1". version으로 profile을 구분하지 않는다.
    if "packet_version" in data and data["packet_version"] != PACKET_VERSION:
        errors.append(f"packet_version은 '{PACKET_VERSION}'이어야 한다 — standard/extended 구분은 packet_profile로 한다")

    if "goal" in data and len(str(data["goal"])) < 10:
        errors.append("goal이 너무 짧다 (최소 10자)")

    if "why" in data and len(str(data.get("why", "")).strip()) < 5:
        errors.append("why가 너무 짧다 (최소 5자) — 이 작업이 필요한 이유를 명시해야 한다")

    if "allowed_paths" in data:
        paths = data["allowed_paths"]
        if not isinstance(paths, list) or len(paths) == 0:
            errors.append("allowed_paths는 1개 이상 필요")
        else:
            # 중복 검사 (정규화 후)
            normalized = [_normalize_path(p) for p in paths]
            if len(normalized) != len(set(normalized)):
                errors.append("allowed_paths에 중복 경로 존재")

    if "forbidden_paths" in data and "allowed_paths" in data:
        forbidden = set(_normalize_path(p) for p in data.get("forbidden_paths", []))
        allowed = set(_normalize_path(p) for p in data.get("allowed_paths", []))
        overlap = forbidden & allowed
        if overlap:
            errors.append(f"allowed_paths와 forbidden_paths 겹침: {sorted(overlap)}")

    if "constraints" in data:
        constraints = data["constraints"]
        if not isinstance(constraints, dict):
            errors.append("constraints는 object")
        else:
            must_not_modify = constraints.get("must_not_modify", [])
            if must_not_modify and not isinstance(must_not_modify, list):
                errors.append("constraints.must_not_modify는 string[]")
            elif isinstance(must_not_modify, list):
                forbidden = data.get("forbidden_paths", [])
                if must_not_modify and not isinstance(forbidden, list):
                    errors.append("constraints.must_not_modify가 있으면 forbidden_paths는 string[]여야 한다")
                elif must_not_modify:
                    forbidden_set = {_normalize_path(p) for p in forbidden}
                    missing = [
                        p for p in must_not_modify
                        if _normalize_path(p) not in forbidden_set
                    ]
                    if missing:
                        errors.append(
                            "constraints.must_not_modify ⊆ forbidden_paths 규칙 위반: "
                            f"{missing}"
                        )

            has_tool_policy = any(k in constraints for k in ("allowed_tools", "forbidden_tools"))
            if has_tool_policy and effective_profile != "extended":
                errors.append(
                    "standard profile에는 constraints.allowed_tools / forbidden_tools를 넣을 수 없다"
                    " — packet_profile을 'extended'로 설정해야 한다"
                )
            for key in ("allowed_tools", "forbidden_tools"):
                if key in constraints:
                    value = constraints[key]
                    if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
                        errors.append(f"constraints.{key}는 string[] (각 항목은 비어있지 않은 문자열)")
            if constraints.get("allowed_tools") and constraints.get("forbidden_tools"):
                warnings.append(
                    "constraints.allowed_tools와 forbidden_tools가 함께 지정됨"
                    " — 화이트리스트(allowed_tools)를 우선 해석할 것"
                )

    if "done_definition" in data:
        defs = data["done_definition"]
        if not isinstance(defs, list) or len(defs) == 0:
            errors.append("done_definition은 최소 1개 이상 필요")
        elif not all(isinstance(d, str) for d in defs):
            errors.append("done_definition 원소는 모두 문자열이어야 한다 — object[] 전환은 proposal-only")

    if "priority" in data:
        if data["priority"] not in VALID_PRIORITIES:
            errors.append(f"잘못된 priority '{data['priority']}' — 허용: {sorted(VALID_PRIORITIES)}")

    if "required_checks" in data:
        for i, check in enumerate(data["required_checks"]):
            if isinstance(check, dict):
                if "type" not in check:
                    warnings.append(f"required_checks[{i}]: 'type' 필드 권장")
                if "done_ref" in check:
                    idx = _done_ref_to_index(check["done_ref"])
                    if idx is None:
                        errors.append(f"required_checks[{i}].done_ref는 'D-<n>' 형식이어야 한다")
                if "done_ref" in check and "done_index" in check:
                    idx = _done_ref_to_index(check["done_ref"])
                    if isinstance(idx, int) and idx != check["done_index"]:
                        errors.append(
                            f"required_checks[{i}] done_ref/done_index 불일치:"
                            f" {check['done_ref']} vs {check['done_index']}"
                        )
            # 문자열도 허용하지만 구조화 권장
            elif isinstance(check, str):
                warnings.append(f"required_checks[{i}]: 구조화된 객체 권장 (type, value, required)")

    if "deliverables" in data:
        for i, d in enumerate(data["deliverables"]):
            if isinstance(d, dict) and "path" not in d:
                warnings.append(f"deliverables[{i}]: 'path' 필드 권장")
            if isinstance(d, dict) and "done_ref" in d:
                idx = _done_ref_to_index(d["done_ref"])
                if idx is None:
                    errors.append(f"deliverables[{i}].done_ref는 'D-<n>' 형식이어야 한다")
            if isinstance(d, dict) and "done_ref" in d and "done_index" in d:
                idx = _done_ref_to_index(d["done_ref"])
                if isinstance(idx, int) and idx != d["done_index"]:
                    errors.append(
                        f"deliverables[{i}] done_ref/done_index 불일치:"
                        f" {d['done_ref']} vs {d['done_index']}"
                    )

    if "non_goals" in data:
        for i, ng in enumerate(data["non_goals"]):
            if isinstance(ng, dict):
                case = ng.get("case", "")
                if case and case not in NON_GOAL_CASES:
                    warnings.append(f"non_goals[{i}]: 알 수 없는 case '{case}' — 허용: {sorted(NON_GOAL_CASES)}")

    # 3.5. Traceability: done_ref / done_index 범위 검증 + 커버리지 경고
    n_defs = len(data.get("done_definition", []))
    all_traceable = data.get("required_checks", []) + data.get("deliverables", [])

    for i, check in enumerate(data.get("required_checks", [])):
        if isinstance(check, dict):
            idx = None
            label = None
            if "done_ref" in check:
                idx = _done_ref_to_index(check["done_ref"])
                label = f"required_checks[{i}].done_ref={check['done_ref']}"
            elif "done_index" in check:
                idx = check["done_index"]
                label = f"required_checks[{i}].done_index={idx}"
            if label is not None and (not isinstance(idx, int) or idx < 0 or idx >= n_defs):
                errors.append(f"{label} — done_definition 범위 밖 (0~{n_defs - 1})")

    for i, d in enumerate(data.get("deliverables", [])):
        if isinstance(d, dict):
            idx = None
            label = None
            if "done_ref" in d:
                idx = _done_ref_to_index(d["done_ref"])
                label = f"deliverables[{i}].done_ref={d['done_ref']}"
            elif "done_index" in d:
                idx = d["done_index"]
                label = f"deliverables[{i}].done_index={idx}"
            if label is not None and (not isinstance(idx, int) or idx < 0 or idx >= n_defs):
                errors.append(f"{label} — done_definition 범위 밖 (0~{n_defs - 1})")

    # 커버리지 경고 — done_ref/done_index를 하나라도 쓰기 시작했으면 부분 커버리지를 알림
    has_any_trace_link = any(
        isinstance(item, dict) and ("done_index" in item or "done_ref" in item)
        for item in all_traceable
    )
    if n_defs > 0 and has_any_trace_link:
        cov = response_coverage(data)
        if cov < 1.0:
            uncovered = [
                i for i in range(n_defs)
                if not any(
                    isinstance(item, dict) and (
                        item.get("done_index") == i or _done_ref_to_index(item.get("done_ref")) == i
                    )
                    for item in all_traceable
                )
            ]
            warnings.append(
                f"done_definition 커버리지 {cov:.0%}"
                f" — 검증 연결 없는 항목: {uncovered}"
            )

    if "revision" in data:
        if not isinstance(data["revision"], int) or data["revision"] < 1:
            errors.append("revision은 1 이상 정수")

    if "task_id" in data:
        if not isinstance(data["task_id"], str):
            errors.append("task_id는 문자열")
        elif not data["task_id"].strip():
            errors.append("task_id가 비어있다")

    return errors, warnings


# ---------------------------------------------------------------------------
# Render Prompt (3-block compact prompt for Codex worker)
# ---------------------------------------------------------------------------

def render_prompt(data):
    """Codex worker에게 보낼 compact prompt 생성. 3블록 구조."""
    lines = []

    # Block 1: Goal
    lines.append("## Goal")
    lines.append(f"Task: {data.get('task_id', '?')} — {data.get('title', '?')}")
    lines.append(f"{data.get('goal', '')}")
    if data.get("why"):
        lines.append(f"Why: {data['why']}")
    lines.append("")

    # Non-goals
    non_goals = data.get("non_goals", [])
    if non_goals:
        lines.append("### Non-goals (이번 태스크에서 하지 않는 것)")
        for ng in non_goals:
            if isinstance(ng, dict):
                case_tag = f"[{ng.get('case', '?')}]" if ng.get("case") else ""
                lines.append(f"- {case_tag} {ng.get('description', '')}")
            else:
                lines.append(f"- {ng}")
        lines.append("")

    # Block 2: Scope
    lines.append("## Scope")
    lines.append("### Allowed paths (이 경로만 수정 가능)")
    for p in data.get("allowed_paths", []):
        lines.append(f"- {p}")
    forbidden = data.get("forbidden_paths", [])
    if forbidden:
        lines.append("### Forbidden paths (절대 수정 금지)")
        for p in forbidden:
            lines.append(f"- {p}")
    ctx = data.get("context_files", [])
    if ctx:
        lines.append("### Context files (참고용, 읽기만)")
        for p in ctx:
            lines.append(f"- {p}")
    constraints = data.get("constraints", {})
    if constraints:
        lines.append("### Constraints")
        if constraints.get("must_not_modify"):
            lines.append(f"- must_not_modify: {constraints['must_not_modify']}")
        if constraints.get("must_run_tests"):
            lines.append("- must_run_tests: true")
        if constraints.get("must_not_use_network"):
            lines.append("- must_not_use_network: true")
        if constraints.get("notes"):
            lines.append(f"- {constraints['notes']}")
    lines.append("")

    # Block 3: Done Definition
    lines.append("## Done Definition")
    for d in data.get("done_definition", []):
        lines.append(f"- {d}")
    checks = data.get("required_checks", [])
    if checks:
        lines.append("### Required checks")
        for c in checks:
            if isinstance(c, dict):
                extras = []
                if c.get("done_ref"):
                    extras.append(f"done_ref={c['done_ref']}")
                elif c.get("done_index") is not None:
                    extras.append(f"done_index={c['done_index']}")
                # 구조화 required_checks의 추가 필드를 prompt에서 잃지 않는다
                for _k in ("target", "operator", "expected", "evidence_path"):
                    _v = c.get(_k)
                    if _v not in (None, ""):
                        extras.append(f"{_k}={_v}")
                extra_str = f", {', '.join(extras)}" if extras else ""
                lines.append(
                    f"- [{c.get('type', '?')}] {c.get('value', '')}"
                    f" (required={c.get('required', True)}{extra_str})"
                )
            else:
                lines.append(f"- {c}")
    deliverables = data.get("deliverables", [])
    if deliverables:
        lines.append("### Deliverables")
        for d in deliverables:
            if isinstance(d, dict):
                lines.append(f"- {d.get('path', '?')} ({d.get('type', '?')}, required={d.get('required', True)})")
            else:
                lines.append(f"- {d}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_new(args):
    """scaffold 패킷 생성."""
    packet = make_scaffold(args.task_id, args.title, profile=args.profile)
    out_dir = Path(args.dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.task_id}.json"
    if out_path.exists() and not args.force:
        print(f"[ERROR] 이미 존재: {out_path} (--force로 덮어쓰기)", file=sys.stderr)
        sys.exit(1)
    out_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    profile_label = f" [profile={args.profile}]" if args.profile != "standard" else ""
    print(f"[OK] scaffold 생성: {out_path}{profile_label}")
    print(f"[INFO] goal, why, allowed_paths, done_definition 등을 채워야 합니다.")


def cmd_validate(args):
    """packet JSON 검증."""
    total_errors = 0
    for path_str in args.files:
        path = Path(path_str)
        if not path.exists():
            print(f"[ERROR] 파일 없음: {path}", file=sys.stderr)
            total_errors += 1
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"[ERROR] {path.name}: JSON 파싱 실패 — {e}", file=sys.stderr)
            total_errors += 1
            continue

        errors, warnings = validate_packet(data, profile=getattr(args, "profile", None))
        for e in errors:
            print(f"[ERROR] {path.name}: {e}", file=sys.stderr)
        for w in warnings:
            print(f"[WARN] {path.name}: {w}", file=sys.stderr)

        if errors:
            total_errors += len(errors)
        else:
            warn_str = f" ({len(warnings)} warnings)" if warnings else ""
            print(f"[OK] {path.name}: 검증 통과{warn_str}")

    if total_errors:
        sys.exit(1)


def cmd_show(args):
    """packet 조회 (raw JSON 또는 human summary)."""
    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] 파일 없음: {path}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(path.read_text())

    if args.raw:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(f"Task: {data.get('task_id', '?')} — {data.get('title', '?')}")
        print(f"Priority: {data.get('priority', '?')} | Revision: {data.get('revision', '?')}")
        print(f"Goal: {data.get('goal', '?')}")
        print(f"Why: {data.get('why', '?')}")
        print(f"Allowed: {data.get('allowed_paths', [])}")
        forbidden = data.get("forbidden_paths", [])
        if forbidden:
            print(f"Forbidden: {forbidden}")
        print(f"Done: {data.get('done_definition', [])}")
        depends = data.get("depends_on", [])
        if depends:
            print(f"Depends on: {depends}")
        non_goals = data.get("non_goals", [])
        if non_goals:
            print(f"Non-goals: {len(non_goals)}개")
            for ng in non_goals:
                if isinstance(ng, dict):
                    print(f"  [{ng.get('case', '?')}] {ng.get('description', '')}")
                else:
                    print(f"  - {ng}")
        created_by = data.get('created_by', '').strip()
        created_at = data.get('created_at', '?')
        if created_by:
            print(f"Created: {created_at} by {created_by}")
        else:
            print(f"Created: {created_at}")


def cmd_render_prompt(args):
    """Codex worker용 compact prompt 렌더링."""
    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] 파일 없음: {path}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(path.read_text())
    print(render_prompt(data))


def cmd_list(args):
    """packet 목록 조회."""
    packet_dir = Path(args.dir)
    if not packet_dir.exists():
        print("[INFO] packet 디렉토리 없음.")
        return

    files = sorted(packet_dir.glob("*.json"))
    if not files:
        print("[INFO] packet 파일 없음.")
        return

    print(f"{'Task ID':<20} {'Title':<30} {'Priority':<10} {'Rev':<5} {'Depends'}")
    print("-" * 85)
    for f in files:
        try:
            data = json.loads(f.read_text())
            depends = ",".join(data.get("depends_on", [])) or "-"
            print(f"{data.get('task_id', '?'):<20} {data.get('title', '?')[:28]:<30} "
                  f"{data.get('priority', '?'):<10} {data.get('revision', '?'):<5} {depends}")
        except (json.JSONDecodeError, KeyError):
            print(f"{f.stem:<20} [파싱 실패]")

    # 필터링
    if args.priority:
        print(f"\n[필터: priority={args.priority}]")
    if args.group:
        print(f"[필터: parallel_group={args.group}]")


def cmd_check_paths(args):
    """여러 packet 간 경로 겹침 검사."""
    packets = {}
    for path_str in args.files:
        path = Path(path_str)
        if not path.exists():
            print(f"[WARN] 파일 없음: {path}", file=sys.stderr)
            continue
        try:
            data = json.loads(path.read_text())
            task_id = data.get("task_id", path.stem)
            packets[task_id] = [_normalize_path(p) for p in data.get("allowed_paths", [])]
        except json.JSONDecodeError:
            print(f"[WARN] {path.name}: JSON 파싱 실패", file=sys.stderr)

    if len(packets) < 2:
        print("[INFO] 2개 이상 packet 필요.")
        return

    overlaps = []
    task_ids = list(packets.keys())
    for i in range(len(task_ids)):
        for j in range(i + 1, len(task_ids)):
            a_id, b_id = task_ids[i], task_ids[j]
            a_paths, b_paths = set(packets[a_id]), set(packets[b_id])
            common = a_paths & b_paths
            if common:
                overlaps.append((a_id, b_id, common))

    if overlaps:
        print("[WARN] 경로 겹침 감지:")
        for a_id, b_id, common in overlaps:
            print(f"  {a_id} <-> {b_id}: {sorted(common)}")
        sys.exit(1)
    else:
        print(f"[OK] {len(packets)}개 packet 간 경로 겹침 없음.")


def cmd_update_revision(args):
    """packet revision 증가."""
    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] 파일 없음: {path}", file=sys.stderr)
        sys.exit(1)
    data = json.loads(path.read_text())
    old_rev = data.get("revision", 0)
    data["revision"] = old_rev + 1
    data["updated_at"] = _now_iso()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print(f"[OK] {path.name}: revision {old_rev} → {data['revision']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Agent Task Packet 관리자",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="action", required=True)

    # new
    p_new = sub.add_parser("new", help="scaffold 패킷 생성")
    p_new.add_argument("--task-id", required=True, help="태스크 ID (예: TASK-0001)")
    p_new.add_argument("--title", required=True, help="태스크 제목")
    p_new.add_argument("--dir", default=".codex/packets", help="저장 디렉토리 (기본: .codex/packets)")
    p_new.add_argument("--force", action="store_true", help="기존 파일 덮어쓰기")
    p_new.add_argument("--profile", choices=["standard", "extended"], default="standard",
                        help="packet profile (기본: standard)")

    # validate
    p_val = sub.add_parser("validate", help="packet JSON 검증")
    p_val.add_argument("files", nargs="+", help="검증할 packet 파일")
    p_val.add_argument("--profile", choices=["standard", "extended"], default=None,
                        help="검증 profile (기본: 자동 판별)")

    # show
    p_show = sub.add_parser("show", help="packet 조회")
    p_show.add_argument("file", help="packet 파일")
    p_show.add_argument("--raw", action="store_true", help="raw JSON 출력")

    # render-prompt
    p_render = sub.add_parser("render-prompt", help="Codex worker용 prompt 렌더링")
    p_render.add_argument("file", help="packet 파일")

    # list
    p_list = sub.add_parser("list", help="packet 목록")
    p_list.add_argument("--dir", default=".codex/packets", help="packet 디렉토리")
    p_list.add_argument("--priority", help="priority 필터")
    p_list.add_argument("--group", help="parallel_group 필터")

    # check-paths
    p_check = sub.add_parser("check-paths", help="packet 간 경로 겹침 검사")
    p_check.add_argument("files", nargs="+", help="비교할 packet 파일들")

    # update-revision
    p_rev = sub.add_parser("update-revision", help="packet revision 증가")
    p_rev.add_argument("file", help="packet 파일")

    args = parser.parse_args()
    actions = {
        "new": cmd_new, "validate": cmd_validate,
        "show": cmd_show, "render-prompt": cmd_render_prompt,
        "list": cmd_list, "check-paths": cmd_check_paths,
        "update-revision": cmd_update_revision,
    }
    actions[args.action](args)


if __name__ == "__main__":
    main()
