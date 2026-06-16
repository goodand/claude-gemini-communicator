#!/usr/bin/env python3
"""edge-case-generator 통합 래퍼.

validate 함수를 분석하여 경계값·무효값 테스트 입력을 자동 생성한다.

Usage:
    python3 edgegen.py analyze --script <script.py>
    python3 edgegen.py generate --script <script.py> [--output <dir>]
    python3 edgegen.py run --script <script.py> --cases <dir>
    python3 edgegen.py report --results <results.json>
"""
from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import inspect
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

KST = timezone(timedelta(hours=9))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _now_iso():
    return datetime.now(KST).isoformat(timespec="seconds")


def _load_source(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _save_json(path, data):
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _err(msg):
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


# ---------------------------------------------------------------------------
# analyze: validate 함수에서 검증 규칙 추출
# ---------------------------------------------------------------------------

def _find_set_constants(source):
    """소스에서 set/frozenset 상수 정의를 추출한다."""
    constants = {}
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
                    # set literal: {a, b, c}
                    if isinstance(node.value, ast.Set):
                        vals = []
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Constant):
                                vals.append(elt.value)
                        if vals:
                            constants[name] = vals
    return constants


def _find_validate_functions(source):
    """validate_ 또는 validate로 시작하는 함수를 찾는다."""
    tree = ast.parse(source)
    funcs = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.FunctionDef)
            and node.name.startswith("validate")
            and not node.name.startswith("cmd_")
        ):
            funcs.append(node)
    return funcs


def _get_validate_source(source):
    """실제 validate 함수 본문만 추출한다."""
    segments = []
    for node in _find_validate_functions(source):
        segment = ast.get_source_segment(source, node)
        if segment:
            segments.append(segment)
    return "\n\n".join(segments)


def _guess_enum_field(validate_source, constant_name):
    """VALID_* 상수가 검증하는 실제 필드명을 추정한다."""
    patterns = [
        rf'data\[\s*[\'"]([\w]+)[\'"]\s*\]\s+not in\s+{re.escape(constant_name)}',
        rf'data\.get\(\s*[\'"]([\w]+)[\'"]\s*.*?\)\s+not in\s+{re.escape(constant_name)}',
    ]
    for pattern in patterns:
        match = re.search(pattern, validate_source)
        if match:
            return match.group(1)

    lowered = constant_name.lower()
    if lowered.startswith("valid_"):
        lowered = lowered[len("valid_"):]
    if lowered.endswith("ies"):
        return lowered[:-3] + "y"
    if lowered.endswith("s"):
        return lowered[:-1]
    return lowered


def _guess_path_field(validate_source):
    """경로 안전성 검사가 적용되는 필드명을 추정한다."""
    for field in ("locked_paths", "allowed_paths", "forbidden_paths", "context_files"):
        if f'"{field}" in data' in validate_source or f"'{field}' in data" in validate_source:
            return field
    return "_path_field"


def _guess_path_base(validate_source):
    """상대경로 해석 기준을 추정한다."""
    if "_resolve_repo_path" in validate_source or "show-toplevel" in validate_source:
        return "repo_root"
    return "cwd"


