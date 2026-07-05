#!/usr/bin/env python3
"""
Bridge 2: Integrated Codebase Orchestrator
==========================================

목적: 개별 스킬들을 순차적으로 실행하여 "구조-의존성-위험요소"를 한 번에 리포트

분석 파이프라인:
Step 1 (Mapper): 프로젝트 전체 모듈 그래프 및 edge-list 추출
Step 2 (Depsolve): package.json 등 명세서 기반 패키지 충돌/순환 분석
Step 3 (Classifier): edge-list를 넘겨받아 전체 구조가 DAG인지 Cyclic인지 판별
Step 4 (Report): 위 데이터들을 취합하여 통합 마크다운 리포트 생성

Usage:
    # Full analysis pipeline
    python codebase_orchestrator.py /path/to/project
    
    # With specific outputs
    python codebase_orchestrator.py /project -o report.md --format markdown
    
    # JSON output for programmatic use
    python codebase_orchestrator.py /project --format json
    
    # Skip specific steps
    python codebase_orchestrator.py /project --skip-depsolve
"""

from __future__ import annotations
import argparse
import json
import sys
import os
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


def get_skills_root() -> str:
    """Get skills root directory"""
    if os.environ.get("SKILLS_ROOT"):
        return os.environ["SKILLS_ROOT"]
    script_dir = Path(__file__).resolve().parent
    return str(script_dir.parent.parent)


# =============================================================================
# Pipeline Steps
# =============================================================================

@dataclass
class StepResult:
    """단일 스텝 실행 결과"""
    name: str
    success: bool
    data: dict = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: int = 0
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


@dataclass
class OrchestratorResult:
    """통합 분석 결과"""
    project_path: str
    timestamp: str
    steps: list[StepResult] = field(default_factory=list)
    
    # Step outputs
    mapper_output: dict = field(default_factory=dict)
    depsolve_output: dict = field(default_factory=dict)
    classifier_output: dict = field(default_factory=dict)
    bridge_output: dict = field(default_factory=dict)
    
    # Aggregated insights
    insights: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "metadata": {
                "project_path": self.project_path,
                "timestamp": self.timestamp,
                "total_steps": len(self.steps),
                "successful_steps": sum(1 for s in self.steps if s.success),
            },
            "steps": [s.to_dict() for s in self.steps],
            "mapper": self.mapper_output,
            "depsolve": self.depsolve_output,
            "classifier": self.classifier_output,
            "bridge": self.bridge_output,
            "insights": self.insights,
        }


