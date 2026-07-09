#!/usr/bin/env python3
"""
Depsolve Bridge Extensions
==========================

depsolve-analyzer에 브릿지 연동용 출력 포맷 추가

추가 포맷:
1. edge-list: graph-structure-classifier 입력용
2. import-map: 패키지명별 사용 위치 정보

Usage:
    # As module extension
    from depsolve_bridge_ext import EdgeListFormatter, ImportMapFormatter
    
    # As CLI wrapper
    python depsolve_bridge_ext.py /project --format edge-list
    python depsolve_bridge_ext.py /project --format import-map
"""

from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Optional
from dataclasses import dataclass, field
from collections import defaultdict


# =============================================================================
# Edge List Formatter (for graph-structure-classifier)
# =============================================================================

class EdgeListFormatter:
    """
    depsolve 분석 결과를 edge-list 형식으로 변환
    
    출력 형식: [["source", "target"], ...]
    - 패키지 의존성 그래프를 edge-list로 표현
    - graph-structure-classifier와 호환
    """
    
    def __init__(self, analysis_result: dict):
        self.result = analysis_result
    
    def to_edge_list(self) -> list[list[str]]:
        """
        분석 결과를 edge-list로 변환
        
        소스:
        1. mermaid_diagram에서 추출 (간단한 파싱)
        2. issues에서 순환/다이아몬드 정보 추출
        """
        edges: list[list[str]] = []
        seen: set[tuple[str, str]] = set()
        
        # 1. Mermaid 다이어그램에서 엣지 추출
        mermaid = self.result.get("mermaid_diagram", "")
        if mermaid:
            edges.extend(self._parse_mermaid_edges(mermaid, seen))
        
        # 2. Issues에서 관계 추출
        for issue in self.result.get("issues", []):
            issue_edges = self._extract_edges_from_issue(issue, seen)
            edges.extend(issue_edges)
        
        return edges
    
    def _parse_mermaid_edges(self, mermaid: str, seen: set) -> list[list[str]]:
        """Mermaid 다이어그램에서 엣지 파싱"""
        edges = []
        
        for line in mermaid.split('\n'):
            line = line.strip()
            
            # 형식: nodeA["label"] --> nodeB["label"]
            # 또는: nodeA --> nodeB
            if '-->' in line or '-.>' in line:
                # 화살표로 분리
                arrow = '-->' if '-->' in line else '-.>'
                parts = line.split(arrow)
                
                if len(parts) >= 2:
                    source = self._extract_node_id(parts[0])
                    target = self._extract_node_id(parts[1])
                    
                    if source and target and (source, target) not in seen:
                        seen.add((source, target))
                        edges.append([source, target])
        
        return edges
    
    def _extract_node_id(self, node_str: str) -> Optional[str]:
        """Mermaid 노드 문자열에서 ID 추출"""
        node_str = node_str.strip()
        
        # ["label"] 또는 [label] 형식에서 ID 추출
        if '[' in node_str:
            node_id = node_str.split('[')[0].strip()
        else:
            node_id = node_str.split('|')[0].strip() if '|' in node_str else node_str
        
        # 특수문자 제거
        node_id = node_id.replace('"', '').replace("'", '').strip()
        
        return node_id if node_id else None
    
    def _extract_edges_from_issue(self, issue: dict, seen: set) -> list[list[str]]:
        """Issue에서 엣지 추출"""
        edges = []
        issue_type = issue.get("type", "")
        
        if issue_type == "circular":
            # 순환 경로에서 엣지 추출
            evidence = issue.get("evidence", {}).get("data", {})
            path = evidence.get("path", [])
            
            for i in range(len(path) - 1):
                source, target = path[i], path[i + 1]
                if (source, target) not in seen:
                    seen.add((source, target))
                    edges.append([source, target])
        
        elif issue_type == "diamond":
            # 다이아몬드 구조에서 엣지 추출
            evidence = issue.get("evidence", {}).get("data", {})
            top = evidence.get("top")
            left = evidence.get("left")
            right = evidence.get("right")
            bottom = evidence.get("bottom")
            
            if top and left:
                if (top, left) not in seen:
                    seen.add((top, left))
                    edges.append([top, left])
            if top and right:
                if (top, right) not in seen:
                    seen.add((top, right))
                    edges.append([top, right])
            if left and bottom:
                if (left, bottom) not in seen:
                    seen.add((left, bottom))
                    edges.append([left, bottom])
            if right and bottom:
                if (right, bottom) not in seen:
                    seen.add((right, bottom))
                    edges.append([right, bottom])
        
        return edges
    
    def to_json(self) -> str:
        """JSON 문자열로 출력"""
        return json.dumps(self.to_edge_list(), ensure_ascii=False)


