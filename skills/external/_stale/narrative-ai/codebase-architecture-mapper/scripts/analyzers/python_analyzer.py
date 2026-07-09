"""
Python Analyzer - AST-based static analysis (Phase 2)

Analyzes:
- Module imports (import, from...import)
- Class inheritance (external + internal)
- Function calls (cross-module)
- Class nodes with methods
- Package-level aggregation
"""

from __future__ import annotations
import ast
from pathlib import Path
from collections import defaultdict
from dataclasses import dataclass, field

from .base import BaseAnalyzer, AnalysisResult, Node, Edge


@dataclass
class ClassInfo:
    """Detailed class information"""
    name: str
    bases: list[str] = field(default_factory=list)
    methods: list[str] = field(default_factory=list)
    is_abstract: bool = False
    decorators: list[str] = field(default_factory=list)


@dataclass  
class FunctionInfo:
    """Detailed function information"""
    name: str
    is_async: bool = False
    decorators: list[str] = field(default_factory=list)
    calls: list[str] = field(default_factory=list)


class PythonAnalyzer(BaseAnalyzer):
    """Python source code analyzer using ast module"""
    
    EXTENSIONS = (".py",)
    LANGUAGE = "python"
    
    def __init__(
        self, 
        project_root: Path, 
        exclude_patterns: list[str] | None = None,
        include_class_nodes: bool = False,  # Phase 2: separate class nodes
        include_package_aggregation: bool = False,  # Phase 2: package level
    ):
        super().__init__(project_root, exclude_patterns)
        self.include_class_nodes = include_class_nodes
        self.include_package_aggregation = include_package_aggregation
        
        # Cache for module -> file path mapping
        self._module_map: dict[str, str] = {}
        # Cache for imported names -> source module
        self._import_map: dict[str, dict[str, str]] = defaultdict(dict)
        # Cache for class definitions per module
        self._class_map: dict[str, dict[str, ClassInfo]] = defaultdict(dict)
    
    def analyze(self) -> AnalysisResult:
        """Analyze all Python files in project"""
        result = AnalysisResult()
        files = self.find_files()
        
        # First pass: build module map and collect class definitions
        self._build_module_map(files)
        self._collect_class_definitions(files)
        
        # Second pass: analyze each file with full context
        for file_path in files:
            file_result = self.analyze_file(file_path)
            result.merge(file_result)
        
        # Phase 2: Add package-level aggregation
        if self.include_package_aggregation:
            pkg_result = self._aggregate_packages(result)
            result.merge(pkg_result)
        
        # Deduplicate edges
        result.edges = self._deduplicate_edges(result.edges)
        
        return result
    
    def _collect_class_definitions(self, files: list[Path]) -> None:
        """First pass: collect all class definitions for internal inheritance resolution"""
        self._class_map.clear()
        
        for file_path in files:
            rel_path = self.get_relative_path(file_path)
            try:
                source = file_path.read_text(encoding="utf-8", errors="ignore")
                tree = ast.parse(source, filename=str(file_path))
            except:
                continue
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = ClassInfo(
                        name=node.name,
                        bases=[self._get_name(b) for b in node.bases if self._get_name(b)],
                        methods=[n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))],
                        decorators=[self._get_name(d) for d in node.decorator_list if self._get_name(d)],
                    )
                    # Check if abstract
                    if any('abstract' in d.lower() for d in class_info.decorators if d):
                        class_info.is_abstract = True
                    if any('ABC' in b for b in class_info.bases):
                        class_info.is_abstract = True
                    
                    self._class_map[rel_path][node.name] = class_info
    
    def _aggregate_packages(self, result: AnalysisResult) -> AnalysisResult:
        """Aggregate module-level dependencies to package level"""
        pkg_result = AnalysisResult()
        
        # Collect unique packages
        packages = set()
        for node in result.nodes:
            if "/" in node.id:
                pkg = "/".join(node.id.split("/")[:-1])
                if pkg:
                    packages.add(pkg)
        
        # Create package nodes
        for pkg in packages:
            pkg_node = Node(
                id=f"[pkg]{pkg}",
                type="package",
                language=self.LANGUAGE,
                path=pkg,
            )
            pkg_result.nodes.append(pkg_node)
        
        # Aggregate edges to package level
        pkg_edges: dict[tuple[str, str], int] = defaultdict(int)
        for edge in result.edges:
            src_pkg = "/".join(edge.source.split("/")[:-1]) if "/" in edge.source else ""
            tgt_pkg = "/".join(edge.target.split("/")[:-1]) if "/" in edge.target else ""
            
            # Skip if same package or no package
            if src_pkg and tgt_pkg and src_pkg != tgt_pkg:
                # Remove :: class notation for package aggregation
                src_pkg = src_pkg.split("::")[0]
                tgt_pkg = tgt_pkg.split("::")[0]
                pkg_edges[(f"[pkg]{src_pkg}", f"[pkg]{tgt_pkg}")] += 1
        
        for (src, tgt), weight in pkg_edges.items():
            pkg_result.edges.append(Edge(
                source=src,
                target=tgt,
                type="PACKAGE_DEP",
                weight=weight,
            ))
        
        return pkg_result
    
    def _get_name(self, node: ast.AST) -> str | None:
        """Extract name from AST node (class-level helper)"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return None
    
    def _build_module_map(self, files: list[Path]) -> None:
        """Build mapping from module names to file paths"""
        self._module_map.clear()
        for file_path in files:
            rel_path = self.get_relative_path(file_path)
            # Convert path to module name
            module_name = rel_path.replace("/", ".").replace("\\", ".")
            if module_name.endswith(".py"):
                module_name = module_name[:-3]
            if module_name.endswith(".__init__"):
                module_name = module_name[:-9]
            self._module_map[module_name] = rel_path
    
    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a single Python file"""
        result = AnalysisResult()
        rel_path = self.get_relative_path(file_path)
        
        try:
            source = file_path.read_text(encoding="utf-8", errors="ignore")
            tree = ast.parse(source, filename=str(file_path))
        except SyntaxError as e:
            result.errors.append(f"Syntax error in {rel_path}: {e}")
            return result
        except Exception as e:
            result.errors.append(f"Error reading {rel_path}: {e}")
            return result
        
        # Get class definitions for this file (from first pass)
        file_classes = self._class_map.get(rel_path, {})
        
        # Extract info from AST with enhanced visitor
        visitor = PythonASTVisitor(
            rel_path, 
            self._module_map, 
            self.project_root,
            local_classes=set(file_classes.keys()),  # Phase 2: pass local class names
        )
        visitor.visit(tree)
        
        # Create node for this module
        module_node = Node(
            id=rel_path,
            type="module",
            language=self.LANGUAGE,
            path=rel_path,
            classes=visitor.classes,
            functions=visitor.functions,
        )
        result.nodes.append(module_node)
        
        # Phase 2: Create separate class nodes if enabled
        if self.include_class_nodes:
            for class_name, class_info in file_classes.items():
                class_node = Node(
                    id=f"{rel_path}::{class_name}",
                    type="class",
                    language=self.LANGUAGE,
                    path=rel_path,
                    functions=class_info.methods,  # Methods stored in functions field
                )
                result.nodes.append(class_node)
        
        # Add edges
        result.edges.extend(visitor.edges)
        
        # Store import map for this file
        self._import_map[rel_path] = visitor.imported_names
        
        return result
    
    def _deduplicate_edges(self, edges: list[Edge]) -> list[Edge]:
        """Remove duplicate edges, keeping highest weight"""
        edge_map: dict[tuple[str, str, str], Edge] = {}
        for edge in edges:
            key = (edge.source, edge.target, edge.type)
            if key in edge_map:
                edge_map[key].weight += 1
            else:
                edge_map[key] = edge
        return list(edge_map.values())