class CodebaseOrchestrator:
    """
    통합 코드베이스 분석 오케스트레이터
    
    파이프라인 실행 순서:
    1. Mapper → 모듈 그래프 추출
    2. Depsolve → 패키지 의존성 분석
    3. Classifier → 구조 분류 (DAG/Cyclic)
    4. Bridge → Phantom-Source 매핑
    5. Report → 통합 리포트 생성
    """
    
    def __init__(self, project_path: Path, skills_root: Optional[str] = None):
        self.project = project_path.resolve()
        self.skills_root = Path(skills_root or get_skills_root())
        self.result = OrchestratorResult(
            project_path=str(self.project),
            timestamp=datetime.now().isoformat(),
        )
    
    def run_pipeline(
        self,
        skip_mapper: bool = False,
        skip_depsolve: bool = False,
        skip_classifier: bool = False,
        skip_bridge: bool = False,
    ) -> OrchestratorResult:
        """전체 파이프라인 실행"""
        
        # Step 1: Mapper
        if not skip_mapper:
            self._run_mapper()
        
        # Step 2: Depsolve
        if not skip_depsolve:
            self._run_depsolve()
        
        # Step 3: Classifier (requires mapper output)
        if not skip_classifier and self.result.mapper_output:
            self._run_classifier()
        
        # Step 4: Bridge (requires both mapper and depsolve)
        if not skip_bridge and self.result.mapper_output and self.result.depsolve_output:
            self._run_bridge()
        
        # Step 5: Generate insights
        self._generate_insights()
        
        return self.result
    
    def _run_mapper(self) -> None:
        """Step 1: codebase-architecture-mapper 실행"""
        import time
        start = time.time()
        
        mapper_script = self.skills_root / "codebase-architecture-mapper/scripts/mapper.py"
        
        if not mapper_script.exists():
            self.result.steps.append(StepResult(
                name="mapper",
                success=False,
                error=f"Mapper script not found: {mapper_script}"
            ))
            return
        
        try:
            proc = subprocess.run(
                [sys.executable, str(mapper_script), str(self.project), "--class-nodes"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if proc.returncode == 0:
                self.result.mapper_output = json.loads(proc.stdout)
                self.result.steps.append(StepResult(
                    name="mapper",
                    success=True,
                    data={
                        "nodes": len(self.result.mapper_output.get("nodes", [])),
                        "edges": len(self.result.mapper_output.get("edges", [])),
                    },
                    duration_ms=int((time.time() - start) * 1000),
                ))
            else:
                self.result.steps.append(StepResult(
                    name="mapper",
                    success=False,
                    error=proc.stderr[:500],
                    duration_ms=int((time.time() - start) * 1000),
                ))
        except Exception as e:
            self.result.steps.append(StepResult(
                name="mapper",
                success=False,
                error=str(e),
            ))
    
    def _run_depsolve(self) -> None:
        """Step 2: depsolve-analyzer 실행"""
        import time
        start = time.time()
        
        # depsolve가 스킬로 설치된 경우
        depsolve_script = self.skills_root / "depsolve-analyzer/scripts/run_depsolve.py"
        
        # 프로젝트 내부에 있는 경우 (fallback)
        if not depsolve_script.exists():
            depsolve_script = self.project / "depsolve_ext" / "cli.py"
        
        if not depsolve_script.exists():
            # 모듈로 실행 시도
            try:
                proc = subprocess.run(
                    [sys.executable, "-m", "depsolve_ext", "analyze", str(self.project), "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=120,
                    cwd=str(self.project),
                )
                
                if proc.returncode == 0 and proc.stdout.strip():
                    self.result.depsolve_output = json.loads(proc.stdout)
                    self.result.steps.append(StepResult(
                        name="depsolve",
                        success=True,
                        data={
                            "issues": len(self.result.depsolve_output.get("issues", [])),
                            "ecosystem": self.result.depsolve_output.get("ecosystem", "unknown"),
                        },
                        duration_ms=int((time.time() - start) * 1000),
                    ))
                    return
            except Exception:
                pass
            
            self.result.steps.append(StepResult(
                name="depsolve",
                success=False,
                error="depsolve-analyzer not found",
            ))
            return
        
        try:
            proc = subprocess.run(
                [sys.executable, str(depsolve_script), "analyze", str(self.project), "--format", "json"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if proc.returncode == 0 and proc.stdout.strip():
                self.result.depsolve_output = json.loads(proc.stdout)
                self.result.steps.append(StepResult(
                    name="depsolve",
                    success=True,
                    data={
                        "issues": len(self.result.depsolve_output.get("issues", [])),
                        "ecosystem": self.result.depsolve_output.get("ecosystem", "unknown"),
                    },
                    duration_ms=int((time.time() - start) * 1000),
                ))
            else:
                self.result.steps.append(StepResult(
                    name="depsolve",
                    success=False,
                    error=proc.stderr[:500] if proc.stderr else "No output",
                    duration_ms=int((time.time() - start) * 1000),
                ))
        except Exception as e:
            self.result.steps.append(StepResult(
                name="depsolve",
                success=False,
                error=str(e),
            ))
    
    def _run_classifier(self) -> None:
        """Step 3: graph-structure-classifier 실행"""
        import time
        start = time.time()
        
        classifier_script = self.skills_root / "graph-structure-classifier/scripts/classifier.py"
        
        if not classifier_script.exists():
            self.result.steps.append(StepResult(
                name="classifier",
                success=False,
                error=f"Classifier script not found: {classifier_script}"
            ))
            return
        
        # edge-list 추출
        edge_list = self.result.mapper_output.get("edge_list", [])
        if not edge_list:
            edges = self.result.mapper_output.get("edges", [])
            edge_list = [[e.get("source"), e.get("target")] for e in edges]
        
        if not edge_list:
            self.result.steps.append(StepResult(
                name="classifier",
                success=False,
                error="No edges to classify",
            ))
            return
        
        try:
            # stdin으로 edge-list 전달
            proc = subprocess.run(
                [sys.executable, str(classifier_script), "-"],
                input=json.dumps(edge_list),
                capture_output=True,
                text=True,
                timeout=60,
            )
            
            if proc.returncode == 0 and proc.stdout.strip():
                self.result.classifier_output = json.loads(proc.stdout)
                self.result.steps.append(StepResult(
                    name="classifier",
                    success=True,
                    data={
                        "structure_type": self.result.classifier_output.get("structure_type", "unknown"),
                        "has_cycle": self.result.classifier_output.get("stats", {}).get("has_cycle", False),
                    },
                    duration_ms=int((time.time() - start) * 1000),
                ))
            else:
                self.result.steps.append(StepResult(
                    name="classifier",
                    success=False,
                    error=proc.stderr[:500] if proc.stderr else "No output",
                    duration_ms=int((time.time() - start) * 1000),
                ))
        except Exception as e:
            self.result.steps.append(StepResult(
                name="classifier",
                success=False,
                error=str(e),
            ))
    
    def _run_bridge(self) -> None:
        """Step 4: depsolve-mapper bridge 실행"""
        import time
        start = time.time()
        
        # Bridge 내부 로직 직접 실행
        try:
            from depsolve_mapper_bridge import DependencyModuleBridge
            
            bridge = DependencyModuleBridge(
                depsolve_data=self.result.depsolve_output,
                mapper_data=self.result.mapper_output,
                project_path=self.project,
            )
            
            bridge_result = bridge.full_analysis()
            self.result.bridge_output = bridge_result.to_dict()
            
            self.result.steps.append(StepResult(
                name="bridge",
                success=True,
                data={
                    "phantom_mappings": len(bridge_result.phantom_mappings),
                    "stability_reports": len(bridge_result.stability_report),
                },
                duration_ms=int((time.time() - start) * 1000),
            ))
        except ImportError:
            # 외부 스크립트로 실행
            bridge_script = Path(__file__).parent / "depsolve_mapper_bridge.py"
            
            if not bridge_script.exists():
                self.result.steps.append(StepResult(
                    name="bridge",
                    success=False,
                    error="Bridge script not found",
                ))
                return
            
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    json.dump(self.result.mapper_output, f)
                    mapper_file = f.name
                
                proc = subprocess.run(
                    [sys.executable, str(bridge_script), 
                     "--depsolve", "-", 
                     "--mapper", mapper_file],
                    input=json.dumps(self.result.depsolve_output),
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                
                os.unlink(mapper_file)
                
                if proc.returncode == 0 and proc.stdout.strip():
                    self.result.bridge_output = json.loads(proc.stdout)
                    self.result.steps.append(StepResult(
                        name="bridge",
                        success=True,
                        data={
                            "phantom_mappings": len(self.result.bridge_output.get("phantom_mappings", [])),
                        },
                        duration_ms=int((time.time() - start) * 1000),
                    ))
                else:
                    self.result.steps.append(StepResult(
                        name="bridge",
                        success=False,
                        error=proc.stderr[:500] if proc.stderr else "No output",
                    ))
            except Exception as e:
                self.result.steps.append(StepResult(
                    name="bridge",
                    success=False,
                    error=str(e),
                ))
    
    def _generate_insights(self) -> None:
        """분석 결과 기반 인사이트 생성"""
        insights = {
            "health_score": 100,
            "risk_factors": [],
            "recommendations": [],
        }
        
        # 1. 구조 건전성 평가
        if self.result.classifier_output:
            struct_type = self.result.classifier_output.get("structure_type", "")
            has_cycle = self.result.classifier_output.get("stats", {}).get("has_cycle", False)
            
            if has_cycle:
                insights["health_score"] -= 30
                insights["risk_factors"].append({
                    "type": "circular_dependency",
                    "severity": "high",
                    "description": "Circular dependencies detected in module graph",
                })
                insights["recommendations"].append(
                    "Break circular dependencies by extracting shared code into separate modules"
                )
            
            if struct_type == "DAG":
                insights["risk_factors"].append({
                    "type": "complex_structure",
                    "severity": "medium",
                    "description": "Multiple inheritance or diamond dependencies present",
                })
        
        # 2. Phantom 의존성 평가
        if self.result.depsolve_output:
            issues = self.result.depsolve_output.get("issues", [])
            phantoms = [i for i in issues if i.get("type") == "phantom"]
            
            if phantoms:
                insights["health_score"] -= len(phantoms) * 5
                insights["risk_factors"].append({
                    "type": "phantom_dependencies",
                    "severity": "high",
                    "count": len(phantoms),
                    "packages": [i.get("evidence", {}).get("data", {}).get("package") for i in phantoms[:5]],
                })
                insights["recommendations"].append(
                    f"Add {len(phantoms)} missing packages to your dependency manifest"
                )
        
        # 3. Bridge 분석 평가
        if self.result.bridge_output:
            summary = self.result.bridge_output.get("summary", {})
            avg_stability = summary.get("avg_stability", 1.0)
            
            if avg_stability < 0.8:
                insights["health_score"] -= 20
                insights["risk_factors"].append({
                    "type": "import_instability",
                    "severity": "medium",
                    "stability_score": avg_stability,
                })
                insights["recommendations"].append(
                    "Review and fix unstable imports across the codebase"
                )
        
        # 4. 복잡도 평가
        if self.result.mapper_output:
            nodes = len(self.result.mapper_output.get("nodes", []))
            edges = len(self.result.mapper_output.get("edges", []))
            
            if nodes > 0:
                density = edges / nodes
                if density > 5:
                    insights["risk_factors"].append({
                        "type": "high_coupling",
                        "severity": "medium",
                        "edge_density": round(density, 2),
                    })
                    insights["recommendations"].append(
                        "Consider refactoring to reduce module coupling"
                    )
        
        insights["health_score"] = max(0, insights["health_score"])
        self.result.insights = insights


# =============================================================================
# Report Generation
# =============================================================================

def generate_markdown_report(result: OrchestratorResult) -> str:
    """통합 마크다운 리포트 생성"""
    lines = [
        "# Integrated Codebase Analysis Report",
        "",
        f"**Project**: `{result.project_path}`",
        f"**Generated**: {result.timestamp}",
        "",
        "---",
        "",
    ]
    
    # Health Score
    insights = result.insights
    health = insights.get("health_score", 0)
    health_emoji = "🟢" if health >= 80 else "🟡" if health >= 60 else "🔴"
    
    lines.extend([
        "## Executive Summary",
        "",
        f"### Health Score: {health_emoji} {health}/100",
        "",
    ])
    
    # Risk Factors
    risks = insights.get("risk_factors", [])
    if risks:
        lines.append("### Risk Factors")
        lines.append("")
        for risk in risks:
            severity_emoji = "🔴" if risk["severity"] == "high" else "🟡"
            lines.append(f"- {severity_emoji} **{risk['type']}**: {risk.get('description', '')}")
        lines.append("")
    
    # Recommendations
    recommendations = insights.get("recommendations", [])
    if recommendations:
        lines.append("### Recommendations")
        lines.append("")
        for rec in recommendations:
            lines.append(f"- 💡 {rec}")
        lines.append("")
    
    lines.append("---")
    lines.append("")
    
    # Pipeline Steps Summary
    lines.extend([
        "## Analysis Pipeline",
        "",
        "| Step | Status | Duration | Details |",
        "|------|--------|----------|---------|",
    ])
    
    for step in result.steps:
        status = "✅" if step.success else "❌"
        duration = f"{step.duration_ms}ms" if step.duration_ms else "-"
        details = ", ".join(f"{k}: {v}" for k, v in step.data.items()) if step.data else step.error or "-"
        lines.append(f"| {step.name} | {status} | {duration} | {details[:50]} |")
    
    lines.append("")
    
    # Module Structure (from mapper)
    if result.mapper_output:
        analysis = result.mapper_output.get("analysis", {})
        lines.extend([
            "## Module Structure",
            "",
            f"- **Total Modules**: {len(result.mapper_output.get('nodes', []))}",
            f"- **Total Dependencies**: {len(result.mapper_output.get('edges', []))}",
        ])
        
        if analysis.get("hub_nodes"):
            lines.append(f"- **Hub Modules**: {', '.join(h['id'].split('/')[-1] for h in analysis['hub_nodes'][:5])}")
        
        lines.append("")
    
    # Dependency Structure (from classifier)
    if result.classifier_output:
        lines.extend([
            "## Dependency Structure",
            "",
            f"- **Structure Type**: {result.classifier_output.get('structure_type', 'unknown')}",
            f"- **Has Cycles**: {'Yes ⚠️' if result.classifier_output.get('stats', {}).get('has_cycle') else 'No ✅'}",
        ])
        
        stats = result.classifier_output.get("stats", {})
        if stats.get("max_in_degree"):
            lines.append(f"- **Max In-Degree**: {stats['max_in_degree']}")
        
        lines.append("")
    
    # Dependency Issues (from depsolve)
    if result.depsolve_output:
        issues = result.depsolve_output.get("issues", [])
        lines.extend([
            "## Dependency Issues",
            "",
            f"- **Ecosystem**: {result.depsolve_output.get('ecosystem', 'unknown')}",
            f"- **Total Issues**: {len(issues)}",
        ])
        
        # Group by type
        by_type = {}
        for issue in issues:
            t = issue.get("type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        
        if by_type:
            lines.append("")
            lines.append("| Issue Type | Count |")
            lines.append("|------------|-------|")
            for t, count in sorted(by_type.items()):
                lines.append(f"| {t} | {count} |")
        
        lines.append("")
    
    # Phantom-Source Mapping (from bridge)
    if result.bridge_output:
        summary = result.bridge_output.get("summary", {})
        lines.extend([
            "## Import Analysis",
            "",
            f"- **Files with Phantom Imports**: {summary.get('files_with_phantoms', 0)}",
            f"- **Average Import Stability**: {summary.get('avg_stability', 0):.0%}",
        ])
        
        phantoms = result.bridge_output.get("phantom_mappings", [])
        if phantoms:
            lines.append("")
            lines.append("### Phantom Dependencies by Usage")
            lines.append("")
            lines.append("| Package | Files Using | Ecosystem |")
            lines.append("|---------|-------------|-----------|")
            for pm in phantoms[:10]:
                lines.append(f"| `{pm['package']}` | {pm.get('usage_count', 0)} | {pm.get('ecosystem', '-')} |")
        
        lines.append("")
    
    # Mermaid Diagram
    if result.mapper_output:
        edges = result.mapper_output.get("edges", [])[:30]
        if edges:
            lines.extend([
                "## Module Dependency Graph",
                "",
                "```mermaid",
                "flowchart TD",
            ])
            
            node_ids = {}
            for i, edge in enumerate(edges):
                src = edge.get("source", "")
                tgt = edge.get("target", "")
                
                if src not in node_ids:
                    node_ids[src] = f"n{len(node_ids)}"
                if tgt not in node_ids:
                    node_ids[tgt] = f"n{len(node_ids)}"
                
                src_label = src.split("/")[-1] if "/" in src else src
                tgt_label = tgt.split("/")[-1] if "/" in tgt else tgt
                
                lines.append(f"    {node_ids[src]}[{src_label}] --> {node_ids[tgt]}[{tgt_label}]")
            
            lines.append("```")
            lines.append("")
    
    return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Integrated Codebase Orchestrator - Full pipeline analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Full analysis with markdown report
    python codebase_orchestrator.py /path/to/project
    
    # JSON output
    python codebase_orchestrator.py /project --format json
    
    # Save report to file
    python codebase_orchestrator.py /project -o analysis_report.md
    
    # Skip specific steps
    python codebase_orchestrator.py /project --skip-classifier
        """
    )
    
    parser.add_argument(
        "project",
        type=str,
        help="Path to project directory"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "markdown"],
        default="markdown",
        help="Output format (default: markdown)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (default: stdout)"
    )
    
    parser.add_argument(
        "--skip-mapper",
        action="store_true",
        help="Skip mapper step"
    )
    
    parser.add_argument(
        "--skip-depsolve",
        action="store_true",
        help="Skip depsolve step"
    )
    
    parser.add_argument(
        "--skip-classifier",
        action="store_true",
        help="Skip classifier step"
    )
    
    parser.add_argument(
        "--skip-bridge",
        action="store_true",
        help="Skip bridge step"
    )
    
    parser.add_argument(
        "--skills-root",
        type=str,
        help="Override SKILLS_ROOT path"
    )
    
    args = parser.parse_args()
    
    # Validate project path
    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Error: Project path not found: {project}", file=sys.stderr)
        sys.exit(1)
    
    # Run orchestrator
    orchestrator = CodebaseOrchestrator(
        project_path=project,
        skills_root=args.skills_root,
    )
    
    result = orchestrator.run_pipeline(
        skip_mapper=args.skip_mapper,
        skip_depsolve=args.skip_depsolve,
        skip_classifier=args.skip_classifier,
        skip_bridge=args.skip_bridge,
    )
    
    # Generate output
    if args.format == "json":
        output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    else:
        output = generate_markdown_report(result)
    
    # Write output
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Report written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