# =============================================================================
# Import Map Formatter (for bridge integration)
# =============================================================================

@dataclass
class ImportLocation:
    """Import 위치 정보"""
    file: str
    line: Optional[int] = None
    import_type: str = "unknown"
    context: str = "source"  # source, test, config


@dataclass 
class PackageImportMap:
    """패키지별 Import 맵"""
    package: str
    ecosystem: str
    is_phantom: bool
    locations: list[ImportLocation] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "package": self.package,
            "ecosystem": self.ecosystem,
            "is_phantom": self.is_phantom,
            "usage_count": len(self.locations),
            "locations": [
                {
                    "file": loc.file,
                    "line": loc.line,
                    "import_type": loc.import_type,
                    "context": loc.context,
                }
                for loc in self.locations
            ]
        }


class ImportMapFormatter:
    """
    depsolve 분석 결과를 import-map 형식으로 변환
    
    출력: 패키지명 -> 사용 위치 매핑
    - Phantom 탐지 결과와 결합
    - 각 패키지가 어디서 import되는지 추적
    """
    
    def __init__(self, analysis_result: dict):
        self.result = analysis_result
    
    def to_import_map(self) -> list[PackageImportMap]:
        """Import 맵 생성"""
        import_maps: dict[str, PackageImportMap] = {}
        
        # Issues에서 phantom 정보 추출
        for issue in self.result.get("issues", []):
            if issue.get("type") != "phantom":
                continue
            
            evidence = issue.get("evidence", {}).get("data", {})
            package = evidence.get("package", "")
            ecosystem = evidence.get("ecosystem", "unknown")
            files = evidence.get("files", [])
            
            if not package:
                continue
            
            locations = []
            for loc_str in issue.get("locations", []):
                # 형식: "package (file:line)" 또는 "package@version (file:line)"
                if "(" in loc_str and ")" in loc_str:
                    file_part = loc_str.split("(")[1].rstrip(")")
                    if ":" in file_part:
                        file_path, line_str = file_part.rsplit(":", 1)
                        try:
                            line = int(line_str)
                        except ValueError:
                            line = None
                    else:
                        file_path = file_part
                        line = None
                    
                    locations.append(ImportLocation(
                        file=file_path,
                        line=line,
                        context=self._detect_context(file_path),
                    ))
            
            # 파일 목록에서 추가
            for file_path in files:
                if not any(loc.file == file_path for loc in locations):
                    locations.append(ImportLocation(
                        file=file_path,
                        context=self._detect_context(file_path),
                    ))
            
            import_maps[package] = PackageImportMap(
                package=package,
                ecosystem=ecosystem,
                is_phantom=True,
                locations=locations,
            )
        
        return list(import_maps.values())
    
    def _detect_context(self, file_path: str) -> str:
        """파일 경로에서 컨텍스트 추론"""
        path_lower = file_path.lower()
        
        if any(x in path_lower for x in ['test', 'spec', '__test__']):
            return "test"
        if any(x in path_lower for x in ['config', '.config.', 'setup.py', 'conftest']):
            return "config"
        if any(x in path_lower for x in ['script', 'bin/', 'tools/']):
            return "script"
        
        return "source"
    
    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        import_maps = self.to_import_map()
        
        return {
            "metadata": {
                "project": self.result.get("project_path", ""),
                "ecosystem": self.result.get("ecosystem", "unknown"),
                "total_packages": len(import_maps),
                "phantom_count": sum(1 for m in import_maps if m.is_phantom),
            },
            "packages": [m.to_dict() for m in import_maps]
        }
    
    def to_json(self) -> str:
        """JSON 문자열로 출력"""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)


# =============================================================================
# Mapper Edge Tagger (External/Internal classification)
# =============================================================================

