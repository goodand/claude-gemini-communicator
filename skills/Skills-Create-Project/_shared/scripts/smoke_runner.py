#!/usr/bin/env python3
"""v0 경량 smoke runner — 각 skill의 최소 실행 가능성 확인.

quick_validate와 구별:
  quick_validate = 구조 검증 (SKILL.md, scripts/ 존재 등)
  smoke          = 실행 검증 (scripts/evals/references/contracts 중 하나를 실제로 읽거나 실행)

SKILL.md 존재 확인만으로 smoke pass 처리하지 않음.
External API/network 필요 동작은 ast_parse/json_load/md_read 기반으로 대체.

Usage:
  python3 _shared/scripts/smoke_runner.py [--skills-root SKILLS_ROOT]
  Output: machine-readable JSON to stdout
  Exit: 0 if all pass, 1 if any fail
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

_SELF_DIR = Path(__file__).parent
DEFAULT_SKILLS_ROOT = _SELF_DIR.parent.parent  # Skills-Create-Project/
DEFAULT_MANIFEST = _SELF_DIR.parent / "smoke_manifest.json"


def build_command(skills_root: Path, entry: dict) -> list:
    t = entry["type"]
    target = str(skills_root / entry["target"])
    if t == "ast_parse":
        # 실제 Python 소스를 읽고 AST 파싱 (read-only syntax check — __pycache__ 쓰기 없음)
        return [sys.executable, "-c",
                f"import ast; ast.parse(open({target!r}).read()); print('syntax ok')"]
    elif t == "json_load":
        # JSON 파일을 실제로 파싱 (유효성 확인)
        return [sys.executable, "-c",
                f"import json; json.load(open({target!r})); print('json ok')"]
    elif t == "md_read":
        # references/knowledge_bases 파일 실제 읽기 + 최소 크기 확인
        min_b = entry.get("min_bytes", 100)
        return [sys.executable, "-c",
                f"c=open({target!r}).read(); assert len(c)>={min_b},"
                f" f'only {{len(c)}} bytes'; print(f'md ok {{len(c)}}b')"]
    else:
        raise ValueError(f"unknown smoke type: {t!r}")


def run(skills_root: Path, manifest_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text())
    results = {}

    for skill, entry in manifest["skills"].items():
        cmd = build_command(skills_root, entry)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        results[skill] = {
            "status": "pass" if proc.returncode == 0 else "fail",
            "type": entry["type"],
            "target": entry["target"],
            "exit_code": proc.returncode,
            "stderr": proc.stderr.strip()[:300] if proc.stderr else "",
        }

    passed = [k for k, r in results.items() if r["status"] == "pass"]
    failed = [k for k, r in results.items() if r["status"] == "fail"]

    summary = {
        "smoke_version": manifest["version"],
        "total": len(results),
        "passed": len(passed),
        "failed": len(failed),
        "status": "PASS" if not failed else "FAIL",
        "failed_skills": {k: results[k] for k in failed},
        "passed_skills": passed,
    }

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if not failed else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--skills-root", default=str(DEFAULT_SKILLS_ROOT))
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST))
    args = ap.parse_args()
    return run(Path(args.skills_root), Path(args.manifest))


if __name__ == "__main__":
    sys.exit(main())
