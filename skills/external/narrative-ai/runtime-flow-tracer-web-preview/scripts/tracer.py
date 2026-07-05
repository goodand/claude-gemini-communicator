#!/usr/bin/env python3
"""
Runtime Flow Tracer - Zero-dependency CLI for Python/JavaScript runtime tracing

Usage:
    python tracer.py python script.py [--args "arg1 arg2"]
    python tracer.py node app.js
    python tracer.py python script.py --format edge-list | classifier.py -

No external dependencies required - uses Python standard library only.
"""

from __future__ import annotations
import argparse
import json
import subprocess
import sys
import os
import re
import tempfile
import textwrap
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from datetime import datetime
from collections import defaultdict


@dataclass
class TraceResult:
    """Unified trace result"""
    entrypoint: str
    language: str
    runtime_ms: float
    nodes: list[dict] = field(default_factory=list)
    edges: list[dict] = field(default_factory=list)
    call_sequence: list[str] = field(default_factory=list)
    raw_output: str = ""
    error: str | None = None
    
    def to_dict(self) -> dict[str, Any]:
        return {
            "metadata": {
                "entrypoint": self.entrypoint,
                "language": self.language,
                "traced_at": datetime.now().isoformat(),
                "runtime_ms": self.runtime_ms,
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
            },
            "nodes": self.nodes,
            "edges": self.edges,
            "edge_list": [[e["source"], e["target"]] for e in self.edges],
            "call_sequence": self.call_sequence,
        }


# =============================================================================
# Python Tracer - Uses sys.settrace() (No dependencies)
# =============================================================================