class MapperEdgeTagger:
    """
    codebase-architecture-mapper의 edge에 External/Internal 태그 추가
    
    depsolve의 manifest 정보를 활용하여:
    - External: 외부 라이브러리 (npm, pypi 패키지)
    - Internal: 프로젝트 내부 모듈
    """
    
    def __init__(
        self, 
        mapper_output: dict,
        manifest_packages: set[str] = None,
        project_modules: set[str] = None,
    ):
        self.mapper_output = mapper_output
        self.manifest_packages = manifest_packages or set()
        self.project_modules = project_modules or self._extract_project_modules()
    
    def _extract_project_modules(self) -> set[str]:
        """프로젝트 내부 모듈 추출"""
        modules = set()
        
        for node in self.mapper_output.get("nodes", []):
            node_id = node.get("id", "")
            modules.add(node_id)
            
            # 파일 경로에서 모듈명 추출
            if "/" in node_id:
                # src/auth/login.py -> auth.login
                path_parts = node_id.replace(".py", "").split("/")
                # src 제외
                if path_parts and path_parts[0] in ("src", "lib", "app"):
                    path_parts = path_parts[1:]
                modules.add(".".join(path_parts))
        
        return modules
    
    def tag_edges(self) -> list[dict]:
        """엣지에 target_type 태그 추가"""
        tagged_edges = []
        
        for edge in self.mapper_output.get("edges", []):
            target = edge.get("target", "")
            
            # 분류 로직
            target_type = self._classify_target(target)
            
            tagged_edge = {
                **edge,
                "metadata": {
                    **edge.get("metadata", {}),
                    "target_type": target_type,
                }
            }
            tagged_edges.append(tagged_edge)
        
        return tagged_edges
    
    def _classify_target(self, target: str) -> str:
        """타겟을 External/Internal로 분류"""
        target_normalized = target.lower().replace("-", "_")
        
        # 1. 프로젝트 내부 모듈 체크
        for mod in self.project_modules:
            mod_normalized = mod.lower().replace("-", "_")
            # 클래스 수준 엣지(src/auth/login.py::LoginService)도 내부로 인식하도록
            # '::' 구분자 경계를 함께 검사한다.
            if (target_normalized == mod_normalized
                    or target_normalized.startswith(f"{mod_normalized}.")
                    or target_normalized.startswith(f"{mod_normalized}::")):
                return "internal"
        
        # 2. manifest에 선언된 패키지 체크
        base_package = target.split(".")[0].lower().replace("-", "_")
        if base_package in {p.lower().replace("-", "_") for p in self.manifest_packages}:
            return "external_declared"
        
        # 3. 상대 경로 import
        if target.startswith("."):
            return "internal_relative"
        
        # 4. 그 외는 external (아마도 stdlib 또는 undeclared)
        return "external_unknown"
    
    def to_dict(self) -> dict:
        """태그된 결과 반환"""
        return {
            **self.mapper_output,
            "edges": self.tag_edges(),
            "metadata": {
                **self.mapper_output.get("metadata", {}),
                "tagged": True,
                "internal_modules": len(self.project_modules),
                "declared_packages": len(self.manifest_packages),
            }
        }


# =============================================================================
# CLI
# =============================================================================

def main():
    """CLI 진입점"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Depsolve Bridge Extensions - Additional output formats",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Output Formats:
    edge-list   : [[source, target], ...] for graph-structure-classifier
    import-map  : {package: [locations]} for phantom tracking

Examples:
    # Convert analysis result to edge-list
    python depsolve_bridge_ext.py analysis.json --format edge-list
    
    # Generate import map from analysis
    python depsolve_bridge_ext.py analysis.json --format import-map
    
    # Stdin input
    python -m depsolve_ext analyze /project --format json | \\
        python depsolve_bridge_ext.py - --format edge-list
        """
    )
    
    parser.add_argument(
        "input",
        help="depsolve analysis JSON file or '-' for stdin"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["edge-list", "import-map", "tagged-mapper"],
        default="edge-list",
        help="Output format (default: edge-list)"
    )
    
    parser.add_argument(
        "--mapper",
        type=str,
        help="Mapper output JSON (for tagged-mapper format)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (default: stdout)"
    )
    
    args = parser.parse_args()
    
    # Load input
    if args.input == "-":
        data = json.loads(sys.stdin.read())
    else:
        with open(args.input) as f:
            data = json.load(f)
    
    # Generate output
    if args.format == "edge-list":
        formatter = EdgeListFormatter(data)
        output = formatter.to_json()
    
    elif args.format == "import-map":
        formatter = ImportMapFormatter(data)
        output = formatter.to_json()
    
    elif args.format == "tagged-mapper":
        if not args.mapper:
            print("Error: --mapper required for tagged-mapper format", file=sys.stderr)
            sys.exit(1)
        
        with open(args.mapper) as f:
            mapper_data = json.load(f)
        
        # Extract manifest packages from depsolve
        manifest_pkgs = set()
        summary = data.get("summary", {})
        # depsolve는 직접 manifest 정보를 노출하지 않으므로 추정
        
        tagger = MapperEdgeTagger(mapper_data, manifest_pkgs)
        output = json.dumps(tagger.to_dict(), indent=2, ensure_ascii=False)
    
    else:
        output = json.dumps(data, indent=2, ensure_ascii=False)
    
    # Write output
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
