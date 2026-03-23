# Implementation Plan — codebase-analysis-spec-v0-core-implementation

- recorded_at: `2026-03-23-11-50`
- source_request: `references/codebase-analysis-implementation-request-at2026-03-23-10-49.md`
- workspace: `.worktrees/codebase-analysis-spec-v0-core-implementation`
- branch: `feat/codebase-analysis-spec-v0-core-implementation`

## Baseline

- base_commit: `6873d61`
- baseline test: 4/4 pass
- 기존 기능: `build_summary()` (coarse survey), CLI `--output` / `--include-top-level` / `--exclude-top-level`

## 구현 목표

기존 coarse summary를 보존하면서 canonical artifact triple + graph_meta.json 생성 기능을 추가한다.

## 코드로 내려야 하는 Spec 결정

- `ALLOWED_GRAPH_KINDS = {"codebase_graph", "analysis_graph", "merged_graph"}` 상수를 두고, `build_canonical_graph`의 `graph_kind` 인자를 이 집합으로 validate한다 (spec:213-222)
- `merged_graph`는 `graph_kind` 값으로만 허용하고, analysis/orchestration graph와 병합하는 코드 경로를 만들지 않는다 (spec:78,165)
- graph core에 넣는 edge/node 조건: 해당 파일이 실재하고(`file-first anchor`), import 구문에서 기계적으로 추출 가능하며(`재현 가능한 구조 사실`), src→dst 방향이 있는 경우(`directioned relation`) (spec:41-42)
- 위 세 조건을 하나라도 만족하지 않으면 sidecar evidence로 보낸다. 예: resolve 실패한 import, 존재하지 않는 대상 파일, 판단이 필요한 경고 (spec:42,282)

## Node 대상 범위

- 비Python 파일은 source scope에 포함되고 code/config/manifest/script family에 속하면 node-only를 허용한다.
  - 허용: `.js`, `.ts`, `.tsx`, `.jsx`, `.json`, `.yaml`, `.yml`, `.toml`, `Dockerfile`, `Makefile`, shell script
- documentation-only text artifact는 canonical graph node 대상에서 제외한다.
  - 제외: `.md`, `.txt`, `.rst`, `README*`, `CHANGELOG*`, `LICENSE*`

## 접근 방식

### Step 1. Python import edge 추출 함수

- 의존: 없음 (독립 구현 가능)
- 검증: Step 1 완료 후 단독 단위 테스트로 확인

시그니처:

```python
def extract_imports(py_file: Path, root: Path) -> tuple[list[dict], list[dict]]:
    """
    Returns:
        edges: [{"src": "file:src/app.py", "dst": "file:src/core.py", "rel": "IMPORTS", ...}, ...]
        sidecar: [{"evidence_kind": "unresolved", "subject_anchor": "file:src/app.py", ...}, ...]
    """
```

동작:
- `ast.parse()` 성공 시:
  - `ast.Import` → 각 `alias.name`을 module name으로 추출
  - `ast.ImportFrom` → `node.module`을 module name으로 추출, `node.level > 0`이면 relative import
- module name → file path 해석:
  - `module.replace(".", "/") + ".py"` 또는 `module.replace(".", "/") + "/__init__.py"` 시도
  - repo 안에 해당 파일이 존재하면 → edge (graph core)
  - 존재하지 않으면 → sidecar evidence (`evidence_kind="unresolved"`)
- `ast.parse()` 실패 시:
  - edge 없이 빈 리스트 반환
  - sidecar evidence (`evidence_kind="warning"`, reason="parse failure")

엣지 케이스:
- `__init__.py`: 패키지 디렉토리의 `__init__.py`로 resolve
- relative import (`from . import x`): `py_file`의 디렉토리 기준으로 resolve
- circular import: 탐지하지 않음 (graph에 cycle이 있어도 정상, anomaly는 sidecar 아님)
- encoding 에러: `ast.parse` 실패와 동일하게 처리
- `import *`: module name만 추출, 개별 symbol은 무시

### Step 2a. 노드 생성

- 의존: 없음 (Step 1과 병렬 가능)
- 검증: `len(nodes) > 0`, 각 node에 `id`, `kind`, `name` 존재

```python
def collect_nodes(root: Path, excludes: set[str], ...) -> list[dict]:
```

