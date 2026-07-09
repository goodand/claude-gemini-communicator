#!/usr/bin/env python3
"""
Bridge 1: Dependency-Module Mapper (depsolve ↔ codebase-architecture-mapper)
============================================================================

목적: Package-level 의존성과 Module-level 코드 사이의 간극을 메움

핵심 기능:
1. Phantom 패키지 추적: depsolve가 찾아낸 phantom이 어떤 소스 파일에서 import되는지 매핑
2. Import 안정성 검사: 특정 모듈이 참조하는 외부 라이브러리가 설치되어 있는지 확인
3. 사용처 분석: 특정 패키지가 프로젝트의 어떤 파일에서 사용되는지 추적

Usage:
    # From depsolve output + mapper output
    python depsolve_mapper_bridge.py --depsolve phantoms.json --mapper arch.json
    
    # Pipeline (stdin)
    python depsolve_ext analyze /project --format json | \
        python depsolve_mapper_bridge.py --mapper arch.json -
    
    # Integrated analysis
    python depsolve_mapper_bridge.py --project /path/to/project --full-analysis
"""

from __future__ import annotations
import argparse
import json
import sys
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from collections import defaultdict


def get_skills_root() -> str:
    """Get skills root directory"""
    if os.environ.get("SKILLS_ROOT"):
        return os.environ["SKILLS_ROOT"]
    script_dir = Path(__file__).resolve().parent
    return str(script_dir.parent.parent)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class PhantomMapping:
    """Phantom 패키지와 소스 파일 매핑"""
    package: str
    ecosystem: str
    used_in: list[str]           # 소스 파일 목록
    import_lines: list[dict]      # [{file, line, import_type}]
    status: str = "PHANTOM"
    installed_version: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "package": self.package,
            "ecosystem": self.ecosystem,
            "status": self.status,
            "used_in": self.used_in,
            "usage_count": len(self.used_in),
            "import_lines": self.import_lines,
            "installed_version": self.installed_version,
        }


@dataclass
class ImportStability:
    """Import 안정성 검사 결과"""
    source_file: str
    imports: list[dict]           # [{package, status, version}]
    stable_count: int = 0
    unstable_count: int = 0
    
    @property
    def stability_score(self) -> float:
        total = self.stable_count + self.unstable_count
        return self.stable_count / total if total > 0 else 1.0
    
    def to_dict(self) -> dict:
        return {
            "source_file": self.source_file,
            "stability_score": round(self.stability_score, 2),
            "stable_imports": self.stable_count,
            "unstable_imports": self.unstable_count,
            "imports": self.imports,
        }


@dataclass
class BridgeResult:
    """브릿지 분석 결과"""
    phantom_mappings: list[PhantomMapping] = field(default_factory=list)
    stability_report: list[ImportStability] = field(default_factory=list)
    external_deps: dict[str, list[str]] = field(default_factory=dict)  # pkg -> [files]
    internal_modules: dict[str, list[str]] = field(default_factory=dict)  # module -> [dependents]
    
    def to_dict(self) -> dict:
        return {
            "summary": {
                "total_phantoms": len(self.phantom_mappings),
                "files_with_phantoms": len(set(
                    f for pm in self.phantom_mappings for f in pm.used_in
                )),
                "avg_stability": round(
                    sum(s.stability_score for s in self.stability_report) / 
                    len(self.stability_report) if self.stability_report else 1.0, 2
                ),
            },
            "phantom_mappings": [pm.to_dict() for pm in self.phantom_mappings],
            "stability_report": [s.to_dict() for s in self.stability_report],
            "external_dependencies": self.external_deps,
            "internal_modules": self.internal_modules,
        }


# =============================================================================
# Bridge Core
# =============================================================================

