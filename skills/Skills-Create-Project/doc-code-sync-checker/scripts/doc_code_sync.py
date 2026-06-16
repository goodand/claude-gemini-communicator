#!/usr/bin/env python3
"""doc-code-sync-checker pairwise vertical slices.

v0.1은 문서 1개와 코드 1개를 비교하는 pairwise smoke-test checker다.
현재 구현 slice는 아래 네 규칙군을 end-to-end로 닫는다.
- `required_field`
- `path_safety`
- `transition_rule`
- `enum_value`
`normalize`는 별도 CLI가 아니라 compare 내부 단계로 둔다.

Usage:
    python3 doc_code_sync.py extract-doc --doc <file>
    python3 doc_code_sync.py extract-code --script <file>
    python3 doc_code_sync.py compare --doc-rules <json> --code-rules <json>
    python3 doc_code_sync.py report --results <results.json>
"""

from __future__ import annotations

import argparse
import ast
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
RULE_REQUIRED_FIELD = "required_field"
RULE_PATH_SAFETY = "path_safety"
RULE_TRANSITION = "transition_rule"
RULE_ENUM = "enum_value"
SUPPORTED_RULE_KINDS = {RULE_REQUIRED_FIELD, RULE_PATH_SAFETY, RULE_TRANSITION, RULE_ENUM}
MISMATCH_ENUM_SET_CHANGED = "enum_value_set_changed"
MISMATCH_TRANSITION_SET_CHANGED = "transition_rule_set_changed"
MISMATCH_PATH_RULE_CHANGED = "path_rule_condition_changed"

DOC_SECTION_REQUIRED = "## Core 필수 필드 (v0.1)"
DOC_SECTION_PATH = "## locked_paths 규칙"
DOC_SECTION_TRANSITION = "### 유효 전이 테이블"
CODE_CONSTANT = "REQUIRED_FIELDS"
CODE_ENUM_STATUSES = "VALID_STATUSES"
CODE_TRANSITIONS = "VALID_TRANSITIONS"

PATH_RULE_SUBSET = "locked_paths_subset_allowed_paths"
PATH_RULE_TRAILING_SLASH = "normalize_trailing_slash"
PATH_RULE_TRAVERSAL = "forbid_path_traversal"
PATH_RULE_ABSOLUTE = "forbid_absolute_path"
PATH_RULE_SYMLINK = "forbid_symlink"


def _now_iso() -> str:
    return datetime.now(KST).isoformat(timespec="seconds")


