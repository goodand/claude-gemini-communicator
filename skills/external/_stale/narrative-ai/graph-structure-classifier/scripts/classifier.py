#!/usr/bin/env python3
"""
Graph Structure Classifier - Waterfall Algorithm

Classify: Tree → DAG → MultiEdgeDAG → DirectedGraph

Usage:
    python classifier.py edges.json [--format json|mermaid|graphml]
    echo '[["A","B"]]' | python classifier.py -
"""

from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from collections import defaultdict


class StructureType(Enum):
    """Graph structure types (constraint order)"""
    TREE = "Tree"
    DAG = "DAG"
    MULTI_EDGE_DAG = "MultiEdgeDAG"
    DIRECTED_GRAPH = "DirectedGraph"
    INVALID = "Invalid"


@dataclass
class ClassificationResult:
    """Classification result"""
    structure_type: StructureType
    reason: str
    step_failed: int | None = None
    node_count: int = 0
    edge_count: int = 0
    unique_edge_count: int = 0
    has_cycle: bool = False
    cycle_nodes: list[str] = field(default_factory=list)
    max_in_degree: int = 0
    multi_parent_nodes: list[str] = field(default_factory=list)
    root_nodes: list[str] = field(default_factory=list)
    unreachable_nodes: list[str] = field(default_factory=list)
    duplicate_edges: list[tuple[str, str]] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "structure_type": self.structure_type.value,
            "reason": self.reason,
            "step_failed": self.step_failed,
            "stats": {
                "nodes": self.node_count,
                "edges": self.edge_count,
                "unique_edges": self.unique_edge_count,
                "max_in_degree": self.max_in_degree,
                "has_cycle": self.has_cycle,
            },
            "details": {
                "cycle_nodes": self.cycle_nodes,
                "multi_parent_nodes": self.multi_parent_nodes,
                "root_nodes": self.root_nodes,
                "unreachable_nodes": self.unreachable_nodes,
                "duplicate_edges": [list(e) for e in self.duplicate_edges],
            }
        }