class DependencyModuleBridge:
    """
    Bridge between depsolve (package-level) and mapper (module-level)
    
    데이터 매핑:
    - depsolve: PhantomResult, Issue 목록
    - mapper: Node, Edge 목록 (IMPORT 타입 엣지)
    """
    
    def __init__(
        self,
        depsolve_data: Optional[dict] = None,
        mapper_data: Optional[dict] = None,
        project_path: Optional[Path] = None,
    ):
        self.depsolve_data = depsolve_data or {}
        self.mapper_data = mapper_data or {}
        self.project_path = project_path
        
        # Parsed data
        self.phantoms: list[dict] = []
        self.edges: list[dict] = []
        self.nodes: list[dict] = []
        
        self._parse_inputs()
    
    def _parse_inputs(self) -> None:
        """Parse input data from both tools"""
        # Parse depsolve output (AnalysisResult format)
        if self.depsolve_data:
            issues = self.depsolve_data.get("issues", [])
            for issue in issues:
                if issue.get("type") == "phantom":
                    # Extract package and file info from locations
                    locations = issue.get("locations", [])
                    evidence = issue.get("evidence", {}).get("data", {})
                    
                    self.phantoms.append({
                        "name": evidence.get("package", ""),
                        "ecosystem": evidence.get("ecosystem", "unknown"),
                        "files": evidence.get("files", []),
                        "locations": locations,
                    })
        
        # Parse mapper output
        if self.mapper_data:
            self.nodes = self.mapper_data.get("nodes", [])
            self.edges = self.mapper_data.get("edges", [])
    
    def map_phantoms_to_sources(self) -> list[PhantomMapping]:
        """
        Phantom 패키지가 어떤 소스 파일에서 import되는지 매핑
        
        알고리즘:
        1. depsolve의 phantom 목록 순회
        2. mapper의 edge 중 target이 phantom인 것 필터
        3. source 파일 목록 추출
        """
        mappings: list[PhantomMapping] = []
        
        for phantom in self.phantoms:
            pkg_name = phantom["name"]
            ecosystem = phantom["ecosystem"]
            
            # depsolve가 이미 제공한 파일 정보
            files_from_depsolve = phantom.get("files", [])
            
            # mapper edge에서 추가 정보 수집
            import_lines: list[dict] = []
            used_in: set[str] = set(files_from_depsolve)
            
            for edge in self.edges:
                if edge.get("type") != "IMPORT":
                    continue
                
                target = edge.get("target", "")
                
                # 패키지명 매칭 (정규화 고려)
                target_normalized = target.lower().replace("-", "_").replace(".", "_")
                pkg_normalized = pkg_name.lower().replace("-", "_").replace(".", "_")
                
                if target_normalized == pkg_normalized or target.startswith(f"{pkg_name}."):
                    source = edge.get("source", "")
                    used_in.add(source)
                    
                    metadata = edge.get("metadata", {})
                    import_lines.append({
                        "file": source,
                        "line": metadata.get("line"),
                        "import_type": metadata.get("import_type", "unknown"),
                    })
            
            if used_in:
                mappings.append(PhantomMapping(
                    package=pkg_name,
                    ecosystem=ecosystem,
                    used_in=sorted(used_in),
                    import_lines=import_lines,
                ))
        
        return mappings
    
    def analyze_import_stability(self, installed_packages: set[str] = None) -> list[ImportStability]:
        """
        각 소스 파일의 import 안정성 검사
        
        안정: manifest에 선언되어 있고 설치됨
        불안정: phantom (선언 안 됨) 또는 버전 충돌
        """
        if installed_packages is None:
            installed_packages = self._get_installed_packages()
        
        # File -> [imports] 매핑
        file_imports: dict[str, list[dict]] = defaultdict(list)
        
        for edge in self.edges:
            if edge.get("type") != "IMPORT":
                continue
            
            source = edge.get("source", "")
            target = edge.get("target", "")
            
            # 외부 패키지인지 확인 (내부 모듈 제외)
            if self._is_external_package(target):
                is_stable = target.lower() in installed_packages
                file_imports[source].append({
                    "package": target,
                    "status": "stable" if is_stable else "unstable",
                    "is_phantom": not is_stable,
                })
        
        # 안정성 리포트 생성
        reports: list[ImportStability] = []
        for source_file, imports in file_imports.items():
            stable = sum(1 for imp in imports if imp["status"] == "stable")
            unstable = len(imports) - stable
            
            reports.append(ImportStability(
                source_file=source_file,
                imports=imports,
                stable_count=stable,
                unstable_count=unstable,
            ))
        
        return sorted(reports, key=lambda x: x.stability_score)
    
    def classify_dependencies(self) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
        """
        의존성을 External(외부 라이브러리)과 Internal(내부 모듈)로 분류
        
        Returns:
            (external_deps, internal_modules)
        """
        external: dict[str, list[str]] = defaultdict(list)
        internal: dict[str, list[str]] = defaultdict(list)
        
        internal_modules = {n.get("id", "") for n in self.nodes}
        
        for edge in self.edges:
            if edge.get("type") != "IMPORT":
                continue
            
            source = edge.get("source", "")
            target = edge.get("target", "")
            
            # target이 프로젝트 내부 모듈인지 확인
            is_internal = any(
                target == mod or target.startswith(f"{mod}.")
                for mod in internal_modules
            )
            
            if is_internal:
                internal[target].append(source)
            else:
                external[target].append(source)
        
        return dict(external), dict(internal)
    
    def full_analysis(self) -> BridgeResult:
        """전체 분석 실행"""
        phantom_mappings = self.map_phantoms_to_sources()
        stability_report = self.analyze_import_stability()
        external_deps, internal_modules = self.classify_dependencies()
        
        return BridgeResult(
            phantom_mappings=phantom_mappings,
            stability_report=stability_report,
            external_deps=external_deps,
            internal_modules=internal_modules,
        )
    
    def _is_external_package(self, target: str) -> bool:
        """외부 패키지 여부 확인"""
        # 상대 경로 import 제외
        if target.startswith("."):
            return False
        
        # 프로젝트 내부 모듈 제외 — 노드 ID(전체 상대경로)와 직접 대조한다.
        # IMPORT edge의 target은 src/auth/login.py 같은 전체 경로이므로,
        # 파일명 stem(login)만 모아 비교하면 모든 로컬 import가 external로
        # 오분류돼 phantom 의존성으로 오탐된다.
        local_node_ids = {n.get("id", "") for n in self.nodes}
        if target in local_node_ids:
            return False

        # 클래스 노드 ID 대응 (예: src/auth/login.py::LoginService)
        if "::" in target and target.split("::")[0] in local_node_ids:
            return False

        return True
    
    def _get_installed_packages(self) -> set[str]:
        """설치된 패키지 목록 조회"""
        installed = set()
        
        # depsolve 데이터에서 추출
        if self.depsolve_data:
            manifest = self.depsolve_data.get("manifest", {})
            installed.update(k.lower() for k in manifest.get("js_deps", []))
            installed.update(k.lower() for k in manifest.get("py_deps", []))
        
        return installed