def _err(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def _load_json(path: str) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dump_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _rule(kind: str, name: str, source: str, evidence: str) -> dict[str, object]:
    return {
        "kind": kind,
        "name": name,
        "source": source,
        "value": True,
        "evidence": evidence,
    }


def _section_lines(path: Path, heading: str) -> list[str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    in_section = False
    section: list[str] = []

    for raw_line in lines:
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped == heading:
            in_section = True
            continue

        if in_section and stripped.startswith("#"):
            break

        if not in_section:
            continue
        section.append(line)

    return section


def _extract_required_field_rows(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    for line in _section_lines(path, DOC_SECTION_REQUIRED):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        parts = [part.strip() for part in stripped.split("|")[1:-1]]
        if len(parts) < 3:
            continue
        if parts[0] == "필드" or set(parts[0]) == {"-"}:
            continue

        field_name = parts[0].strip("`").strip()
        description = parts[2]
        if not field_name:
            continue
        rows.append(
            _rule(
                RULE_REQUIRED_FIELD,
                field_name,
                "doc",
                f"{DOC_SECTION_REQUIRED} 표 — {field_name}: {description}",
            )
        )

    return rows


def _append_unique_rule(
    rules: list[dict[str, object]],
    seen: set[str],
    kind: str,
    name: str,
    source: str,
    evidence: str,
) -> None:
    if name in seen:
        return
    seen.add(name)
    rules.append(_rule(kind, name, source, evidence))


def _extract_path_safety_doc_rules(path: Path) -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []
    seen: set[str] = set()

    for line in _section_lines(path, DOC_SECTION_PATH):
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        bullet = stripped[2:]

        if "locked_paths ⊆" in bullet or ("allowed_paths" in bullet and "범위 확장 불가" in bullet):
            _append_unique_rule(
                rules,
                seen,
                RULE_PATH_SAFETY,
                PATH_RULE_SUBSET,
                "doc",
                f"{DOC_SECTION_PATH} bullet — {bullet}",
            )
        if "trailing `/` 통일" in bullet or "trailing / 통일" in bullet:
            _append_unique_rule(
                rules,
                seen,
                RULE_PATH_SAFETY,
                PATH_RULE_TRAILING_SLASH,
                "doc",
                f"{DOC_SECTION_PATH} bullet — {bullet}",
            )
        if (".." in bullet or "`..`" in bullet) and ("방지" in bullet or "금지" in bullet):
            _append_unique_rule(
                rules,
                seen,
                RULE_PATH_SAFETY,
                PATH_RULE_TRAVERSAL,
                "doc",
                f"{DOC_SECTION_PATH} bullet — {bullet}",
            )
        if "절대경로" in bullet and ("방지" in bullet or "금지" in bullet):
            _append_unique_rule(
                rules,
                seen,
                RULE_PATH_SAFETY,
                PATH_RULE_ABSOLUTE,
                "doc",
                f"{DOC_SECTION_PATH} bullet — {bullet}",
            )
        if "symlink" in bullet and ("방지" in bullet or "금지" in bullet):
            _append_unique_rule(
                rules,
                seen,
                RULE_PATH_SAFETY,
                PATH_RULE_SYMLINK,
                "doc",
                f"{DOC_SECTION_PATH} bullet — {bullet}",
            )

    return rules


def _transition_name(from_status: str, to_status: str) -> str:
    return f"{from_status}->{to_status}"


def _extract_transition_doc_rules(path: Path) -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []
    seen: set[str] = set()

    for line in _section_lines(path, DOC_SECTION_TRANSITION):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        parts = [part.strip() for part in stripped.split("|")[1:-1]]
        if len(parts) < 3:
            continue
        if parts[0] == "From" or set(parts[0]) == {"-"}:
            continue

        from_status = parts[0].strip("`").strip()
        to_status = parts[1].strip("`").strip()
        condition = parts[2]
        if not from_status or not to_status:
            continue

        name = _transition_name(from_status, to_status)
        _append_unique_rule(
            rules,
            seen,
            RULE_TRANSITION,
            name,
            "doc",
            f"{DOC_SECTION_TRANSITION} row — {from_status} -> {to_status}: {condition}",
        )

    return rules


def _extract_status_enum_doc_rules(path: Path) -> list[dict[str, object]]:
    rules: list[dict[str, object]] = []
    seen: set[str] = set()

    for line in _section_lines(path, DOC_SECTION_TRANSITION):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue

        parts = [part.strip() for part in stripped.split("|")[1:-1]]
        if len(parts) < 3:
            continue
        if parts[0] == "From" or set(parts[0]) == {"-"}:
            continue

        for raw_value in (parts[0], parts[1]):
            value = raw_value.strip("`").strip()
            if not value:
                continue
            _append_unique_rule(
                rules,
                seen,
                RULE_ENUM,
                f"status:{value}",
                "doc",
                f"{DOC_SECTION_TRANSITION} unique status value — {value}",
            )

    return rules


def _extract_required_fields_constant(path: Path) -> tuple[list[dict[str, object]], bool]:
    source_text = path.read_text(encoding="utf-8")
    tree = ast.parse(source_text, filename=str(path))
    names: list[str] = []
    validate_missing_check = False

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == CODE_CONSTANT:
                    if isinstance(node.value, ast.Set):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                names.append(elt.value)
        elif isinstance(node, ast.FunctionDef) and node.name == "validate_packet":
            for subnode in ast.walk(node):
                if isinstance(subnode, ast.Assign):
                    for target in subnode.targets:
                        if isinstance(target, ast.Name) and target.id == "missing":
                            source = ast.get_source_segment(source_text, subnode) or ""
                            if "REQUIRED_FIELDS" in source and "set(data.keys())" in source:
                                validate_missing_check = True

    rules = [
        _rule(
            RULE_REQUIRED_FIELD,
            name,
            "code",
            f"{CODE_CONSTANT} set literal"
            + (" + validate_packet missing-field branch" if validate_missing_check else ""),
        )
        for name in names
    ]
    return rules, validate_missing_check


def _function_source(tree: ast.AST, source_text: str, fn_name: str) -> str:
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            return ast.get_source_segment(source_text, node) or ""
    return ""


def _extract_path_safety_code_rules(path: Path) -> list[dict[str, object]]:
    source_text = path.read_text(encoding="utf-8")
    tree = ast.parse(source_text, filename=str(path))
    validate_source = _function_source(tree, source_text, "validate_dispatch")
    rules: list[dict[str, object]] = []
    seen: set[str] = set()

    if "def _normalize_path(" in source_text and 'if not p.endswith("/")' in source_text:
        _append_unique_rule(
            rules,
            seen,
            RULE_PATH_SAFETY,
            PATH_RULE_TRAILING_SLASH,
            "code",
            "_normalize_path helper trailing slash normalization",
        )

    if '".."' in validate_source and "in ps" in validate_source:
        _append_unique_rule(
            rules,
            seen,
            RULE_PATH_SAFETY,
            PATH_RULE_TRAVERSAL,
            "code",
            "validate_dispatch locked_paths branch — '..' in ps",
        )

    if 'ps.startswith("/")' in validate_source or "ps.startswith('/')" in validate_source:
        _append_unique_rule(
            rules,
            seen,
            RULE_PATH_SAFETY,
            PATH_RULE_ABSOLUTE,
            "code",
            "validate_dispatch locked_paths branch — absolute path check",
        )

    if "os.path.lexists(resolved)" in validate_source and "os.path.islink(resolved)" in validate_source:
        _append_unique_rule(
            rules,
            seen,
            RULE_PATH_SAFETY,
            PATH_RULE_SYMLINK,
            "code",
            "validate_dispatch locked_paths branch — symlink check",
        )

    if "ps not in allowed_paths" in validate_source and "packet allowed_paths 범위 밖" in validate_source:
        _append_unique_rule(
            rules,
            seen,
            RULE_PATH_SAFETY,
            PATH_RULE_SUBSET,
            "code",
            "validate_dispatch locked_paths branch — locked_paths subset of packet allowed_paths",
        )

    return rules


def _extract_transition_code_rules(path: Path) -> list[dict[str, object]]:
    source_text = path.read_text(encoding="utf-8")
    tree = ast.parse(source_text, filename=str(path))
    rules: list[dict[str, object]] = []
    seen: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (isinstance(target, ast.Name) and target.id == CODE_TRANSITIONS):
                continue
            if not isinstance(node.value, ast.Dict):
                continue

            for key_node, value_node in zip(node.value.keys, node.value.values):
                if not isinstance(key_node, ast.Constant) or not isinstance(key_node.value, str):
                    continue
                from_status = key_node.value
                if not isinstance(value_node, ast.Set):
                    continue
                for elt in value_node.elts:
                    if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
                        continue
                    to_status = elt.value
                    name = _transition_name(from_status, to_status)
                    _append_unique_rule(
                        rules,
                        seen,
                        RULE_TRANSITION,
                        name,
                        "code",
                        f"{CODE_TRANSITIONS}[{from_status!r}] contains {to_status!r}",
                    )

    return rules


def _extract_string_set_constant(path: Path, constant_name: str, rule_kind: str, prefix: str) -> list[dict[str, object]]:
    source_text = path.read_text(encoding="utf-8")
    tree = ast.parse(source_text, filename=str(path))
    rules: list[dict[str, object]] = []
    seen: set[str] = set()

    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not (isinstance(target, ast.Name) and target.id == constant_name):
                continue
            if not isinstance(node.value, ast.Set):
                continue

            for elt in node.value.elts:
                if not isinstance(elt, ast.Constant) or not isinstance(elt.value, str):
                    continue
                value = elt.value
                _append_unique_rule(
                    rules,
                    seen,
                    rule_kind,
                    f"{prefix}:{value}",
                    "code",
                    f"{constant_name} contains {value!r}",
                )

    return rules


def _load_rules_payload(path: str, expected_command: str) -> dict[str, object]:
    payload = _load_json(path)
    if isinstance(payload, list):
        return {
            "status": "implemented",
            "command": expected_command,
            "rules": payload,
        }
    if not isinstance(payload, dict):
        _err(f"규칙 JSON 형식이 잘못됨: {path}")
    if "rules" not in payload or not isinstance(payload["rules"], list):
        _err(f"'rules' 배열이 없음: {path}")
    return payload


def _normalize_rules(rules: list[dict[str, object]], rule_kind: str) -> dict[str, dict[str, object]]:
    normalized: dict[str, dict[str, object]] = {}
    for rule in rules:
        kind = str(rule.get("kind", "")).strip()
        name = str(rule.get("name", "")).strip()
        if kind != rule_kind or not name:
            continue
        normalized[name] = rule
    return normalized


def _group_enum_rules_by_field(
    rules: dict[str, dict[str, object]],
) -> dict[str, dict[str, object]]:
    grouped: dict[str, dict[str, object]] = {}
    for name, rule in rules.items():
        if ":" not in name:
            continue
        field, value = name.split(":", 1)
        field = field.strip()
        value = value.strip()
        if not field or not value:
            continue
        bucket = grouped.setdefault(field, {"values": set(), "evidence": []})
        bucket["values"].add(value)
        evidence = str(rule.get("evidence", "")).strip()
        if evidence:
            bucket["evidence"].append(evidence)
    return grouped


def _enum_typed_mismatch(
    doc_rules: dict[str, dict[str, object]],
    code_rules: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    doc_grouped = _group_enum_rules_by_field(doc_rules)
    code_grouped = _group_enum_rules_by_field(code_rules)
    fields = sorted(set(doc_grouped) & set(code_grouped))
    typed: list[dict[str, object]] = []

    for field in fields:
        doc_values = set(doc_grouped[field]["values"])
        code_values = set(code_grouped[field]["values"])
        if doc_values == code_values:
            continue

        doc_only = sorted(doc_values - code_values)
        code_only = sorted(code_values - doc_values)
        typed.append(
            {
                "kind": MISMATCH_ENUM_SET_CHANGED,
                "name": field,
                "doc_values": sorted(doc_values),
                "code_values": sorted(code_values),
                "doc_only": doc_only,
                "code_only": code_only,
                "doc_evidence": sorted(set(doc_grouped[field]["evidence"])),
                "code_evidence": sorted(set(code_grouped[field]["evidence"])),
                "reason": f"{field} 허용값 집합이 문서와 코드에서 다름",
                "action": f"{field} enum의 doc/code 허용값 집합 정렬 검토",
            }
        )

    return typed


def _transition_typed_mismatch(
    doc_rules: dict[str, dict[str, object]],
    code_rules: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    doc_values = sorted(doc_rules)
    code_values = sorted(code_rules)
    if doc_values == code_values:
        return []

    doc_only = sorted(set(doc_values) - set(code_values))
    code_only = sorted(set(code_values) - set(doc_values))
    return [
        {
            "kind": MISMATCH_TRANSITION_SET_CHANGED,
            "name": "status_transitions",
            "doc_values": doc_values,
            "code_values": code_values,
            "doc_only": doc_only,
            "code_only": code_only,
            "doc_evidence": [str(doc_rules[name].get("evidence", "")).strip() for name in doc_values],
            "code_evidence": [str(code_rules[name].get("evidence", "")).strip() for name in code_values],
            "reason": "상태 전이 집합이 문서와 코드에서 다름",
            "action": "전이표와 VALID_TRANSITIONS 정렬 검토",
        }
    ]


def _path_typed_mismatch(
    doc_rules: dict[str, dict[str, object]],
    code_rules: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    doc_values = sorted(doc_rules)
    code_values = sorted(code_rules)
    if doc_values == code_values:
        return []

    doc_only = sorted(set(doc_values) - set(code_values))
    code_only = sorted(set(code_values) - set(doc_values))
    return [
        {
            "kind": MISMATCH_PATH_RULE_CHANGED,
            "name": "locked_paths_conditions",
            "doc_values": doc_values,
            "code_values": code_values,
            "doc_only": doc_only,
            "code_only": code_only,
            "doc_evidence": [str(doc_rules[name].get("evidence", "")).strip() for name in doc_values],
            "code_evidence": [str(code_rules[name].get("evidence", "")).strip() for name in code_values],
            "reason": "경로 안전 규칙 조건 집합이 문서와 코드에서 다름",
            "action": "locked_paths 경로 규칙의 doc/code 조건 집합 정렬 검토",
        }
    ]


def _extract_doc_rules(path: Path, rule_kind: str) -> tuple[list[dict[str, object]], str]:
    if rule_kind == RULE_REQUIRED_FIELD:
        rules = _extract_required_field_rows(path)
        return rules, f"{DOC_SECTION_REQUIRED} markdown table"
    if rule_kind == RULE_PATH_SAFETY:
        rules = _extract_path_safety_doc_rules(path)
        return rules, f"{DOC_SECTION_PATH} bullet list"
    if rule_kind == RULE_TRANSITION:
        rules = _extract_transition_doc_rules(path)
        return rules, f"{DOC_SECTION_TRANSITION} markdown table"
    if rule_kind == RULE_ENUM:
        rules = _extract_status_enum_doc_rules(path)
        return rules, f"{DOC_SECTION_TRANSITION} unique status values"
    _err(f"지원하지 않는 rule_kind: {rule_kind}")
    raise AssertionError("unreachable")


def _extract_code_rules(path: Path, rule_kind: str) -> tuple[list[dict[str, object]], dict[str, object]]:
    if rule_kind == RULE_REQUIRED_FIELD:
        rules, validate_missing_check = _extract_required_fields_constant(path)
        return rules, {
            "source_constant": CODE_CONSTANT,
            "validate_missing_check": validate_missing_check,
        }
    if rule_kind == RULE_PATH_SAFETY:
        rules = _extract_path_safety_code_rules(path)
        return rules, {
            "source_function": "validate_dispatch",
            "normalize_helper": "_normalize_path",
        }
    if rule_kind == RULE_TRANSITION:
        rules = _extract_transition_code_rules(path)
        return rules, {
            "source_constant": CODE_TRANSITIONS,
        }
    if rule_kind == RULE_ENUM:
        rules = _extract_string_set_constant(path, CODE_ENUM_STATUSES, RULE_ENUM, "status")
        return rules, {
            "source_constant": CODE_ENUM_STATUSES,
        }
    _err(f"지원하지 않는 rule_kind: {rule_kind}")
    raise AssertionError("unreachable")


def cmd_extract_doc(args: argparse.Namespace) -> None:
    doc_path = Path(args.doc)
    if not doc_path.is_file():
        _err(f"문서 파일 없음: {doc_path}")

    rules, supported_pattern = _extract_doc_rules(doc_path, args.rule_kind)
    payload = {
        "status": "implemented" if rules else "partial",
        "scope": "pairwise_smoke_test",
        "command": "extract-doc",
        "rule_kind": args.rule_kind,
        "doc": str(doc_path),
        "rules": rules,
        "supported_pattern": supported_pattern,
        "message": f"{args.rule_kind} 문서 추출 완료" if rules else f"{args.rule_kind} 문서 규칙을 찾지 못함",
        "generated_at": _now_iso(),
    }
    _dump_json(payload)


def cmd_extract_code(args: argparse.Namespace) -> None:
    script_path = Path(args.script)
    if not script_path.is_file():
        _err(f"스크립트 파일 없음: {script_path}")

    rules, metadata = _extract_code_rules(script_path, args.rule_kind)
    payload = {
        "status": "implemented" if rules else "partial",
        "scope": "pairwise_smoke_test",
        "command": "extract-code",
        "rule_kind": args.rule_kind,
        "script": str(script_path),
        "rules": rules,
        "message": f"{args.rule_kind} 코드 추출 완료" if rules else f"{args.rule_kind} 코드 규칙을 찾지 못함",
        "generated_at": _now_iso(),
    }
    payload.update(metadata)
    _dump_json(payload)


def _missing_action(rule_kind: str, direction: str, name: str) -> str:
    if rule_kind == RULE_REQUIRED_FIELD:
        if direction == "code":
            return f"{CODE_CONSTANT} 또는 validate evidence에 '{name}' 추가 검토"
        return f"{DOC_SECTION_REQUIRED} 표에 '{name}' 문서화 검토"
    if rule_kind == RULE_PATH_SAFETY:
        if direction == "code":
            return f"validate_dispatch 경로 검증에 '{name}' 규칙 구현 검토"
        return f"{DOC_SECTION_PATH}에 '{name}' 규칙 문서화 검토"
    if rule_kind == RULE_TRANSITION:
        if direction == "code":
            return f"{CODE_TRANSITIONS}에 '{name}' 전이 추가 검토"
        return f"{DOC_SECTION_TRANSITION}에 '{name}' 전이 문서화 검토"
    if rule_kind == RULE_ENUM:
        if direction == "code":
            return f"{CODE_ENUM_STATUSES}에 '{name}' 허용값 추가 검토"
        return f"status enum 문서에 '{name}' 허용값 문서화 검토"
    return f"'{name}' 규칙 정합성 검토"


def cmd_compare(args: argparse.Namespace) -> None:
    doc_payload = _load_rules_payload(args.doc_rules, "extract-doc")
    code_payload = _load_rules_payload(args.code_rules, "extract-code")
    doc_rule_kind = str(doc_payload.get("rule_kind", RULE_REQUIRED_FIELD)).strip()
    code_rule_kind = str(code_payload.get("rule_kind", RULE_REQUIRED_FIELD)).strip()

    if doc_rule_kind != code_rule_kind:
        _err(
            "문서/코드 규칙 종류가 다름: "
            f"doc='{doc_rule_kind or '?'}', code='{code_rule_kind or '?'}'"
        )
    if doc_rule_kind not in SUPPORTED_RULE_KINDS:
        _err(f"지원하지 않는 compare rule_kind: {doc_rule_kind}")

    doc_rules = _normalize_rules(doc_payload["rules"], doc_rule_kind)
    code_rules = _normalize_rules(code_payload["rules"], doc_rule_kind)

    doc_names = set(doc_rules)
    code_names = set(code_rules)

    missing_in_code = [
        {
            "kind": doc_rule_kind,
            "name": name,
            "doc_evidence": doc_rules[name]["evidence"],
            "action": _missing_action(doc_rule_kind, "code", name),
        }
        for name in sorted(doc_names - code_names)
    ]
    missing_in_doc = [
        {
            "kind": doc_rule_kind,
            "name": name,
            "code_evidence": code_rules[name]["evidence"],
            "action": _missing_action(doc_rule_kind, "doc", name),
        }
        for name in sorted(code_names - doc_names)
    ]
    mismatch = []
    if doc_rule_kind == RULE_ENUM:
        typed_mismatch = _enum_typed_mismatch(doc_rules, code_rules)
    elif doc_rule_kind == RULE_TRANSITION:
        typed_mismatch = _transition_typed_mismatch(doc_rules, code_rules)
    elif doc_rule_kind == RULE_PATH_SAFETY:
        typed_mismatch = _path_typed_mismatch(doc_rules, code_rules)
    else:
        typed_mismatch = []

    payload = {
        "status": "implemented",
        "scope": "pairwise_smoke_test",
        "command": "compare",
        "rule_kind": doc_rule_kind,
        "pair": {
            "doc": doc_payload.get("doc", args.doc_rules),
            "script": code_payload.get("script", args.code_rules),
        },
        "normalization": {
            "mode": "internal_compare_stage",
            "implemented": True,
            "key": f"{doc_rule_kind}.name exact match",
        },
        "doc_rule_count": len(doc_rules),
        "code_rule_count": len(code_rules),
        "missing_in_code": missing_in_code,
        "missing_in_doc": missing_in_doc,
        "mismatch": mismatch,
        "typed_mismatch": typed_mismatch,
        "message": f"{doc_rule_kind} 비교 완료",
        "compared_at": _now_iso(),
    }
    _dump_json(payload)


def cmd_report(args: argparse.Namespace) -> None:
    results = _load_json(args.results)
    if not isinstance(results, dict):
        _err(f"비교 결과 형식이 잘못됨: {args.results}")

    pair = results.get("pair", {})
    missing_in_code = results.get("missing_in_code", [])
    missing_in_doc = results.get("missing_in_doc", [])
    mismatch = results.get("mismatch", [])
    typed_mismatch = results.get("typed_mismatch", [])

    lines = [
        "# Doc-Code Drift Report",
        "",
        f"- pair: {pair.get('doc', '?')} <-> {pair.get('script', '?')}",
        f"- rule_kind: `{results.get('rule_kind', RULE_REQUIRED_FIELD)}`",
        f"- compared_at: `{results.get('compared_at', '?')}`",
        "",
        f"- missing_in_code: {len(missing_in_code)}",
    ]
    if missing_in_code:
        for item in missing_in_code:
            lines.append(f"  - {item['name']} -> {item['action']}")
    else:
        lines.append("  - 없음")

    lines.append(f"- missing_in_doc: {len(missing_in_doc)}")
    if missing_in_doc:
        for item in missing_in_doc:
            lines.append(f"  - {item['name']} -> {item['action']}")
    else:
        lines.append("  - 없음")

    lines.append(f"- mismatch: {len(mismatch)}")
    if mismatch:
        for item in mismatch:
            lines.append(f"  - {item}")
    else:
        lines.append("  - 없음")

    lines.append(f"- typed_mismatch: {len(typed_mismatch)}")
    if typed_mismatch:
        for item in typed_mismatch:
            kind = item.get("kind", "?")
            name = item.get("name", "?")
            doc_only = ", ".join(item.get("doc_only", [])) or "-"
            code_only = ", ".join(item.get("code_only", [])) or "-"
            action = item.get("action", "후속 정렬 검토")
            lines.append(
                f"  - [{kind}] {name} | doc_only={doc_only} | code_only={code_only} -> {action}"
            )
    else:
        lines.append("  - 없음")

    print("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="doc-code-sync-checker pairwise vertical slices (v0.1 smoke-test)"
    )
    sub = parser.add_subparsers(dest="command")

    p_doc = sub.add_parser("extract-doc", help="문서 규칙 추출")
    p_doc.add_argument("--doc", required=True, help="reference 문서 경로")
    p_doc.add_argument(
        "--rule-kind",
        default=RULE_REQUIRED_FIELD,
        choices=sorted(SUPPORTED_RULE_KINDS),
        help="비교할 rule kind",
    )

    p_code = sub.add_parser("extract-code", help="코드 규칙 추출")
    p_code.add_argument("--script", required=True, help="validate 포함 스크립트 경로")
    p_code.add_argument(
        "--rule-kind",
        default=RULE_REQUIRED_FIELD,
        choices=sorted(SUPPORTED_RULE_KINDS),
        help="비교할 rule kind",
    )

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
