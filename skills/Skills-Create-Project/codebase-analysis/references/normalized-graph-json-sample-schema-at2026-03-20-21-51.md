# normalized_graph.json Sample Schema

## Purpose

Provide a tool-neutral sample schema for the canonical graph snapshot artifact.

## Sample Shape

```json
{
  "graph_id": "codebase_graph_my_repo_2026-03-20-21-51",
  "generated_at": "2026-03-20T21:51:00+09:00",
  "source_scope": "repo_root",
  "graph_kind": "codebase_graph",
  "schema_version": "1",
  "node_schema_version": "1",
  "edge_schema_version": "1",
  "metadata": {
    "generator": "dependency-graph-analyst",
    "source_tools": ["tree_survey", "import_extractor", "manifest_reader"],
    "notes": ["codebase graph only", "orchestration graph excluded"]
  },
  "nodes": [
    {
      "id": "file:src/app.py",
      "kind": "File",
      "name": "app.py",
      "path": "src/app.py",
      "parent_id": "folder:src",
      "region": "src",
      "source_tool": "tree_survey",
      "confidence": 1.0,
      "attrs": {
        "language": "python"
      }
    },
    {
      "id": "func:src/app.py:main",
      "kind": "Function",
      "name": "main",
      "path": "src/app.py",
      "parent_id": "file:src/app.py",
      "region": "src",
      "source_tool": "import_extractor",
      "confidence": 0.95,
      "attrs": {
        "line": 10
      }
    }
  ],
  "edges": [
    {
      "src": "file:src/app.py",
      "dst": "file:src/core.py",
      "rel": "IMPORTS",
      "kind": "static_dependency",
      "source_tool": "import_extractor",
      "confidence": 1.0,
      "evidence_path": "src/app.py",
      "attrs": {
        "line": 3
      }
    },
    {
      "src": "file:src/app.py",
      "dst": "func:src/app.py:main",
      "rel": "DECLARES",
      "kind": "containment",
      "source_tool": "tree_survey",
      "confidence": 1.0,
      "evidence_path": "src/app.py",
      "attrs": {}
    }
  ],
  "overlays": [
    {
      "overlay_kind": "anomaly",
      "name": "cycle_candidate",
      "items": [
        {
          "edge_ref": {
            "src": "file:src/app.py",
            "dst": "file:src/core.py",
            "rel": "IMPORTS"
          },
          "attrs": {
            "cycle_id": "cycle:1"
          }
        }
      ]
    }
  ]
}
```

## Required Top-Level Fields

- `graph_id`
- `generated_at`
- `source_scope`
- `graph_kind`
- `schema_version`
- `nodes`
- `edges`

## `graph_kind`

Recommended values:
- `codebase_graph`
- `analysis_graph`
- `merged_graph`

## Node Rules

Required:
- `id`
- `kind`
- `name`

Recommended:
- `path`
- `parent_id`
- `region`
- `source_tool`
- `confidence`
- `attrs`

## Edge Rules

Required:
- `src`
- `dst`
- `rel`

Recommended:
- `kind`
- `source_tool`
- `confidence`
- `evidence_path`
- `attrs`

## Notes

- `normalized_graph.json` is the full snapshot artifact.
- `nodes.jsonl` and `edges.jsonl` should be derivable from the same canonical graph model.
- bundle forms are:
  - full snapshot bundle: `normalized_graph.json`
  - canonical bundle with derived split exports: `normalized_graph.json` + `nodes.jsonl` + `edges.jsonl` + optional `graph_meta.json`
  - split-only fixture/export: `nodes.jsonl` + `edges.jsonl` + optional `graph_meta.json`
- if `normalized_graph.json` is absent and top-level metadata must be preserved, `graph_meta.json` becomes required for that split-only form.
- render/export targets must not add semantic fields that do not exist in canonical artifacts.
