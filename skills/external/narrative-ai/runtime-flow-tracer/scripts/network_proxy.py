#!/usr/bin/env python3
"""
network_proxy.py - Mitmproxy addon for network traffic capture

Captures HTTP/HTTPS traffic and exports as structured data:
- Request/Response pairs
- Headers, body, timing
- WebSocket messages
- API call graphs

Usage:
    # As standalone proxy
    mitmdump -s network_proxy.py --set output=trace.json
    
    # With specific port
    mitmdump -s network_proxy.py -p 8080 --set output=trace.json
    
    # Filter specific domains
    mitmdump -s network_proxy.py --set domains=api.example.com,cdn.example.com
    
    # Combine with web_tracer.py
    python web_tracer.py https://example.com --proxy localhost:8080

Integration:
    The captured data can be merged with JS traces via bridge.py
"""

import json
import time
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from urllib.parse import urlparse

try:
    from mitmproxy import http, ctx, websocket
    from mitmproxy.addonmanager import Loader
    MITMPROXY_AVAILABLE = True
except ImportError:
    MITMPROXY_AVAILABLE = False


@dataclass
class RequestTrace:
    """Single request trace."""
    seq: int
    timestamp: float
    method: str
    url: str
    host: str
    path: str
    query: str
    request_headers: Dict[str, str]
    request_body: Optional[str]
    request_size: int
    
    # Response (filled later)
    status_code: Optional[int] = None
    status_text: Optional[str] = None
    response_headers: Optional[Dict[str, str]] = None
    response_body: Optional[str] = None
    response_size: int = 0
    
    # Timing
    duration_ms: Optional[float] = None
    
    # Classification
    content_type: Optional[str] = None
    resource_type: str = "other"
    is_api: bool = False
    
    # Error
    error: Optional[str] = None


@dataclass
class WebSocketTrace:
    """WebSocket message trace."""
    seq: int
    timestamp: float
    url: str
    direction: str  # "send" or "receive"
    message_type: str  # "text" or "binary"
    message: str
    size: int