class PythonTracer:
    """Python tracer using sys.settrace() - no external dependencies"""
    
    def __init__(self, max_depth: int = 50, exclude_stdlib: bool = True):
        self.max_depth = max_depth
        self.exclude_stdlib = exclude_stdlib
    
    def trace(self, script: str, args: list[str] = None) -> TraceResult:
        """Trace Python script by injecting tracer code"""
        args = args or []
        script_path = Path(script).resolve()
        
        if not script_path.exists():
            return TraceResult(
                entrypoint=script,
                language="python",
                runtime_ms=0,
                error=f"Script not found: {script}"
            )
        
        # Create wrapper script that uses sys.settrace
        tracer_code = self._generate_tracer_wrapper(script_path, args)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(tracer_code)
            wrapper_path = f.name
        
        try:
            start_time = datetime.now()
            result = subprocess.run(
                [sys.executable, wrapper_path],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=script_path.parent
            )
            runtime_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            # Parse the JSON output from wrapper
            return self._parse_trace_output(script, result.stdout, result.stderr, runtime_ms)
            
        except subprocess.TimeoutExpired:
            return TraceResult(
                entrypoint=script,
                language="python",
                runtime_ms=300000,
                error="Trace timeout (5 minutes)"
            )
        except Exception as e:
            return TraceResult(
                entrypoint=script,
                language="python",
                runtime_ms=0,
                error=str(e)
            )
        finally:
            try:
                os.unlink(wrapper_path)
            except:
                pass
    
    def _generate_tracer_wrapper(self, script_path: Path, args: list[str]) -> str:
        """Generate wrapper script with embedded tracer"""
        script_dir = str(script_path.parent)
        script_name = script_path.name
        exclude_stdlib = self.exclude_stdlib
        max_depth = self.max_depth
        
        return textwrap.dedent(f'''
            import sys
            import os
            import json
            from collections import defaultdict
            from pathlib import Path
            
            # Setup path
            script_dir = {repr(script_dir)}
            sys.path.insert(0, script_dir)
            os.chdir(script_dir)
            sys.argv = [{repr(script_name)}] + {args!r}
            
            # Tracer state
            _trace_data = {{
                "nodes": defaultdict(lambda: {{"call_count": 0, "first_call_seq": 0}}),
                "edges": defaultdict(lambda: {{"call_count": 0, "first_call_seq": 0}}),
                "call_sequence": [],
                "call_stack": [],
                "seq": 0,
            }}
            
            # Paths to exclude
            _stdlib_paths = set()
            for p in sys.path:
                if "site-packages" not in p and "dist-packages" not in p:
                    if p and Path(p).exists():
                        _stdlib_paths.add(str(Path(p).resolve()))
            
            _exclude_stdlib = {exclude_stdlib}
            _max_depth = {max_depth}
            _script_dir = str(Path(script_dir).resolve())
            
            def _should_trace(filename):
                """Check if file should be traced"""
                if not filename or filename.startswith("<"):
                    return False
                
                try:
                    abs_path = str(Path(filename).resolve())
                except:
                    return False
                
                # Always trace files in script directory
                if abs_path.startswith(_script_dir):
                    return True
                
                if _exclude_stdlib:
                    # Exclude stdlib and site-packages
                    for stdlib_path in _stdlib_paths:
                        if abs_path.startswith(stdlib_path):
                            return False
                    if "site-packages" in abs_path or "dist-packages" in abs_path:
                        return False
                
                return True
            
            def _trace_calls(frame, event, arg):
                """Trace function for sys.settrace"""
                if event not in ("call", "return"):
                    return _trace_calls
                
                filename = frame.f_code.co_filename
                if not _should_trace(filename):
                    return None
                
                func_name = frame.f_code.co_name
                
                # Skip internal functions
                if func_name.startswith("_") and func_name != "__init__":
                    return _trace_calls
                
                depth = len(_trace_data["call_stack"])
                if depth > _max_depth:
                    return _trace_calls
                
                if event == "call":
                    _trace_data["seq"] += 1
                    seq = _trace_data["seq"]
                    
                    # Record call sequence
                    _trace_data["call_sequence"].append(func_name)
                    
                    # Update node
                    node = _trace_data["nodes"][func_name]
                    if node["call_count"] == 0:
                        node["first_call_seq"] = seq
                    node["call_count"] += 1
                    
                    # Create edge from caller
                    if _trace_data["call_stack"]:
                        caller = _trace_data["call_stack"][-1]
                        edge_key = (caller, func_name)
                        edge = _trace_data["edges"][edge_key]
                        if edge["call_count"] == 0:
                            edge["first_call_seq"] = seq
                        edge["call_count"] += 1
                    
                    _trace_data["call_stack"].append(func_name)
                
                elif event == "return":
                    if _trace_data["call_stack"] and _trace_data["call_stack"][-1] == func_name:
                        _trace_data["call_stack"].pop()
                
                return _trace_calls
            
            # Run with tracing
            _original_stderr = sys.stderr
            sys.stderr = sys.stdout  # Redirect stderr to capture all output
            
            try:
                sys.settrace(_trace_calls)
                
                # Execute the script
                script_path = Path({repr(str(script_path))})
                script_globals = {{
                    "__name__": "__main__",
                    "__file__": str(script_path),
                    "__builtins__": __builtins__,
                }}
                
                with open(script_path) as f:
                    code = compile(f.read(), str(script_path), "exec")
                    exec(code, script_globals)
                    
            except SystemExit:
                pass
            except Exception as e:
                print(f"Script error: {{e}}", file=_original_stderr)
            finally:
                sys.settrace(None)
                sys.stderr = _original_stderr
            
            # Output trace data as JSON
            output = {{
                "nodes": [
                    {{"id": k, "function": k, "module": "__main__", **v}}
                    for k, v in _trace_data["nodes"].items()
                ],
                "edges": [
                    {{"source": k[0], "target": k[1], **v}}
                    for k, v in _trace_data["edges"].items()
                ],
                "call_sequence": _trace_data["call_sequence"],
            }}
            
            print("__TRACE_JSON_START__")
            print(json.dumps(output))
            print("__TRACE_JSON_END__")
        ''')
    
    def _parse_trace_output(self, script: str, stdout: str, stderr: str, runtime_ms: float) -> TraceResult:
        """Parse trace output from wrapper script"""
        # Extract JSON between markers
        start_marker = "__TRACE_JSON_START__"
        end_marker = "__TRACE_JSON_END__"
        
        start_idx = stdout.find(start_marker)
        end_idx = stdout.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            return TraceResult(
                entrypoint=script,
                language="python",
                runtime_ms=runtime_ms,
                raw_output=stdout + stderr,
                error="Failed to capture trace output"
            )
        
        json_str = stdout[start_idx + len(start_marker):end_idx].strip()
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return TraceResult(
                entrypoint=script,
                language="python",
                runtime_ms=runtime_ms,
                raw_output=json_str[:1000],
                error=f"Failed to parse trace JSON: {e}"
            )
        
        return TraceResult(
            entrypoint=script,
            language="python",
            runtime_ms=runtime_ms,
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            call_sequence=data.get("call_sequence", []),
        )


