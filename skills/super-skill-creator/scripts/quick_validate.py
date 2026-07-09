#!/usr/bin/env python3
"""Validate skill directory structure and SKILL.md quality.

사용법:
    python3 quick_validate.py <skill_dir>
    python3 quick_validate.py <skill_dir> --strict
"""
from __future__ import annotations

import re
import sys
from pathlib import Path


DOC_EXTS = {".md", ".txt", ".rst"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".bmp", ".ico"}
CODELIKE_EXTS = {
    ".py", ".sh", ".bash", ".zsh", ".js", ".ts", ".tsx", ".jsx",
    ".rb", ".go", ".rs", ".java", ".c", ".cc", ".cpp", ".cxx",
    ".swift", ".kt", ".kts", ".php",
}


def validate_frontmatter(text):
    """YAML frontmatter 존재 및 필수 필드 검증."""
    if not text.startswith("---\n"):
        return False, "Missing YAML frontmatter start"

    parts = text.split("---", 2)
    if len(parts) < 3:
        return False, "Invalid YAML frontmatter"

    frontmatter = parts[1]
    if not re.search(r"(?m)^name:\s*", frontmatter):
        return False, "Missing 'name' field"
    if not re.search(r"(?m)^description:\s*", frontmatter):
        return False, "Missing 'description' field"

    return True, "OK"


def validate_description_pattern(text):
    """description이 'Use this skill when...' 패턴을 따르는지 확인."""
    parts = text.split("---", 2)
    if len(parts) < 3:
        return True, "Skipped (no frontmatter)"

    frontmatter = parts[1]
    if "Use this skill when" in frontmatter:
        return True, "OK"
    return False, "description에 'Use this skill when...' 패턴이 없습니다. 트리거 조건을 명시하세요."


def validate_line_count(text, max_lines=50):
    """SKILL.md 줄 수 제한 검증."""
    lines = text.strip().split("\n")
    count = len(lines)
    if count <= max_lines:
        return True, f"OK ({count}줄)"
    return False, f"SKILL.md가 {count}줄입니다 (제한: {max_lines}줄). 상세 내용을 references/로 이동하세요."


def validate_structure(skill_dir):
    """필수 디렉토리 및 필수 파일 존재 확인."""
    warnings = []
    for subdir in ["scripts", "references", "evals"]:
        path = skill_dir / subdir
        if not path.is_dir():
            warnings.append(f"디렉토리 없음: {subdir}/")

    # 필수 파일: references/troubleshooting.md
    ts_path = skill_dir / "references" / "troubleshooting.md"
    if not ts_path.is_file():
        warnings.append(
            "references/troubleshooting.md 없음. "
            "Codex 실험 중 발견된 버그·오류를 기록하는 필수 파일입니다."
        )
    return warnings


def validate_scripts_have_help(skill_dir):
    """scripts/ 내 .py 파일에 argparse 또는 --help 지원 여부."""
    warnings = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return warnings

    for py_file in scripts_dir.glob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="replace")
        if "argparse" not in content and "ArgumentParser" not in content:
            if "sys.argv" in content:
                warnings.append(
                    f"{py_file.name}: argparse를 사용하세요. --help 지원이 필요합니다."
                )
    return warnings


def validate_future_annotations(skill_dir):
    """Python 3.9 호환: from __future__ import annotations 확인."""
    warnings = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return warnings

    for py_file in scripts_dir.glob("*.py"):
        content = py_file.read_text(encoding="utf-8", errors="replace")
        if "str | None" in content or "list[" in content.lower():
            if "from __future__ import annotations" not in content:
                warnings.append(
                    f"{py_file.name}: Python 3.10+ 문법 감지. "
                    "'from __future__ import annotations'를 추가하세요."
                )
    return warnings