동작:
- `iter_files()` 재사용, documentation-only 파일 필터링
- 필터 기준: `DOC_ONLY_SUFFIXES = {".md", ".txt", ".rst"}`, `DOC_ONLY_PREFIXES = {"README", "CHANGELOG", "LICENSE"}`
- 각 파일 → `{"id": "file:<rel_path>", "kind": "File", "name": "<filename>", "path": "<rel_path>", "parent_id": "folder:<parent_rel>", "region": "<top_level_dir>", "source_tool": "tree_survey", "confidence": 1.0}`
- 각 디렉토리(파일의 parent 기준 수집) → `{"id": "folder:<rel_path>", "kind": "Folder", "name": "<dirname>", ...}`
- 빈 디렉토리: 파일이 없으면 Folder 노드도 생성하지 않음
- symlink: resolve 후 repo 밖이면 제외

### Step 2b. 엣지 + sidecar 수집

- 의존: Step 1 (`extract_imports`) + Step 2a (노드 목록으로 resolve 대상 확인)
- 검증: Python 파일이 있으면 `len(edges) >= 0`, sidecar에 unresolved가 있으면 required fields 존재

동작:
- Step 2a의 노드 목록에서 `.py` 파일만 추출
- 각 `.py` 파일에 `extract_imports()` 호출
- 반환된 edges → graph core edges로 누적
- 반환된 sidecar → sidecar evidence로 누적

### Step 2c. Graph 조립

- 의존: Step 2a + Step 2b
- 검증: 반환 dict에 7개 required top-level fields 존재

```python
def build_canonical_graph(
    root: Path,
    graph_kind: str = "codebase_graph",
    excludes: set[str] | None = None,
    include_top_level_names: set[str] | None = None,
    exclude_top_level_names: set[str] | None = None,
) -> tuple[dict, list[dict]]:
    """
    Returns:
        graph_dict: normalized_graph.json 형태의 dict
        sidecar_evidence: sidecar evidence record list
    """
```

동작:
- `graph_kind`를 `ALLOWED_GRAPH_KINDS`로 validate, 불일치 시 `ValueError`
- Step 2a → nodes, Step 2b → edges + sidecar
- 조립:

```python
{
    "graph_id": f"codebase_graph_{root.name}_{timestamp}",
    "generated_at": iso8601_now,
    "source_scope": str(root),
    "graph_kind": graph_kind,
    "schema_version": "1",
    "nodes": nodes,
    "edges": edges,
}
```

### Step 3. Artifact 출력 함수

- 의존: Step 2c
- 검증: output_dir에 4개 파일 존재, 각 파일이 valid JSON/JSONL

```python
def write_canonical_artifacts(
    graph_dict: dict,
    sidecar_evidence: list[dict],
    output_dir: Path,
) -> dict:
    """
    Returns: graph_meta dict (for test verification)
    """
```

출력 파일:
- `normalized_graph.json` — `json.dumps(graph_dict, ensure_ascii=False, indent=2)`
- `nodes.jsonl` — `graph_dict["nodes"]`를 한 줄씩 `json.dumps(node)`
- `edges.jsonl` — `graph_dict["edges"]`를 한 줄씩 `json.dumps(edge)`
- `graph_meta.json`:

```python
{
    "graph_id": graph_dict["graph_id"],
    "schema_version": graph_dict["schema_version"],
    "generated_at": graph_dict["generated_at"],
    "source_scope": graph_dict["source_scope"],
    "graph_kind": graph_dict["graph_kind"],
    "artifact_paths": {
        "normalized_graph": "normalized_graph.json",
        "nodes": "nodes.jsonl",
        "edges": "edges.jsonl",
    },
    "trace_id": str(uuid4()),
    "artifact_location": str(output_dir),
}
```

sidecar routing:
- `sidecar_evidence`가 비어 있지 않으면 → `sidecar_evidence.jsonl` 출력 (한 줄씩)
- 비어 있어도 코드에 `if sidecar_evidence:` 분기가 존재해야 함 (routing path 증거)

에러 처리:
- `output_dir`이 없으면 `mkdir(parents=True, exist_ok=True)`
- 쓰기 실패 시 예외를 그대로 올림 (caller가 처리)

### Step 4. CLI 확장

- 의존: Step 2c + Step 3

`--canonical-output <dir>` 옵션 추가. 동작 매트릭스:

| `--output` | `--canonical-output` | coarse summary | canonical artifacts |
|---|---|---|---|
| 없음 | 없음 | stdout 출력 | 생성 안 함 |
| 있음 | 없음 | 파일 저장 | 생성 안 함 |
| 없음 | 있음 | stdout 출력 | `<dir>/`에 생성 |
| 있음 | 있음 | 파일 저장 | `<dir>/`에 생성 |

