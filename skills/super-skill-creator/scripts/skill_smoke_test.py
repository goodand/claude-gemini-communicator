#!/usr/bin/env python3
"""Skill smoke test — SKILL.md 작동 가능성과 스크립트 실행을 검증한다.

사용법:
    python3 skill_smoke_test.py <skill_dir>
    python3 skill_smoke_test.py <skill_dir> --verbose
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def check_skill_md(skill_dir, verbose=False):
    """SKILL.md 필수 섹션 존재 확인."""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [("ERROR", "SKILL.md 없음")]

    text = skill_md.read_text(encoding="utf-8")
    results = []

    required_sections = ["## When to use", "## Workflow", "## Scripts", "## References", "## Notes"]
    for section in required_sections:
        if section in text:
            if verbose:
                results.append(("OK", f"섹션 존재: {section}"))
        else:
            results.append(("WARN", f"섹션 누락: {section}"))

    # Workflow에 scripts/ 포인터가 있는지
    if "scripts/" in text or "scripts\\" in text:
        if verbose:
            results.append(("OK", "Workflow에 scripts/ 포인터 있음"))
    else:
        results.append(("WARN", "SKILL.md에 scripts/ 참조가 없음"))

    # References에 references/ 포인터가 있는지
    if "references/" in text or "references\\" in text:
        if verbose:
            results.append(("OK", "references/ 포인터 있음"))
    else:
        results.append(("WARN", "SKILL.md에 references/ 참조가 없음"))

    return results


def check_scripts_run(skill_dir, verbose=False):
    """scripts/ 내 .py 파일이 --help로 실행 가능한지 확인."""
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return [("WARN", "scripts/ 디렉토리 없음")]

    results = []
    py_files = list(scripts_dir.glob("*.py"))

    if not py_files:
        results.append(("WARN", "scripts/ 에 .py 파일 없음"))
        return results

    for py_file in py_files:
        try:
            r = subprocess.run(
                [sys.executable, str(py_file), "--help"],
                capture_output=True, text=True, timeout=10,
            )
            if r.returncode == 0:
                results.append(("OK", f"{py_file.name} --help 성공"))
            else:
                results.append(("WARN", f"{py_file.name} --help 실패 (exit {r.returncode})"))
                if verbose and r.stderr:
                    results.append(("INFO", f"  stderr: {r.stderr.strip()[:200]}"))
        except subprocess.TimeoutExpired:
            results.append(("WARN", f"{py_file.name} --help 타임아웃 (10초)"))
        except FileNotFoundError:
            results.append(("ERROR", "Python 인터프리터를 찾을 수 없음"))
            break

    return results


def check_evals(skill_dir, verbose=False):
    """evals/evals.json 존재 및 기본 구조 확인."""
    evals_file = skill_dir / "evals" / "evals.json"
    if not evals_file.exists():
        return [("WARN", "evals/evals.json 없음")]

    import json
    try:
        data = json.loads(evals_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [("ERROR", f"evals.json 파싱 실패: {e}")]

    results = []

    # 스키마 확인: skill_name + evals 배열
    if "skill_name" not in data:
        results.append(("WARN", "evals.json에 skill_name 필드 없음"))
    if "evals" not in data:
        results.append(("ERROR", "evals.json에 evals 배열 없음"))
        return results

    evals = data["evals"]
    if len(evals) < 4:
        results.append(("WARN", f"eval 수 부족: {len(evals)}개 (권장 4개 이상)"))

    for ev in evals:
        missing = [f for f in ["id", "prompt", "expected_output", "assertions"] if f not in ev]
        if missing:
            results.append(("WARN", f"eval id={ev.get('id','?')}: 필드 누락 {missing}"))

    if not results:
        results.append(("OK", f"evals.json 정상 ({len(evals)}개 eval)"))

    return results


def check_references(skill_dir, verbose=False):
    """references/ 파일 존재 확인."""
    refs_dir = skill_dir / "references"
    if not refs_dir.is_dir():
        return [("WARN", "references/ 디렉토리 없음")]

    ref_files = [f for f in refs_dir.iterdir() if f.is_file() and f.name != ".gitkeep"]
    if not ref_files:
        return [("WARN", "references/ 에 파일 없음")]

    return [("OK", f"references/ 에 {len(ref_files)}개 파일")]


def main():
    if len(sys.argv) < 2:
        print("Usage: skill_smoke_test.py <skill_dir> [--verbose]")
        sys.exit(1)

    skill_dir = Path(sys.argv[1])
    verbose = "--verbose" in sys.argv

    if str(skill_dir) == "--help" or str(skill_dir) == "-h":
        print("Usage: skill_smoke_test.py <skill_dir> [--verbose]")
        print("  skill_dir: 검증할 스킬 디렉토리 경로")
        print("  --verbose: 상세 출력")
        sys.exit(0)

    if not skill_dir.is_dir():
        print(f"[ERROR] 디렉토리 없음: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Smoke testing: {skill_dir.name}")
    print("=" * 50)

    all_results = []
    checks = [
        ("SKILL.md 구조", check_skill_md),
        ("Scripts 실행", check_scripts_run),
        ("Evals 구조", check_evals),
        ("References 존재", check_references),
    ]

    has_error = False
    for label, check_fn in checks:
        results = check_fn(skill_dir, verbose)
        all_results.extend(results)
        print(f"\n[{label}]")
        for level, msg in results:
            prefix = {"OK": "  v", "WARN": "  !", "ERROR": "  x", "INFO": "   "}.get(level, "  ?")
            print(f"{prefix} {msg}")
            if level == "ERROR":
                has_error = True

    # 요약
    ok_count = sum(1 for l, _ in all_results if l == "OK")
    warn_count = sum(1 for l, _ in all_results if l == "WARN")
    err_count = sum(1 for l, _ in all_results if l == "ERROR")

    print(f"\n{'=' * 50}")
    print(f"결과: OK={ok_count}  WARN={warn_count}  ERROR={err_count}")

    if has_error:
        print("Smoke test FAILED")
        sys.exit(1)
    elif warn_count > 0:
        print("Smoke test PASSED (경고 있음)")
        sys.exit(0)
    else:
        print("Smoke test PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