class NetworkTracer:
    """Mitmproxy addon for network traffic capture."""
    
    def __init__(self):
        self.traces: List[RequestTrace] = []
        self.websocket_traces: List[WebSocketTrace] = []
        self.seq = 0
        self.ws_seq = 0
        
        # Config (set via mitmproxy options)
        self.output_file: str = "network_trace.json"
        self.domains: Set[str] = set()  # Empty = capture all
        self.max_body_size: int = 100 * 1024  # 100KB
        self.capture_bodies: bool = True
        self.exclude_patterns: List[re.Pattern] = []
        
        # Flow tracking for timing
        self.flow_start_times: Dict[str, float] = {}
        
        # API detection patterns
        self.api_patterns = [
            re.compile(r'/api/'),
            re.compile(r'/v\d+/'),
            re.compile(r'\.json$'),
            re.compile(r'/graphql'),
            re.compile(r'/rest/'),
        ]
    
    def load(self, loader: Loader):
        """Register mitmproxy options."""
        loader.add_option(
            name="output",
            typespec=str,
            default="network_trace.json",
            help="Output file for traces",
        )
        loader.add_option(
            name="domains",
            typespec=str,
            default="",
            help="Comma-separated list of domains to capture (empty = all)",
        )
        loader.add_option(
            name="max_body",
            typespec=int,
            default=100 * 1024,
            help="Max body size to capture (bytes)",
        )
        loader.add_option(
            name="no_bodies",
            typespec=bool,
            default=False,
            help="Skip capturing request/response bodies",
        )
        loader.add_option(
            name="exclude",
            typespec=str,
            default="",
            help="Regex patterns to exclude (comma-separated)",
        )
    
    def configure(self, updated):
        """Update configuration from mitmproxy options."""
        if "output" in updated:
            self.output_file = ctx.options.output
        if "domains" in updated:
            domains_str = ctx.options.domains
            self.domains = set(d.strip() for d in domains_str.split(",") if d.strip())
        if "max_body" in updated:
            self.max_body_size = ctx.options.max_body
        if "no_bodies" in updated:
            self.capture_bodies = not ctx.options.no_bodies
        if "exclude" in updated:
            exclude_str = ctx.options.exclude
            self.exclude_patterns = [
                re.compile(p.strip()) for p in exclude_str.split(",") if p.strip()
            ]
    
    def _should_capture(self, url: str, host: str) -> bool:
        """Check if this request should be captured."""
        # Domain filter
        if self.domains and host not in self.domains:
            # Check if host ends with any domain
            if not any(host.endswith(f".{d}") or host == d for d in self.domains):
                return False
        
        # Exclude patterns
        for pattern in self.exclude_patterns:
            if pattern.search(url):
                return False
        
        return True
    
    def _classify_resource(self, url: str, content_type: Optional[str]) -> str:
        """Classify resource type."""
        if content_type:
            ct = content_type.lower()
            if "javascript" in ct:
                return "script"
            if "css" in ct:
                return "stylesheet"
            if "html" in ct:
                return "document"
            if "json" in ct:
                return "json"
            if "xml" in ct:
                return "xml"
            if ct.startswith("image/"):
                return "image"
            if ct.startswith("font/") or "font" in ct:
                return "font"
            if ct.startswith("video/"):
                return "video"
            if ct.startswith("audio/"):
                return "audio"
        
        # URL-based classification
        path = urlparse(url).path.lower()
        if path.endswith((".js", ".mjs")):
            return "script"
        if path.endswith(".css"):
            return "stylesheet"
        if path.endswith((".html", ".htm")):
            return "document"
        if path.endswith(".json"):
            return "json"
        if path.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico")):
            return "image"
        if path.endswith((".woff", ".woff2", ".ttf", ".eot")):
            return "font"
        
        return "other"
    
    def _is_api_call(self, url: str, content_type: Optional[str]) -> bool:
        """Check if request is an API call."""
        if content_type and "json" in content_type.lower():
            return True
        
        for pattern in self.api_patterns:
            if pattern.search(url):
                return True
        
        return False
    
    def _get_body(self, content: bytes, content_type: Optional[str]) -> Optional[str]:
        """Extract body as string if appropriate."""
        if not self.capture_bodies:
            return None
        
        if len(content) > self.max_body_size:
            return f"[Body too large: {len(content)} bytes]"
        
        if not content:
            return None
        
        # Try to decode as text
        try:
            text = content.decode("utf-8")
            
            # Try to parse as JSON for prettier output
            if content_type and "json" in content_type.lower():
                try:
                    parsed = json.loads(text)
                    return json.dumps(parsed, indent=2, ensure_ascii=False)
                except json.JSONDecodeError:
                    pass
            
            return text
        except UnicodeDecodeError:
            return f"[Binary data: {len(content)} bytes]"
    
    def request(self, flow: http.HTTPFlow):
        """Handle request start."""
        url = flow.request.pretty_url
        host = flow.request.host
        
        if not self._should_capture(url, host):
            return
        
        # Track start time
        self.flow_start_times[flow.id] = time.time()
        
        self.seq += 1
        
        # Parse URL
        parsed = urlparse(url)
        
        # Get body
        request_body = self._get_body(
            flow.request.content or b"",
            flow.request.headers.get("Content-Type")
        )
        
        trace = RequestTrace(
            seq=self.seq,
            timestamp=time.time(),
            method=flow.request.method,
            url=url,
            host=host,
            path=parsed.path,
            query=parsed.query,
            request_headers=dict(flow.request.headers),
            request_body=request_body,
            request_size=len(flow.request.content or b""),
        )
        
        self.traces.append(trace)
        flow.trace_seq = self.seq  # Store for response matching
        
        ctx.log.info(f"[{self.seq}] {flow.request.method} {url}")
    
    def response(self, flow: http.HTTPFlow):
        """Handle response."""
        if not hasattr(flow, "trace_seq"):
            return
        
        # Find matching trace
        trace = next((t for t in self.traces if t.seq == flow.trace_seq), None)
        if not trace:
            return
        
        # Calculate duration
        start_time = self.flow_start_times.pop(flow.id, None)
        if start_time:
            trace.duration_ms = (time.time() - start_time) * 1000
        
        # Response data
        trace.status_code = flow.response.status_code
        trace.status_text = flow.response.reason
        trace.response_headers = dict(flow.response.headers)
        trace.response_size = len(flow.response.content or b"")
        
        # Content type and classification
        content_type = flow.response.headers.get("Content-Type", "")
        trace.content_type = content_type
        trace.resource_type = self._classify_resource(flow.request.pretty_url, content_type)
        trace.is_api = self._is_api_call(flow.request.pretty_url, content_type)
        
        # Response body
        trace.response_body = self._get_body(
            flow.response.content or b"",
            content_type
        )
        
        ctx.log.info(f"[{trace.seq}] <- {trace.status_code} ({trace.duration_ms:.0f}ms)")
    
    def error(self, flow: http.HTTPFlow):
        """Handle errors."""
        if not hasattr(flow, "trace_seq"):
            return
        
        trace = next((t for t in self.traces if t.seq == flow.trace_seq), None)
        if trace:
            trace.error = str(flow.error)
            ctx.log.error(f"[{trace.seq}] Error: {flow.error}")
    
    def websocket_message(self, flow: http.HTTPFlow):
        """Handle WebSocket messages."""
        if not flow.websocket:
            return
        
        msg = flow.websocket.messages[-1]
        
        self.ws_seq += 1
        
        ws_trace = WebSocketTrace(
            seq=self.ws_seq,
            timestamp=time.time(),
            url=flow.request.pretty_url,
            direction="send" if msg.from_client else "receive",
            message_type="text" if msg.is_text else "binary",
            message=msg.text if msg.is_text else f"[Binary: {len(msg.content)} bytes]",
            size=len(msg.content),
        )
        
        self.websocket_traces.append(ws_trace)
        ctx.log.info(f"[WS:{self.ws_seq}] {ws_trace.direction}: {len(msg.content)} bytes")
    
    def done(self):
        """Export traces when proxy stops."""
        self._export_traces()
    
    def _export_traces(self):
        """Export collected traces to file."""
        output = {
            "metadata": {
                "captured_at": datetime.now().isoformat(),
                "tracer": "network_proxy",
                "total_requests": len(self.traces),
                "total_websocket_messages": len(self.websocket_traces),
            },
            "requests": [asdict(t) for t in self.traces],
            "websocket": [asdict(t) for t in self.websocket_traces],
        }
        
        output_path = Path(self.output_file)
        output_path.write_text(json.dumps(output, indent=2, default=str))
        ctx.log.info(f"Exported {len(self.traces)} traces to {self.output_file}")


