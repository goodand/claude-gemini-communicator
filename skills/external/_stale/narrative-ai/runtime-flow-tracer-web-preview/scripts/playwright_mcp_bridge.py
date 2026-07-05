#!/usr/bin/env python3
"""
playwright_mcp_bridge.py - Bridge between Playwright MCP and runtime-flow-tracer

Converts Playwright MCP outputs to tracer-compatible formats:
- Console messages → function call traces
- Network requests → API call graph
- Snapshots → DOM state timeline

Usage:
    # Convert Playwright MCP console output
    python playwright_mcp_bridge.py console mcp_console.json -o trace.json
    
    # Convert network requests to API call graph
    python playwright_mcp_bridge.py network mcp_network.json --format mermaid
    
    # Combine multiple MCP outputs
    python playwright_mcp_bridge.py combine --console console.json --network network.json
    
    # Parse Playwright trace file (.zip)
    python playwright_mcp_bridge.py trace trace.zip -o analysis.json

Integration with Playwright MCP:
    1. Run Playwright MCP with --save-session or capture tool outputs
    2. Use this bridge to convert outputs to tracer format
    3. Combine with runtime traces via bridge.py
"""

from __future__ import annotations
import argparse
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field, asdict


@dataclass
class TraceNode:
    """Node in the trace graph"""
    id: str
    function: str
    source: str  # "console", "network", "snapshot"
    call_count: int = 1
    first_call_seq: int = 0
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "function": self.function,
            "source": self.source,
            "call_count": self.call_count,
            "first_call_seq": self.first_call_seq,
            **self.metadata
        }


@dataclass 
class TraceEdge:
    """Edge in the trace graph"""
    source: str
    target: str
    call_count: int = 1
    first_call_seq: int = 0
    
    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "call_count": self.call_count,
            "first_call_seq": self.first_call_seq
        }


