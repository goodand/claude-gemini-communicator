#!/usr/bin/env python3
"""
GraphML + Positional Encoding Formatter

LLM context injection format with layer depth and position encoding.
"""

from __future__ import annotations
import json
from collections import defaultdict, deque
from typing import Any

try:
    from classifier import GraphStructureClassifier, ClassificationResult, StructureType
except ImportError:
    from .classifier import GraphStructureClassifier, ClassificationResult, StructureType


class LayerCalculator:
    """Topological sort based layer calculator"""
    
    @staticmethod
    def calculate_layers(classifier: GraphStructureClassifier) -> dict[str, int]:
        """Calculate layer depth for each node (in-degree 0 = layer 0)"""
        if not classifier.nodes:
            return {}
        
        in_degree = {n: 0 for n in classifier.nodes}
        for target, sources in classifier.reverse_adj.items():
            in_degree[target] = len(set(sources))
        
        layers = {}
        queue = deque()
        
        for node in classifier.nodes:
            if in_degree[node] == 0:
                layers[node] = 0
                queue.append(node)
        
        if not queue:
            start = next(iter(classifier.nodes))
            layers[start] = 0
            queue.append(start)
        
        while queue:
            node = queue.popleft()
            for neighbor in classifier.adj_list.get(node, []):
                if neighbor not in layers:
                    layers[neighbor] = layers[node] + 1
                    queue.append(neighbor)
                else:
                    layers[neighbor] = max(layers[neighbor], layers[node] + 1)
        
        for node in classifier.nodes:
            if node not in layers:
                layers[node] = -1
        
        return layers


class GraphMLFormatter:
    """GraphML + Positional Encoding formatter"""
    
    @staticmethod
    def format(classifier: GraphStructureClassifier, result: ClassificationResult) -> str:
        """Generate GraphML JSON with layer/position encoding"""
        layers = LayerCalculator.calculate_layers(classifier)
        in_deg = classifier.get_in_degrees()
        out_deg = classifier.get_out_degrees()
        
        # Group by layer for positions
        layer_nodes: dict[int, list[str]] = defaultdict(list)
        for node, layer in layers.items():
            layer_nodes[layer].append(node)
        
        positions = {}
        for layer, nodes in layer_nodes.items():
            for i, node in enumerate(sorted(nodes)):
                positions[node] = {"x": i * 100, "y": layer * 100}
        
        # Build nodes
        nodes_out = []
        for node in sorted(classifier.nodes):
            node_data = {
                "id": node,
                "layer": layers.get(node, -1),
                "position": positions.get(node, {"x": 0, "y": 0}),
                "in_degree": in_deg.get(node, 0),
                "out_degree": out_deg.get(node, 0),
            }
            if in_deg.get(node, 0) == 0:
                node_data["type"] = "root"
            elif out_deg.get(node, 0) == 0:
                node_data["type"] = "leaf"
            else:
                node_data["type"] = "intermediate"
            nodes_out.append(node_data)
        
        # Build edges
        edge_weights: dict[tuple, int] = defaultdict(int)
        for e in classifier.edges:
            edge_weights[e] += 1
        
        edges_out = []
        seen = set()
        for src, tgt in classifier.edges:
            if (src, tgt) in seen:
                continue
            seen.add((src, tgt))
            edges_out.append({
                "source": src,
                "target": tgt,
                "weight": edge_weights[(src, tgt)],
                "layer_diff": layers.get(tgt, 0) - layers.get(src, 0),
            })
        
        # Layer summary
        summary = []
        for layer in sorted(layer_nodes.keys()):
            nodes = sorted(layer_nodes[layer])
            summary.append({"layer": layer, "count": len(nodes), "nodes": nodes})
        
        output = {
            "meta": {
                "structure_type": result.structure_type.value,
                "node_count": result.node_count,
                "edge_count": result.edge_count,
                "max_layer": max(layers.values()) if layers else 0,
            },
            "nodes": nodes_out,
            "edges": edges_out,
            "layer_summary": summary,
        }
        
        return json.dumps(output, indent=2, ensure_ascii=False)
    
    @staticmethod
    def format_for_llm_context(classifier: GraphStructureClassifier, result: ClassificationResult) -> str:
        """Generate concise Markdown for LLM context"""
        layers = LayerCalculator.calculate_layers(classifier)
        layer_nodes: dict[int, list[str]] = defaultdict(list)
        for node, layer in layers.items():
            layer_nodes[layer].append(node)
        
        lines = [
            f"# Graph: {result.structure_type.value}",
            f"Nodes: {result.node_count}, Edges: {result.edge_count}",
            "",
        ]
        
        for layer in sorted(layer_nodes.keys()):
            nodes = sorted(layer_nodes[layer])
            lines.append(f"**Layer {layer}**: {', '.join(nodes)}")
        
        if result.root_nodes:
            lines.append(f"\n**Roots**: {', '.join(result.root_nodes)}")
        
        return "\n".join(lines)