class NetworkAnalyzer:
    """Analyze network traces and generate insights."""
    
    @staticmethod
    def analyze(traces: List[Dict]) -> Dict[str, Any]:
        """Analyze request patterns."""
        analysis = {
            "total_requests": len(traces),
            "by_method": defaultdict(int),
            "by_status": defaultdict(int),
            "by_resource_type": defaultdict(int),
            "by_host": defaultdict(int),
            "api_calls": [],
            "slow_requests": [],  # > 1000ms
            "errors": [],
            "total_request_size": 0,
            "total_response_size": 0,
        }
        
        for trace in traces:
            analysis["by_method"][trace["method"]] += 1
            
            if trace.get("status_code"):
                analysis["by_status"][trace["status_code"]] += 1
            
            analysis["by_resource_type"][trace.get("resource_type", "other")] += 1
            analysis["by_host"][trace["host"]] += 1
            
            analysis["total_request_size"] += trace.get("request_size", 0)
            analysis["total_response_size"] += trace.get("response_size", 0)
            
            if trace.get("is_api"):
                analysis["api_calls"].append({
                    "seq": trace["seq"],
                    "method": trace["method"],
                    "url": trace["url"],
                    "status": trace.get("status_code"),
                    "duration_ms": trace.get("duration_ms"),
                })
            
            if trace.get("duration_ms") and trace["duration_ms"] > 1000:
                analysis["slow_requests"].append({
                    "seq": trace["seq"],
                    "url": trace["url"],
                    "duration_ms": trace["duration_ms"],
                })
            
            if trace.get("error") or (trace.get("status_code") and trace["status_code"] >= 400):
                analysis["errors"].append({
                    "seq": trace["seq"],
                    "url": trace["url"],
                    "status": trace.get("status_code"),
                    "error": trace.get("error"),
                })
        
        return dict(analysis)
    
    @staticmethod
    def to_call_graph(traces: List[Dict]) -> Dict[str, Any]:
        """Convert API calls to call graph format."""
        nodes = {}
        edges = []
        
        # Group by host + path pattern
        for trace in traces:
            if not trace.get("is_api"):
                continue
            
            # Create node ID from host + path
            parsed = urlparse(trace["url"])
            # Generalize path (replace IDs with :id)
            path = re.sub(r'/\d+', '/:id', parsed.path)
            node_id = f"{trace['method']} {parsed.netloc}{path}"
            
            if node_id not in nodes:
                nodes[node_id] = {
                    "id": node_id,
                    "method": trace["method"],
                    "host": parsed.netloc,
                    "path": path,
                    "call_count": 0,
                    "statuses": defaultdict(int),
                    "avg_duration_ms": 0,
                    "total_duration_ms": 0,
                }
            
            nodes[node_id]["call_count"] += 1
            nodes[node_id]["statuses"][trace.get("status_code", 0)] += 1
            if trace.get("duration_ms"):
                nodes[node_id]["total_duration_ms"] += trace["duration_ms"]
        
        # Calculate averages
        for node in nodes.values():
            if node["call_count"] > 0:
                node["avg_duration_ms"] = node["total_duration_ms"] / node["call_count"]
            node["statuses"] = dict(node["statuses"])
        
        # Infer edges from timing (sequential calls)
        sorted_traces = sorted(
            [t for t in traces if t.get("is_api")],
            key=lambda t: t["seq"]
        )
        
        prev_node_id = None
        for trace in sorted_traces:
            parsed = urlparse(trace["url"])
            path = re.sub(r'/\d+', '/:id', parsed.path)
            node_id = f"{trace['method']} {parsed.netloc}{path}"
            
            if prev_node_id and prev_node_id != node_id:
                # Find existing edge
                existing = next(
                    (e for e in edges if e["from"] == prev_node_id and e["to"] == node_id),
                    None
                )
                if existing:
                    existing["call_count"] += 1
                else:
                    edges.append({
                        "from": prev_node_id,
                        "to": node_id,
                        "call_count": 1,
                    })
            
            prev_node_id = node_id
        
        return {
            "metadata": {
                "type": "api_call_graph",
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
            "nodes": list(nodes.values()),
            "edges": edges,
        }
    
    @staticmethod
    def to_mermaid(call_graph: Dict) -> str:
        """Convert call graph to Mermaid diagram."""
        lines = ["flowchart LR"]
        
        node_ids = {}
        for i, node in enumerate(call_graph.get("nodes", [])):
            node_id = f"N{i}"
            node_ids[node["id"]] = node_id
            
            label = f"{node['method']} {node['path']}"
            count = node.get("call_count", 1)
            
            if count > 1:
                lines.append(f'    {node_id}["{label}<br/>({count}x, {node.get("avg_duration_ms", 0):.0f}ms)"]')
            else:
                lines.append(f'    {node_id}["{label}"]')
        
        for edge in call_graph.get("edges", []):
            from_id = node_ids.get(edge["from"])
            to_id = node_ids.get(edge["to"])
            if from_id and to_id:
                lines.append(f'    {from_id} --> {to_id}')
        
        return "\n".join(lines)


# Mitmproxy addon instance
addons = [NetworkTracer()]


# CLI for standalone analysis
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze network traces")
    parser.add_argument("input", help="Input trace JSON file")
    parser.add_argument("--format", choices=["analysis", "graph", "mermaid"],
                        default="analysis", help="Output format")
    parser.add_argument("--output", "-o", help="Output file")
    
    args = parser.parse_args()
    
    # Load traces
    with open(args.input) as f:
        data = json.load(f)
    
    traces = data.get("requests", [])
    
    if args.format == "analysis":
        result = NetworkAnalyzer.analyze(traces)
        output = json.dumps(result, indent=2)
    elif args.format == "graph":
        result = NetworkAnalyzer.to_call_graph(traces)
        output = json.dumps(result, indent=2)
    elif args.format == "mermaid":
        graph = NetworkAnalyzer.to_call_graph(traces)
        output = NetworkAnalyzer.to_mermaid(graph)
    
    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)