def extract_rules(source):
    """소스 코드에서 검증 규칙을 추출한다."""
    constants = _find_set_constants(source)
    validate_source = _get_validate_source(source)
    rules = []

    if not validate_source:
        return rules

    # 패턴 1: REQUIRED_FIELDS 참조
    for name, vals in constants.items():
        upper = name.upper()
        if name not in validate_source:
            continue
        if "REQUIRED" in upper and "FIELD" in upper:
            rules.append({
                "type": "required_field",
                "constant": name,
                "fields": sorted(vals),
                "description": f"필수 필드 {len(vals)}개 존재 확인",
            })
        elif "FORBIDDEN" in upper and "FIELD" in upper:
            rules.append({
                "type": "forbidden_field",
                "constant": name,
                "fields": sorted(vals),
                "description": f"금지 필드 {len(vals)}개 부재 확인",
            })
        elif "VALID" in upper and ("STATUS" in upper or "PRIORITIES" in upper or "TYPES" in upper):
            rules.append({
                "type": "enum_value",
                "constant": name,
                "field": _guess_enum_field(validate_source, name),
                "values": sorted(vals),
                "description": f"열거형 {name}: {len(vals)}개 유효 값",
            })
        elif "TRANSITION" in upper:
            rules.append({
                "type": "cross_field",
                "constant": name,
                "description": f"상태 전이 테이블: {name}",
            })

    # 패턴 2: len() 검사 (문자열 길이)
    len_pattern = re.compile(
        r'len\((?:str\()?data(?:\[|\.get\()[\'"]([\w]+)[\'"]'
        r'.*?<\s*(\d+)'
    )
    for m in len_pattern.finditer(validate_source):
        field, min_len = m.group(1), int(m.group(2))
        rules.append({
            "type": "string_length",
            "field": field,
            "min_length": min_len,
            "description": f"{field}: 최소 {min_len}자",
        })

    # 패턴 3: path safety (".." in, startswith("/"), islink)
    path_field = _guess_path_field(validate_source)
    path_base = _guess_path_base(validate_source)
    if '".."' in validate_source or "'..'" in validate_source:
        rules.append({
            "type": "path_safety",
            "check": "path_traversal",
            "field": path_field,
            "path_base": path_base,
            "description": "'..' path traversal 검사",
        })
    if 'startswith("/")' in validate_source or "startswith('/')" in validate_source:
        rules.append({
            "type": "path_safety",
            "check": "absolute_path",
            "field": path_field,
            "path_base": path_base,
            "description": "절대경로 검사",
        })
    if "islink" in validate_source:
        rules.append({
            "type": "path_safety",
            "check": "symlink",
            "field": path_field,
            "path_base": path_base,
            "description": "symlink 검사",
        })

    # 패턴 4: isinstance 타입 검사
    isinstance_pattern = re.compile(
        r'isinstance\((?:data(?:\[|\.get\()[\'"]([\w]+)[\'"].*?),\s*(list|str|int|dict)\)'
    )
    for m in isinstance_pattern.finditer(validate_source):
        field, expected_type = m.group(1), m.group(2)
        rules.append({
            "type": "type_check",
            "field": field,
            "expected_type": expected_type,
            "description": f"{field}: 타입 {expected_type} 확인",
        })

    # 패턴 5: 배열 길이 검사
    list_len_pattern = re.compile(
        r'len\((?:data(?:\[|\.get\()[\'"]([\w]+)[\'"].*?)\)\s*==\s*0'
    )
    for m in list_len_pattern.finditer(validate_source):
        field = m.group(1)
        rules.append({
            "type": "list_constraint",
            "field": field,
            "min_items": 1,
            "description": f"{field}: 최소 1개 이상",
        })

    # 패턴 6: cross-field (subset, overlap 등)
    if "subset" in validate_source.lower() or "⊆" in validate_source or "_within_scope" in validate_source:
        rules.append({
            "type": "cross_field",
            "check": "subset",
            "description": "경로 범위 포함 관계 검사 (locked ⊆ allowed)",
        })
    if "overlap" in validate_source.lower() or "겹침" in validate_source:
        rules.append({
            "type": "cross_field",
            "check": "overlap",
            "description": "경로 겹침 검사",
        })

    # 중복 제거
    seen = set()
    unique = []
    for r in rules:
        key = json.dumps(r, sort_keys=True)
        if key not in seen:
            seen.add(key)
            unique.append(r)

    return unique


