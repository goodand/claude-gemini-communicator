#!/usr/bin/env python3
"""
Architecture Bridge - Connect static and dynamic analysis tools

Bridges:
- codebase-architecture-mapper (static analysis) → 
- class-hierarchy-classifier (dynamic MRO analysis)

Usage:
    # From mapper output
    python bridge.py arch.json --verify-inheritance
    
    # Pipe from mapper
    python mapper.py /project --class-nodes | python bridge.py - --verify-all
    
    # Select specific classes
    python bridge.py arch.json --classes UserService,BaseRepository
"""

from __future__ import annotations
import argparse
import json
import sys
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


def get_skills_root() -> str:
    """
    Get skills root directory.
    Priority: SKILLS_ROOT env var > relative path from this script
    """
    # 1. Check environment variable
    if os.environ.get("SKILLS_ROOT"):
        return os.environ["SKILLS_ROOT"]
    
    # 2. Calculate relative path from this script
    # This script: .../codebase-architecture-mapper/scripts/bridge.py
    # Skills root: .../  (2 levels up from scripts/)
    script_dir = Path(__file__).resolve().parent
    skills_root = script_dir.parent.parent
    
    return str(skills_root)


@dataclass
class ClassNode:
    """Represents a class extracted from mapper output"""
    id: str                          # e.g., "src/auth/login.py::LoginService"
    name: str                        # e.g., "LoginService"
    module_path: str                 # e.g., "src/auth/login.py"
    import_path: str                 # e.g., "src.auth.login.LoginService"
    parents: list[str] = field(default_factory=list)
    is_internal: bool = False


@dataclass 
class InheritanceEdge:
    """Represents an inheritance relationship"""
    child_id: str
    parent_id: str
    child_name: str
    parent_name: str
    is_internal: bool = False


