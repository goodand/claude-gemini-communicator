# Smoke Report — export_canonical_graph

- created_at: `2026-03-21-12-49`
- scope: `canonical graph artifact -> DOT / CSV / Cypher export`
- script: [export_canonical_graph.py](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/scripts/export_canonical_graph.py)
- helper_wrapper: [run_export_canonical_graph_smoke.sh](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/scripts/run_export_canonical_graph_smoke.sh)
- fixture: [graph-sample-at2026-03-20-22-45](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/codebase-analysis/references/fixtures/graph-sample-at2026-03-20-22-45/README.md)
- archive_dir: [logs/smoke/export_canonical_graph/2026-03-21-19-13](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13)

## Runner

- wrapper command: `scripts/run_export_canonical_graph_smoke.sh 2026-03-21-19-13`
- archive layout: `logs/smoke/export_canonical_graph/<timestamp>/<case>/`
- tmp work dir: `tmp/export_canonical_graph_smoke/<timestamp>/`

## Executions

### 1. normalized_graph.json input
- command path: `scripts/run_export_canonical_graph_smoke.sh 2026-03-21-19-13`
- result: `PASS`
- input_mode: `normalized_graph`
- graph_id: `codebase_graph_sample_2026-03-20-22-45`
- graph_kind: `codebase_graph`
- node_count: `3`
- edge_count: `2`

Outputs:
- [graph.dot](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/graph.dot)
- [nodes.csv](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/nodes.csv)
- [rels.csv](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/rels.csv)
- [graph.cypher](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/graph.cypher)
- [export_summary.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/export_summary.json)
- [warnings.log](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/warnings.log)
- [stderr.log](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/stderr.log)
- [stdout.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/normalized_graph/stdout.json)

Interpretation:
- this is the canonical full snapshot path
- `warnings.log` and `stderr.log` are expected to stay empty in the clean path

### 2. nodes.jsonl + edges.jsonl input
- command path: `scripts/run_export_canonical_graph_smoke.sh 2026-03-21-19-13`
- result: `PASS`
- input_mode: `jsonl_only`
- graph_id: `graph_from_jsonl`
- graph_kind: `unknown_graph_kind`
- node_count: `3`
- edge_count: `2`

Warnings:
- `split-only export without graph_meta.json uses fallback metadata`
- `graph_id=graph_from_jsonl is a temporary fallback identifier`
- `graph_kind=unknown_graph_kind indicates missing top-level metadata`
- `prefer --normalized-graph for canonical full snapshot or add --graph-meta for split-only metadata preservation`

Outputs:
- [graph.dot](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/graph.dot)
- [nodes.csv](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/nodes.csv)
- [rels.csv](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/rels.csv)
- [graph.cypher](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/graph.cypher)
- [export_summary.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/export_summary.json)
- [warnings.log](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/warnings.log)
- [stderr.log](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/stderr.log)
- [stdout.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_only/stdout.json)

Interpretation:
- this is a split-only export path
- it is useful for structure-only export smoke
- it is not a canonical replacement for `normalized_graph.json`
- without `graph_meta.json`, top-level metadata is not preserved

### 3. nodes.jsonl + edges.jsonl + graph_meta.json input
- command path: `scripts/run_export_canonical_graph_smoke.sh 2026-03-21-19-13`
- result: `PASS`
- input_mode: `jsonl_with_meta`
- graph_id: `codebase_graph_sample_2026-03-20-22-45`
- graph_kind: `codebase_graph`
- node_count: `3`
- edge_count: `2`

Outputs:
- [graph.dot](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/graph.dot)
- [nodes.csv](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/nodes.csv)
- [rels.csv](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/rels.csv)
- [graph.cypher](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/graph.cypher)
- [export_summary.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/export_summary.json)
- [warnings.log](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/warnings.log)
- [stderr.log](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/stderr.log)
- [stdout.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/my-second-identity/logs/smoke/export_canonical_graph/2026-03-21-19-13/jsonl_with_meta/stdout.json)

Interpretation:
- this is the split-only metadata preservation path
- it is valid for split-form fixture/export consumption
- it preserves top-level metadata via `graph_meta.json`
- it still does not replace `normalized_graph.json` as the canonical full snapshot
- its `warnings.log` and `stderr.log` are expected to stay empty in the clean path

## Findings

1. canonical artifact에서 DOT / CSV / Cypher export는 기본 경로 기준으로 동작한다.
2. `normalized_graph.json` 경로는 메타데이터를 유지한다.
3. `nodes.jsonl + edges.jsonl` 경로는 graph structure export는 가능하지만, `graph_id`와 `graph_kind`는 explicit fallback metadata로 표시된다.
4. `nodes.jsonl + edges.jsonl + graph_meta.json` 경로는 split-only 형태에서도 top-level metadata를 보존할 수 있다.
5. `jsonl_with_meta`는 split-only metadata preservation 경로로 유효하지만, canonical full snapshot의 대체물은 아니다.

## Improvement Archive

### Immediate follow-up
- JSONL-only 경로에 metadata sidecar 또는 별도 `--graph-meta` 입력을 추가할 것
- `graph_from_jsonl` 같은 fallback identifier를 임시값임을 명시할 것
- `graph_kind`가 비어 있으면 warning 또는 explicit fallback 정책을 둘 것
- script help에 split-only metadata preservation 용도를 명시할 것

### Contract-level follow-up
- canonical full snapshot과 split-only export의 경계를 문서에서 계속 유지할 것
- `graph_meta.json`은 canonical replacement가 아니라 split-form sidecar라는 점을 유지할 것

### Usability follow-up
- exporter summary에 `input_mode`를 추가하면 smoke 보고와 디버깅이 쉬워진다
- `--archive-dir`를 사용해 canonical smoke archive layout을 자동 생성한다

## Verdict
- current status: `PASS with follow-ups`
- next priority: `warning promotion / archive policy for jsonl_only`