def cmd_analyze(args):
    source = _load_source(args.script)
    rules = extract_rules(source)

    if not rules:
        print("[WARN] 검증 규칙을 찾지 못함", file=sys.stderr)

    print(json.dumps({
        "script": args.script,
        "rules_found": len(rules),
        "rules": rules,
        "analyzed_at": _now_iso(),
    }, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# generate: 규칙별 edge case JSON 생성
# ---------------------------------------------------------------------------

def _default_enum_value(field, values):
    """필드 성격에 맞는 기본 enum 값을 고른다."""
    preferred = {
        "priority": "medium",
        "status": "queued",
    }
    target = preferred.get(field)
    if target in values:
        return target
    return values[0] if values else "placeholder"


def _placeholder_for_field(field, enum_defaults):
    """필드명 기반 기본 placeholder 생성."""
    if field in enum_defaults:
        return enum_defaults[field]
    if field.endswith("_version"):
        return "0.1"
    if field == "task_id":
        return "TASK-0001"
    if field == "dispatch_id":
        return "DISPATCH-0001"
    if field == "title":
        return "테스트 작업 제목"
    if field == "goal":
        return "충분히 긴 테스트 목표 설명입니다"
    if field == "why":
        return "테스트 이유"
    if field in {"created_at", "updated_at"}:
        return _now_iso()
    if field in {"created_by", "assigned_agent"}:
        return "tester"
    if field == "branch":
        return "feat/test-task"
    if field == "worktree_path":
        return ".worktrees/test-task"
    if field == "packet_path":
        return "agent-task-packet/.codex/packets/TASK-0001.json"
    if field.endswith("_paths") or field in {"allowed_paths", "forbidden_paths", "locked_paths", "context_files"}:
        return ["src/"]
    if field == "history":
        now = _now_iso()
        return [{"from": None, "to": "queued", "at": now, "by": "tester", "reason": "test"}]
    if field in {"done_definition", "required_checks", "deliverables"}:
        return ["placeholder"]
    if field == "constraints":
        return {}
    if field == "revision":
        return 1
    return "placeholder"


def _build_baseline_input(rules):
    """검증을 통과할 가능성이 높은 baseline 객체를 만든다."""
    required_fields = []
    enum_defaults = {}

    for rule in rules:
        if rule["type"] == "required_field":
            required_fields = rule.get("fields", [])
        elif rule["type"] == "enum_value":
            field = rule.get("field")
            if field:
                enum_defaults[field] = _default_enum_value(field, rule.get("values", []))

    baseline = {}
    for field in required_fields:
        baseline[field] = _placeholder_for_field(field, enum_defaults)

    return baseline


def _clone_with_overrides(baseline, overrides):
    data = copy.deepcopy(baseline)
    data.update(copy.deepcopy(overrides))
    return data


def _path_value(field, raw_path):
    if field.endswith("_paths") or field in {"allowed_paths", "forbidden_paths", "locked_paths", "context_files"}:
        return [raw_path]
    return raw_path


def _find_repo_root(start_dir=None):
    """현재 경로에서 가장 가까운 git repo root를 찾는다."""
    current = Path(start_dir or os.getcwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / ".git").exists():
            return str(candidate)
    return str(current)


def _make_symlink_fixture(case_name, path_base="cwd"):
    """현재 작업 디렉토리 아래에 실제 symlink fixture를 만든다."""
    fixture_root = tempfile.mkdtemp(prefix=f".edgegen-{case_name}-", dir=".")
    target_dir = os.path.join(fixture_root, "real")
    link_path = os.path.join(fixture_root, "link")
    os.makedirs(target_dir, exist_ok=True)
    os.symlink(target_dir, link_path)
    base_dir = _find_repo_root() if path_base == "repo_root" else os.getcwd()
    rel_path = os.path.relpath(os.path.abspath(link_path), base_dir)
    return fixture_root, rel_path


def _apply_case_setup(case):
    """케이스별 실행 전 setup 적용. (patched_input, cleanup_dir) 반환."""
    test_input = copy.deepcopy(case.get("input", {}))
    setup = case.get("setup")
    if not setup:
        return test_input, None

    kind = setup.get("kind")
    if kind == "symlink":
        field = setup.get("field")
        if not field:
            raise ValueError("symlink setup에 field가 없다")
        path_base = setup.get("path_base", "cwd")
        cleanup_dir, rel_path = _make_symlink_fixture(case.get("name", "case"), path_base)
        test_input[field] = _path_value(field, rel_path)
        return test_input, cleanup_dir

    return test_input, None


def _gen_required_field_cases(rule, baseline):
    """필수 필드 규칙에서 edge case 생성."""
    fields = rule.get("fields", [])
    cases = []

    # 전체 누락
    cases.append({
        "name": "empty_object",
        "input": {},
        "expect": "fail",
        "reason": "필수 필드 전부 누락",
    })

    cases.append({
        "name": "minimal_valid",
        "input": copy.deepcopy(baseline),
        "expect": "pass",
        "reason": "모든 필수 필드 placeholder로 존재",
    })

    # 각 필드를 하나씩 제거
    for f in fields:
        reduced = copy.deepcopy(baseline)
        reduced.pop(f, None)
        cases.append({
            "name": f"missing_{f}",
            "input": reduced,
            "expect": "fail",
            "reason": f"필수 필드 '{f}' 누락",
        })

    return cases


def _gen_forbidden_field_cases(rule, baseline):
    """금지 필드 규칙에서 edge case 생성."""
    fields = rule.get("fields", [])
    cases = []

    for f in fields:
        cases.append({
            "name": f"forbidden_{f}",
            "input": _clone_with_overrides(baseline, {f: "should_not_exist"}),
            "expect": "fail",
            "reason": f"금지 필드 '{f}' 포함",
        })

    return cases


def _gen_string_length_cases(rule, baseline):
    """문자열 길이 규칙에서 edge case 생성."""
    field = rule.get("field", "unknown")
    min_len = rule.get("min_length", 1)
    cases = []

    cases.append({
        "name": f"{field}_empty",
        "input": _clone_with_overrides(baseline, {field: ""}),
        "expect": "fail",
        "reason": f"{field} 빈 문자열",
    })

    cases.append({
        "name": f"{field}_whitespace_only",
        "input": _clone_with_overrides(baseline, {field: " " * min_len}),
        "expect": "warn_or_fail",
        "reason": f"{field} 공백만 (strip 후 0자)",
    })

    if min_len > 1:
        cases.append({
            "name": f"{field}_boundary_minus1",
            "input": _clone_with_overrides(baseline, {field: "a" * (min_len - 1)}),
            "expect": "fail",
            "reason": f"{field} {min_len-1}자 (경계값 미달)",
        })

    cases.append({
        "name": f"{field}_boundary_exact",
        "input": _clone_with_overrides(baseline, {field: "a" * min_len}),
        "expect": "pass",
        "reason": f"{field} 정확히 {min_len}자 (경계값)",
    })

    cases.append({
        "name": f"{field}_numeric_type",
        "input": _clone_with_overrides(baseline, {field: 12345}),
        "expect": "warn_or_fail",
        "reason": f"{field} 숫자 타입 (str() 변환 시 통과 가능)",
    })

    return cases


def _gen_enum_value_cases(rule, baseline):
    """열거형 규칙에서 edge case 생성."""
    field = rule.get("field", "_enum_field")
    values = rule.get("values", [])
    constant_name = rule.get("constant", "UNKNOWN")
    cases = []

    # 유효 값 각각
    for v in values[:4]:  # 대표 4개
        cases.append({
            "name": f"{constant_name}_valid_{v}",
            "input": _clone_with_overrides(baseline, {field: v}),
            "expect": "pass",
            "reason": f"유효 값 '{v}'",
        })

    # 무효 값
    invalid_candidates = ["invalid", "", None, "UNKNOWN", "완료"]
    for inv in invalid_candidates:
        inv_name = str(inv).replace(" ", "_")
        cases.append({
            "name": f"{constant_name}_invalid_{inv_name}",
            "input": _clone_with_overrides(baseline, {field: inv}),
            "expect": "fail",
            "reason": f"무효 값 '{inv}'",
        })

    # 대소문자 변형
    if values:
        v = values[0]
        variant = v.upper() if v != v.upper() else v.capitalize()
        cases.append({
            "name": f"{constant_name}_case_variation",
            "input": _clone_with_overrides(baseline, {field: variant}),
            "expect": "fail",
            "reason": f"대소문자 변형 '{v}' → '{v.upper()}'",
        })

    return cases


def _gen_path_safety_cases(rule, baseline):
    """경로 안전성 규칙에서 edge case 생성."""
    check = rule.get("check", "")
    field = rule.get("field", "_path_field")
    path_base = rule.get("path_base", "cwd")
    cases = []

    if check == "path_traversal":
        for p in ["../secret", "src/../../etc/passwd", "a/../b"]:
            cases.append({
                "name": f"traversal_{p.replace('/', '_').replace('.', '')}",
                "input": _clone_with_overrides(baseline, {field: _path_value(field, p)}),
                "expect": "fail",
                "reason": f"path traversal: '{p}'",
            })

    elif check == "absolute_path":
        for p in ["/etc/passwd", "/tmp/test", "/root"]:
            cases.append({
                "name": f"absolute_{p.replace('/', '_')}",
                "input": _clone_with_overrides(baseline, {field: _path_value(field, p)}),
                "expect": "fail",
                "reason": f"절대경로: '{p}'",
            })

    elif check == "symlink":
        cases.append({
            "name": "symlink_path",
            "input": _clone_with_overrides(baseline, {field: _path_value(field, "__EDGEGEN_SYMLINK__")}),
            "expect": "fail",
            "reason": "symlink 경로 (run 단계에서 실제 fixture 생성)",
            "setup": {
                "kind": "symlink",
                "field": field,
                "path_base": path_base,
            },
        })

    # 공통 정상 케이스
    for p in ["src/", "src/auth/", "tests/test_auth.py"]:
        cases.append({
            "name": f"valid_path_{p.replace('/', '_')}",
            "input": _clone_with_overrides(baseline, {field: _path_value(field, p)}),
            "expect": "pass",
            "reason": f"정상 상대경로: '{p}'",
        })

    return cases


def _gen_list_constraint_cases(rule, baseline):
    """배열 제약 규칙에서 edge case 생성."""
    field = rule.get("field", "unknown")
    cases = []

    cases.append({"name": f"{field}_empty_list", "input": _clone_with_overrides(baseline, {field: []}), "expect": "fail", "reason": "빈 배열"})
    cases.append({"name": f"{field}_string_type", "input": _clone_with_overrides(baseline, {field: "not_a_list"}), "expect": "fail", "reason": "문자열 (타입 오류)"})
    cases.append({"name": f"{field}_null", "input": _clone_with_overrides(baseline, {field: None}), "expect": "fail", "reason": "null"})
    cases.append({"name": f"{field}_single_item", "input": _clone_with_overrides(baseline, {field: ["one"]}), "expect": "pass", "reason": "단일 항목"})
    cases.append({"name": f"{field}_mixed_types", "input": _clone_with_overrides(baseline, {field: [123, None, ""]}), "expect": "warn_or_fail", "reason": "항목 내부 타입 혼재"})

    return cases


def _gen_type_check_cases(rule, baseline):
    """타입 검사 규칙에서 edge case 생성."""
    field = rule.get("field", "unknown")
    expected_type = rule.get("expected_type", "str")
    cases = []

    valid_value = baseline.get(field, _placeholder_for_field(field, {}))
    cases.append({
        "name": f"{field}_type_valid",
        "input": _clone_with_overrides(baseline, {field: valid_value}),
        "expect": "pass",
        "reason": f"{field} 정상 타입 {expected_type}",
    })

    invalid_values = {
        "int": ["1", 1.5, None],
        "str": [123, None, ""],
        "list": ["not_a_list", None, {}],
        "dict": ["not_a_dict", None, []],
    }
    for idx, invalid in enumerate(invalid_values.get(expected_type, [None])):
        cases.append({
            "name": f"{field}_type_invalid_{idx+1}",
            "input": _clone_with_overrides(baseline, {field: invalid}),
            "expect": "fail",
            "reason": f"{field} 잘못된 타입 {type(invalid).__name__}",
        })

    return cases


def _gen_cross_field_cases(rule, baseline):
    """필드 간 관계 규칙에서 edge case 생성."""
    check = rule.get("check", "")
    cases = []

    if check == "subset":
        cases.append({
            "name": "locked_outside_allowed",
            "input": _clone_with_overrides(baseline, {"allowed_paths": ["src/"], "locked_paths": ["tests/"]}),
            "expect": "fail",
            "reason": "locked_paths가 allowed_paths 범위 밖",
        })
        cases.append({
            "name": "locked_within_allowed",
            "input": _clone_with_overrides(baseline, {"allowed_paths": ["src/"], "locked_paths": ["src/auth/"]}),
            "expect": "pass",
            "reason": "locked_paths ⊆ allowed_paths",
        })

    if check == "overlap":
        cases.append({
            "name": "allowed_forbidden_overlap",
            "input": _clone_with_overrides(baseline, {"allowed_paths": ["src/"], "forbidden_paths": ["src/"]}),
            "expect": "fail",
            "reason": "allowed와 forbidden 겹침",
        })

    return cases


def generate_cases(rules, baseline):
    """규칙 목록에서 전체 edge case 생성."""
    generators = {
        "required_field": _gen_required_field_cases,
        "forbidden_field": _gen_forbidden_field_cases,
        "string_length": _gen_string_length_cases,
        "enum_value": _gen_enum_value_cases,
        "path_safety": _gen_path_safety_cases,
        "list_constraint": _gen_list_constraint_cases,
        "cross_field": _gen_cross_field_cases,
        "type_check": _gen_type_check_cases,
    }

    all_cases = []
    for rule in rules:
        gen = generators.get(rule["type"])
        if gen:
            cases = gen(rule, baseline)
            for c in cases:
                c["rule_type"] = rule["type"]
                c["rule_description"] = rule.get("description", "")
            all_cases.extend(cases)

    return all_cases


def cmd_generate(args):
    source = _load_source(args.script)
    rules = extract_rules(source)

    if not rules:
        _err("검증 규칙을 찾지 못함")

    baseline = _build_baseline_input(rules)
    cases = generate_cases(rules, baseline)
    output_dir = args.output or "edge_cases"
    os.makedirs(output_dir, exist_ok=True)

    # 전체 케이스 저장
    summary_path = os.path.join(output_dir, "cases_summary.json")
    _save_json(summary_path, {
        "script": args.script,
        "rules_count": len(rules),
        "cases_count": len(cases),
        "baseline_input": baseline,
        "generated_at": _now_iso(),
        "cases": cases,
    })

    # 규칙 유형별 그룹 저장
    by_type = {}
    for c in cases:
        rt = c["rule_type"]
        by_type.setdefault(rt, []).append(c)

    for rt, group in by_type.items():
        type_path = os.path.join(output_dir, f"cases_{rt}.json")
        _save_json(type_path, group)

    print(f"[OK] {len(cases)}개 edge case 생성 → {output_dir}/")
    print(f"     규칙 {len(rules)}개 → 케이스 {len(cases)}개")
    for rt, group in sorted(by_type.items()):
        print(f"     {rt}: {len(group)}개")


# ---------------------------------------------------------------------------
# run: edge case로 validate 실행
# ---------------------------------------------------------------------------

def _import_validate_func(script_path):
    """스크립트에서 validate 함수를 동적 임포트."""
    spec = importlib.util.spec_from_file_location("target_module", script_path)
    if spec is None or spec.loader is None:
        _err(f"모듈 spec/loader 생성 실패: {script_path}")
    module = importlib.util.module_from_spec(spec)

    old_argv = sys.argv[:]
    try:
        sys.argv = [script_path]
        spec.loader.exec_module(module)
    finally:
        sys.argv = old_argv

    # validate 함수 탐색
    candidates = []
    for name in dir(module):
        func = getattr(module, name)
        if not callable(func):
            continue
        if not (name.startswith("validate") and not name.startswith("cmd_")):
            continue
        try:
            sig = inspect.signature(func)
        except (TypeError, ValueError):
            continue
        if len(sig.parameters) == 1:
            candidates.append((name, func))

    if candidates:
        candidates.sort(key=lambda item: (0 if item[0].startswith("validate_") else 1, item[0]))
        return candidates[0]

    return None, None


def cmd_run(args):
    cases_path = os.path.join(args.cases, "cases_summary.json")
    if not os.path.isfile(cases_path):
        _err(f"케이스 파일 없음: {cases_path}")

    with open(cases_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    cases = data.get("cases", [])

    func_name, validate_func = _import_validate_func(args.script)
    if not validate_func:
        _err(f"validate 함수를 찾지 못함: {args.script}")

    print(f"[INFO] {func_name}() 사용, {len(cases)}개 케이스 실행", file=sys.stderr)

    results = []
    pass_count = 0
    fail_count = 0
    unexpected = 0

    for c in cases:
        cleanup_dir = None
        expected = c.get("expect", "unknown")
        name = c.get("name", "?")

        try:
            test_input, cleanup_dir = _apply_case_setup(c)
            ret = validate_func(test_input)
            # (errors, warnings) 튜플 반환 가정
            if isinstance(ret, tuple) and len(ret) == 2:
                errors, warnings = ret
            else:
                errors, warnings = [], []

            actual = "fail" if errors else "pass"

            match = False
            if expected == "fail" and actual == "fail":
                match = True
            elif expected == "pass" and actual == "pass":
                match = True
            elif expected in ("pass_or_warn", "warn_or_fail"):
                match = True  # 유연한 기대

            if match:
                pass_count += 1
                status = "OK"
            else:
                unexpected += 1
                status = "UNEXPECTED"
                fail_count += 1

            results.append({
                "name": name,
                "expected": expected,
                "actual": actual,
                "status": status,
                "errors": errors[:3] if errors else [],
                "warnings": warnings[:3] if warnings else [],
            })

        except Exception as e:
            fail_count += 1
            results.append({
                "name": name,
                "expected": expected,
                "actual": "exception",
                "status": "EXCEPTION",
                "error_message": str(e),
            })
        finally:
            if cleanup_dir:
                shutil.rmtree(cleanup_dir, ignore_errors=True)

    # 결과 출력
    print(f"\n{'Name':40s} {'Expected':12s} {'Actual':8s} {'Status':12s}")
    print("-" * 75)
    for r in results:
        marker = "" if r["status"] == "OK" else " ←"
        print(f"{r['name']:40s} {r['expected']:12s} {r['actual']:8s} {r['status']:12s}{marker}")

    print(f"\n총 {len(results)}개: OK={pass_count}, UNEXPECTED={unexpected}, EXCEPTION={fail_count - unexpected}")

    # 결과 저장
    results_path = os.path.join(args.cases, "run_results.json")
    _save_json(results_path, {
        "script": args.script,
        "validate_func": func_name,
        "total": len(results),
        "ok": pass_count,
        "unexpected": unexpected,
        "run_at": _now_iso(),
        "results": results,
    })
    print(f"\n결과 저장: {results_path}", file=sys.stderr)


# ---------------------------------------------------------------------------
# report: 결과 분석
# ---------------------------------------------------------------------------

def cmd_report(args):
    with open(args.results, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = data.get("results", [])
    unexpected = [r for r in results if r.get("status") in ("UNEXPECTED", "EXCEPTION")]

    print("=" * 60)
    print(f"EDGE CASE REPORT — {data.get('script', '?')}")
    print(f"validate: {data.get('validate_func', '?')}")
    print(f"실행: {data.get('run_at', '?')}")
    print("=" * 60)
    print(f"\n총 {data.get('total', 0)}개 중 OK={data.get('ok', 0)}, 문제={len(unexpected)}")

    if unexpected:
        print(f"\n{'─' * 60}")
        print("문제 케이스 상세:")
        print(f"{'─' * 60}")
        for r in unexpected:
            print(f"\n  [{r['status']}] {r['name']}")
            print(f"    기대: {r['expected']} → 실제: {r['actual']}")
            if r.get("errors"):
                print(f"    에러: {r['errors'][0]}")
            if r.get("error_message"):
                print(f"    예외: {r['error_message']}")

        print(f"\n{'─' * 60}")
        print("조치 가이드:")
        print(f"{'─' * 60}")

        fail_expected_pass = [r for r in unexpected if r.get("expected") == "fail" and r.get("actual") == "pass"]
        pass_expected_fail = [r for r in unexpected if r.get("expected") == "pass" and r.get("actual") == "fail"]
        exceptions = [r for r in unexpected if r.get("status") == "EXCEPTION"]

        if fail_expected_pass:
            print(f"\n  실패해야 하는데 통과 ({len(fail_expected_pass)}건) → validate에 검증 규칙 추가 필요:")
            for r in fail_expected_pass:
                print(f"    - {r['name']}")

        if pass_expected_fail:
            print(f"\n  통과해야 하는데 실패 ({len(pass_expected_fail)}건) → 과잉 검증 또는 정상 범위 재검토:")
            for r in pass_expected_fail:
                print(f"    - {r['name']}")

        if exceptions:
            print(f"\n  예외 발생 ({len(exceptions)}건) → 입력 타입 처리 또는 방어 코드 필요:")
            for r in exceptions:
                print(f"    - {r['name']}: {r.get('error_message', '?')}")
    else:
        print("\n모든 케이스가 기대대로 동작. 검증 규칙 정합.")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="edge-case-generator 통합 래퍼"
    )
    sub = parser.add_subparsers(dest="command")

    # analyze
    p_analyze = sub.add_parser("analyze", help="validate 함수에서 검증 규칙 추출")
    p_analyze.add_argument("--script", required=True, help="대상 스크립트 경로")

    # generate
    p_gen = sub.add_parser("generate", help="규칙별 edge case JSON 생성")
    p_gen.add_argument("--script", required=True, help="대상 스크립트 경로")
    p_gen.add_argument("--output", "-o", help="출력 디렉토리 (기본: edge_cases)")

    # run
    p_run = sub.add_parser("run", help="edge case로 validate 실행")
    p_run.add_argument("--script", required=True, help="대상 스크립트 경로")
    p_run.add_argument("--cases", required=True, help="케이스 디렉토리")

    # report
    p_report = sub.add_parser("report", help="실행 결과 분석·보고")
    p_report.add_argument("--results", required=True, help="run_results.json 경로")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    cmds = {
        "analyze": cmd_analyze,
        "generate": cmd_generate,
        "run": cmd_run,
        "report": cmd_report,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
