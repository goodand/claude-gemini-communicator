#!/usr/bin/env python3
"""
Bridge script for integrating codebase-architecture-mapper with runtime-flow-tracer

Usage:
    # Filter runtime trace to only functions from static analysis
    python bridge.py filter mapper_output.json trace_output.json
    
    # Merge static and dynamic analysis results
    python bridge.py merge mapper_output.json trace_output.json
    
    # Generate combined architecture document
    python bridge.py report mapper_output.json trace_output.json -o ARCHITECTURE.md
"""

from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime


def load_json(path: str) -> dict:
    """Load JSON file or stdin"""
    if path == "-":
        return json.loads(sys.stdin.read())
    with open(path) as f:
        return json.load(f)


def extract_functions_from_mapper(mapper_data: dict) -> set[str]:
    """Extract function names from codebase-architecture-mapper output"""
    functions = set()
    
    for node in mapper_data.get("nodes", []):
        # Extract functions defined in modules
        for func in node.get("functions", []):
            functions.add(func)
        
        # Extract class methods
        for cls in node.get("classes", []):
            functions.add(cls)  # Include class names too
    
    return functions


def extract_modules_from_mapper(mapper_data: dict) -> set[str]:
    """Extract module paths from codebase-architecture-mapper output"""
    modules = set()
    
    for node in mapper_data.get("nodes", []):
        if node.get("type") == "module":
            path = node.get("path", node.get("id", ""))
            modules.add(path)
            # Also add module name without extension
            modules.add(Path(path).stem)
    
    return modules


def filter_trace_by_mapper(trace_data: dict, mapper_data: dict) -> dict:
    """Filter runtime trace to only include functions from static analysis
    
    This helps focus on project code and exclude library calls.
    """
    known_functions = extract_functions_from_mapper(mapper_data)
    known_modules = extract_modules_from_mapper(mapper_data)
    
    # Filter nodes
    filtered_nodes = []
    included_node_ids = set()
    
    for node in trace_data.get("nodes", []):
        func_name = node.get("function", node.get("id", ""))
        module = node.get("module", node.get("file", ""))
        
        # Include if function or module is in mapper output
        if func_name in known_functions or module in known_modules:
            filtered_nodes.append(node)
            included_node_ids.add(node.get("id"))
    
    # Filter edges to only include nodes we're keeping
    filtered_edges = []
    for edge in trace_data.get("edges", []):
        if edge["source"] in included_node_ids and edge["target"] in included_node_ids:
            filtered_edges.append(edge)
    
    # Filter call sequence
    filtered_sequence = [
        call for call in trace_data.get("call_sequence", [])
        if call in included_node_ids
    ]
    
    # Build filtered result
    result = {
        "metadata": {
            **trace_data.get("metadata", {}),
            "filtered_by": "codebase-architecture-mapper",
            "original_node_count": len(trace_data.get("nodes", [])),
            "filtered_node_count": len(filtered_nodes),
        },
        "nodes": filtered_nodes,
        "edges": filtered_edges,
        "edge_list": [[e["source"], e["target"]] for e in filtered_edges],
        "call_sequence": filtered_sequence,
    }
    
    return result


def merge_static_and_dynamic(mapper_data: dict, trace_data: dict) -> dict:
    """Merge static (mapper) and dynamic (tracer) analysis results
    
    Creates a comprehensive view with:
    - Static structure (imports, inheritance)
    - Runtime behavior (actual calls, frequencies)
    """
    # Build node lookup
    static_nodes = {n.get("id"): n for n in mapper_data.get("nodes", [])}
    dynamic_nodes = {n.get("id"): n for n in trace_data.get("nodes", [])}
    
    # Merge nodes
    merged_nodes = []
    all_node_ids = set(static_nodes.keys()) | set(dynamic_nodes.keys())
    
    for node_id in all_node_ids:
        static = static_nodes.get(node_id, {})
        dynamic = dynamic_nodes.get(node_id, {})
        
        merged = {
            "id": node_id,
            "static": {
                "type": static.get("type"),
                "language": static.get("language"),
                "path": static.get("path"),
                "classes": static.get("classes", []),
                "functions": static.get("functions", []),
                "layer": static.get("layer"),
            } if static else None,
            "dynamic": {
                "function": dynamic.get("function"),
                "module": dynamic.get("module"),
                "call_count": dynamic.get("call_count", 0),
                "first_call_seq": dynamic.get("first_call_seq"),
            } if dynamic else None,
            "coverage": {
                "in_static": bool(static),
                "in_dynamic": bool(dynamic),
                "executed": bool(dynamic),
            }
        }
        merged_nodes.append(merged)
    
    # Merge edges
    static_edges = {(e["source"], e["target"]): e for e in mapper_data.get("edges", [])}
    dynamic_edges = {(e["source"], e["target"]): e for e in trace_data.get("edges", [])}
    
    merged_edges = []
    all_edge_keys = set(static_edges.keys()) | set(dynamic_edges.keys())
    
    for src, tgt in all_edge_keys:
        static = static_edges.get((src, tgt), {})
        dynamic = dynamic_edges.get((src, tgt), {})
        
        merged = {
            "source": src,
            "target": tgt,
            "static_type": static.get("type"),  # IMPORT, INHERITANCE, etc.
            "dynamic_call_count": dynamic.get("call_count", 0),
            "in_static": bool(static),
            "in_dynamic": bool(dynamic),
        }
        merged_edges.append(merged)
    
    # Calculate coverage statistics
    static_only_nodes = len([n for n in merged_nodes if n["static"] and not n["dynamic"]])
    dynamic_only_nodes = len([n for n in merged_nodes if n["dynamic"] and not n["static"]])
    both_nodes = len([n for n in merged_nodes if n["static"] and n["dynamic"]])
    
    result = {
        "metadata": {
            "merged_at": datetime.now().isoformat(),
            "static_source": mapper_data.get("metadata", {}).get("project_root"),
            "dynamic_source": trace_data.get("metadata", {}).get("entrypoint"),
        },
        "coverage": {
            "total_nodes": len(merged_nodes),
            "static_only": static_only_nodes,
            "dynamic_only": dynamic_only_nodes,
            "both": both_nodes,
            "execution_coverage": both_nodes / len(merged_nodes) if merged_nodes else 0,
        },
        "nodes": merged_nodes,
        "edges": merged_edges,
    }
    
    return result