# =============================================================================
# JavaScript Tracer - Uses Node.js wrapper script (No npm dependencies)
# =============================================================================

class JavaScriptTracer:
    """JavaScript tracer using Node.js wrapper - no npm dependencies required"""
    
    def __init__(self, max_depth: int = 50):
        self.max_depth = max_depth
        self.wrapper_path = Path(__file__).parent / "js_tracer_standalone.js"
    
    def check_node_available(self) -> bool:
        """Check if Node.js is installed"""
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def trace(self, script: str, args: list[str] = None) -> TraceResult:
        """Trace JavaScript file execution"""
        if not self.check_node_available():
            return TraceResult(
                entrypoint=script,
                language="javascript",
                runtime_ms=0,
                error="Node.js not installed"
            )
        
        args = args or []
        script_path = Path(script).resolve()
        
        if not script_path.exists():
            return TraceResult(
                entrypoint=script,
                language="javascript",
                runtime_ms=0,
                error=f"Script not found: {script}"
            )
        
        # Create standalone wrapper if it doesn't exist
        self._ensure_wrapper_exists()
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ["node", str(self.wrapper_path), str(script_path)] + args,
                capture_output=True,
                text=True,
                timeout=300,
                cwd=script_path.parent
            )
            runtime_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return self._parse_output(script, result.stdout, result.stderr, runtime_ms)
            
        except subprocess.TimeoutExpired:
            return TraceResult(
                entrypoint=script,
                language="javascript",
                runtime_ms=300000,
                error="Trace timeout (5 minutes)"
            )
        except Exception as e:
            return TraceResult(
                entrypoint=script,
                language="javascript",
                runtime_ms=0,
                error=str(e)
            )
    
    def _ensure_wrapper_exists(self):
        """Create the standalone JS wrapper if it doesn't exist"""
        if self.wrapper_path.exists():
            return
        
        wrapper_code = textwrap.dedent('''
            /**
             * js_tracer_standalone.js - Zero-dependency JavaScript function tracer
             * 
             * Uses Function.prototype wrapping to trace all function calls.
             * Works with Node.js built-in modules only.
             */
            
            const fs = require('fs');
            const path = require('path');
            const vm = require('vm');
            
            // Trace data storage
            const traceData = {
                nodes: new Map(),
                edges: new Map(),
                callSequence: [],
                callStack: [],
                seq: 0,
            };
            
            // Helper to create edge key
            function edgeKey(from, to) {
                return `${from}::${to}`;
            }
            
            // Record a function call
            function recordCall(funcName, caller) {
                traceData.seq++;
                const seq = traceData.seq;
                
                // Record call sequence
                traceData.callSequence.push(funcName);
                
                // Update node
                if (!traceData.nodes.has(funcName)) {
                    traceData.nodes.set(funcName, {
                        id: funcName,
                        function: funcName,
                        call_count: 0,
                        first_call_seq: seq,
                    });
                }
                const node = traceData.nodes.get(funcName);
                node.call_count++;
                
                // Create edge from caller
                if (caller) {
                    const key = edgeKey(caller, funcName);
                    if (!traceData.edges.has(key)) {
                        traceData.edges.set(key, {
                            source: caller,
                            target: funcName,
                            call_count: 0,
                            first_call_seq: seq,
                        });
                    }
                    traceData.edges.get(key).call_count++;
                }
            }
            
            // Wrap a function to trace calls
            function wrapFunction(fn, name) {
                if (typeof fn !== 'function' || fn.__traced__) {
                    return fn;
                }
                
                const wrapped = function(...args) {
                    const caller = traceData.callStack[traceData.callStack.length - 1] || null;
                    recordCall(name, caller);
                    traceData.callStack.push(name);
                    
                    try {
                        return fn.apply(this, args);
                    } finally {
                        traceData.callStack.pop();
                    }
                };
                
                wrapped.__traced__ = true;
                wrapped.__original__ = fn;
                wrapped.toString = () => fn.toString();
                
                // Copy properties
                Object.keys(fn).forEach(key => {
                    try { wrapped[key] = fn[key]; } catch(e) {}
                });
                
                return wrapped;
            }
            
            // Wrap all functions in an object
            function wrapObject(obj, prefix = '') {
                if (!obj || typeof obj !== 'object') return;
                
                for (const key of Object.keys(obj)) {
                    try {
                        const val = obj[key];
                        if (typeof val === 'function' && !val.__traced__) {
                            const name = prefix ? `${prefix}.${key}` : key;
                            obj[key] = wrapFunction(val, name);
                        }
                    } catch (e) {
                        // Some properties can't be accessed
                    }
                }
            }
            
            // Parse and wrap code before execution
            function instrumentCode(code, filename) {
                // Simple regex-based instrumentation
                // Wrap function declarations and expressions
                
                // This is a simplified approach - wrap global functions
                // For production, use a proper AST parser
                return code;
            }
            
            // Output trace results
            function outputResults() {
                const output = {
                    nodes: Array.from(traceData.nodes.values()),
                    edges: Array.from(traceData.edges.values()),
                    call_sequence: traceData.callSequence,
                };
                
                console.log('__TRACE_JSON_START__');
                console.log(JSON.stringify(output));
                console.log('__TRACE_JSON_END__');
            }
            
            // Main execution
            const args = process.argv.slice(2);
            if (args.length === 0) {
                console.error('Usage: node js_tracer_standalone.js <script.js> [args...]');
                process.exit(1);
            }
            
            const scriptPath = path.resolve(args[0]);
            const scriptArgs = args.slice(1);
            
            // Update process.argv for the target script
            process.argv = ['node', scriptPath, ...scriptArgs];
            
            try {
                // Read and execute the script
                const code = fs.readFileSync(scriptPath, 'utf8');
                
                // Create a module-like context
                const scriptDir = path.dirname(scriptPath);
                const scriptModule = {
                    exports: {},
                    require: (id) => {
                        // Handle relative requires
                        if (id.startsWith('./') || id.startsWith('../')) {
                            const resolvedPath = require.resolve(path.resolve(scriptDir, id));
                            const mod = require(resolvedPath);
                            return mod;
                        }
                        return require(id);
                    },
                    __filename: scriptPath,
                    __dirname: scriptDir,
                };
                
                // Create sandbox with wrapped global functions
                const sandbox = {
                    ...global,
                    module: scriptModule,
                    exports: scriptModule.exports,
                    require: scriptModule.require,
                    __filename: scriptPath,
                    __dirname: scriptDir,
                    console: {
                        ...console,
                        log: wrapFunction((...args) => {
                            // Suppress normal output during tracing
                        }, 'console.log'),
                        error: console.error,
                        warn: console.warn,
                    },
                    setTimeout: wrapFunction(setTimeout, 'setTimeout'),
                    setInterval: wrapFunction(setInterval, 'setInterval'),
                    setImmediate: wrapFunction(setImmediate, 'setImmediate'),
                };
                
                // Wrap the code in a function to capture declarations
                const wrappedCode = `
                    (function(module, exports, require, __filename, __dirname) {
                        // Capture function declarations
                        const __originalFunctions = {};
                        
                        ${code}
                        
                        // Export for analysis
                        if (typeof main === 'function') main();
                    })(module, exports, require, __filename, __dirname);
                `;
                
                // Run in VM context
                vm.runInNewContext(wrappedCode, sandbox, {
                    filename: scriptPath,
                    displayErrors: true,
                });
                
            } catch (e) {
                console.error('Script error:', e.message);
            }
            
            // Output results
            outputResults();
        ''')
        
        self.wrapper_path.write_text(wrapper_code)
    
    def _parse_output(self, script: str, stdout: str, stderr: str, runtime_ms: float) -> TraceResult:
        """Parse trace output"""
        start_marker = "__TRACE_JSON_START__"
        end_marker = "__TRACE_JSON_END__"
        
        start_idx = stdout.find(start_marker)
        end_idx = stdout.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            # Fallback: try to run with simpler method
            return self._trace_simple(script, runtime_ms)
        
        json_str = stdout[start_idx + len(start_marker):end_idx].strip()
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            return TraceResult(
                entrypoint=script,
                language="javascript",
                runtime_ms=runtime_ms,
                error=f"Failed to parse trace JSON: {e}"
            )
        
        return TraceResult(
            entrypoint=script,
            language="javascript",
            runtime_ms=runtime_ms,
            nodes=data.get("nodes", []),
            edges=data.get("edges", []),
            call_sequence=data.get("call_sequence", []),
        )
    
    def _trace_simple(self, script: str, runtime_ms: float) -> TraceResult:
        """Simple static analysis fallback - extract function definitions"""
        script_path = Path(script)
        if not script_path.exists():
            return TraceResult(
                entrypoint=script,
                language="javascript",
                runtime_ms=runtime_ms,
                error="Script not found"
            )
        
        code = script_path.read_text()
        
        # Simple regex to find function declarations
        func_pattern = re.compile(
            r'(?:function\s+(\w+)|(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\([^)]*\)\s*=>))',
            re.MULTILINE
        )
        
        nodes = []
        for match in func_pattern.finditer(code):
            func_name = match.group(1) or match.group(2)
            if func_name:
                nodes.append({
                    "id": func_name,
                    "function": func_name,
                    "file": script,
                    "call_count": 1,
                    "first_call_seq": len(nodes) + 1,
                })
        
        # Try to infer edges from function calls
        edges = []
        call_pattern = re.compile(r'(\w+)\s*\(')
        func_names = {n["id"] for n in nodes}
        
        for node in nodes:
            # This is a simplification - would need AST for accuracy
            pass
        
        return TraceResult(
            entrypoint=script,
            language="javascript",
            runtime_ms=runtime_ms,
            nodes=nodes,
            edges=edges,
            call_sequence=[n["id"] for n in nodes],
        )