class PythonASTVisitor(ast.NodeVisitor):
    """AST visitor for extracting code structure (Phase 2 enhanced)"""
    
    def __init__(
        self, 
        file_path: str, 
        module_map: dict[str, str], 
        project_root: Path,
        local_classes: set[str] | None = None,  # Phase 2: local class names
    ):
        self.file_path = file_path
        self.module_map = module_map
        self.project_root = project_root
        self.local_classes = local_classes or set()
        
        self.classes: list[str] = []
        self.functions: list[str] = []
        self.edges: list[Edge] = []
        self.imported_names: dict[str, str] = {}  # name -> source module
        
        # Track current scope for nested definitions
        self._scope_stack: list[str] = []
    
    def visit_Import(self, node: ast.Import) -> None:
        """Handle: import module, import module as alias"""
        for alias in node.names:
            module_name = alias.name
            local_name = alias.asname or alias.name.split(".")[0]
            
            target_path = self._resolve_module(module_name)
            if target_path:
                self.edges.append(Edge(
                    source=self.file_path,
                    target=target_path,
                    type="IMPORT",
                    metadata={"imported": module_name}
                ))
                self.imported_names[local_name] = target_path
        
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle: from module import name"""
        if node.module is None:
            # Relative import without module (from . import x)
            module_name = ""
        else:
            module_name = node.module
        
        # Handle relative imports
        if node.level > 0:
            module_name = self._resolve_relative_import(module_name, node.level)
        
        target_path = self._resolve_module(module_name)
        if target_path:
            imported_items = [
                alias.asname or alias.name 
                for alias in node.names 
                if alias.name != "*"
            ]
            
            self.edges.append(Edge(
                source=self.file_path,
                target=target_path,
                type="IMPORT",
                metadata={"imported": imported_items} if imported_items else {}
            ))
            
            # Track imported names
            for alias in node.names:
                if alias.name != "*":
                    local_name = alias.asname or alias.name
                    self.imported_names[local_name] = target_path
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Handle class definitions and inheritance (Phase 2: internal + external)"""
        class_name = node.name
        self.classes.append(class_name)
        
        # Check inheritance
        for base in node.bases:
            base_name = self._get_name(base)
            if base_name:
                root_name = base_name.split(".")[0]
                
                # Phase 2: Check internal inheritance first (same file)
                if root_name in self.local_classes and root_name != class_name:
                    self.edges.append(Edge(
                        source=f"{self.file_path}::{class_name}",
                        target=f"{self.file_path}::{root_name}",
                        type="INHERITANCE",
                        metadata={"internal": True}
                    ))
                # External inheritance (from imported module)
                elif root_name in self.imported_names:
                    source_module = self.imported_names[root_name]
                    self.edges.append(Edge(
                        source=f"{self.file_path}::{class_name}",
                        target=f"{source_module}::{base_name}",
                        type="INHERITANCE",
                        metadata={"internal": False}
                    ))
        
        # Visit class body
        self._scope_stack.append(class_name)
        self.generic_visit(node)
        self._scope_stack.pop()
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Handle function definitions"""
        if not self._scope_stack:  # Top-level function
            self.functions.append(node.name)
        
        # Visit function body for calls
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Handle async function definitions"""
        if not self._scope_stack:
            self.functions.append(node.name)
        
        self._scope_stack.append(node.name)
        self.generic_visit(node)
        self._scope_stack.pop()
    
    def visit_Call(self, node: ast.Call) -> None:
        """Handle function calls to detect cross-module calls"""
        func_name = self._get_name(node.func)
        if func_name:
            root_name = func_name.split(".")[0]
            # Check if calling imported function/class
            if root_name in self.imported_names:
                source_module = self.imported_names[root_name]
                self.edges.append(Edge(
                    source=self.file_path,
                    target=source_module,
                    type="FUNCTION_CALL",
                    metadata={"called": func_name}
                ))
        
        self.generic_visit(node)
    
    def _resolve_module(self, module_name: str) -> str | None:
        """Resolve module name to file path"""
        if not module_name:
            return None
        
        # Direct match
        if module_name in self.module_map:
            return self.module_map[module_name]
        
        # Check parent packages
        parts = module_name.split(".")
        for i in range(len(parts), 0, -1):
            partial = ".".join(parts[:i])
            if partial in self.module_map:
                return self.module_map[partial]
        
        # External module (not in project)
        return None
    
    def _resolve_relative_import(self, module_name: str, level: int) -> str:
        """Resolve relative import to absolute module name"""
        # Get current module's package path
        current_parts = self.file_path.replace("\\", "/").split("/")
        if current_parts[-1].endswith(".py"):
            current_parts[-1] = current_parts[-1][:-3]
        
        # Go up 'level' directories
        if len(current_parts) >= level:
            base_parts = current_parts[:-level]
        else:
            base_parts = []
        
        if module_name:
            base_parts.append(module_name.replace(".", "/"))
        
        return ".".join(base_parts).replace("/", ".")
    
    def _get_name(self, node: ast.AST) -> str | None:
        """Extract name from AST node"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            value = self._get_name(node.value)
            if value:
                return f"{value}.{node.attr}"
            return node.attr
        elif isinstance(node, ast.Call):
            return self._get_name(node.func)
        return None
