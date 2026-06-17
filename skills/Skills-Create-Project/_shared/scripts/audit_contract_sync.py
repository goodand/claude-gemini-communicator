#!/usr/bin/env python3
"""Contract 4-point sync auditor — registry / template / builder / reference 정합성 검사.

Canonical contract registry (.json) 를 기준으로 template, builder 코드 상수,
reference 문서가 일치하는지 12-fact 검사를 수행한다.

사용법:
    python3 audit_contract_sync.py [--skills-root PATH] [--format text|json]

종료 코드: 0=all in_sync, 1=drift 있음, 2=error 있음
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# 경로 상수 — skills_root 기준 상대 경로
# ---------------------------------------------------------------------------

PACKET_REGISTRY = "agent-task-packet/references/contracts/packet_contract_v0_1.json"
DISPATCH_REGISTRY = "codex-worktree-dispatch/references/contracts/dispatch_contract_v0_1.json"

BUILDER_PY = "agent-task-packet/scripts/packet_builder.py"
# C1 (R3): dispatch_manager.py is the OPERATIONAL owner of the dispatch state machine.
# Its VALID_*/REQUIRED_FIELDS/FORBIDDEN_FIELDS are audited against the registry too,
# so the operational tables are no longer un-audited. Audit-only — read, never modified.
DISPATCH_MANAGER_PY = "codex-worktree-dispatch/scripts/dispatch_manager.py"

# 템플릿은 skills_root 기준 상대 경로 (_shared/templates/)
# self-contained: cross-repo my-second-identity 의존 제거됨 (BLOCKER-CLOSURE-0002)
TEMPLATE_REL = Path("_shared") / "templates"

PACKET_TEMPLATE_STD = TEMPLATE_REL / "task_packet_standard_template.json"
PACKET_TEMPLATE_EXT = TEMPLATE_REL / "task_packet_extended_template.json"
DISPATCH_TEMPLATE_STD = TEMPLATE_REL / "dispatch_state_standard_template.json"
DISPATCH_TEMPLATE_EXT = TEMPLATE_REL / "dispatch_state_extended_template.json"
TEMPLATE_MANIFEST = TEMPLATE_REL / "template_manifest.json"

# ---------------------------------------------------------------------------
# Builder 상수 추출 — Python 소스에서 regex + ast.literal_eval
# ---------------------------------------------------------------------------

# set literal 패턴: CONST = {\n    "a", "b", ...\n}
_SET_RE = re.compile(
    r'^(?P<name>[A-Z_]+)\s*=\s*(?P<body>\{[^}]+\})',
    re.MULTILINE,
)

# dict literal 패턴: CONST = {\n    "key": {"v1", "v2"}, ...\n}
_DICT_RE = re.compile(
    r'^(?P<name>[A-Z_]+)\s*=\s*(?P<body>\{[^}]+?\n\})',
    re.MULTILINE | re.DOTALL,
)

# validate_dispatch 함수 내부의 required = { ... } 블록
_DISPATCH_REQUIRED_RE = re.compile(
    r'def validate_dispatch\(.*?\n\s+required\s*=\s*(?P<body>\{[^}]+\})',
    re.DOTALL,
)


def _safe_literal_eval(expr: str) -> Any:
    """set() 호출을 빈 set으로 변환한 뒤 ast.literal_eval 시도."""
    # set() -> frozenset() 변환 후 평가 — ast.literal_eval은 set()를 지원하지 않는다
    cleaned = expr.strip()
    cleaned = re.sub(r'\bset\(\)', '""', cleaned)  # 빈 set placeholder
    # 후행 쉼표 뒤 주석 제거
    cleaned = re.sub(r'#[^\n]*', '', cleaned)
    try:
        result = ast.literal_eval(cleaned)
        return result
    except (ValueError, SyntaxError):
        return None


def _extract_set_constant(src: str, name: str) -> set[str] | None:
    """Python 소스에서 이름이 name인 set 상수를 추출."""
    # 정규식으로 해당 상수 블록 찾기
    pattern = re.compile(
        rf'^{re.escape(name)}\s*=\s*(?P<body>\{{[^}}]+\}})',
        re.MULTILINE,
    )
    m = pattern.search(src)
    if not m:
        return None
    body = m.group("body")
    result = _safe_literal_eval(body)
    if isinstance(result, set):
        return result
    if isinstance(result, (list, tuple)):
        return set(result)
    return None


def _extract_dict_constant(src: str, name: str) -> dict | None:
    """Python 소스에서 이름이 name인 dict 상수를 추출 (값이 set인 경우 포함)."""
    # 여러 줄에 걸친 dict — 닫는 } 까지 캡처
    pattern = re.compile(
        rf'^{re.escape(name)}\s*=\s*(?P<body>\{{.*?^\}})',
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(src)
    if not m:
        return None
    body = m.group("body")
    result = _safe_literal_eval(body)
    if isinstance(result, dict):
        # 값 중 frozenset/string placeholder → set 변환
        out = {}
        for k, v in result.items():
            if isinstance(v, frozenset):
                out[k] = set(v)
            elif isinstance(v, set):
                out[k] = v
            elif v == "":
                out[k] = set()  # set() placeholder
            elif isinstance(v, (list, tuple)):
                out[k] = set(v)
            else:
                out[k] = v
        return out
    return None


def _extract_validate_dispatch_required(src: str) -> set[str] | None:
    """validate_dispatch() 함수 내부의 required = { ... } 블록에서 필드 집합 추출."""
    m = _DISPATCH_REQUIRED_RE.search(src)
    if not m:
        return None
    body = m.group("body")
    result = _safe_literal_eval(body)
    if isinstance(result, set):
        return result
    return None


# ---------------------------------------------------------------------------
# JSON 로딩 유틸
# ---------------------------------------------------------------------------

def _load_json(path: Path) -> dict | None:
    """JSON 파일 로딩. 파일 없으면 None 반환."""
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Fact 검사 엔진
# ---------------------------------------------------------------------------

class AuditRow:
    """검사 결과 한 행."""
    __slots__ = ("fact_id", "owner", "status", "detail")

    def __init__(self, fact_id: str, owner: str, status: str = "in_sync", detail: str = ""):
        self.fact_id = fact_id
        self.owner = owner
        self.status = status
        self.detail = detail


def _compare_sets(
    fact_id: str,
    owner: str,
    registry_set: set[str],
    builder_set: set[str] | None,
    *,
    template_set: set[str] | None = None,
    template_label: str = "",
) -> AuditRow:
    """두 (또는 세) 집합을 비교하여 AuditRow 반환."""
    if builder_set is None:
        return AuditRow(fact_id, owner, "error", "builder 상수를 추출할 수 없음")

    parts: list[str] = []

    # registry vs builder 비교
    if registry_set != builder_set:
        only_reg = sorted(registry_set - builder_set)
        only_bld = sorted(builder_set - registry_set)
        if only_reg:
            parts.append(f"registry에만 있음: {only_reg}")
        if only_bld:
            parts.append(f"builder에만 있음: {only_bld}")

    # template 비교 (있을 때만)
    if template_set is not None:
        label = template_label or "template"
        if registry_set != template_set:
            only_reg = sorted(registry_set - template_set)
            only_tpl = sorted(template_set - registry_set)
            if only_reg:
                parts.append(f"{label}에 없음: {only_reg}")
            if only_tpl:
                parts.append(f"{label}에만 있음: {only_tpl}")

    if parts:
        detail = f"registry: {len(registry_set)}, builder: {len(builder_set)}"
        if template_set is not None:
            detail += f", {template_label or 'template'}: {len(template_set)}"
        detail += " — " + "; ".join(parts)
        return AuditRow(fact_id, owner, "drift", detail)

    return AuditRow(fact_id, owner, "in_sync", "")


def _compare_dicts(
    fact_id: str,
    owner: str,
    registry_dict: dict,
    builder_dict: dict | None,
) -> AuditRow:
    """transition dict를 비교. 키 집합과 각 키의 값 집합을 모두 검사."""
    if builder_dict is None:
        return AuditRow(fact_id, owner, "error", "builder 상수를 추출할 수 없음")

    # registry의 값을 set으로 변환
    reg_norm: dict[str, set[str]] = {}
    for k, v in registry_dict.items():
        if isinstance(v, list):
            reg_norm[k] = set(v)
        elif isinstance(v, set):
            reg_norm[k] = v
        else:
            reg_norm[k] = set()

    bld_norm: dict[str, set[str]] = {}
    for k, v in builder_dict.items():
        if isinstance(v, (list, tuple)):
            bld_norm[k] = set(v)
        elif isinstance(v, set):
            bld_norm[k] = v
        else:
            bld_norm[k] = set()

    diffs: list[str] = []

    # 키 비교
    reg_keys = set(reg_norm.keys())
    bld_keys = set(bld_norm.keys())
    if reg_keys != bld_keys:
        only_reg = sorted(reg_keys - bld_keys)
        only_bld = sorted(bld_keys - reg_keys)
        if only_reg:
            diffs.append(f"registry에만 있는 키: {only_reg}")
        if only_bld:
            diffs.append(f"builder에만 있는 키: {only_bld}")

    # 공통 키의 값 비교
    for k in sorted(reg_keys & bld_keys):
        if reg_norm[k] != bld_norm[k]:
            only_r = sorted(reg_norm[k] - bld_norm[k])
            only_b = sorted(bld_norm[k] - reg_norm[k])
            parts = []
            if only_r:
                parts.append(f"registry에만: {only_r}")
            if only_b:
                parts.append(f"builder에만: {only_b}")
            diffs.append(f"'{k}' 값 차이: {', '.join(parts)}")

    if diffs:
        return AuditRow(fact_id, owner, "drift", "; ".join(diffs))
    return AuditRow(fact_id, owner, "in_sync", "")


def _check_template_fields_subset(
    fact_id: str,
    owner: str,
    template_keys: set[str] | None,
    registry_allowed: set[str],
    template_label: str,
) -> AuditRow:
    """템플릿 필드가 registry required + optional의 부분집합인지 검사."""
    if template_keys is None:
        return AuditRow(fact_id, owner, "error", f"{template_label} 로드 실패")

    extra = sorted(template_keys - registry_allowed)
    if extra:
        return AuditRow(fact_id, owner, "drift", f"{template_label}에 허용되지 않은 필드: {extra}")
    return AuditRow(fact_id, owner, "in_sync", "")


def _check_template_manifest(
    manifest: dict | None,
    template_dir: Path,
) -> AuditRow:
    """template_manifest.json의 최소 계약을 검사."""
    if manifest is None:
        return AuditRow(
            "template_manifest_inventory",
            "template_manifest",
            "error",
            "template_manifest.json 파일 없음",
        )

    required_keys = {"manifest_version", "canonical", "local_support", "legacy_alias"}
    missing_keys = sorted(required_keys - set(manifest.keys()))
    if missing_keys:
        return AuditRow(
            "template_manifest_inventory",
            "template_manifest",
            "drift",
            f"manifest 필수 키 누락: {missing_keys}",
        )

    categories = ("canonical", "local_support", "legacy_alias")
    class_sets: dict[str, set[str]] = {}
    for key in categories:
        value = manifest.get(key)
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            return AuditRow(
                "template_manifest_inventory",
                "template_manifest",
                "drift",
                f"{key}는 string[] 이어야 함",
            )
        class_sets[key] = set(value)

    overlaps: list[str] = []
    for idx, left in enumerate(categories):
        for right in categories[idx + 1:]:
            dup = sorted(class_sets[left] & class_sets[right])
            if dup:
                overlaps.append(f"{left}/{right} 중복: {dup}")

    actual_templates = {
        path.name
        for path in template_dir.iterdir()
        if path.is_file() and path.name.endswith("_template.json")
    }
    registered = set().union(*class_sets.values())
    missing_on_disk = sorted(registered - actual_templates)
    missing_in_manifest = sorted(actual_templates - registered)

    parts: list[str] = []
    if overlaps:
        parts.extend(overlaps)
    if missing_on_disk:
        parts.append(f"manifest에만 있음: {missing_on_disk}")
    if missing_in_manifest:
        parts.append(f"manifest 미등록: {missing_in_manifest}")

    if parts:
        return AuditRow(
            "template_manifest_inventory",
            "template_manifest",
            "drift",
            "; ".join(parts),
        )

    return AuditRow("template_manifest_inventory", "template_manifest", "in_sync", "")


# ---------------------------------------------------------------------------
# 메인 감사 로직
# ---------------------------------------------------------------------------

def run_audit(skills_root: Path) -> list[AuditRow]:
    """12개 fact에 대해 정합성 검사를 수행하고 결과 리스트 반환."""
    rows: list[AuditRow] = []

    # ── 파일 로딩 ──
    packet_reg = _load_json(skills_root / PACKET_REGISTRY)
    dispatch_reg = _load_json(skills_root / DISPATCH_REGISTRY)

    builder_path = skills_root / BUILDER_PY
    builder_src: str | None = None
    if builder_path.is_file():
        builder_src = builder_path.read_text(encoding="utf-8")

    # C1: read dispatch_manager.py (operational owner) for the dispatch_mgr_* facts.
    dm_path = skills_root / DISPATCH_MANAGER_PY
    dm_src: str | None = dm_path.read_text(encoding="utf-8") if dm_path.is_file() else None

    dispatch_tpl_std = _load_json(skills_root / DISPATCH_TEMPLATE_STD)
    dispatch_tpl_ext = _load_json(skills_root / DISPATCH_TEMPLATE_EXT)
    template_manifest = _load_json(skills_root / TEMPLATE_MANIFEST)

    rows.append(
        _check_template_manifest(
            template_manifest,
            (skills_root / TEMPLATE_REL).resolve(),
        )
    )

    # ── 에러 핸들링: registry 로드 실패 ──
    if packet_reg is None:
        for fid in [
            "packet_required_fields", "packet_optional_fields",
            "packet_extended_fields", "packet_forbidden_fields",
            "packet_priority_enum", "packet_check_types_enum",
            "packet_non_goals_case_enum",
        ]:
            rows.append(AuditRow(fid, "packet_contract", "error", "registry 파일 없음"))
        packet_reg = {}

    if dispatch_reg is None:
        for fid in [
            "dispatch_status_enum", "dispatch_transitions",
            "dispatch_required_fields", "dispatch_forbidden_fields",
            "dispatch_template_fields",
            "dispatch_mgr_status_enum", "dispatch_mgr_transitions",
            "dispatch_mgr_required_fields", "dispatch_mgr_forbidden_fields",
        ]:
            rows.append(AuditRow(fid, "dispatch_contract", "error", "registry 파일 없음"))
        dispatch_reg = {}

    if builder_src is None:
        for fid in [
            "packet_required_fields", "packet_optional_fields",
            "packet_extended_fields", "packet_forbidden_fields",
            "packet_priority_enum", "packet_check_types_enum",
            "packet_non_goals_case_enum",
            "dispatch_status_enum", "dispatch_transitions",
            "dispatch_required_fields", "dispatch_forbidden_fields",
        ]:
            # registry 에러와 중복되지 않도록 기존 fact_id 확인
            if not any(r.fact_id == fid for r in rows):
                rows.append(AuditRow(fid, "packet_contract", "error", "builder 파일 없음"))
        if not any(r.fact_id == "dispatch_template_fields" for r in rows):
            rows.append(AuditRow("dispatch_template_fields", "dispatch_contract", "error",
                                 "builder 파일 없음"))

    # 파일 누락 시 이미 에러 행이 등록되었으므로 검사 스킵
    if not packet_reg or not dispatch_reg or builder_src is None:
        # 아직 등록되지 않은 fact만 추가 검사
        if packet_reg and builder_src is not None:
            pass  # packet 검사는 아래에서
        if dispatch_reg and builder_src is not None:
            pass  # dispatch 검사는 아래에서
        # 모든 파일이 없으면 바로 반환
        if not packet_reg and not dispatch_reg:
            return rows
        if builder_src is None:
            return rows

    # ── Builder 상수 추출 ──
    b_required = _extract_set_constant(builder_src, "REQUIRED_FIELDS")
    b_optional = _extract_set_constant(builder_src, "OPTIONAL_FIELDS")
    b_extended = _extract_set_constant(builder_src, "EXTENDED_FIELDS")
    b_forbidden = _extract_set_constant(builder_src, "FORBIDDEN_FIELDS")
    b_priorities = _extract_set_constant(builder_src, "VALID_PRIORITIES")
    b_check_types = _extract_set_constant(builder_src, "VALID_CHECK_TYPES")
    b_non_goals = _extract_set_constant(builder_src, "NON_GOAL_CASES")
    b_dispatch_statuses = _extract_set_constant(builder_src, "DISPATCH_STATUSES")
    b_dispatch_transitions = _extract_dict_constant(builder_src, "DISPATCH_TRANSITIONS")
    b_dispatch_forbidden = _extract_set_constant(builder_src, "DISPATCH_FORBIDDEN_FIELDS")
    b_dispatch_required = _extract_validate_dispatch_required(builder_src)

    # C1: dispatch_manager.py operational tables (different symbol names than packet_builder).
    m_dispatch_statuses = _extract_set_constant(dm_src, "VALID_STATUSES") if dm_src else None
    m_dispatch_transitions = _extract_dict_constant(dm_src, "VALID_TRANSITIONS") if dm_src else None
    m_dispatch_forbidden = _extract_set_constant(dm_src, "FORBIDDEN_FIELDS") if dm_src else None
    m_dispatch_required = _extract_set_constant(dm_src, "REQUIRED_FIELDS") if dm_src else None

    # ── Packet Facts (1–7) ──
    if packet_reg:
        p_fields = packet_reg.get("fields", {})
        p_enums = packet_reg.get("enums", {})

        # 1. packet_required_fields
        if not any(r.fact_id == "packet_required_fields" for r in rows):
            rows.append(_compare_sets(
                "packet_required_fields", "packet_contract",
                set(p_fields.get("required", [])), b_required,
            ))

        # 2. packet_optional_fields
        if not any(r.fact_id == "packet_optional_fields" for r in rows):
            rows.append(_compare_sets(
                "packet_optional_fields", "packet_contract",
                set(p_fields.get("core_optional", [])), b_optional,
            ))

        # 3. packet_extended_fields
        if not any(r.fact_id == "packet_extended_fields" for r in rows):
            rows.append(_compare_sets(
                "packet_extended_fields", "packet_contract",
                set(p_fields.get("extended_only", [])), b_extended,
            ))

        # 4. packet_forbidden_fields
        if not any(r.fact_id == "packet_forbidden_fields" for r in rows):
            rows.append(_compare_sets(
                "packet_forbidden_fields", "packet_contract",
                set(p_fields.get("forbidden", [])), b_forbidden,
            ))

        # 5. packet_priority_enum
        if not any(r.fact_id == "packet_priority_enum" for r in rows):
            rows.append(_compare_sets(
                "packet_priority_enum", "packet_contract",
                set(p_enums.get("priority", [])), b_priorities,
            ))

        # 6. packet_check_types_enum
        if not any(r.fact_id == "packet_check_types_enum" for r in rows):
            rows.append(_compare_sets(
                "packet_check_types_enum", "packet_contract",
                set(p_enums.get("required_checks_type", [])), b_check_types,
            ))

        # 7. packet_non_goals_case_enum
        if not any(r.fact_id == "packet_non_goals_case_enum" for r in rows):
            rows.append(_compare_sets(
                "packet_non_goals_case_enum", "packet_contract",
                set(p_enums.get("non_goals_case", [])), b_non_goals,
            ))

    # ── Dispatch Facts (8–12) ──
    if dispatch_reg:
        d_enums = dispatch_reg.get("enums", {})
        d_fields = dispatch_reg.get("fields", {})
        d_transitions = dispatch_reg.get("transitions", {})

        # template $schema_notes에서 dispatch_status_enum 추출
        tpl_std_statuses: set[str] | None = None
        if dispatch_tpl_std:
            schema_notes = dispatch_tpl_std.get("$schema_notes", {})
            enum_list = schema_notes.get("dispatch_status_enum")
            if enum_list is not None:
                tpl_std_statuses = set(enum_list)

        # 8. dispatch_status_enum — registry vs builder vs template
        if not any(r.fact_id == "dispatch_status_enum" for r in rows):
            rows.append(_compare_sets(
                "dispatch_status_enum", "dispatch_contract",
                set(d_enums.get("dispatch_status", [])), b_dispatch_statuses,
                template_set=tpl_std_statuses,
                template_label="template_std",
            ))

        # 9. dispatch_transitions
        if not any(r.fact_id == "dispatch_transitions" for r in rows):
            rows.append(_compare_dicts(
                "dispatch_transitions", "dispatch_contract",
                d_transitions, b_dispatch_transitions,
            ))

        # 10. dispatch_required_fields — registry vs validate_dispatch required
        if not any(r.fact_id == "dispatch_required_fields" for r in rows):
            rows.append(_compare_sets(
                "dispatch_required_fields", "dispatch_contract",
                set(d_fields.get("required", [])), b_dispatch_required,
            ))

        # 11. dispatch_forbidden_fields
        if not any(r.fact_id == "dispatch_forbidden_fields" for r in rows):
            rows.append(_compare_sets(
                "dispatch_forbidden_fields", "dispatch_contract",
                set(d_fields.get("forbidden", [])), b_dispatch_forbidden,
            ))

        # 12. dispatch_template_fields — 템플릿 키가 registry allowed 부분집합인지
        if not any(r.fact_id == "dispatch_template_fields" for r in rows):
            reg_allowed = (
                set(d_fields.get("required", []))
                | set(d_fields.get("optional", []))
                | set(d_fields.get("reserved", []))
                | {"$schema_notes"}  # 메타 필드 허용
            )
            # 표준 + 확장 템플릿 모두 검사
            tpl_keys_list: list[tuple[str, set[str] | None]] = []
            if dispatch_tpl_std:
                tpl_keys_list.append(("std", set(dispatch_tpl_std.keys())))
            if dispatch_tpl_ext:
                tpl_keys_list.append(("ext", set(dispatch_tpl_ext.keys())))

            if not tpl_keys_list:
                rows.append(AuditRow("dispatch_template_fields", "dispatch_contract",
                                     "error", "dispatch 템플릿 파일 없음"))
            else:
                all_extra: list[str] = []
                for label, tkeys in tpl_keys_list:
                    extra = tkeys - reg_allowed
                    if extra:
                        all_extra.append(f"{label}: {sorted(extra)}")
                if all_extra:
                    rows.append(AuditRow("dispatch_template_fields", "dispatch_contract",
                                         "drift", "허용되지 않은 필드 — " + "; ".join(all_extra)))
                else:
                    rows.append(AuditRow("dispatch_template_fields", "dispatch_contract",
                                         "in_sync", ""))

        # ── C1: dispatch_manager.py operational tables vs registry (closes R3/G1) ──
        # dispatch_manager is the operational owner; its tables were previously un-audited.
        # Audit-only: dispatch_manager.py is read, never modified.
        if not any(r.fact_id == "dispatch_mgr_status_enum" for r in rows):
            rows.append(_compare_sets(
                "dispatch_mgr_status_enum", "dispatch_contract",
                set(d_enums.get("dispatch_status", [])), m_dispatch_statuses,
            ))
        if not any(r.fact_id == "dispatch_mgr_transitions" for r in rows):
            # dispatch_manager omits terminal statuses (no outgoing) from VALID_TRANSITIONS,
            # whereas the registry lists them with empty arrays. Drop empty-valued registry
            # keys so the two representations compare on equal terms (real transition
            # differences are still detected).
            reg_trans_nonempty = {k: v for k, v in d_transitions.items() if v}
            rows.append(_compare_dicts(
                "dispatch_mgr_transitions", "dispatch_contract",
                reg_trans_nonempty, m_dispatch_transitions,
            ))
        if not any(r.fact_id == "dispatch_mgr_required_fields" for r in rows):
            rows.append(_compare_sets(
                "dispatch_mgr_required_fields", "dispatch_contract",
                set(d_fields.get("required", [])), m_dispatch_required,
            ))
        if not any(r.fact_id == "dispatch_mgr_forbidden_fields" for r in rows):
            rows.append(_compare_sets(
                "dispatch_mgr_forbidden_fields", "dispatch_contract",
                set(d_fields.get("forbidden", [])), m_dispatch_forbidden,
            ))

    return rows


# ---------------------------------------------------------------------------
# 출력 포매터
# ---------------------------------------------------------------------------

def format_text(rows: list[AuditRow]) -> str:
    """Markdown 테이블 형식으로 결과 출력."""
    lines = [
        "| fact_id | owner | status | detail |",
        "|---------|-------|--------|--------|",
    ]
    for r in rows:
        lines.append(f"| {r.fact_id} | {r.owner} | {r.status} | {r.detail} |")
    return "\n".join(lines)


def format_json(rows: list[AuditRow]) -> str:
    """JSON 형식으로 결과 출력."""
    data = [
        {"fact_id": r.fact_id, "owner": r.owner, "status": r.status, "detail": r.detail}
        for r in rows
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# skills_root 자동 탐지
# ---------------------------------------------------------------------------

def _detect_skills_root() -> Path | None:
    """스크립트 위치에서 상위 디렉토리를 탐색해 agent-task-packet/ 을 포함하는 디렉토리 반환."""
    current = Path(__file__).resolve().parent
    for _ in range(10):
        if (current / "agent-task-packet").is_dir():
            return current
        current = current.parent
    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Contract 4-point sync auditor — registry/template/builder/reference 정합성 검사",
    )
    parser.add_argument(
        "--skills-root",
        type=Path,
        default=None,
        help="Skills-Create-Project 루트 경로 (기본값: 자동 탐지)",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="출력 형식 (기본값: text)",
    )
    args = parser.parse_args()

    skills_root = args.skills_root
    if skills_root is None:
        skills_root = _detect_skills_root()
    if skills_root is None:
        print("ERROR: skills_root를 찾을 수 없습니다. --skills-root 옵션을 지정하세요.", file=sys.stderr)
        sys.exit(2)

    skills_root = skills_root.resolve()

    rows = run_audit(skills_root)

    if args.format == "json":
        print(format_json(rows))
    else:
        print(format_text(rows))

    # 종료 코드 결정
    statuses = {r.status for r in rows}
    if "error" in statuses:
        sys.exit(2)
    if "drift" in statuses:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