# =============================================================================
# Report Generation
# =============================================================================

def generate_markdown_report(result: BridgeResult) -> str:
    """마크다운 리포트 생성"""
    lines = [
        "# Dependency-Module Bridge Report",
        "",
        "## Summary",
        "",
        f"- **Total Phantoms**: {result.to_dict()['summary']['total_phantoms']}",
        f"- **Files with Phantoms**: {result.to_dict()['summary']['files_with_phantoms']}",
        f"- **Average Stability**: {result.to_dict()['summary']['avg_stability']:.0%}",
        "",
    ]
    
    # Phantom Mappings
    if result.phantom_mappings:
        lines.extend([
            "## Phantom Dependencies",
            "",
            "| Package | Ecosystem | Usage Count | Files |",
            "|---------|-----------|-------------|-------|",
        ])
        for pm in result.phantom_mappings:
            files = ", ".join(pm.used_in[:3])
            if len(pm.used_in) > 3:
                files += f" (+{len(pm.used_in) - 3} more)"
            lines.append(f"| `{pm.package}` | {pm.ecosystem} | {len(pm.used_in)} | {files} |")
        lines.append("")
    
    # Stability Report (unstable files only)
    unstable_files = [s for s in result.stability_report if s.unstable_count > 0]
    if unstable_files:
        lines.extend([
            "## Files with Unstable Imports",
            "",
            "| File | Stability | Unstable Imports |",
            "|------|-----------|------------------|",
        ])
        for sf in unstable_files[:10]:
            unstable_pkgs = [i["package"] for i in sf.imports if i["status"] == "unstable"]
            lines.append(f"| `{sf.source_file}` | {sf.stability_score:.0%} | {', '.join(unstable_pkgs[:3])} |")
        lines.append("")
    
    # External Dependencies Summary
    if result.external_deps:
        lines.extend([
            "## External Dependencies",
            "",
            f"Total external packages: {len(result.external_deps)}",
            "",
            "Top 10 most used:",
            "",
        ])
        sorted_deps = sorted(result.external_deps.items(), key=lambda x: len(x[1]), reverse=True)
        for pkg, files in sorted_deps[:10]:
            lines.append(f"- `{pkg}`: {len(files)} files")
        lines.append("")
    
    return "\n".join(lines)