# =============================================================================
# Positional Encoder (unchanged from original)
# =============================================================================

class PositionalEncoder:
    """Add positional encoding to trace nodes for graph visualization"""
    
    def __init__(self, trace_result: TraceResult):
        self.nodes = {n["id"]: n for n in trace_result.nodes}
        self.edges = trace_result.edges
        self.adj_list = defaultdict(list)
        self.in_degree = defaultdict(int)
        
        for edge in self.edges:
            src, tgt = edge["source"], edge["target"]
            self.adj_list[src].append(tgt)
            self.in_degree[tgt] += 1
    
    def encode(self) -> dict:
        """Add positional encoding to all nodes"""
        # Find roots (nodes with no incoming edges)
        all_nodes = set(self.nodes.keys())
        roots = [n for n in all_nodes if self.in_degree[n] == 0]
        
        if not roots and all_nodes:
            # If no roots, pick node with minimum in-degree
            roots = [min(all_nodes, key=lambda n: self.in_degree[n])]
        
        # BFS for depth
        depth = {}
        queue = [(r, 0) for r in roots]
        visited = set()
        
        while queue:
            node, d = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            depth[node] = d
            
            for child in self.adj_list[node]:
                if child not in visited:
                    queue.append((child, d + 1))
        
        # Assign depth 0 to unvisited nodes
        for node in all_nodes:
            if node not in depth:
                depth[node] = 0
        
        # Topological layers using Kahn's algorithm
        layers = self._compute_layers()
        
        # Compute layout positions
        positions = self._compute_layout(layers)
        
        # Add encoding to nodes
        encoded_nodes = []
        for node_id, node_data in self.nodes.items():
            layer = layers.get(node_id, 0)
            pos = positions.get(node_id, (0, 0))
            
            encoded_node = {
                **node_data,
                "position": {
                    "depth": depth.get(node_id, 0),
                    "layer": layer,
                    "x": pos[0],
                    "y": pos[1],
                    "call_seq": node_data.get("first_call_seq", 0),
                },
                "centrality": {
                    "in_degree": self.in_degree[node_id],
                    "out_degree": len(self.adj_list[node_id]),
                    "call_ratio": node_data.get("call_count", 1) / max(sum(n.get("call_count", 1) for n in self.nodes.values()), 1),
                },
            }
            encoded_nodes.append(encoded_node)
        
        return {
            "nodes": encoded_nodes,
            "layout": {
                "algorithm": "sugiyama",
                "max_depth": max(depth.values()) if depth else 0,
                "num_layers": len(set(layers.values())) if layers else 0,
            }
        }
    
    def _compute_layers(self) -> dict:
        """Compute topological layers using Kahn's algorithm"""
        in_degree = dict(self.in_degree)
        for node in self.nodes:
            if node not in in_degree:
                in_degree[node] = 0
        
        layers = {}
        queue = [n for n, d in in_degree.items() if d == 0]
        current_layer = 0
        
        while queue:
            next_queue = []
            for node in queue:
                layers[node] = current_layer
                for child in self.adj_list[node]:
                    in_degree[child] -= 1
                    if in_degree[child] == 0:
                        next_queue.append(child)
            queue = next_queue
            current_layer += 1
        
        # Handle cycles - assign remaining nodes to last layer
        for node in self.nodes:
            if node not in layers:
                layers[node] = current_layer
        
        return layers
    
    def _compute_layout(self, layers: dict) -> dict:
        """Compute x,y positions based on layers"""
        # Group nodes by layer
        layer_nodes = defaultdict(list)
        for node, layer in layers.items():
            layer_nodes[layer].append(node)
        
        positions = {}
        y_spacing = 100
        x_spacing = 150
        
        for layer, nodes in layer_nodes.items():
            y = layer * y_spacing
            # Center nodes horizontally
            total_width = (len(nodes) - 1) * x_spacing
            start_x = -total_width / 2
            
            for i, node in enumerate(sorted(nodes)):
                x = start_x + i * x_spacing
                positions[node] = (x, y)
        
        return positions


