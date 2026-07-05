#!/usr/bin/env python3
"""
Troubleshooting-CoT Bridge - 연계 스킬 오케스트레이터

Phase별 분석 스킬을 subprocess로 호출하여 트러블슈팅 컨텍스트를 수집.

Usage:
    python bridge.py identify-modules /path/to/project
    python bridge.py check-deps /path/to/project --verify
    python bridge.py classify-structure --project /path/to/project
    python bridge.py trace-runtime python /path/to/script.py
    python bridge.py full-scan /path/to/project --exclude .venv,node_modules
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any


# =============================================================================
# Bootstrap: skill_paths.py import
# =============================================================================

def _bootstrap_skill_paths():
    """skill-path-resolver에서 SkillPaths를 import한다."""
    # 상대 경로: .../troubleshooting-cot-2/scripts/bridge.py → skills root
    script_dir = Path(__file__).resolve().parent
    skills_root = script_dir.parent.parent

    resolver_dir = skills_root / "skill-path-resolver" / "scripts"
    if resolver_dir.is_dir():
        sys.path.insert(0, str(resolver_dir))
        from skill_paths import SkillPaths
        return SkillPaths(str(skills_root))

    # 폴백: 환경변수
    env_root = os.environ.get("SKILLS_ROOT")
    if env_root:
        resolver_dir = Path(env_root) / "skill-path-resolver" / "scripts"
        if resolver_dir.is_dir():
            sys.path.insert(0, str(resolver_dir))
            from skill_paths import SkillPaths
            return SkillPaths(env_root)

    return None


# =============================================================================
# Data
# =============================================================================

@dataclass
class RunResult:
    success: bool
    stdout: str
    stderr: str
    returncode: int
    parsed_json: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# =============================================================================
# SkillRunner
# =============================================================================

class SkillRunner:
    """레지스트리 기반 스킬 스크립트 실행기."""

    SKILL_REGISTRY: Dict[str, tuple] = {
        "mapper":     ("codebase-architecture-mapper", "mapper.py"),
        "depsolve":   ("depsolve-analyzer", "run_depsolve.py"),
        "classifier": ("graph-structure-classifier", "classifier.py"),
        "tracer":     ("runtime-flow-tracer", "tracer.py"),
    }

    def __init__(self, paths):
        self.paths = paths

    def resolve(self, skill_key: str) -> Optional[str]:
        if skill_key not in self.SKILL_REGISTRY:
            return None
        skill_name, script_name = self.SKILL_REGISTRY[skill_key]
        return self.paths.get_script(skill_name, script_name)

    def run(
        self,
        skill_key: str,
        extra_args: List[str],
        stdin_data: Optional[str] = None,
        timeout: int = 120,
    ) -> RunResult:
        script_path = self.resolve(skill_key)
        if not script_path:
            skill_name = self.SKILL_REGISTRY.get(skill_key, (skill_key,))[0]
            return RunResult(
                success=False, stdout="", stderr="", returncode=-1,
                error_message=f"Skill not found: {skill_name}",
            )

        cmd = [sys.executable, script_path] + extra_args
        try:
            proc = subprocess.run(
                cmd,
                input=stdin_data,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                success=False, stdout="", stderr="", returncode=-2,
                error_message=f"Timeout ({timeout}s): {skill_key}",
            )
        except FileNotFoundError as e:
            return RunResult(
                success=False, stdout="", stderr="", returncode=-3,
                error_message=f"Script not found: {e}",
            )

        parsed = None
        try:
            parsed = json.loads(proc.stdout)
        except (json.JSONDecodeError, ValueError):
            pass

        return RunResult(
            success=proc.returncode == 0,
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
            parsed_json=parsed,
        )


# =============================================================================
# Subcommands
# =============================================================================

def cmd_identify_modules(args, runner: SkillRunner) -> int:
    """Phase 0: mapper로 hub/connector 모듈 식별."""
    extra = [args.project_path, "-f", "json", "--stats"]
    if args.exclude:
        extra.extend(["--exclude", args.exclude])

    result = runner.run("mapper", extra)
    if not result.success:
        print(f"[ERROR] mapper: {result.error_message or result.stderr}", file=sys.stderr)
        return 1

    if args.json:
        print(result.stdout)
        return 0

    data = result.parsed_json
    if not data:
        print("[ERROR] mapper output is not valid JSON", file=sys.stderr)
        print(result.stdout[:500], file=sys.stderr)
        return 1

    meta = data.get("metadata", {})
    analysis = data.get("analysis", {})

    print("=" * 60)
    print("  Phase 0: Module Impact Analysis")
    print("=" * 60)
    print(f"\n  Modules: {meta.get('total_files', '?')}")
    print(f"  Edges:   {meta.get('total_edges', '?')}")

    hubs = analysis.get("hub_nodes", [])
    if hubs:
        print("\n  --- Hub Modules (high in-degree, impact source) ---")
        for item in hubs[:10]:
            if isinstance(item, dict):
                print(f"    {item.get('id', '?')}  (in-degree: {item.get('in_degree', '?')})")
            elif isinstance(item, list):
                print(f"    {item[0]}  (in-degree: {item[1]})")

    connectors = analysis.get("connector_nodes", [])
    if connectors:
        print("\n  --- Connector Modules (high out-degree, change propagator) ---")
        for item in connectors[:10]:
            if isinstance(item, dict):
                print(f"    {item.get('id', '?')}  (out-degree: {item.get('out_degree', '?')})")
            elif isinstance(item, list):
                print(f"    {item[0]}  (out-degree: {item[1]})")

    entries = analysis.get("entry_points", [])
    if entries:
        print("\n  --- Entry Points (no incoming deps) ---")
        for ep in entries[:10]:
            print(f"    {ep}")

    return 0


def cmd_check_deps(args, runner: SkillRunner) -> int:
    """Phase 0: depsolve로 의존성 문제 탐지."""
    extra = ["analyze", args.project_path, "--format", "json"]
    if args.verify:
        extra.append("--verify")

    result = runner.run("depsolve", extra)

    if result.error_message and result.returncode < 0:
        print(f"[ERROR] depsolve: {result.error_message}", file=sys.stderr)
        return 2

    if args.json:
        print(result.stdout)
        return result.returncode

    data = result.parsed_json
    if not data:
        # depsolve console 출력 그대로 표시
        print("=" * 60)
        print("  Phase 0: Dependency Analysis")
        print("=" * 60)
        print(result.stdout)
        return result.returncode

    print("=" * 60)
    print("  Phase 0: Dependency Analysis")
    print("=" * 60)

    issues = data.get("issues", data.get("phantoms", []))
    if issues:
        print(f"\n  Issues found: {len(issues)}")
        for issue in issues[:15]:
            if isinstance(issue, dict):
                severity = issue.get("severity", "?")
                title = issue.get("title", issue.get("message", issue.get("name", "")))
                suggestion = issue.get("suggestion", "")
                print(f"    [{severity}] {title}")
                if suggestion:
                    print(f"           -> {suggestion}")
            else:
                print(f"    - {issue}")
    else:
        print("\n  No dependency issues detected.")

    return result.returncode


def cmd_classify_structure(args, runner: SkillRunner) -> int:
    """Phase 2: mapper output → classifier로 구조 분류."""
    edge_list_json = None

    if args.input:
        if args.input == "-":
            edge_list_json = sys.stdin.read()
        else:
            with open(args.input) as f:
                edge_list_json = f.read()
    elif args.project_path:
        extra = [args.project_path, "-f", "edge-list"]
        if args.exclude:
            extra.extend(["--exclude", args.exclude])

        mapper_result = runner.run("mapper", extra)
        if not mapper_result.success:
            print(f"[ERROR] mapper: {mapper_result.error_message or mapper_result.stderr}", file=sys.stderr)
            return 2
        edge_list_json = mapper_result.stdout

    if not edge_list_json or not edge_list_json.strip():
        print("[ERROR] No edge list data to classify", file=sys.stderr)
        return 2

    result = runner.run("classifier", ["-", "-f", "json"], stdin_data=edge_list_json)

    if result.error_message and result.returncode < 0:
        print(f"[ERROR] classifier: {result.error_message}", file=sys.stderr)
        return 2

    if args.json:
        print(result.stdout)
        return result.returncode

    data = result.parsed_json
    if not data:
        print(result.stdout)
        return result.returncode

    stats = data.get("stats", {})
    details = data.get("details", {})

    print("=" * 60)
    print("  Phase 2: Structure Classification")
    print("=" * 60)
    print(f"\n  Structure: {data.get('structure_type', '?')}")
    print(f"  Reason:    {data.get('reason', '?')}")
    print(f"  Nodes: {stats.get('nodes', '?')}  Edges: {stats.get('edges', '?')}")
    print(f"  Has cycles: {stats.get('has_cycle', '?')}")

    cycle_nodes = details.get("cycle_nodes", [])
    if cycle_nodes:
        print(f"\n  WARNING — Cycle nodes: {cycle_nodes}")

    multi_parent = details.get("multi_parent_nodes", [])
    if multi_parent:
        print(f"  Multi-parent nodes: {multi_parent[:10]}")

    return result.returncode


def cmd_trace_runtime(args, runner: SkillRunner) -> int:
    """Phase 3: tracer로 런타임 콜그래프 수집."""
    extra = [args.language, args.script, "--format", "json"]
    if args.max_depth:
        extra.extend(["--max-depth", str(args.max_depth)])

    result = runner.run("tracer", extra, timeout=300)

    if not result.success and result.returncode < 0:
        print(f"[ERROR] tracer: {result.error_message}", file=sys.stderr)
        return 1

    if args.json:
        print(result.stdout)
        return result.returncode

    data = result.parsed_json
    if not data:
        print(result.stdout)
        return result.returncode

    meta = data.get("metadata", {})

    print("=" * 60)
    print("  Phase 3: Runtime Flow Analysis")
    print("=" * 60)
    print(f"\n  Entrypoint: {meta.get('entrypoint', '?')}")
    print(f"  Runtime:    {meta.get('runtime_ms', 0):.0f}ms")
    print(f"  Functions:  {meta.get('node_count', '?')}")
    print(f"  Call edges: {meta.get('edge_count', '?')}")

    seq = data.get("call_sequence", [])
    if seq:
        print(f"\n  Call sequence (first 20):")
        for i, fn in enumerate(seq[:20]):
            print(f"    {i+1}. {fn}")

    nodes = data.get("nodes", [])
    if nodes:
        hot = sorted(nodes, key=lambda n: n.get("call_count", 0), reverse=True)[:5]
        print(f"\n  Hot functions:")
        for n in hot:
            print(f"    {n.get('function', '?')}: {n.get('call_count', 0)} calls")

    return 0


def cmd_full_scan(args, runner: SkillRunner) -> int:
    """종합 스캔: mapper → classifier + depsolve (순차)."""
    print("=" * 60)
    print("  Full Troubleshooting Scan")
    print("=" * 60)
    errors = 0

    # Step 1: Mapper
    print("\n[1/3] Architecture mapper...")
    mapper_args = [args.project_path, "-f", "json", "--stats"]
    if args.exclude:
        mapper_args.extend(["--exclude", args.exclude])

    mapper_result = runner.run("mapper", mapper_args)
    edge_list_json = None

    if mapper_result.success and mapper_result.parsed_json:
        data = mapper_result.parsed_json
        meta = data.get("metadata", {})
        analysis = data.get("analysis", {})
        print(f"  Modules: {meta.get('total_files', '?')}")
        print(f"  Edges:   {meta.get('total_edges', '?')}")
        hubs = analysis.get("hub_nodes", [])
        if hubs:
            hub_names = [h.get("id", "?") if isinstance(h, dict) else h[0] if isinstance(h, list) else str(h) for h in hubs[:5]]
            print(f"  Hubs:    {hub_names}")
        # edge_list 추출
        edge_list = data.get("edge_list", [])
        if edge_list:
            edge_list_json = json.dumps(edge_list)
    else:
        print(f"  FAILED: {mapper_result.error_message or mapper_result.stderr[:200]}")
        errors += 1

    # Step 2: Classifier
    print("\n[2/3] Structure classifier...")
    if edge_list_json:
        cls_result = runner.run("classifier", ["-", "-f", "json"], stdin_data=edge_list_json)
        if cls_result.parsed_json:
            cls_data = cls_result.parsed_json
            print(f"  Structure: {cls_data.get('structure_type', '?')}")
            print(f"  Has cycles: {cls_data.get('stats', {}).get('has_cycle', '?')}")
            cycle_nodes = cls_data.get("details", {}).get("cycle_nodes", [])
            if cycle_nodes:
                print(f"  WARNING — Cycle nodes: {cycle_nodes}")
        else:
            print(f"  FAILED: {cls_result.error_message or cls_result.stderr[:200]}")
            errors += 1
    else:
        print("  SKIPPED (no edge data from mapper)")

    # Step 3: Depsolve
    print("\n[3/3] Dependency analysis...")
    dep_result = runner.run("depsolve", ["analyze", args.project_path, "--format", "json"])
    if dep_result.returncode < 0:
        print(f"  FAILED: {dep_result.error_message}")
        errors += 1
    elif dep_result.parsed_json:
        issues = dep_result.parsed_json.get("issues", dep_result.parsed_json.get("phantoms", []))
        if issues:
            print(f"  Issues: {len(issues)}")
            for issue in issues[:5]:
                if isinstance(issue, dict):
                    title = issue.get("title", issue.get("message", issue.get("name", "")))
                    print(f"    [{issue.get('severity', '?')}] {title}")
                else:
                    print(f"    - {issue}")
        else:
            print("  No dependency issues.")
    else:
        # console 출력 표시
        if dep_result.stdout.strip():
            for line in dep_result.stdout.strip().split("\n")[:10]:
                print(f"  {line}")
        elif dep_result.stderr.strip():
            print(f"  FAILED: {dep_result.stderr[:200]}")
            errors += 1

    if args.json:
        combined = {
            "mapper": mapper_result.parsed_json,
            "classifier": cls_result.parsed_json if edge_list_json else None,
            "depsolve": dep_result.parsed_json,
        }
        print("\n" + json.dumps(combined, ensure_ascii=False, indent=2))

    print(f"\n{'=' * 60}")
    print(f"  Scan complete. Errors: {errors}")
    return 1 if errors else 0


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        prog="bridge",
        description="Troubleshooting-CoT Bridge: 연계 스킬 오케스트레이터",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Phase-Skill Mapping:
              Phase 0: identify-modules, check-deps
              Phase 2: classify-structure
              Phase 3: trace-runtime
              All:     full-scan

            Examples:
              python bridge.py identify-modules /path/to/project
              python bridge.py check-deps /path/to/project --verify
              python bridge.py classify-structure --project /path/to/project
              python bridge.py trace-runtime python script.py
              python bridge.py full-scan /path/to/project --exclude .venv,node_modules
        """),
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # identify-modules
    p = sub.add_parser("identify-modules", help="Phase 0: hub/connector 모듈 식별")
    p.add_argument("project_path", help="프로젝트 루트 디렉토리")
    p.add_argument("--exclude", help="제외 패턴 (쉼표 구분)")
    p.add_argument("--json", action="store_true", help="JSON 원본 출력")

    # check-deps
    p = sub.add_parser("check-deps", help="Phase 0: 의존성 문제 탐지")
    p.add_argument("project_path", help="프로젝트 루트 디렉토리")
    p.add_argument("--verify", action="store_true", help="런타임 검증")
    p.add_argument("--json", action="store_true", help="JSON 원본 출력")

    # classify-structure
    p = sub.add_parser("classify-structure", help="Phase 2: 모듈 그래프 구조 분류")
    grp = p.add_mutually_exclusive_group(required=True)
    grp.add_argument("--input", help="Edge list JSON 파일 (- = stdin)")
    grp.add_argument("--project", dest="project_path", help="프로젝트 경로 (mapper 자동 실행)")
    p.add_argument("--exclude", help="제외 패턴 (mapper용)")
    p.add_argument("--json", action="store_true", help="JSON 원본 출력")

    # trace-runtime
    p = sub.add_parser("trace-runtime", help="Phase 3: 런타임 콜그래프 추적")
    p.add_argument("language", choices=["python", "node", "js"], help="언어/런타임")
    p.add_argument("script", help="추적할 스크립트 경로")
    p.add_argument("--max-depth", type=int, default=50, help="최대 추적 깊이")
    p.add_argument("--json", action="store_true", help="JSON 원본 출력")

    # full-scan
    p = sub.add_parser("full-scan", help="종합 스캔 (mapper + classifier + depsolve)")
    p.add_argument("project_path", help="프로젝트 루트 디렉토리")
    p.add_argument("--exclude", help="제외 패턴 (쉼표 구분)")
    p.add_argument("--json", action="store_true", help="JSON 원본도 함께 출력")

    args = parser.parse_args()

    # Bootstrap
    paths = _bootstrap_skill_paths()
    if paths is None:
        print("[ERROR] skill-path-resolver not found.", file=sys.stderr)
        print("Set SKILLS_ROOT or ensure skill-path-resolver exists.", file=sys.stderr)
        sys.exit(2)

    runner = SkillRunner(paths)

    commands = {
        "identify-modules": cmd_identify_modules,
        "check-deps": cmd_check_deps,
        "classify-structure": cmd_classify_structure,
        "trace-runtime": cmd_trace_runtime,
        "full-scan": cmd_full_scan,
    }

    sys.exit(commands[args.command](args, runner))


if __name__ == "__main__":
    main()
