# Output Format Reference

## JSON Output (Default)

```json
{
  "metadata": {
    "project_root": "/path/to/project",
    "languages": {"python": 10, "typescript": 5},
    "total_files": 15,
    "total_edges": 17
  },
  "nodes": [
    {
      "id": "src/auth/login.py",
      "type": "module",
      "language": "python",
      "layer": 1,
      "classes": ["LoginService"],
      "functions": ["authenticate"]
    }
  ],
  "edges": [
    {
      "source": "main.py",
      "target": "src/auth/login.py",
      "type": "IMPORT",
      "metadata": {"imported": ["LoginService"]}
    }
  ],
  "edge_list": [["main.py", "src/auth/login.py"]],
  "analysis": {
    "hub_nodes": [{"id": "...", "in_degree": 5}],
    "connector_nodes": [{"id": "...", "out_degree": 4}],
    "entry_points": ["main.py"],
    "leaf_nodes": ["utils/crypto.py"],
    "edge_type_breakdown": {"IMPORT": 10, "FUNCTION_CALL": 3},
    "layer_distribution": {"0": 5, "1": 3, "2": 2},
    "max_depth": 2
  }
}
```

## PROJECT_ARCHITECTURE.md (via context_generator.py)

```markdown
# PROJECT_ARCHITECTURE.md

## Overview
| Metric | Value |
|--------|-------|
| Total Nodes | 16 |
| Languages | python: 11, typescript: 5 |

## Nodes by Layer
### Layer 0: Entry Points / UI
- `main.py` (functions: main)
- `LoginForm.tsx`

### Layer 1: Controllers / API
- `login.py` (classes: LoginService)

## Key Nodes
### Hub Nodes (most depended upon)
| Node | In-Degree | Impact |
|------|-----------|--------|
| `user_service.py` | 3 | 🔴 Critical |

### Entry Points (no incoming dependencies)
- `main.py`
- `frontend/components/LoginForm.tsx`

## Critical Paths
1. `main.py` → `login.py` → `validators.py`

## Dependency Summary
### IMPORT (10 edges)
| Source | Target | Details |
|--------|--------|---------|
| `main.py` | `login.py` | imports: LoginService |

## Diagram
[Mermaid flowchart auto-generated]
```

## Edge Types

| Type | Description | Example |
|------|-------------|---------|
| `IMPORT` | Module import | `from auth import login` |
| `INHERITANCE` | Class extends | `class UserService(BaseRepo)` |
| `FUNCTION_CALL` | Cross-module call | `user_service.get_user()` |
| `PACKAGE_DEP` | Package dependency (--package-level) | `auth → utils` |

## Analysis Fields

| Field | Description |
|-------|-------------|
| `hub_nodes` | Nodes with highest in-degree (most depended upon) |
| `connector_nodes` | Nodes with highest out-degree (most dependencies) |
| `entry_points` | Nodes with zero in-degree |
| `leaf_nodes` | Nodes with zero out-degree |
| `layer_distribution` | Node count per topological layer |