def validate_tdd_files(skill_dir):
    """구현 파일/스크립트가 있으면 TDD 파일 존재 여부 확인."""
    findings = []
    scripts_dir = skill_dir / "scripts"
    tests_dir = skill_dir / "tests"

    has_tdd_file = False
    if scripts_dir.is_dir():
        has_tdd_file = has_tdd_file or any(
            path.name.startswith("test_") and path.suffix == ".py"
            for path in scripts_dir.glob("*.py")
        )
    if tests_dir.is_dir():
        has_tdd_file = has_tdd_file or any(
            path.name.startswith("test_") and path.suffix == ".py"
            for path in tests_dir.glob("*.py")
        )

    has_implementation_artifact = False
    if scripts_dir.is_dir():
        for path in scripts_dir.iterdir():
            if not path.is_file():
                continue
            if path.name.startswith("test_"):
                continue
            if path.suffix in DOC_EXTS or path.suffix in IMAGE_EXTS:
                continue
            has_implementation_artifact = True
            break

    if not has_implementation_artifact:
        for path in skill_dir.rglob("*"):
            if not path.is_file():
                continue
            if any(part in {
                "references",
                "knowledge_bases",
                "checklist-forconsistency-evaluation",
                "checklist-forimplementation",
                "legacy",
                "evals",
                "__pycache__",
                ".git",
            } for part in path.parts):
                continue
            if path.parent == scripts_dir or path.parent == tests_dir:
                continue
            if path.suffix in CODELIKE_EXTS:
                has_implementation_artifact = True
                break

    if has_implementation_artifact and not has_tdd_file:
        findings.append(
            "구현 파일 또는 scripts/가 있는데 TDD 파일이 없습니다. "
            "`scripts/test_*.py` 또는 `tests/test_*.py`를 추가하세요."
        )
    return findings


def validate_canonical_kb_presence(skill_dir):
    """정합성 checklist가 있으면 canonical KB 기준이 존재하는지 확인."""
    warnings = []
    kb_dir = skill_dir / "knowledge_bases"
    consistency_dir = skill_dir / "checklist-forconsistency-evaluation"

    if not kb_dir.is_dir() or not consistency_dir.is_dir():
        return warnings

    kb_files = list(kb_dir.glob("*.md"))
    consistency_files = list(consistency_dir.glob("*.md"))
    if not kb_files or not consistency_files:
        return warnings

    for kb_file in kb_files:
        text = kb_file.read_text(encoding="utf-8", errors="replace")
        if "## Canonical Design Takeaways" in text:
            return warnings

    warnings.append(
        "knowledge_bases/와 정합성 checklist가 있습니다. "
        "checklist source of truth로 사용할 Canonical Design Takeaways KB를 추가하세요."
    )
    return warnings


def main():
    if len(sys.argv) < 2:
        print("Usage: quick_validate.py <skill_dir> [--strict]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    strict = "--strict" in sys.argv

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        print("Missing SKILL.md")
        sys.exit(1)

    text = skill_md.read_text(encoding="utf-8")
    errors = []
    warnings = []

    # 필수: frontmatter
    ok, msg = validate_frontmatter(text)
    if not ok:
        errors.append(msg)

    # 필수: description 패턴
    ok, msg = validate_description_pattern(text)
    if not ok:
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    # 필수: 줄 수
    ok, msg = validate_line_count(text)
    if not ok:
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    # 구조 검증
    struct_warnings = validate_structure(skill_dir)
    warnings.extend(struct_warnings)

    # 스크립트 검증
    warnings.extend(validate_scripts_have_help(skill_dir))
    warnings.extend(validate_future_annotations(skill_dir))
    warnings.extend(validate_canonical_kb_presence(skill_dir))
    tdd_findings = validate_tdd_files(skill_dir)
    if strict:
        errors.extend(tdd_findings)
    else:
        warnings.extend(tdd_findings)

    # 결과 출력
    for w in warnings:
        print(f"[WARN] {w}", file=sys.stderr)

    if errors:
        for e in errors:
            print(f"[ERROR] {e}", file=sys.stderr)
        print("Validation failed")
        sys.exit(1)

    print("Validation passed")


if __name__ == "__main__":
    main()