class GraphStructureClassifier:
    """Waterfall graph structure classifier"""
    
    def __init__(self):
        self.adj_list: dict[str, list[str]] = defaultdict(list)
        self.reverse_adj: dict[str, list[str]] = defaultdict(list)
        self.nodes: set[str] = set()
        self.edges: list[tuple[str, str]] = []
        self.edge_set: set[tuple[str, str]] = set()
        
    def load_edges(self, edges: list) -> None:
        """Load edge data"""
        self.adj_list.clear()
        self.reverse_adj.clear()
        self.nodes.clear()
        self.edges.clear()
        self.edge_set.clear()
        
        for edge in edges:
            if isinstance(edge, dict):
                source = str(edge.get("source", ""))
                target = str(edge.get("target", ""))
            else:
                source, target = str(edge[0]), str(edge[1])
            
            if not source or not target:
                continue
                
            self.nodes.add(source)
            self.nodes.add(target)
            self.edges.append((source, target))
            self.edge_set.add((source, target))
            self.adj_list[source].append(target)
            self.reverse_adj[target].append(source)
    
    def classify(self) -> ClassificationResult:
        """Waterfall classification"""
        result = ClassificationResult(
            structure_type=StructureType.INVALID,
            reason="",
            node_count=len(self.nodes),
            edge_count=len(self.edges),
            unique_edge_count=len(self.edge_set),
        )
        
        if not self.nodes:
            result.reason = "Empty graph"
            return result
        
        if not self.edges:
            if len(self.nodes) == 1:
                result.structure_type = StructureType.TREE
                result.reason = "Single node tree"
                result.root_nodes = list(self.nodes)
                return result
            result.structure_type = StructureType.DIRECTED_GRAPH
            result.reason = "Disconnected nodes"
            return result
        
        # Step 2: Cycle detection
        cycle_info = self._detect_cycle()
        result.has_cycle = cycle_info["has_cycle"]
        result.cycle_nodes = cycle_info["cycle_nodes"]
        
        if result.has_cycle:
            result.structure_type = StructureType.DIRECTED_GRAPH
            result.reason = f"Cycle: {result.cycle_nodes}"
            result.step_failed = 2
            return result
        
        # Step 3: Multi-edge and in-degree
        degree_info = self._analyze_degrees()
        result.max_in_degree = degree_info["max_in_degree"]
        result.multi_parent_nodes = degree_info["multi_parent_nodes"]
        result.duplicate_edges = degree_info["duplicate_edges"]
        
        if result.duplicate_edges:
            result.structure_type = StructureType.MULTI_EDGE_DAG
            result.reason = f"Duplicate edges: {result.duplicate_edges[:3]}"
            result.step_failed = 3
            return result
        
        if result.max_in_degree > 1:
            result.structure_type = StructureType.DAG
            result.reason = f"Multi-parent nodes: {result.multi_parent_nodes}"
            result.step_failed = 3
            return result
        
        # Step 4: Connectivity
        conn_info = self._check_connectivity()
        result.root_nodes = conn_info["root_nodes"]
        result.unreachable_nodes = conn_info["unreachable_nodes"]
        
        if len(result.root_nodes) != 1:
            result.structure_type = StructureType.DAG
            result.reason = f"Multiple roots: {result.root_nodes}"
            result.step_failed = 4
            return result
        
        if result.unreachable_nodes:
            result.structure_type = StructureType.DAG
            result.reason = f"Disconnected: {result.unreachable_nodes}"
            result.step_failed = 4
            return result
        
        result.structure_type = StructureType.TREE
        result.reason = "Single root, single parent, acyclic, connected"
        return result
    
    def _detect_cycle(self) -> dict:
        """DFS 3-color cycle detection"""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in self.nodes}
        cycle_nodes = []
        
        def dfs(node, path):
            color[node] = GRAY
            path.append(node)
            for neighbor in self.adj_list.get(node, []):
                if color[neighbor] == GRAY:
                    idx = path.index(neighbor)
                    cycle_nodes.extend(path[idx:])
                    return True
                if color[neighbor] == WHITE and dfs(neighbor, path):
                    return True
            color[node] = BLACK
            path.pop()
            return False
        
        for node in self.nodes:
            if color[node] == WHITE and dfs(node, []):
                return {"has_cycle": True, "cycle_nodes": cycle_nodes}
        return {"has_cycle": False, "cycle_nodes": []}
    
    def _analyze_degrees(self) -> dict:
        """Analyze in-degrees and duplicate edges"""
        in_degree = defaultdict(int)
        for target, sources in self.reverse_adj.items():
            in_degree[target] = len(set(sources))
        
        max_in = max(in_degree.values()) if in_degree else 0
        multi_parent = [n for n, d in in_degree.items() if d > 1]
        
        edge_count = defaultdict(int)
        for e in self.edges:
            edge_count[e] += 1
        duplicates = [e for e, c in edge_count.items() if c > 1]
        
        return {
            "max_in_degree": max_in,
            "multi_parent_nodes": multi_parent,
            "duplicate_edges": duplicates,
        }
    
    def _check_connectivity(self) -> dict:
        """Check connectivity and find roots"""
        roots = [n for n in self.nodes if n not in self.reverse_adj or not self.reverse_adj[n]]
        
        if not roots:
            return {"root_nodes": [], "unreachable_nodes": list(self.nodes)}
        
        reachable = set()
        for root in roots:
            queue = [root]
            while queue:
                node = queue.pop(0)
                if node in reachable:
                    continue
                reachable.add(node)
                queue.extend(self.adj_list.get(node, []))
        
        return {
            "root_nodes": roots,
            "unreachable_nodes": list(self.nodes - reachable),
        }
    
    def get_in_degrees(self) -> dict[str, int]:
        return {n: len(set(self.reverse_adj.get(n, []))) for n in self.nodes}
    
    def get_out_degrees(self) -> dict[str, int]:
        return {n: len(set(self.adj_list.get(n, []))) for n in self.nodes}


def classify_graph(edges: list) -> ClassificationResult:
    """Convenience function"""
    c = GraphStructureClassifier()
    c.load_edges(edges)
    return c.classify()


def format_mermaid(classifier: GraphStructureClassifier) -> str:
    """Generate Mermaid flowchart"""
    lines = ["flowchart TD"]
    for node in sorted(classifier.nodes):
        lines.append(f"    {node}[{node}]")
    seen = set()
    for src, tgt in classifier.edges:
        if (src, tgt) not in seen:
            lines.append(f"    {src} --> {tgt}")
            seen.add((src, tgt))
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Graph Structure Classifier")
    parser.add_argument("input", help="JSON file or '-' for stdin")
    parser.add_argument("-f", "--format", choices=["json", "mermaid", "graphml"], default="json")
    parser.add_argument("-o", "--output", help="Output file")
    args = parser.parse_args()
    
    # Load input
    if args.input == "-":
        data = json.loads(sys.stdin.read())
    else:
        with open(args.input) as f:
            data = json.load(f)
    
    edges = [tuple(e) if isinstance(e, list) else e for e in data]
    
    classifier = GraphStructureClassifier()
    classifier.load_edges(edges)
    result = classifier.classify()
    
    # Format output
    if args.format == "json":
        output = json.dumps(result.to_dict(), indent=2, ensure_ascii=False)
    elif args.format == "mermaid":
        output = format_mermaid(classifier)
    elif args.format == "graphml":
        from graphml_formatter import GraphMLFormatter
        output = GraphMLFormatter.format(classifier, result)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
    else:
        print(output)
    
    # Exit code
    if result.structure_type.value in ["Tree", "DAG", "MultiEdgeDAG"]:
        return 0
    elif result.structure_type.value == "DirectedGraph":
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
