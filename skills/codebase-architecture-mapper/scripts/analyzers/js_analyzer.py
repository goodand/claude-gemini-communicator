"""
JavaScript/TypeScript Analyzer - Regex-based static analysis

Analyzes:
- ES6 imports (import ... from)
- CommonJS requires (require(...))
- Dynamic imports (import(...))
- Re-exports (export ... from)
"""

from __future__ import annotations
import re
from pathlib import Path

from .base import BaseAnalyzer, AnalysisResult, Node, Edge


class JSAnalyzer(BaseAnalyzer):
    """JavaScript/TypeScript source code analyzer using regex"""
    
    EXTENSIONS = (".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs")
    LANGUAGE = "javascript"
    
    # Regex patterns for import detection
    PATTERNS = {
        # import x from 'module'
        # import { x, y } from 'module'
        # import * as x from 'module'
        # import 'module'
        "es6_import": re.compile(
            r"""import\s+(?:"""
            r"""(?:[\w*{}\s,]+)\s+from\s+)?"""  # Optional imported names
            r"""['"]([^'"]+)['"]""",  # Module path
            re.MULTILINE
        ),
        
        # const x = require('module')
        # require('module')
        "commonjs_require": re.compile(
            r"""(?:const|let|var)?\s*"""
            r"""(?:[\w{}\s,]+\s*=\s*)?"""
            r"""require\s*\(\s*['"]([^'"]+)['"]\s*\)""",
            re.MULTILINE
        ),
        
        # import('module')
        "dynamic_import": re.compile(
            r"""import\s*\(\s*['"]([^'"]+)['"]\s*\)""",
            re.MULTILINE
        ),
        
        # export { x } from 'module'
        # export * from 'module'
        "reexport": re.compile(
            r"""export\s+(?:[\w*{}\s,]+\s+)?from\s+['"]([^'"]+)['"]""",
            re.MULTILINE
        ),
    }
    
    # Regex for class detection
    CLASS_PATTERN = re.compile(
        r"""(?:export\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?""",
        re.MULTILINE
    )
    
    # Regex for function detection (top-level only, simplified)
    FUNCTION_PATTERN = re.compile(
        r"""(?:export\s+)?(?:async\s+)?function\s+(\w+)""",
        re.MULTILINE
    )
    
    # Arrow function exports
    ARROW_EXPORT_PATTERN = re.compile(
        r"""export\s+(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[\w]+)\s*=>""",
        re.MULTILINE
    )
    
    def __init__(self, project_root: Path, exclude_patterns: list[str] | None = None):
        super().__init__(project_root, exclude_patterns)
        self._file_map: dict[str, str] = {}  # Resolved imports -> file paths
    
    def analyze(self) -> AnalysisResult:
        """Analyze all JS/TS files in project"""
        result = AnalysisResult()
        files = self.find_files()
        
        # Build file map for resolution
        self._build_file_map(files)
        
        # Analyze each file
        for file_path in files:
            file_result = self.analyze_file(file_path)
            result.merge(file_result)
        
        # Deduplicate edges
        result.edges = self._deduplicate_edges(result.edges)
        
        return result
    
    def _build_file_map(self, files: list[Path]) -> None:
        """Build mapping for import resolution"""
        self._file_map.clear()
        for file_path in files:
            rel_path = self.get_relative_path(file_path)
            # Store with and without extension
            self._file_map[rel_path] = rel_path
            
            # Without extension
            for ext in self.EXTENSIONS:
                if rel_path.endswith(ext):
                    no_ext = rel_path[:-len(ext)]
                    self._file_map[no_ext] = rel_path
                    # Also store /index variants
                    if no_ext.endswith("/index"):
                        self._file_map[no_ext[:-6]] = rel_path
                    break
    
    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a single JS/TS file"""
        result = AnalysisResult()
        rel_path = self.get_relative_path(file_path)
        
        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            result.errors.append(f"Error reading {rel_path}: {e}")
            return result
        
        # Remove comments to avoid false matches
        source_no_comments = self._remove_comments(source)
        
        # Extract imports
        imports = self._extract_imports(source_no_comments)
        
        # Extract classes and functions
        classes = self._extract_classes(source_no_comments)
        functions = self._extract_functions(source_no_comments)
        
        # Determine language variant
        lang = "typescript" if file_path.suffix in (".ts", ".tsx") else "javascript"
        
        # Create node
        node = Node(
            id=rel_path,
            type="module",
            language=lang,
            path=rel_path,
            classes=[c[0] for c in classes],  # class name only
            functions=functions,
        )
        result.nodes.append(node)
        
        # Create edges for imports
        for import_path, import_type in imports:
            resolved = self._resolve_import(import_path, file_path)
            if resolved:
                result.edges.append(Edge(
                    source=rel_path,
                    target=resolved,
                    type="IMPORT",
                    metadata={"import_type": import_type}
                ))
        
        # Create edges for class inheritance
        for class_name, base_class in classes:
            if base_class:
                result.edges.append(Edge(
                    source=f"{rel_path}::{class_name}",
                    target=base_class,  # May need resolution
                    type="INHERITANCE",
                ))
        
        return result
    
    def _remove_comments(self, source: str) -> str:
        """Remove single-line and multi-line comments"""
        # Remove single-line comments
        source = re.sub(r'//.*$', '', source, flags=re.MULTILINE)
        # Remove multi-line comments
        source = re.sub(r'/\*[\s\S]*?\*/', '', source)
        return source
    
    def _extract_imports(self, source: str) -> list[tuple[str, str]]:
        """Extract all import paths and their types"""
        imports = []
        
        for pattern_name, pattern in self.PATTERNS.items():
            for match in pattern.finditer(source):
                import_path = match.group(1)
                imports.append((import_path, pattern_name))
        
        return imports
    
    def _extract_classes(self, source: str) -> list[tuple[str, str | None]]:
        """Extract class names and their base classes"""
        classes = []
        for match in self.CLASS_PATTERN.finditer(source):
            class_name = match.group(1)
            base_class = match.group(2)  # May be None
            classes.append((class_name, base_class))
        return classes
    
    def _extract_functions(self, source: str) -> list[str]:
        """Extract top-level function names"""
        functions = []
        
        # Regular functions
        for match in self.FUNCTION_PATTERN.finditer(source):
            functions.append(match.group(1))
        
        # Arrow function exports
        for match in self.ARROW_EXPORT_PATTERN.finditer(source):
            functions.append(match.group(1))
        
        return functions
    
    def _resolve_import(self, import_path: str, from_file: Path) -> str | None:
        """Resolve import path to actual file path"""
        # Skip node_modules and external packages
        if not import_path.startswith(".") and not import_path.startswith("/"):
            return None  # External package
        
        # Resolve relative path
        from_dir = from_file.parent
        
        if import_path.startswith("./") or import_path.startswith("../"):
            # Relative import
            resolved = (from_dir / import_path).resolve()
            try:
                rel_resolved = str(resolved.relative_to(self.project_root))
            except ValueError:
                return None  # Outside project
        elif import_path.startswith("/"):
            # Absolute from project root
            rel_resolved = import_path.lstrip("/")
        else:
            rel_resolved = import_path
        
        # Normalize path separators
        rel_resolved = rel_resolved.replace("\\", "/")
        
        # Try to find in file map
        if rel_resolved in self._file_map:
            return self._file_map[rel_resolved]
        
        # Try with extensions
        for ext in self.EXTENSIONS:
            candidate = rel_resolved + ext
            if candidate in self._file_map:
                return self._file_map[candidate]
        
        # Try /index variants
        for ext in self.EXTENSIONS:
            candidate = f"{rel_resolved}/index{ext}"
            if candidate in self._file_map:
                return self._file_map[candidate]
        
        return None
    
    def _deduplicate_edges(self, edges: list[Edge]) -> list[Edge]:
        """Remove duplicate edges"""
        edge_map: dict[tuple[str, str, str], Edge] = {}
        for edge in edges:
            key = (edge.source, edge.target, edge.type)
            if key in edge_map:
                edge_map[key].weight += 1
            else:
                edge_map[key] = edge
        return list(edge_map.values())
