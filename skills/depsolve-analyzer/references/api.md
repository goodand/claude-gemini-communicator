# Depsolve API Reference

## Main Entry Point

### `analyze(project_path, verify=False, include_dev=True, max_nodes=50)`

Analyze a project for dependency issues.

**Parameters:**
- `project_path` (str): Path to project directory
- `verify` (bool): Enable runtime verification (check actual installations)
- `include_dev` (bool): Include devDependencies
- `max_nodes` (int): Maximum nodes in Mermaid diagram

**Returns:** `AnalysisResult`

```python
from depsolve_ext import analyze, Severity

result = analyze("./my-project", verify=True)

print(f"Ecosystem: {result.ecosystem}")
print(f"Total packages: {result.summary.total_packages}")

for issue in result.issues:
    if issue.severity == Severity.HIGH:
        print(f"[{issue.severity.value}] {issue.title}")

# Mermaid diagram
print(result.mermaid_diagram)
```

---

## Core Classes

### DependencyAnalyzer

Main analyzer class that orchestrates all analysis.

```python
from depsolve_ext import DependencyAnalyzer
from pathlib import Path

analyzer = DependencyAnalyzer(
    project_path=Path("./my-project"),
    verify_runtime=True,
    include_dev=True
)

result = analyzer.analyze(max_nodes=100)
```

### DependencyGraph

Graph data structure for dependency analysis.

```python
from depsolve_ext import DependencyGraph, DependencyEdge

graph = DependencyGraph()
graph.add_node("packageA", "1.0.0")
graph.add_edge(DependencyEdge(source="packageA", target="packageB", version_range="^2.0"))

# Find issues
cycles = graph.find_cycles()
diamonds = graph.find_diamonds()

# Visualization
mermaid = graph.to_mermaid(max_nodes=50)
dot = graph.to_dot(max_nodes=50)

# Queries
deps = graph.get_transitive_dependencies("packageA")
depth = graph.get_depth("packageB")
```

### PhantomDetector

Detect undeclared dependencies.

```python
from depsolve_ext import PhantomDetector
from pathlib import Path

detector = PhantomDetector(
    project_path=Path("./my-project"),
    js_deps={"react", "lodash"},
    py_deps={"requests", "flask"},
    verify=True
)

phantoms = detector.detect()

for p in phantoms:
    if p.is_phantom:
        print(f"Phantom: {p.package} ({p.ecosystem.value})")
        for imp in p.imports:
            print(f"  - {imp.file}:{imp.line}")
```

### ImportExtractor

Extract imports from source files.

```python
from depsolve_ext import ImportExtractor
from pathlib import Path

extractor = ImportExtractor(
    include_types=True,      # Include TypeScript type imports
    filter_stdlib=True       # Filter standard library
)

# From file
imports = extractor.extract_file(Path("./src/App.tsx"))

# From content
imports = extractor.extract_content("import React from 'react';", "App.tsx")

for imp in imports:
    print(f"{imp.package} ({imp.import_type.value}) at {imp.file}:{imp.line}")
```

---

## Data Models

### AnalysisResult

```python
@dataclass
class AnalysisResult:
    project_path: str
    ecosystem: str           # "npm", "pip", "npm+python", etc.
    issues: List[Issue]
    summary: Summary
    mermaid_diagram: Optional[str]
```

### Issue

```python
@dataclass
class Issue:
    type: IssueType          # PHANTOM, CIRCULAR, DIAMOND, etc.
    severity: Severity       # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    locations: List[Location]
    evidence: Evidence
    suggestion: str
```

### PhantomResult

```python
@dataclass
class PhantomResult:
    package: str
    imports: List[ImportInfo]
    is_phantom: bool         # False if found as transitive
    installed_version: Optional[str]
    reason: str
    ecosystem: Ecosystem     # JAVASCRIPT, PYTHON, etc.
```

### ImportInfo

```python
@dataclass
class ImportInfo:
    module: str              # Full import path
    package: str             # Extracted package name
    file: str
    line: int
    import_type: ImportType  # STATIC, REQUIRE, DYNAMIC, TYPE_ONLY, etc.
    file_context: FileContext  # SOURCE, CONFIG, TEST, SCRIPT
    is_type_only: bool
    ecosystem: Ecosystem
```

---

## Enums

### Ecosystem
```python
class Ecosystem(Enum):
    JAVASCRIPT = "javascript"
    PYTHON = "python"
    GO = "go"
    RUST = "rust"
    UNKNOWN = "unknown"
```

### IssueType
```python
class IssueType(Enum):
    CIRCULAR = "circular"
    DIAMOND = "diamond"
    PHANTOM = "phantom"
    VERSION_CONFLICT = "version_conflict"
    MULTI_VERSION = "multi_version"
```

### Severity
```python
class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### ImportType
```python
class ImportType(Enum):
    STATIC = "import"        # import x from 'y'
    REQUIRE = "require"      # require('y')
    DYNAMIC = "dynamic_import"  # import('y')
    TYPE_ONLY = "type_import"   # import type { x } from 'y'
    RE_EXPORT = "re_export"  # export * from 'y'
    FROM_IMPORT = "from_import"  # from x import y (Python)
```

---

## Reporters

### ConsoleReporter

```python
from depsolve_ext import ConsoleReporter

reporter = ConsoleReporter(use_color=True, verbose=True)
reporter.report(result)
```

### JsonReporter

```python
from depsolve_ext import JsonReporter

reporter = JsonReporter(indent=2)
reporter.report(result)  # Outputs JSON
```

### MarkdownReporter

```python
from depsolve_ext import MarkdownReporter

reporter = MarkdownReporter()
reporter.report(result)  # Outputs Markdown
```

---

## Override System

### OverrideConfig

```python
from depsolve_ext import OverrideConfig, OverrideApplicator

# Load from project
config = OverrideConfig.load(Path("./my-project"))

# Apply to phantoms
applicator = OverrideApplicator(config)
modified_phantoms = applicator.apply(phantoms)

print(applicator.stats)
# {'typo_corrected': 2, 'alias_resolved': 5, 'internal_marked': 3, ...}
```

### Built-in Aliases

Common Python import aliases are built-in:

| Import Name | Package Name |
|-------------|--------------|
| pil | pillow |
| cv2 | opencv-python |
| sklearn | scikit-learn |
| yaml | pyyaml |
| bs4 | beautifulsoup4 |
| dotenv | python-dotenv |

---

## Standard Library Filters

The analyzer automatically filters:

- **Node.js**: `fs`, `path`, `http`, `https`, `crypto`, `os`, etc. (40+ modules)
- **Python**: `os`, `sys`, `json`, `re`, `datetime`, `pathlib`, etc. (200+ modules)
- **Go**: `fmt`, `os`, `io`, `net`, `http`, etc.
