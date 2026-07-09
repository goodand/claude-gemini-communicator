"""
Output Formatter - Convert analysis results to various formats (Phase 2)

Supported formats:
- JSON (default, classifier-compatible)
- GraphML with positional encoding
- Mermaid flowchart
- Adjacency list

Phase 2 additions:
- Hub node analysis (most connected)
- Dependency statistics
- Critical path identification
"""

from __future__ import annotations
import json
from datetime import datetime
from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from analyzers.base import AnalysisResult, Node, Edge


class OutputFormatter:
    """Format analysis results for various outputs (Phase 2 enhanced)"""
    
    def __init__(self, result: AnalysisResult, project_root: str):
        self.result = result
        self.project_root = project_root
        self._layers: dict[str, int] = {}
        self._positions: dict[str, tuple[int, int]] = {}
        self._in_degree: dict[str, int] = {}
        self._out_degree: dict[str, int] = {}
    
    def to_json(self, include_layers: bool = True, include_analysis: bool = True) -> dict:
        """
        Convert to JSON format compatible with graph-structure-classifier
        
        Output structure:
        {
            "metadata": {...},
            "nodes": [...],
            "edges": [...],
            "edge_list": [["src", "tgt"], ...],
            "analysis": {...}  # Phase 2: hub nodes, stats
        }
        """
        # Calculate layers if requested
        if include_layers:
            self._calculate_layers()
        
        # Calculate degrees for analysis
        self._calculate_degrees()
        
        # Count languages
        lang_counts = defaultdict(int)
        for node in self.result.nodes:
            lang_counts[node.language] += 1
        
        output = {
            "metadata": {
                "project_root": self.project_root,
                "analyzed_at": datetime.now().isoformat(),
                "languages": dict(lang_counts),
                "total_files": len(self.result.nodes),
                "total_edges": len(self.result.edges),
                "errors": len(self.result.errors),
            },
            "nodes": [],
            "edges": [],
            "edge_list": [],  # For classifier compatibility
        }
        
        # Add nodes with layer info
        for node in self.result.nodes:
            node_dict = node.to_dict()
            if include_layers and node.id in self._layers:
                node_dict["layer"] = self._layers[node.id]
            if node.id in self._positions:
                node_dict["position"] = {
                    "x": self._positions[node.id][0],
                    "y": self._positions[node.id][1]
                }
            output["nodes"].append(node_dict)
        
        # Add edges
        for edge in self.result.edges:
            output["edges"].append(edge.to_dict())
            output["edge_list"].append([edge.source, edge.target])
        
        # Phase 2: Add analysis section
        if include_analysis:
            output["analysis"] = self._generate_analysis()
        
        # Add errors if any
        if self.result.errors:
            output["errors"] = self.result.errors
        
        return output
    
    def to_json_string(self, indent: int = 2, include_layers: bool = True) -> str:
        """Convert to JSON string"""
        return json.dumps(
            self.to_json(include_layers), 
            indent=indent, 
            ensure_ascii=False
        )
    
    def _calculate_degrees(self) -> None:
        """Calculate in-degree and out-degree for all nodes"""
        self._in_degree.clear()
        self._out_degree.clear()
        
        all_nodes = {node.id for node in self.result.nodes}
        
        for node in all_nodes:
            self._in_degree[node] = 0
            self._out_degree[node] = 0
        
        for edge in self.result.edges:
            if edge.target in all_nodes:
                self._in_degree[edge.target] = self._in_degree.get(edge.target, 0) + 1
            if edge.source in all_nodes:
                self._out_degree[edge.source] = self._out_degree.get(edge.source, 0) + 1
    
    def _generate_analysis(self) -> dict:
        """Generate analysis section with hub nodes, stats, etc."""
        all_nodes = {node.id for node in self.result.nodes}
        
        # Hub nodes (most depended upon - high in-degree)
        hub_nodes = sorted(
            [(node, self._in_degree.get(node, 0)) for node in all_nodes],
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5
        
        # Connector nodes (most dependencies - high out-degree)
        connector_nodes = sorted(
            [(node, self._out_degree.get(node, 0)) for node in all_nodes],
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5
        
        # Entry points (no incoming edges)
        entry_points = [
            node for node in all_nodes 
            if self._in_degree.get(node, 0) == 0 and self._out_degree.get(node, 0) > 0
        ]
        
        # Leaf nodes (no outgoing edges)
        leaf_nodes = [
            node for node in all_nodes
            if self._out_degree.get(node, 0) == 0 and self._in_degree.get(node, 0) > 0
        ]
        
        # Isolated nodes (no edges at all)
        isolated_nodes = [
            node for node in all_nodes
            if self._in_degree.get(node, 0) == 0 and self._out_degree.get(node, 0) == 0
        ]
        
        # Edge type breakdown
        edge_types = defaultdict(int)
        for edge in self.result.edges:
            edge_types[edge.type] += 1
        
        # Layer distribution
        layer_dist = defaultdict(int)
        for node_id, layer in self._layers.items():
            layer_dist[layer] += 1
        
        return {
            "hub_nodes": [
                {"id": node, "in_degree": deg}
                for node, deg in hub_nodes if deg > 0
            ],
            "connector_nodes": [
                {"id": node, "out_degree": deg}
                for node, deg in connector_nodes if deg > 0
            ],
            "entry_points": entry_points[:10],  # Limit to 10
            "leaf_nodes": leaf_nodes[:10],
            "isolated_nodes": isolated_nodes[:5],
            "edge_type_breakdown": dict(edge_types),
            "layer_distribution": dict(sorted(layer_dist.items())),
            "max_depth": max(self._layers.values()) if self._layers else 0,
        }
    
    def to_edge_list_only(self) -> str:
        """Output only edge list (for direct classifier piping)"""
        edges = [[e.source, e.target] for e in self.result.edges]
        return json.dumps(edges, ensure_ascii=False)
    
    def to_graphml(self) -> str:
        """
        Convert to GraphML format with positional encoding
        
        Includes:
        - Node attributes (type, language, layer)
        - Edge attributes (type, weight)
        """
        self._calculate_layers()
        self._calculate_positions()
        
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
            '  <key id="type" for="node" attr.name="type" attr.type="string"/>',
            '  <key id="language" for="node" attr.name="language" attr.type="string"/>',
            '  <key id="layer" for="node" attr.name="layer" attr.type="int"/>',
            '  <key id="x" for="node" attr.name="x" attr.type="int"/>',
            '  <key id="y" for="node" attr.name="y" attr.type="int"/>',
            '  <key id="edge_type" for="edge" attr.name="type" attr.type="string"/>',
            '  <key id="weight" for="edge" attr.name="weight" attr.type="int"/>',
            '  <graph id="G" edgedefault="directed">',
        ]
        
        # Add nodes
        for node in self.result.nodes:
            node_id = self._escape_xml(node.id)
            layer = self._layers.get(node.id, 0)
            pos = self._positions.get(node.id, (0, 0))
            
            lines.append(f'    <node id="{node_id}">')
            lines.append(f'      <data key="type">{node.type}</data>')
            lines.append(f'      <data key="language">{node.language}</data>')
            lines.append(f'      <data key="layer">{layer}</data>')
            lines.append(f'      <data key="x">{pos[0]}</data>')
            lines.append(f'      <data key="y">{pos[1]}</data>')
            lines.append('    </node>')
        
        # Add edges
        for i, edge in enumerate(self.result.edges):
            src = self._escape_xml(edge.source)
            tgt = self._escape_xml(edge.target)
            
            lines.append(f'    <edge id="e{i}" source="{src}" target="{tgt}">')
            lines.append(f'      <data key="edge_type">{edge.type}</data>')
            lines.append(f'      <data key="weight">{edge.weight}</data>')
            lines.append('    </edge>')
        
        lines.append('  </graph>')
        lines.append('</graphml>')
        
        return '\n'.join(lines)
    
    def to_mermaid(self) -> str:
        """Convert to Mermaid flowchart format"""
        lines = ["flowchart TD"]
        
        # Add nodes with styling based on type
        node_ids = {}  # Map full path to short id
        for i, node in enumerate(self.result.nodes):
            short_id = f"n{i}"
            node_ids[node.id] = short_id
            
            # Shorten label for readability
            label = node.id.split("/")[-1] if "/" in node.id else node.id
            
            if node.type == "module":
                lines.append(f"    {short_id}[{label}]")
            elif node.type == "class":
                lines.append(f"    {short_id}[/{label}/]")
            else:
                lines.append(f"    {short_id}({label})")
        
        # Add edges with different styles
        seen_edges = set()
        for edge in self.result.edges:
            if edge.source not in node_ids or edge.target not in node_ids:
                continue
            
            src = node_ids[edge.source]
            tgt = node_ids[edge.target]
            edge_key = (src, tgt)
            
            if edge_key in seen_edges:
                continue
            seen_edges.add(edge_key)
            
            if edge.type == "IMPORT":
                lines.append(f"    {src} --> {tgt}")
            elif edge.type == "INHERITANCE":
                lines.append(f"    {src} -.-> {tgt}")
            elif edge.type == "FUNCTION_CALL":
                lines.append(f"    {src} ==> {tgt}")
            else:
                lines.append(f"    {src} --> {tgt}")
        
        return "\n".join(lines)
    
    def to_adjacency_list(self) -> dict[str, list[str]]:
        """Convert to adjacency list format"""
        adj = defaultdict(list)
        for edge in self.result.edges:
            adj[edge.source].append(edge.target)
        return dict(adj)
    
    def to_adjacency_list_string(self) -> str:
        """Adjacency list as formatted string"""
        adj = self.to_adjacency_list()
        lines = []
        for source in sorted(adj.keys()):
            targets = ", ".join(sorted(adj[source]))
            lines.append(f"{source} -> {targets}")
        return "\n".join(lines)
    
    def _calculate_layers(self) -> None:
        """
        Calculate layer depths using topological sort
        Layer 0 = nodes with no incoming edges (roots)
        """
        # Build in-degree map
        in_degree: dict[str, int] = defaultdict(int)
        adj: dict[str, list[str]] = defaultdict(list)
        
        all_nodes = {node.id for node in self.result.nodes}
        
        for edge in self.result.edges:
            if edge.source in all_nodes and edge.target in all_nodes:
                in_degree[edge.target] += 1
                adj[edge.source].append(edge.target)
        
        # Initialize all nodes
        for node in self.result.nodes:
            if node.id not in in_degree:
                in_degree[node.id] = 0
        
        # BFS for layer assignment
        self._layers.clear()
        queue = [(n, 0) for n in all_nodes if in_degree[n] == 0]
        
        # If no roots found, start from all nodes with minimum in-degree
        if not queue:
            min_deg = min(in_degree.values()) if in_degree else 0
            queue = [(n, 0) for n, d in in_degree.items() if d == min_deg]
        
        visited = set()
        while queue:
            node, layer = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            
            # Assign maximum layer seen
            self._layers[node] = max(self._layers.get(node, 0), layer)
            
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    queue.append((neighbor, layer + 1))
        
        # Assign layer 0 to unvisited nodes
        for node in all_nodes:
            if node not in self._layers:
                self._layers[node] = 0
    
    def _calculate_positions(self) -> None:
        """
        Calculate x,y positions for visualization
        x = position within layer
        y = layer depth
        """
        # Group nodes by layer
        layer_nodes: dict[int, list[str]] = defaultdict(list)
        for node_id, layer in self._layers.items():
            layer_nodes[layer].append(node_id)
        
        # Assign positions
        self._positions.clear()
        y_spacing = 100
        x_spacing = 150
        
        for layer, nodes in layer_nodes.items():
            y = layer * y_spacing
            nodes_sorted = sorted(nodes)
            total_width = (len(nodes_sorted) - 1) * x_spacing
            start_x = -total_width // 2
            
            for i, node_id in enumerate(nodes_sorted):
                x = start_x + i * x_spacing
                self._positions[node_id] = (x, y)
    
    def _escape_xml(self, s: str) -> str:
        """Escape special XML characters"""
        return (s
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;"))