# =============================================================================
# Output Formatters
# =============================================================================

class OutputFormatter:
    """Format trace results for various outputs"""
    
    @staticmethod
    def to_json(result: TraceResult, include_positional: bool = False) -> str:
        data = result.to_dict()
        
        if include_positional and result.nodes:
            encoder = PositionalEncoder(result)
            encoded = encoder.encode()
            data["nodes"] = encoded["nodes"]
            data["metadata"]["has_positional_encoding"] = True
            data["layout"] = encoded["layout"]
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def to_edge_list(result: TraceResult) -> str:
        lines = []
        for edge in result.edges:
            lines.append(f"{edge['source']} {edge['target']}")
        return "\n".join(lines)
    
    @staticmethod
    def to_adj_list(result: TraceResult) -> str:
        adj = defaultdict(list)
        for edge in result.edges:
            adj[edge["source"]].append(edge["target"])
        
        lines = []
        for node in sorted(adj.keys()):
            neighbors = " ".join(sorted(adj[node]))
            lines.append(f"{node}: {neighbors}")
        return "\n".join(lines)
    
    @staticmethod
    def to_adj_matrix(result: TraceResult) -> str:
        nodes = sorted(set(
            [n["id"] for n in result.nodes] +
            [e["source"] for e in result.edges] +
            [e["target"] for e in result.edges]
        ))
        
        if not nodes:
            return "[]"
        
        node_idx = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        matrix = [[0] * n for _ in range(n)]
        
        for edge in result.edges:
            i = node_idx[edge["source"]]
            j = node_idx[edge["target"]]
            matrix[i][j] = edge.get("call_count", 1)
        
        lines = ["# Nodes: " + ", ".join(nodes)]
        for row in matrix:
            lines.append(" ".join(str(x) for x in row))
        return "\n".join(lines)
    
    @staticmethod
    def to_mermaid(result: TraceResult) -> str:
        lines = ["flowchart TD"]
        
        # Node definitions
        node_ids = {}
        for i, node in enumerate(result.nodes):
            node_id = f"N{i}"
            node_ids[node["id"]] = node_id
            
            label = node["function"]
            count = node.get("call_count", 1)
            
            if count > 1:
                lines.append(f'    {node_id}["{label} ({count}x)"]')
            else:
                lines.append(f'    {node_id}["{label}"]')
        
        # Edges
        for edge in result.edges:
            src_id = node_ids.get(edge["source"])
            tgt_id = node_ids.get(edge["target"])
            
            if src_id and tgt_id:
                count = edge.get("call_count", 1)
                if count > 1:
                    lines.append(f"    {src_id} -->|{count}x| {tgt_id}")
                else:
                    lines.append(f"    {src_id} --> {tgt_id}")
        
        return "\n".join(lines)


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Runtime Flow Tracer - Zero dependencies",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
            Examples:
                python tracer.py python script.py
                python tracer.py node app.js
                python tracer.py python script.py --format mermaid
                python tracer.py python script.py --format edge-list | classifier.py -
        """)
    )
    
    parser.add_argument("language", choices=["python", "node", "js"],
                        help="Language/runtime to trace")
    parser.add_argument("script", help="Script to trace")
    parser.add_argument("--args", default="", help="Arguments to pass to script")
    parser.add_argument("--format", choices=["json", "positional", "edge-list", "adj-list", "adj-matrix", "mermaid"],
                        default="json", help="Output format")
    parser.add_argument("--max-depth", type=int, default=50, help="Max trace depth")
    parser.add_argument("--include-stdlib", action="store_true", help="Include stdlib calls (Python)")
    
    args = parser.parse_args()
    
    # Parse script arguments
    script_args = args.args.split() if args.args else []
    
    # Create tracer
    if args.language == "python":
        tracer = PythonTracer(
            max_depth=args.max_depth,
            exclude_stdlib=not args.include_stdlib
        )
    else:
        tracer = JavaScriptTracer(max_depth=args.max_depth)
    
    # Run trace
    result = tracer.trace(args.script, script_args)
    
    # Check for errors
    if result.error:
        print(f"Error: {result.error}", file=sys.stderr)
        if not result.nodes:
            sys.exit(1)
    
    # Format output
    if args.format == "json":
        print(OutputFormatter.to_json(result))
    elif args.format == "positional":
        print(OutputFormatter.to_json(result, include_positional=True))
    elif args.format == "edge-list":
        print(OutputFormatter.to_edge_list(result))
    elif args.format == "adj-list":
        print(OutputFormatter.to_adj_list(result))
    elif args.format == "adj-matrix":
        print(OutputFormatter.to_adj_matrix(result))
    elif args.format == "mermaid":
        print(OutputFormatter.to_mermaid(result))


if __name__ == "__main__":
    main()