def generate_report(mapper_data: dict, trace_data: dict) -> str:
    """Generate combined architecture report in Markdown"""
    merged = merge_static_and_dynamic(mapper_data, trace_data)
    coverage = merged["coverage"]
    
    lines = [
        "# Combined Architecture Report",
        "",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Overview",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Nodes | {coverage['total_nodes']} |",
        f"| Static Only | {coverage['static_only']} (defined but not executed) |",
        f"| Dynamic Only | {coverage['dynamic_only']} (runtime-discovered) |",
        f"| Both | {coverage['both']} (defined and executed) |",
        f"| Execution Coverage | {coverage['execution_coverage']:.1%} |",
        "",
        "## Static vs Dynamic Analysis",
        "",
        "### Defined but Not Executed",
        "Functions/modules found in code but not called during runtime trace:",
        "",
    ]
    
    static_only = [n for n in merged["nodes"] if n["static"] and not n["dynamic"]]
    if static_only:
        for node in static_only[:20]:  # Limit to 20
            lines.append(f"- `{node['id']}`")
        if len(static_only) > 20:
            lines.append(f"- ... and {len(static_only) - 20} more")
    else:
        lines.append("- (none)")
    
    lines.extend([
        "",
        "### Runtime-Discovered (Not in Static)",
        "Functions called at runtime but not found in static analysis:",
        "",
    ])
    
    dynamic_only = [n for n in merged["nodes"] if n["dynamic"] and not n["static"]]
    if dynamic_only:
        for node in dynamic_only[:20]:
            lines.append(f"- `{node['id']}` (called {node['dynamic']['call_count']}x)")
        if len(dynamic_only) > 20:
            lines.append(f"- ... and {len(dynamic_only) - 20} more")
    else:
        lines.append("- (none)")
    
    lines.extend([
        "",
        "### Hot Functions (Most Called)",
        "",
        "| Function | Call Count |",
        "|----------|------------|",
    ])
    
    executed = [n for n in merged["nodes"] if n["dynamic"]]
    executed.sort(key=lambda n: n["dynamic"]["call_count"], reverse=True)
    for node in executed[:10]:
        lines.append(f"| `{node['id']}` | {node['dynamic']['call_count']} |")
    
    lines.extend([
        "",
        "## Edge Analysis",
        "",
        "| Type | Count |",
        "|------|-------|",
        f"| Static Only (defined) | {len([e for e in merged['edges'] if e['in_static'] and not e['in_dynamic']])} |",
        f"| Dynamic Only (runtime) | {len([e for e in merged['edges'] if e['in_dynamic'] and not e['in_static']])} |",
        f"| Both | {len([e for e in merged['edges'] if e['in_static'] and e['in_dynamic']])} |",
    ])
    
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Bridge between codebase-architecture-mapper, runtime-flow-tracer, and web traces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    filter  - Filter trace to only project functions
    merge   - Merge static and dynamic analysis
    report  - Generate combined architecture report
    combine - Combine multiple trace sources (runtime + web + network)

