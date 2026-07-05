"""
Base Analyzer Interface

All language analyzers inherit from this base class.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class Node:
    """Represents a code entity (module, class, function)"""
    id: str
    type: Literal["module", "class", "function", "package"]
    language: str
    path: str | None = None
    classes: list[str] = field(default_factory=list)
    functions: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        result = {
            "id": self.id,
            "type": self.type,
            "language": self.language,
        }
        if self.path:
            result["path"] = self.path
        if self.classes:
            result["classes"] = self.classes
        if self.functions:
            result["functions"] = self.functions
        return result


@dataclass
class Edge:
    """Represents a relationship between code entities"""
    source: str
    target: str
    type: Literal["IMPORT", "INHERITANCE", "FUNCTION_CALL", "PACKAGE_DEP"]
    weight: int = 1
    metadata: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        result = {
            "source": self.source,
            "target": self.target,
            "type": self.type,
        }
        if self.weight != 1:
            result["weight"] = self.weight
        if self.metadata:
            result["metadata"] = self.metadata
        return result
    
    def to_tuple(self) -> tuple[str, str]:
        return (self.source, self.target)


@dataclass
class AnalysisResult:
    """Result from a language analyzer"""
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    
    def merge(self, other: AnalysisResult) -> None:
        """Merge another result into this one"""
        self.nodes.extend(other.nodes)
        self.edges.extend(other.edges)
        self.errors.extend(other.errors)


class BaseAnalyzer(ABC):
    """Base class for language-specific analyzers"""
    
    EXTENSIONS: tuple[str, ...] = ()
    LANGUAGE: str = "unknown"
    
    def __init__(self, project_root: Path, exclude_patterns: list[str] | None = None):
        self.project_root = project_root
        self.exclude_patterns = exclude_patterns or [
            "node_modules", "venv", ".venv", "__pycache__", 
            ".git", ".svn", "dist", "build", ".tox", ".eggs"
        ]
    
    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded from analysis"""
        parts = path.parts
        for pattern in self.exclude_patterns:
            if pattern in parts:
                return True
        return False
    
    def find_files(self) -> list[Path]:
        """Find all files matching this analyzer's extensions"""
        files = []
        for ext in self.EXTENSIONS:
            for file_path in self.project_root.rglob(f"*{ext}"):
                if not self.should_exclude(file_path):
                    files.append(file_path)
        return sorted(files)
    
    def get_relative_path(self, file_path: Path) -> str:
        """Get path relative to project root"""
        try:
            return str(file_path.relative_to(self.project_root))
        except ValueError:
            return str(file_path)
    
    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """Analyze all files and return nodes/edges"""
        pass
    
    @abstractmethod
    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze a single file"""
        pass