class PlaywrightMCPBridge:
    """Convert Playwright MCP outputs to tracer format"""
    
    def __init__(self):
        self.nodes: dict[str, TraceNode] = {}
        self.edges: list[TraceEdge] = []
        self.seq = 0
        self.call_stack: list[str] = []
    
    def parse_console_messages(self, data: dict | list) -> dict:
        """Parse browser_console_messages output
        
        Expected format (from MCP tool):
        [
            {"type": "log", "text": "...", "location": "file.js:10:5", "timestamp": ...},
            ...
        ]
        
        Or wrapped in content array from MCP response.
        """
        messages = self._extract_messages(data)
        
        for msg in messages:
            self.seq += 1
            
            # Extract function name from location or text
            location = msg.get("location", "")
            text = msg.get("text", "")
            msg_type = msg.get("type", "log")
            
            # Try to extract function name
            func_name = self._extract_function_from_log(text, location)
            
            node_id = f"console:{func_name}"
            
            if node_id not in self.nodes:
                self.nodes[node_id] = TraceNode(
                    id=node_id,
                    function=func_name,
                    source="console",
                    first_call_seq=self.seq,
                    metadata={
                        "type": msg_type,
                        "location": location,
                    }
                )
            else:
                self.nodes[node_id].call_count += 1
            
            # Create edge from previous call
            if self.call_stack:
                prev = self.call_stack[-1]
                self._add_edge(prev, node_id)
            
            self.call_stack.append(node_id)
            
            # Pop stack on certain patterns
            if "return" in text.lower() or "end" in text.lower():
                if self.call_stack:
                    self.call_stack.pop()
        
        return self._to_trace_format("console")
    
    def parse_network_requests(self, data: dict | list) -> dict:
        """Parse browser_network_requests output
        
        Expected format:
        [
            {"method": "GET", "url": "...", "status": 200, "resourceType": "xhr", ...},
            ...
        ]
        """
        requests = self._extract_messages(data)
        
        # Group by endpoint pattern
        endpoint_nodes: dict[str, TraceNode] = {}
        prev_endpoint = None
        
        for req in requests:
            self.seq += 1
            
            method = req.get("method", "GET")
            url = req.get("url", "")
            status = req.get("status", 0)
            resource_type = req.get("resourceType", req.get("resource_type", "other"))
            
            # Skip static resources unless explicitly requested
            if resource_type in ("stylesheet", "image", "font", "script"):
                continue
            
            # Create endpoint pattern (generalize IDs)
            endpoint = self._generalize_url(method, url)
            node_id = f"network:{endpoint}"
            
            if node_id not in self.nodes:
                self.nodes[node_id] = TraceNode(
                    id=node_id,
                    function=endpoint,
                    source="network",
                    first_call_seq=self.seq,
                    metadata={
                        "method": method,
                        "statuses": defaultdict(int),
                        "resource_type": resource_type,
                    }
                )
            
            self.nodes[node_id].call_count += 1
            self.nodes[node_id].metadata["statuses"][status] += 1
            
            # Create sequential edges
            if prev_endpoint and prev_endpoint != node_id:
                self._add_edge(prev_endpoint, node_id)
            
            prev_endpoint = node_id
        
        # Convert defaultdict to dict for JSON serialization
        for node in self.nodes.values():
            if "statuses" in node.metadata:
                node.metadata["statuses"] = dict(node.metadata["statuses"])
        
        return self._to_trace_format("network")
    
    def parse_playwright_trace(self, trace_path: str) -> dict:
        """Parse Playwright trace file (.zip)
        
        Playwright traces contain:
        - trace.trace: Main trace data (JSON lines)
        - trace.network: Network events
        - resources/: Screenshots and other resources
        """
        trace_file = Path(trace_path)
        
        if not trace_file.exists():
            return {"error": f"Trace file not found: {trace_path}"}
        
        events = []
        network_events = []
        
        try:
            with zipfile.ZipFile(trace_file, 'r') as zf:
                # Read main trace
                for name in zf.namelist():
                    if name.endswith('.trace'):
                        with zf.open(name) as f:
                            for line in f:
                                try:
                                    event = json.loads(line.decode('utf-8'))
                                    events.append(event)
                                except json.JSONDecodeError:
                                    continue
                    
                    elif name.endswith('.network'):
                        with zf.open(name) as f:
                            for line in f:
                                try:
                                    event = json.loads(line.decode('utf-8'))
                                    network_events.append(event)
                                except json.JSONDecodeError:
                                    continue
        except zipfile.BadZipFile:
            return {"error": "Invalid trace file format"}
        
        # Process trace events
        for event in events:
            self._process_trace_event(event)
        
        # Process network events
        for event in network_events:
            self._process_network_event(event)
        
        return self._to_trace_format("playwright_trace")
    
    def _process_trace_event(self, event: dict):
        """Process a single Playwright trace event"""
        event_type = event.get("type")
        
        if event_type == "action":
            self.seq += 1
            action = event.get("metadata", {})
            action_type = action.get("type", "unknown")
            
            node_id = f"action:{action_type}"
            
            if node_id not in self.nodes:
                self.nodes[node_id] = TraceNode(
                    id=node_id,
                    function=action_type,
                    source="action",
                    first_call_seq=self.seq,
                )
            else:
                self.nodes[node_id].call_count += 1
            
            if self.call_stack:
                self._add_edge(self.call_stack[-1], node_id)
            self.call_stack.append(node_id)
        
        elif event_type == "event":
            event_name = event.get("method", "unknown")
            if "console" in event_name.lower():
                # Handle console events
                params = event.get("params", {})
                text = params.get("text", "")
                func_name = self._extract_function_from_log(text, "")
                
                self.seq += 1
                node_id = f"console:{func_name}"
                
                if node_id not in self.nodes:
                    self.nodes[node_id] = TraceNode(
                        id=node_id,
                        function=func_name,
                        source="console",
                        first_call_seq=self.seq,
                    )
                else:
                    self.nodes[node_id].call_count += 1
    
    def _process_network_event(self, event: dict):
        """Process a network event from trace"""
        if event.get("type") != "resource":
            return
        
        request = event.get("request", {})
        response = event.get("response", {})
        
        method = request.get("method", "GET")
        url = request.get("url", "")
        status = response.get("status", 0)
        
        # Skip non-API requests
        if not url or any(ext in url for ext in ['.css', '.js', '.png', '.jpg', '.gif', '.woff']):
            return
        
        self.seq += 1
        endpoint = self._generalize_url(method, url)
        node_id = f"network:{endpoint}"
        
        if node_id not in self.nodes:
            self.nodes[node_id] = TraceNode(
                id=node_id,
                function=endpoint,
                source="network",
                first_call_seq=self.seq,
                metadata={"method": method, "statuses": {status: 1}}
            )
        else:
            self.nodes[node_id].call_count += 1
            if "statuses" in self.nodes[node_id].metadata:
                statuses = self.nodes[node_id].metadata["statuses"]
                statuses[status] = statuses.get(status, 0) + 1
    
    def _extract_messages(self, data: dict | list) -> list:
        """Extract messages from various MCP response formats"""
        if isinstance(data, list):
            return data
        
        # Handle MCP tool response format
        if "content" in data:
            content = data["content"]
            if isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        try:
                            return json.loads(item["text"])
                        except json.JSONDecodeError:
                            # Try line-by-line parsing
                            lines = item["text"].strip().split("\n")
                            return [{"text": line} for line in lines if line.strip()]
            elif isinstance(content, str):
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    return [{"text": content}]
        
        # Handle direct messages array
        if "messages" in data:
            return data["messages"]
        
        # Handle network requests format
        if "requests" in data:
            return data["requests"]
        
        return []
    
    def _extract_function_from_log(self, text: str, location: str) -> str:
        """Extract function name from console log"""
        # Try to extract from common patterns
        patterns = [
            r'\[(\w+)\]',           # [FunctionName]
            r'(\w+):\s',            # FunctionName: 
            r'(\w+)\(\)',           # FunctionName()
            r'(\w+)\s+called',      # FunctionName called
            r'calling\s+(\w+)',     # calling FunctionName
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Try to extract from location
        if location:
            # Format: file.js:10:5 or file.js:10
            match = re.search(r'(\w+)\.\w+:\d+', location)
            if match:
                return match.group(1)
        
        # Fallback: use first word or truncated text
        words = text.split()
        if words:
            first_word = words[0].strip('[]():,')
            if first_word and len(first_word) < 30:
                return first_word
        
        return text[:30] if text else "unknown"
    
    def _generalize_url(self, method: str, url: str) -> str:
        """Generalize URL by replacing IDs with placeholders"""
        from urllib.parse import urlparse
        
        parsed = urlparse(url)
        path = parsed.path
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/:id', path)
        # Replace UUIDs
        path = re.sub(r'/[a-f0-9-]{36}', '/:uuid', path, flags=re.IGNORECASE)
        # Replace other ID-like patterns
        path = re.sub(r'/[a-zA-Z0-9]{20,}', '/:token', path)
        
        return f"{method} {parsed.netloc}{path}"
    
    def _add_edge(self, source: str, target: str):
        """Add or update edge"""
        for edge in self.edges:
            if edge.source == source and edge.target == target:
                edge.call_count += 1
                return
        
        self.edges.append(TraceEdge(
            source=source,
            target=target,
            first_call_seq=self.seq
        ))
    
    def _to_trace_format(self, source_type: str) -> dict:
        """Convert to unified trace format"""
        return {
            "metadata": {
                "source": f"playwright_mcp:{source_type}",
                "traced_at": datetime.now().isoformat(),
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
            },
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
        }
    
    def reset(self):
        """Reset state for new parsing"""
        self.nodes.clear()
        self.edges.clear()
        self.seq = 0
        self.call_stack.clear()


class OutputFormatter:
    """Format trace results"""
    
    @staticmethod
    def to_mermaid(trace_data: dict) -> str:
        """Convert to Mermaid flowchart"""
        lines = ["flowchart LR"]
        
        node_ids = {}
        for i, node in enumerate(trace_data.get("nodes", [])):
            node_id = f"N{i}"
            node_ids[node["id"]] = node_id
            
            label = node["function"]
            count = node.get("call_count", 1)
            source = node.get("source", "")
            
            # Escape quotes in labels
            label = label.replace('"', "'")
            
            # Different shapes for different sources
            if source == "network":
                if count > 1:
                    lines.append(f'    {node_id}[/"{label} ({count}x)"/]')
                else:
                    lines.append(f'    {node_id}[/"{label}"/]')
            elif source == "console":
                if count > 1:
                    lines.append(f'    {node_id}["{label} ({count}x)"]')
                else:
                    lines.append(f'    {node_id}["{label}"]')
            else:
                if count > 1:
                    lines.append(f'    {node_id}{{"{label} ({count}x)"}}')
                else:
                    lines.append(f'    {node_id}{{"{label}"}}')
        
        for edge in trace_data.get("edges", []):
            src_id = node_ids.get(edge["source"])
            tgt_id = node_ids.get(edge["target"])
            if src_id and tgt_id:
                count = edge.get("call_count", 1)
                if count > 1:
                    lines.append(f'    {src_id} -->|{count}x| {tgt_id}')
                else:
                    lines.append(f'    {src_id} --> {tgt_id}')
        
        return "\n".join(lines)
    
    @staticmethod
    def to_edge_list(trace_data: dict) -> str:
        """Convert to edge list format"""
        lines = []
        for edge in trace_data.get("edges", []):
            lines.append(f"{edge['source']} {edge['target']}")
        return "\n".join(lines)


def combine_traces(*traces: dict) -> dict:
    """Combine multiple trace outputs"""
    combined_nodes = {}
    combined_edges = []
    
    for trace in traces:
        if not trace:
            continue
        
        for node in trace.get("nodes", []):
            node_id = node["id"]
            if node_id in combined_nodes:
                combined_nodes[node_id]["call_count"] += node.get("call_count", 1)
            else:
                combined_nodes[node_id] = node.copy()
        
        for edge in trace.get("edges", []):
            # Check for existing edge
            existing = next(
                (e for e in combined_edges 
                 if e["source"] == edge["source"] and e["target"] == edge["target"]),
                None
            )
            if existing:
                existing["call_count"] += edge.get("call_count", 1)
            else:
                combined_edges.append(edge.copy())
    
    return {
        "metadata": {
            "source": "playwright_mcp:combined",
            "traced_at": datetime.now().isoformat(),
            "node_count": len(combined_nodes),
            "edge_count": len(combined_edges),
        },
        "nodes": list(combined_nodes.values()),
        "edges": combined_edges,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Bridge between Playwright MCP and runtime-flow-tracer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    console  - Parse browser_console_messages output
    network  - Parse browser_network_requests output
    trace    - Parse Playwright trace file (.zip)
    combine  - Combine multiple MCP outputs

Examples:
    # Convert console messages
    python playwright_mcp_bridge.py console mcp_console.json
    
    # Convert network requests to Mermaid
    python playwright_mcp_bridge.py network mcp_network.json --format mermaid
    
    # Parse Playwright trace
    python playwright_mcp_bridge.py trace trace.zip -o analysis.json
    
    # Combine outputs
    python playwright_mcp_bridge.py combine --console c.json --network n.json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Console subcommand
    console_parser = subparsers.add_parser("console", help="Parse console messages")
    console_parser.add_argument("input", help="Console messages JSON file")
    console_parser.add_argument("--format", choices=["json", "mermaid", "edge-list"],
                                default="json", help="Output format")
    console_parser.add_argument("-o", "--output", help="Output file")
    
    # Network subcommand
    network_parser = subparsers.add_parser("network", help="Parse network requests")
    network_parser.add_argument("input", help="Network requests JSON file")
    network_parser.add_argument("--format", choices=["json", "mermaid", "edge-list"],
                                default="json", help="Output format")
    network_parser.add_argument("-o", "--output", help="Output file")
    
    # Trace subcommand
    trace_parser = subparsers.add_parser("trace", help="Parse Playwright trace file")
    trace_parser.add_argument("input", help="Playwright trace file (.zip)")
    trace_parser.add_argument("--format", choices=["json", "mermaid", "edge-list"],
                              default="json", help="Output format")
    trace_parser.add_argument("-o", "--output", help="Output file")
    
    # Combine subcommand
    combine_parser = subparsers.add_parser("combine", help="Combine multiple outputs")
    combine_parser.add_argument("--console", help="Console messages JSON")
    combine_parser.add_argument("--network", help="Network requests JSON")
    combine_parser.add_argument("--trace", help="Playwright trace file")
    combine_parser.add_argument("--format", choices=["json", "mermaid", "edge-list"],
                                default="json", help="Output format")
    combine_parser.add_argument("-o", "--output", help="Output file")
    
    args = parser.parse_args()
    
    bridge = PlaywrightMCPBridge()
    result = None
    
    if args.command == "console":
        with open(args.input) as f:
            data = json.load(f)
        result = bridge.parse_console_messages(data)
    
    elif args.command == "network":
        with open(args.input) as f:
            data = json.load(f)
        result = bridge.parse_network_requests(data)
    
    elif args.command == "trace":
        result = bridge.parse_playwright_trace(args.input)
    
    elif args.command == "combine":
        traces = []
        
        if args.console:
            with open(args.console) as f:
                data = json.load(f)
            bridge.reset()
            traces.append(bridge.parse_console_messages(data))
        
        if args.network:
            with open(args.network) as f:
                data = json.load(f)
            bridge.reset()
            traces.append(bridge.parse_network_requests(data))
        
        if args.trace:
            bridge.reset()
            traces.append(bridge.parse_playwright_trace(args.trace))
        
        result = combine_traces(*traces)
    
    # Format output
    if args.format == "json":
        output = json.dumps(result, indent=2, ensure_ascii=False)
    elif args.format == "mermaid":
        output = OutputFormatter.to_mermaid(result)
    elif args.format == "edge-list":
        output = OutputFormatter.to_edge_list(result)
    
    # Write output
    if args.output:
        Path(args.output).write_text(output)
        print(f"Output written to: {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