- 두 옵션은 독립적. 서로 suppress하지 않음
- `--canonical-output` 지정 시 `build_canonical_graph()` → `write_canonical_artifacts()` 호출
- 기존 `build_summary()` 흐름은 변경 없음

### Step 5. 테스트 추가

- 의존: Step 1 ~ Step 4 전부
- 기존 4개 테스트는 수정하지 않음

공통 fixture (각 테스트에서 `tempfile.TemporaryDirectory`로 생성):

```
tmp/
  src/
    app.py       → "import os\nfrom src import core\n"
    core.py      → "import json\n"
  config.yaml    → "key: value\n"
  README.md      → "# readme\n"
  notes.txt      → "note\n"
```

기대: nodes 3개 (app.py, core.py, config.yaml) + folders, edges 1개 (app→core IMPORTS), README.md와 notes.txt는 제외

테스트 목록:

| 테스트 | fixture | 검증 내용 |
|---|---|---|
| `test_canonical_graph_required_top_level_fields` | 공통 | graph_dict에 `graph_id`, `generated_at`, `source_scope`, `graph_kind`, `schema_version`, `nodes`, `edges` 존재 |
| `test_nodes_have_required_fields` | 공통 | 모든 node에 `id`, `kind`, `name` 존재 |
| `test_edges_have_required_fields` | 공통 | 모든 edge에 `src`, `dst`, `rel` 존재 |
| `test_graph_meta_required_fields` | 공통 + `write_canonical_artifacts` | graph_meta.json에 8개 required fields 존재 |
| `test_artifact_paths_point_to_real_files` | 공통 + write | `artifact_paths`의 각 값이 실제 파일로 존재 |
| `test_sidecar_routing_path_exists` | src/app.py에 `import nonexistent` 추가 | sidecar_evidence 리스트에 1건 이상, `evidence_kind="unresolved"` |
| `test_sidecar_evidence_required_fields` | 위와 동일 | sidecar record에 7개 required fields 존재 |
| `test_merged_graph_kind_allowed` | 공통 | `build_canonical_graph(root, graph_kind="merged_graph")` 성공, `graph_kind`가 `"merged_graph"` |
| `test_invalid_graph_kind_rejected` | 공통 | `build_canonical_graph(root, graph_kind="invalid")` → `ValueError` |
| `test_doc_only_files_excluded` | 공통 | node id에 `README.md`, `notes.txt` 없음, `config.yaml` 있음 |
| `test_cli_canonical_output` | 공통 | `--canonical-output <dir>` 실행 후 4개 파일 존재 |
| `test_cli_both_outputs` | 공통 | `--output <file> --canonical-output <dir>` 둘 다 생성 |
| `test_existing_coarse_summary_preserved` | 공통 | `build_summary()` 결과가 기존과 동일한 키 구조 |
| `test_parse_failure_goes_to_sidecar` | src/bad.py = `"def broken(:\n"` | sidecar에 `evidence_kind="warning"` 1건 |

### Step 의존 관계

```
Step 1 (extract_imports) ──┐
                           ├──→ Step 2b (엣지+sidecar) ──→ Step 2c (조립) ──→ Step 3 (출력) ──→ Step 4 (CLI)
Step 2a (노드 생성) ───────┘
                                                                                                    │
Step 5 (테스트) ←───────────────────────────────────────────────────────────────────────────────────┘
```

### 중간 검증 지점

| 시점 | 확인 내용 | 방법 |
|---|---|---|
| Step 1 완료 | `extract_imports`가 edges/sidecar를 올바르게 반환 | 단독 단위 테스트 |
| Step 2a 완료 | nodes에 required fields 존재, doc-only 파일 제외 | `assert all("id" in n for n in nodes)` |
| Step 2c 완료 | graph_dict에 7개 top-level fields 존재 | `assert set(required) <= set(graph_dict)` |
| Step 3 완료 | output_dir에 4개 파일 존재, valid JSON | `json.loads()` 성공 |
| Step 4 완료 | 기존 4개 테스트 pass (회귀 없음) | `python3.13 test_analyze_codebase.py` |
| Step 5 완료 | 전체 테스트 pass | `python3.13 test_analyze_codebase.py` |

### Step 6. 최종 검증

- `python3.13 scripts/test_analyze_codebase.py` — 기존 4개 + 새 테스트 전체 pass
- temp repo 대상 실제 `--canonical-output` 실행, 4개 artifact 파일 생성 확인
- `log.json`에 최종 테스트 결과 기록