class ArchitectureBridge:
    """Bridge between static mapper and dynamic hierarchy classifier"""
    
    def __init__(self, mapper_output: dict):
        self.data = mapper_output
        self.classes: dict[str, ClassNode] = {}
        self.inheritance_edges: list[InheritanceEdge] = []
        self._parse_mapper_output()
    
    def _parse_mapper_output(self) -> None:
        """Parse mapper JSON output to extract class information"""
        
        # Extract class nodes
        for node in self.data.get("nodes", []):
            if node.get("type") == "class":
                node_id = node["id"]
                # Parse ID format: "module/path.py::ClassName"
                if "::" in node_id:
                    module_path, class_name = node_id.rsplit("::", 1)
                else:
                    module_path = node.get("path", "")
                    class_name = node_id
                
                # Convert file path to import path
                import_path = self._file_to_import_path(module_path, class_name)
                
                self.classes[node_id] = ClassNode(
                    id=node_id,
                    name=class_name,
                    module_path=module_path,
                    import_path=import_path,
                )
            
            # Also extract classes from module nodes
            elif node.get("type") == "module":
                module_path = node.get("path", node["id"])
                for class_name in node.get("classes", []):
                    node_id = f"{module_path}::{class_name}"
                    import_path = self._file_to_import_path(module_path, class_name)
                    
                    if node_id not in self.classes:
                        self.classes[node_id] = ClassNode(
                            id=node_id,
                            name=class_name,
                            module_path=module_path,
                            import_path=import_path,
                        )
        
        # Extract inheritance edges
        for edge in self.data.get("edges", []):
            if edge.get("type") == "INHERITANCE":
                child_id = edge["source"]
                parent_id = edge["target"]
                
                # Parse names from IDs
                child_name = child_id.split("::")[-1] if "::" in child_id else child_id
                parent_name = parent_id.split("::")[-1] if "::" in parent_id else parent_id
                
                is_internal = edge.get("metadata", {}).get("internal", False)
                
                self.inheritance_edges.append(InheritanceEdge(
                    child_id=child_id,
                    parent_id=parent_id,
                    child_name=child_name,
                    parent_name=parent_name,
                    is_internal=is_internal,
                ))
                
                # Update class nodes with parent info
                if child_id in self.classes:
                    self.classes[child_id].parents.append(parent_name)
                    self.classes[child_id].is_internal = is_internal
    
    def _file_to_import_path(self, file_path: str, class_name: str) -> str:
        """Convert file path to Python import path"""
        # Remove .py extension
        if file_path.endswith(".py"):
            file_path = file_path[:-3]
        
        # Convert slashes to dots
        import_path = file_path.replace("/", ".").replace("\\", ".")
        
        # Remove __init__ if present
        if import_path.endswith(".__init__"):
            import_path = import_path[:-9]
        
        # Add class name
        return f"{import_path}.{class_name}"
    
    def get_component_specs(self, class_names: list[str] | None = None) -> dict[str, str]:
        """
        Generate component_specs for hierarchy_classifier
        
        Args:
            class_names: Optional filter for specific classes
        
        Returns:
            Dict mapping class names to import paths
        """
        specs = {}
        
        for node_id, cls in self.classes.items():
            if class_names is None or cls.name in class_names:
                specs[cls.name] = cls.import_path
        
        return specs
    
    def get_relationships_to_verify(self) -> list[tuple[str, str]]:
        """Get all inheritance relationships for verification"""
        relationships = []
        
        for edge in self.inheritance_edges:
            # Only include if both classes are in our class map
            child_exists = any(c.name == edge.child_name for c in self.classes.values())
            parent_exists = any(c.name == edge.parent_name for c in self.classes.values())
            
            if child_exists and parent_exists:
                relationships.append((edge.child_name, edge.parent_name))
        
        return relationships
    
    def print_summary(self) -> None:
        """Print summary of extracted information"""
        print("=" * 70)
        print("  Architecture Bridge - Summary")
        print("=" * 70)
        print(f"\nClasses found: {len(self.classes)}")
        print(f"Inheritance edges: {len(self.inheritance_edges)}")
        
        if self.classes:
            print("\nClass Import Paths:")
            for cls in sorted(self.classes.values(), key=lambda x: x.name):
                parent_str = f" (parents: {', '.join(cls.parents)})" if cls.parents else ""
                print(f"  - {cls.name}: {cls.import_path}{parent_str}")
        
        if self.inheritance_edges:
            print("\nInheritance Relationships:")
            for edge in self.inheritance_edges:
                internal_str = " [internal]" if edge.is_internal else ""
                print(f"  - {edge.child_name} → {edge.parent_name}{internal_str}")
        
        print("=" * 70)
    
    def to_classifier_format(self) -> dict:
        """Convert to hierarchy_classifier compatible format"""
        return {
            "component_specs": self.get_component_specs(),
            "relationships": self.get_relationships_to_verify(),
            "metadata": {
                "source": "codebase-architecture-mapper",
                "total_classes": len(self.classes),
                "total_inheritance": len(self.inheritance_edges),
            }
        }
    
    def run_dynamic_analysis(
        self, 
        class_names: list[str] | None = None,
        verify_all: bool = False,
        highlight: list[str] | None = None,
        project_root: str | None = None,
        classify_structure: bool = False,
    ) -> None:
        """
        Run dynamic analysis using hierarchy_classifier
        
        Args:
            class_names: Specific classes to analyze
            verify_all: Verify all inheritance relationships
            highlight: Keywords to highlight
            project_root: Project root to add to PYTHONPATH
            classify_structure: Run structure classification (Tree/DAG/etc.)
        """
        # Add project root to PYTHONPATH if specified
        if project_root:
            sys.path.insert(0, project_root)
            print(f"📁 Added to PYTHONPATH: {project_root}")
        
        # Get skills root (env var or relative path)
        skills_root = get_skills_root()
        
        try:
            # Try to import hierarchy_classifier (new name)
            classifier_path = os.path.join(skills_root, "class-hierarchy-classifier/scripts")
            sys.path.insert(0, classifier_path)
            from hierarchy_classifier import analyze_hierarchy, verify_relationship
        except ImportError:
            # Fallback to old name for compatibility
            try:
                visualizer_path = os.path.join(skills_root, "class-hierarchy-visualizer/scripts")
                sys.path.insert(0, visualizer_path)
                from hierarchy_visualizer import analyze_hierarchy, verify_relationship
                print("⚠️  Using legacy hierarchy_visualizer (consider upgrading to hierarchy_classifier)")
            except ImportError:
                print("⚠️  hierarchy_classifier not available.")
                print(f"   Searched in: {skills_root}")
                print("   Outputting component_specs for manual use:")
                print(json.dumps(self.get_component_specs(), indent=2))
                return
        
        specs = self.get_component_specs(class_names)
        
        if not specs:
            print("⚠️  No classes to analyze.")
            return
        
        print("\n" + "=" * 70)
        print("  Dynamic MRO Analysis (via hierarchy_classifier)")
        print("=" * 70)
        
        # Run basic hierarchy analysis with optional structure classification
        components = analyze_hierarchy(
            specs, 
            highlight_keywords=highlight,
            classify=classify_structure,
        )
        
        # Verify relationships if requested
        if verify_all and components:
            relationships = self.get_relationships_to_verify()
            for child, parent in relationships:
                if child in components and parent in components:
                    verify_relationship(components, child, parent)