def generate_mermaid_diagram(result: BridgeResult, max_nodes: int = 30) -> str:
    """Phantom 의존성 Mermaid 다이어그램"""
    lines = ["flowchart LR"]
    lines.append("    subgraph Phantoms")
    
    node_id = 0
    phantom_ids = {}
    
    for pm in result.phantom_mappings[:max_nodes]:
        phantom_ids[pm.package] = f"p{node_id}"
        lines.append(f"        p{node_id}[{pm.package}]:::phantom")
        node_id += 1
    
    lines.append("    end")
    lines.append("    subgraph Sources")
    
    file_ids = {}
    for pm in result.phantom_mappings[:max_nodes]:
        for f in pm.used_in[:5]:
            if f not in file_ids:
                file_ids[f] = f"f{node_id}"
                short_name = f.split("/")[-1]
                lines.append(f"        f{node_id}[{short_name}]")
                node_id += 1
    
    lines.append("    end")
    
    # Edges
    for pm in result.phantom_mappings[:max_nodes]:
        pid = phantom_ids.get(pm.package)
        for f in pm.used_in[:5]:
            fid = file_ids.get(f)
            if pid and fid:
                lines.append(f"    {fid} -.-> {pid}")
    
    lines.append("    classDef phantom fill:#ff6b6b,stroke:#c92a2a")
    
    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def load_json(path: str) -> dict:
    """Load JSON from file or stdin"""
    if path == "-":
        return json.loads(sys.stdin.read())
    with open(path) as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Bridge between depsolve-analyzer and codebase-architecture-mapper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # From pre-generated JSON files
    python depsolve_mapper_bridge.py --depsolve analysis.json --mapper arch.json
    
    # Stdin for depsolve output
    python depsolve_ext analyze /project --format json | \\
        python depsolve_mapper_bridge.py --mapper arch.json -
    
    # Full project analysis
    python depsolve_mapper_bridge.py --project /path/to/project --full-analysis
    
    # Mermaid output
    python depsolve_mapper_bridge.py --depsolve analysis.json --mapper arch.json --format mermaid
        """
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="depsolve JSON input (use '-' for stdin)"
    )
    
    parser.add_argument(
        "--depsolve",
        type=str,
        help="depsolve analysis result JSON file"
    )
    
    parser.add_argument(
        "--mapper",
        type=str,
        help="codebase-architecture-mapper output JSON file"
    )
    
    parser.add_argument(
        "--project",
        type=str,
        help="Project path for integrated analysis"
    )
    
    parser.add_argument(
        "--full-analysis",
        action="store_true",
        help="Run full integrated analysis"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "markdown", "mermaid"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (default: stdout)"
    )
    
    parser.add_argument(
        "--phantoms-only",
        action="store_true",
        help="Only output phantom mappings"
    )
    
    parser.add_argument(
        "--stability-only",
        action="store_true",
        help="Only output stability report"
    )
    
    args = parser.parse_args()
    
    # Load data
    depsolve_data = {}
    mapper_data = {}
    
    if args.input:
        depsolve_data = load_json(args.input)
    elif args.depsolve:
        depsolve_data = load_json(args.depsolve)
    
    if args.mapper:
        mapper_data = load_json(args.mapper)
    
    # Run integrated analysis if project path provided
    if args.project and args.full_analysis:
        project = Path(args.project).resolve()
        
        # Run mapper
        skills_root = get_skills_root()
        mapper_script = Path(skills_root) / "codebase-architecture-mapper/scripts/mapper.py"
        
        if mapper_script.exists():
            import subprocess
            result = subprocess.run(
                [sys.executable, str(mapper_script), str(project)],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                mapper_data = json.loads(result.stdout)
        
        # Run depsolve
        depsolve_script = Path(skills_root) / "depsolve-analyzer/scripts/run_depsolve.py"
        if depsolve_script.exists():
            result = subprocess.run(
                [sys.executable, str(depsolve_script), "analyze", str(project), "--format", "json"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                depsolve_data = json.loads(result.stdout)
    
    # Create bridge and analyze
    bridge = DependencyModuleBridge(
        depsolve_data=depsolve_data,
        mapper_data=mapper_data,
        project_path=Path(args.project) if args.project else None,
    )
    
    result = bridge.full_analysis()
    
    # Generate output
    if args.phantoms_only:
        output_data = [pm.to_dict() for pm in result.phantom_mappings]
    elif args.stability_only:
        output_data = [s.to_dict() for s in result.stability_report]
    else:
        output_data = result.to_dict()
    
    if args.format == "json":
        output = json.dumps(output_data, indent=2, ensure_ascii=False)
    elif args.format == "markdown":
        output = generate_markdown_report(result)
    elif args.format == "mermaid":
        output = generate_mermaid_diagram(result)
    else:
        output = json.dumps(output_data, indent=2, ensure_ascii=False)
    
    # Write output
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
