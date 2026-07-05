#!/usr/bin/env python3
"""
web_tracer.py - Playwright-based browser tracer

Traces web application execution by:
1. Launching browser via Playwright
2. Injecting JS tracer (web_injector.js) 
3. Capturing function calls, events, network, DOM mutations
4. Exporting structured trace data

Usage:
    python web_tracer.py <url> [options]
    
Examples:
    # Basic trace
    python web_tracer.py https://example.com
    
    # Interactive mode (keep browser open)
    python web_tracer.py https://example.com --interactive
    
    # With proxy for full network capture
    python web_tracer.py https://example.com --proxy localhost:8080
    
    # Trace specific actions
    python web_tracer.py https://example.com --actions click:#button,wait:2000,scroll:500
"""

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

try:
    from playwright.async_api import async_playwright, Browser, Page, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: playwright not installed. Run: pip install playwright && playwright install chromium")


class WebTracer:
    """Browser-based tracer using Playwright and injected JS."""
    
    def __init__(
        self,
        headless: bool = True,
        proxy: Optional[str] = None,
        timeout: int = 30000,
        user_agent: Optional[str] = None,
    ):
        self.headless = headless
        self.proxy = proxy
        self.timeout = timeout
        self.user_agent = user_agent
        
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
        # Load injector script
        self.injector_path = Path(__file__).parent / "web_injector.js"
        if self.injector_path.exists():
            self.injector_script = self.injector_path.read_text()
        else:
            raise FileNotFoundError(f"Injector script not found: {self.injector_path}")
        
        # Collected data
        self.console_logs: List[Dict] = []
        self.network_requests: List[Dict] = []
        self.page_errors: List[Dict] = []
    
    async def start(self) -> None:
        """Start browser and create page."""
        self.playwright = await async_playwright().start()
        
        launch_options = {
            "headless": self.headless,
        }
        
        if self.proxy:
            launch_options["proxy"] = {"server": self.proxy}
        
        self.browser = await self.playwright.chromium.launch(**launch_options)
        
        context_options = {}
        if self.user_agent:
            context_options["user_agent"] = self.user_agent
        
        self.context = await self.browser.new_context(**context_options)
        self.page = await self.context.new_page()
        
        # Inject tracer script on every page/frame
        await self.context.add_init_script(self.injector_script)
        
        # Set up event listeners
        self._setup_listeners()
    
    def _setup_listeners(self) -> None:
        """Set up page event listeners for additional data capture."""
        
        # Console logs
        self.page.on("console", lambda msg: self.console_logs.append({
            "ts": time.time(),
            "type": msg.type,
            "text": msg.text,
            "location": str(msg.location) if msg.location else None,
        }))
        
        # Page errors
        self.page.on("pageerror", lambda error: self.page_errors.append({
            "ts": time.time(),
            "message": str(error),
        }))
        
        # Network requests (Playwright level)
        self.page.on("request", lambda req: self.network_requests.append({
            "ts": time.time(),
            "type": "request",
            "method": req.method,
            "url": req.url,
            "resource_type": req.resource_type,
            "headers": dict(req.headers) if req.headers else {},
        }))
        
        self.page.on("response", lambda res: self._handle_response(res))
    
    def _handle_response(self, response) -> None:
        """Handle response event."""
        # Find matching request
        for req in reversed(self.network_requests):
            if req.get("url") == response.url and req.get("type") == "request":
                req["status"] = response.status
                req["status_text"] = response.status_text
                break
    
    async def navigate(self, url: str, wait_until: str = "commit") -> None:
        """Navigate to URL and wait for page load."""
        try:
            await self.page.goto(url, wait_until=wait_until, timeout=self.timeout)
        except Exception as e:
            # Fallback to domcontentloaded on network errors
            if "net::" in str(e):
                try:
                    await self.page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
                except:
                    pass
    
    async def execute_actions(self, actions: List[str]) -> None:
        """Execute a list of actions on the page.
        
        Actions format:
        - click:<selector>
        - type:<selector>:<text>
        - wait:<ms>
        - scroll:<pixels>
        - screenshot:<filename>
        - evaluate:<js_code>
        """
        for action in actions:
            parts = action.split(":", 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            
            if cmd == "click":
                await self.page.click(arg)
            elif cmd == "type":
                selector, text = arg.split(":", 1)
                await self.page.type(selector, text)
            elif cmd == "wait":
                await asyncio.sleep(int(arg) / 1000)
            elif cmd == "scroll":
                await self.page.evaluate(f"window.scrollBy(0, {arg})")
            elif cmd == "screenshot":
                await self.page.screenshot(path=arg or "screenshot.png")
            elif cmd == "evaluate":
                await self.page.evaluate(arg)
            elif cmd == "hover":
                await self.page.hover(arg)
            elif cmd == "fill":
                selector, text = arg.split(":", 1)
                await self.page.fill(selector, text)
            else:
                print(f"Unknown action: {cmd}", file=sys.stderr)
    
    async def get_trace_data(self) -> Dict[str, Any]:
        """Extract trace data from injected JS tracer."""
        try:
            js_traces = await self.page.evaluate("window.__getTraceData__()")
        except Exception as e:
            js_traces = {
                "metadata": {"error": str(e)},
                "traces": {}
            }
        
        return {
            "metadata": {
                "url": self.page.url,
                "title": await self.page.title(),
                "traced_at": datetime.now().isoformat(),
                "tracer": "web_tracer",
            },
            "js_traces": js_traces,
            "console_logs": self.console_logs,
            "network_requests": self.network_requests,
            "page_errors": self.page_errors,
        }
    
    async def wait_for_user(self) -> None:
        """Wait for user to interact (interactive mode)."""
        print("\n[Interactive Mode] Browser is open. Press Enter to capture traces and exit...")
        await asyncio.get_event_loop().run_in_executor(None, input)
    
    async def close(self) -> None:
        """Clean up resources."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


class TraceConverter:
    """Convert raw web trace data to unified format compatible with tracer.py."""
    
    @staticmethod
    def to_unified_format(trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert web trace to unified tracer.py format."""
        nodes = {}
        edges = []
        call_seq = 0
        
        js_traces = trace_data.get("js_traces", {}).get("traces", {})
        
        # Process function calls
        for call in js_traces.get("calls", []):
            fn_name = call.get("fn", "unknown")
            
            if fn_name not in nodes:
                nodes[fn_name] = {
                    "id": fn_name,
                    "function": fn_name,
                    "context": call.get("context", "global"),
                    "call_count": 0,
                    "first_call_seq": call.get("seq", 0),
                }
            
            nodes[fn_name]["call_count"] += 1
            
            # Create edge from caller
            caller = call.get("caller")
            if caller:
                if caller not in nodes:
                    nodes[caller] = {
                        "id": caller,
                        "function": caller,
                        "context": "unknown",
                        "call_count": 0,
                        "first_call_seq": 0,
                    }
                
                edge_key = f"{caller}->{fn_name}"
                existing = next((e for e in edges if e["from"] == caller and e["to"] == fn_name), None)
                if existing:
                    existing["call_count"] += 1
                else:
                    edges.append({
                        "from": caller,
                        "to": fn_name,
                        "call_count": 1,
                    })
        
        # Process events as nodes
        for event in js_traces.get("events", []):
            event_name = f"[Event:{event.get('type', 'unknown')}]"
            if event_name not in nodes:
                nodes[event_name] = {
                    "id": event_name,
                    "function": event_name,
                    "context": "event",
                    "call_count": 0,
                    "first_call_seq": event.get("seq", 0),
                    "is_event": True,
                }
            nodes[event_name]["call_count"] += 1
        
        # Process network requests as nodes
        for req in js_traces.get("network", []):
            req_name = f"[{req.get('type', 'http').upper()}:{req.get('method', 'GET')}]"
            if req_name not in nodes:
                nodes[req_name] = {
                    "id": req_name,
                    "function": req_name,
                    "context": "network",
                    "call_count": 0,
                    "first_call_seq": req.get("seq", 0),
                    "is_network": True,
                }
            nodes[req_name]["call_count"] += 1
        
        return {
            "metadata": {
                "entrypoint": trace_data.get("metadata", {}).get("url", "unknown"),
                "language": "javascript",
                "environment": "browser",
                "traced_at": trace_data.get("metadata", {}).get("traced_at"),
                "node_count": len(nodes),
                "edge_count": len(edges),
            },
            "nodes": list(nodes.values()),
            "edges": edges,
            "raw": {
                "console_logs": trace_data.get("console_logs", []),
                "page_errors": trace_data.get("page_errors", []),
                "network_requests": trace_data.get("network_requests", []),
                "js_traces": js_traces,
            }
        }
    
    @staticmethod
    def to_mermaid(unified_data: Dict[str, Any]) -> str:
        """Convert unified format to Mermaid flowchart."""
        lines = ["flowchart TD"]
        
        # Create node definitions
        node_ids = {}
        for i, node in enumerate(unified_data.get("nodes", [])):
            node_id = f"N{i}"
            node_ids[node["id"]] = node_id
            
            label = node["function"]
            count = node.get("call_count", 1)
            
            # Different shapes for different types
            if node.get("is_event"):
                lines.append(f'    {node_id}{{{{{label}}}}}')  # Hexagon
            elif node.get("is_network"):
                lines.append(f'    {node_id}[/{label}/]')  # Parallelogram
            else:
                if count > 1:
                    lines.append(f'    {node_id}["{label} ({count}x)"]')
                else:
                    lines.append(f'    {node_id}["{label}"]')
        
        # Create edges
        for edge in unified_data.get("edges", []):
            from_id = node_ids.get(edge["from"])
            to_id = node_ids.get(edge["to"])
            if from_id and to_id:
                count = edge.get("call_count", 1)
                if count > 1:
                    lines.append(f'    {from_id} -->|{count}x| {to_id}')
                else:
                    lines.append(f'    {from_id} --> {to_id}')
        
        return "\n".join(lines)
    
    @staticmethod
    def to_edge_list(unified_data: Dict[str, Any]) -> str:
        """Convert to edge list format for classifier."""
        lines = []
        for edge in unified_data.get("edges", []):
            lines.append(f"{edge['from']} {edge['to']}")
        return "\n".join(lines)


async def main():
    if not PLAYWRIGHT_AVAILABLE:
        print("Error: playwright is required. Install with: pip install playwright && playwright install chromium")
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Trace web application execution using Playwright",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python web_tracer.py https://example.com
    python web_tracer.py https://example.com --interactive --no-headless
    python web_tracer.py https://example.com --actions "click:#btn,wait:1000"
    python web_tracer.py https://example.com --format mermaid > trace.mmd
        """
    )
    
    parser.add_argument("url", help="URL to trace")
    parser.add_argument("--headless", dest="headless", action="store_true", default=True,
                        help="Run browser in headless mode (default)")
    parser.add_argument("--no-headless", dest="headless", action="store_false",
                        help="Run browser with visible window")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Interactive mode - keep browser open until Enter pressed")
    parser.add_argument("--proxy", help="Proxy server (e.g., localhost:8080)")
    parser.add_argument("--timeout", type=int, default=30000,
                        help="Navigation timeout in ms (default: 30000)")
    parser.add_argument("--actions", help="Actions to execute (comma-separated)")
    parser.add_argument("--format", choices=["json", "unified", "mermaid", "edge-list"],
                        default="unified", help="Output format (default: unified)")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--wait", type=int, default=0,
                        help="Wait time in ms after page load before capturing")
    
    args = parser.parse_args()
    
    # Create tracer
    tracer = WebTracer(
        headless=args.headless and not args.interactive,
        proxy=args.proxy,
        timeout=args.timeout,
    )
    
    try:
        await tracer.start()
        
        # Navigate to URL
        print(f"[*] Navigating to {args.url}...", file=sys.stderr)
        await tracer.navigate(args.url)
        
        # Execute actions if provided
        if args.actions:
            actions = [a.strip() for a in args.actions.split(",")]
            print(f"[*] Executing {len(actions)} actions...", file=sys.stderr)
            await tracer.execute_actions(actions)
        
        # Wait if specified
        if args.wait > 0:
            print(f"[*] Waiting {args.wait}ms...", file=sys.stderr)
            await asyncio.sleep(args.wait / 1000)
        
        # Interactive mode
        if args.interactive:
            await tracer.wait_for_user()
        
        # Get trace data
        print("[*] Capturing traces...", file=sys.stderr)
        raw_data = await tracer.get_trace_data()
        
        # Convert to output format
        if args.format == "json":
            output = json.dumps(raw_data, indent=2, default=str)
        elif args.format == "unified":
            unified = TraceConverter.to_unified_format(raw_data)
            output = json.dumps(unified, indent=2)
        elif args.format == "mermaid":
            unified = TraceConverter.to_unified_format(raw_data)
            output = TraceConverter.to_mermaid(unified)
        elif args.format == "edge-list":
            unified = TraceConverter.to_unified_format(raw_data)
            output = TraceConverter.to_edge_list(unified)
        
        # Write output
        if args.output:
            Path(args.output).write_text(output)
            print(f"[*] Output written to {args.output}", file=sys.stderr)
        else:
            print(output)
        
    finally:
        await tracer.close()


if __name__ == "__main__":
    asyncio.run(main())
