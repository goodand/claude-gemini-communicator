#!/usr/bin/env python3
"""
Codebase Architecture Mapper

Static analysis tool for extracting architecture from source code.
Outputs edge list compatible with graph-structure-classifier.

Usage:
    python mapper.py /path/to/project
    python mapper.py /path/to/project -o architecture.json
    python mapper.py /path/to/project --format mermaid
    python mapper.py /path/to/project | python classifier.py - --format json

Supported languages:
    - Python (.py)
    - JavaScript (.js, .jsx, .mjs, .cjs)
    - TypeScript (.ts, .tsx)
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from analyzers import PythonAnalyzer, JSAnalyzer, AnalysisResult
from output_formatter import OutputFormatter


def analyze_project(
    project_path: Path,
    languages: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    include_class_nodes: bool = False,  # Phase 2
    include_package_aggregation: bool = False,  # Phase 2
) -> AnalysisResult:
    """
    Analyze a project and return combined results from all analyzers.
    
    Args:
        project_path: Root directory of the project
        languages: List of languages to analyze (None = all)
        exclude_patterns: Patterns to exclude from analysis
        include_class_nodes: Create separate nodes for classes
        include_package_aggregation: Add package-level dependency view
    
    Returns:
        Combined AnalysisResult from all analyzers
    """
    result = AnalysisResult()
    
    # Available analyzers with Phase 2 options
    def create_python_analyzer():
        return PythonAnalyzer(
            project_path, 
            exclude_patterns,
            include_class_nodes=include_class_nodes,
            include_package_aggregation=include_package_aggregation,
        )
    
    def create_js_analyzer():
        return JSAnalyzer(project_path, exclude_patterns)
    
    analyzers = {
        "python": create_python_analyzer,
        "javascript": create_js_analyzer,
        "typescript": create_js_analyzer,  # Same analyzer handles both
    }
    
    # Filter analyzers by language
    if languages:
        selected = {}
        for lang in languages:
            lang_lower = lang.lower()
            if lang_lower in analyzers:
                selected[lang_lower] = analyzers[lang_lower]
            elif lang_lower in ("js", "jsx"):
                selected["javascript"] = analyzers["javascript"]
            elif lang_lower in ("ts", "tsx"):
                selected["typescript"] = analyzers["typescript"]
            elif lang_lower == "py":
                selected["python"] = analyzers["python"]
        analyzers = selected
    
    # Remove duplicates (JS and TS use same analyzer)
    used_analyzer_factories = set()
    
    for lang_name, analyzer_factory in analyzers.items():
        factory_id = id(analyzer_factory)
        if factory_id in used_analyzer_factories:
            continue
        used_analyzer_factories.add(factory_id)
        
        analyzer = analyzer_factory()
        lang_result = analyzer.analyze()
        result.merge(lang_result)
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Codebase Architecture Mapper - Extract architecture from source code",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze project and output JSON
    python mapper.py /path/to/project
    
    # Output to file
    python mapper.py /path/to/project -o architecture.json
    
    # Output Mermaid diagram
    python mapper.py /path/to/project --format mermaid
    
    # Pipe to classifier
    python mapper.py /path/to/project --format edge-list | python classifier.py -
    
    # Python only
    python mapper.py /path/to/project --lang python
    
    # Exclude directories
    python mapper.py /path/to/project --exclude tests,docs
        """
    )
    
    parser.add_argument(
        "project",
        type=str,
        help="Path to project root directory"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "edge-list", "graphml", "mermaid", "adjacency"],
        default="json",
        help="Output format (default: json)"
    )
    
    parser.add_argument(
        "--lang", "--language",
        type=str,
        action="append",
        dest="languages",
        help="Languages to analyze (can specify multiple). Options: python, javascript, typescript"
    )
    
    parser.add_argument(
        "--exclude",
        type=str,
        help="Comma-separated patterns to exclude (e.g., 'tests,docs,*.test.py')"
    )
    
    parser.add_argument(
        "--no-layers",
        action="store_true",
        help="Skip layer calculation (faster for large projects)"
    )
    
    parser.add_argument(
        "--class-nodes",
        action="store_true",
        help="[Phase 2] Create separate nodes for each class"
    )
    
    parser.add_argument(
        "--package-level",
        action="store_true", 
        help="[Phase 2] Add package-level dependency aggregation"
    )
    
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Print statistics to stderr"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output (show errors)"
    )
    
    args = parser.parse_args()
    
    # Validate project path
    project_path = Path(args.project).resolve()
    if not project_path.exists():
        print(f"Error: Project path does not exist: {project_path}", file=sys.stderr)
        sys.exit(1)
    if not project_path.is_dir():
        print(f"Error: Project path is not a directory: {project_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse exclude patterns
    exclude_patterns = None
    if args.exclude:
        exclude_patterns = [p.strip() for p in args.exclude.split(",")]
    
    # Analyze project
    result = analyze_project(
        project_path,
        languages=args.languages,
        exclude_patterns=exclude_patterns,
        include_class_nodes=args.class_nodes,  # Phase 2
        include_package_aggregation=args.package_level,  # Phase 2
    )
    
    # Print stats if requested
    if args.stats:
        print(f"Nodes: {len(result.nodes)}", file=sys.stderr)
        print(f"Edges: {len(result.edges)}", file=sys.stderr)
        if result.errors:
            print(f"Errors: {len(result.errors)}", file=sys.stderr)
    
    # Print errors if verbose
    if args.verbose and result.errors:
        print("\nErrors:", file=sys.stderr)
        for error in result.errors[:10]:  # Limit to 10
            print(f"  - {error}", file=sys.stderr)
        if len(result.errors) > 10:
            print(f"  ... and {len(result.errors) - 10} more", file=sys.stderr)
    
    # Format output
    formatter = OutputFormatter(result, str(project_path))
    
    if args.format == "json":
        output = formatter.to_json_string(include_layers=not args.no_layers)
    elif args.format == "edge-list":
        output = formatter.to_edge_list_only()
    elif args.format == "graphml":
        output = formatter.to_graphml()
    elif args.format == "mermaid":
        output = formatter.to_mermaid()
    elif args.format == "adjacency":
        output = formatter.to_adjacency_list_string()
    else:
        output = formatter.to_json_string()
    
    # Write output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output, encoding="utf-8")
        print(f"Output written to: {output_path}", file=sys.stderr)
    else:
        print(output)
    
    # Exit code based on result
    if result.errors:
        sys.exit(1 if not result.nodes else 0)
    return 0


if __name__ == "__main__":
    sys.exit(main())