Examples:
    python bridge.py filter mapper.json trace.json > filtered.json
    python bridge.py merge mapper.json trace.json > merged.json
    python bridge.py report mapper.json trace.json -o ARCHITECTURE.md
    python bridge.py combine runtime.json --web web.json --network network.json
        """
    )
    
    parser.add_argument("command", choices=["filter", "merge", "report", "combine"],
                        help="Command to execute")
    parser.add_argument("mapper_output", nargs="?", help="Output from codebase-architecture-mapper (JSON)")
    parser.add_argument("trace_output", nargs="?", help="Output from runtime-flow-tracer (JSON)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--web", help="Web trace JSON (from web_tracer.py)")
    parser.add_argument("--network", help="Network trace JSON (from network_proxy.py)")
    
    args = parser.parse_args()
    
    # Handle combine command separately
    if args.command == "combine":
        result = combine_traces(
            runtime_path=args.mapper_output,  # Reuse as runtime path
            web_path=args.web,
            network_path=args.network,
        )
        output = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        # Load inputs
        mapper_data = load_json(args.mapper_output)
        trace_data = load_json(args.trace_output)
        
        # Execute command
        if args.command == "filter":
            result = filter_trace_by_mapper(trace_data, mapper_data)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        elif args.command == "merge":
            result = merge_static_and_dynamic(mapper_data, trace_data)
            output = json.dumps(result, indent=2, ensure_ascii=False)
        elif args.command == "report":
            output = generate_report(mapper_data, trace_data)
    
    # Write output
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


def combine_traces(
    runtime_path: str | None = None,
    web_path: str | None = None,
    network_path: str | None = None,
) -> dict:
    """Combine multiple trace sources into unified format.
    
    Merges:
    - Runtime traces (Python/Node.js function calls)
    - Web traces (browser JS execution)
    - Network traces (HTTP/WebSocket)
    """
    nodes = {}
    edges = []
    seq_offset = 0
    
    metadata = {
        "combined_at": datetime.now().isoformat(),
        "sources": [],
    }
    
    # Process runtime traces
    if runtime_path:
        runtime_data = load_json(runtime_path)
        metadata["sources"].append("runtime")
        
        for node in runtime_data.get("nodes", []):
            node_id = f"runtime:{node['id']}"
            nodes[node_id] = {
                **node,
                "id": node_id,
                "source": "runtime",
            }
        
        for edge in runtime_data.get("edges", []):
            edges.append({
                "from": f"runtime:{edge['from']}",
                "to": f"runtime:{edge['to']}",
                "call_count": edge.get("call_count", 1),
                "source": "runtime",
            })
        
        seq_offset = max(
            (n.get("first_call_seq", 0) for n in runtime_data.get("nodes", [])),
            default=0
        )
    
    # Process web traces
    if web_path:
        web_data = load_json(web_path)
        metadata["sources"].append("web")
        
        for node in web_data.get("nodes", []):
            node_id = f"web:{node['id']}"
            nodes[node_id] = {
                **node,
                "id": node_id,
                "source": "web",
                "first_call_seq": node.get("first_call_seq", 0) + seq_offset,
            }
        
        for edge in web_data.get("edges", []):
            edges.append({
                "from": f"web:{edge['from']}",
                "to": f"web:{edge['to']}",
                "call_count": edge.get("call_count", 1),
                "source": "web",
            })
        
        # Get max seq from web traces
        web_seq = max(
            (n.get("first_call_seq", 0) for n in web_data.get("nodes", [])),
            default=0
        )
        seq_offset += web_seq
    
    # Process network traces
    if network_path:
        network_data = load_json(network_path)
        metadata["sources"].append("network")
        
        # Convert network requests to nodes
        from collections import defaultdict
        import re
        from urllib.parse import urlparse
        
        api_nodes = defaultdict(lambda: {
            "call_count": 0,
            "statuses": defaultdict(int),
            "total_duration_ms": 0,
        })
        
        for req in network_data.get("requests", []):
            if not req.get("is_api", False):
                continue
            
            parsed = urlparse(req["url"])
            path = re.sub(r'/\d+', '/:id', parsed.path)
            node_id = f"network:{req['method']} {parsed.netloc}{path}"
            
            api_nodes[node_id]["call_count"] += 1
            api_nodes[node_id]["statuses"][req.get("status_code", 0)] += 1
            if req.get("duration_ms"):
                api_nodes[node_id]["total_duration_ms"] += req["duration_ms"]
        
        for node_id, data in api_nodes.items():
            nodes[node_id] = {
                "id": node_id,
                "function": node_id.split(":", 1)[1],
                "source": "network",
                "call_count": data["call_count"],
                "statuses": dict(data["statuses"]),
                "avg_duration_ms": data["total_duration_ms"] / data["call_count"] if data["call_count"] > 0 else 0,
                "is_network": True,
            }
    
    return {
        "metadata": {
            **metadata,
            "node_count": len(nodes),
            "edge_count": len(edges),
        },
        "nodes": list(nodes.values()),
        "edges": edges,
    }


if __name__ == "__main__":
    main()