def load_input(input_path: str) -> dict:
    """Load mapper output from file or stdin"""
    if input_path == "-":
        return json.loads(sys.stdin.read())
    else:
        with open(input_path) as f:
            return json.load(f)


def main():
    parser = argparse.ArgumentParser(
        description="Bridge between codebase-architecture-mapper and class-hierarchy-classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Summary of classes and inheritance
    python bridge.py arch.json --summary
    
    # Run dynamic MRO analysis
    python bridge.py arch.json --analyze
    
    # Run with structure classification
    python bridge.py arch.json --analyze --classify-structure
    
    # Verify all inheritance relationships
    python bridge.py arch.json --verify-all
    
    # Analyze specific classes
    python bridge.py arch.json --classes UserService,BaseRepository
    
    # Pipe from mapper
    python mapper.py /project --class-nodes | python bridge.py - --analyze
    
    # Output component_specs JSON
    python bridge.py arch.json --output-specs
        """
    )
    
    parser.add_argument(
        "input",
        help="Mapper output JSON file or '-' for stdin"
    )
    
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print summary of extracted classes and inheritance"
    )
    
    parser.add_argument(
        "--analyze",
        action="store_true",
        help="Run dynamic MRO analysis using hierarchy_classifier"
    )
    
    parser.add_argument(
        "--verify-all",
        action="store_true",
        help="Verify all inheritance relationships with issubclass"
    )
    
    parser.add_argument(
        "--classify-structure",
        action="store_true",
        help="Classify structure (Tree/DAG/DirectedGraph) during analysis"
    )
    
    parser.add_argument(
        "--classes",
        type=str,
        help="Comma-separated list of class names to analyze"
    )
    
    parser.add_argument(
        "--highlight",
        type=str,
        help="Comma-separated keywords to highlight"
    )
    
    parser.add_argument(
        "--output-specs",
        action="store_true",
        help="Output component_specs JSON for manual use"
    )
    
    parser.add_argument(
        "--output-json",
        action="store_true",
        help="Output full bridge data as JSON"
    )
    
    parser.add_argument(
        "--project-root",
        type=str,
        help="Project root to add to PYTHONPATH for dynamic analysis"
    )
    
    args = parser.parse_args()
    
    # Load input
    try:
        data = load_input(args.input)
    except Exception as e:
        print(f"Error loading input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Create bridge
    bridge = ArchitectureBridge(data)
    
    # Parse class filter
    class_names = None
    if args.classes:
        class_names = [c.strip() for c in args.classes.split(",")]
    
    # Parse highlight keywords
    highlight = None
    if args.highlight:
        highlight = [h.strip() for h in args.highlight.split(",")]
    
    # Execute requested actions
    if args.output_specs:
        specs = bridge.get_component_specs(class_names)
        print(json.dumps(specs, indent=2, ensure_ascii=False))
        return
    
    if args.output_json:
        output = bridge.to_classifier_format()
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return
    
    if args.summary or (not args.analyze and not args.verify_all):
        bridge.print_summary()
    
    if args.analyze or args.verify_all:
        bridge.run_dynamic_analysis(
            class_names=class_names,
            verify_all=args.verify_all,
            highlight=highlight,
            project_root=args.project_root,
            classify_structure=args.classify_structure,
        )


if __name__ == "__main__":
    main()
