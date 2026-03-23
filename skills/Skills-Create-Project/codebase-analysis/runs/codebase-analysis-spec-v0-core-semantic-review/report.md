# Semantic Review Report — codebase-analysis-spec-v0-core-semantic-review

- recorded_at: `2026-03-23`
- task_id: `codebase-analysis-spec-v0-core-semantic-review`
- review_target: `scripts/analyze_codebase.py` + `scripts/test_analyze_codebase.py`
- base_commit: `6873d61` (worktree branch: `feat/codebase-analysis-spec-v0-core-implementation`)
- reviewer: `claude-sonnet-4-6`

---

## Summary

전체 판정 요약:

| 항목 | 심각도 | 판정 |
|---|---|---|
| P0-1. merged_graph 외부 병합 없음 | P0 | PASS |
| P0-2. sidecar/graph core 역할 경계 | P0 | PASS |
| P0-3. export/view가 source-of-truth 대체 않음 | P0 | PASS |
| P0-4. 기존 테스트 회귀 없음 | P0 | PASS |
| P1-5. optional slice-stage 분기 없음 | P1 | PASS |
| P1-6. DEFINES 미승격 | P1 | PASS |
| P1-7. class hierarchy/detail symbol 미승격 | P1 | PASS |
| P1-8. coarse summary 기능 보존 | P1 | PASS |
| W-9. run artifact 위치 | Warning | PASS |
| W-10. log가 json으로 저장됨 | Warning | PASS |

모든 항목 PASS. 중대 위반 없음.

---

## P0 Hard-Fail Review Items

### P0-1. `merged_graph`가 외부 graph 또는 analysis/orchestration graph와 병합되지 않았는지

**판정: PASS**

**Evidence:**

1. `analyze_codebase.py:26` — `ALLOWED_GRAPH_KINDS = {"codebase_graph", "analysis_graph", "merged_graph"}`. `merged_graph`는 허용 `graph_kind` 값의 하나로만 정의됨.

2. `analyze_codebase.py:354-394` — `build_canonical_graph()` 함수는 `graph_kind` 파라미터를 `ALLOWED_GRAPH_KINDS`로 validate만 하고, 다른 graph dict를 인수로 받거나 병합하는 코드 경로가 없음. `merged_graph`를 지정해도 노드/엣지 수집 절차는 `codebase_graph`와 동일함.

3. Runtime 검증: `build_canonical_graph(root, graph_kind='merged_graph')`와 `build_canonical_graph(root, graph_kind='codebase_graph')` 결과 비교 — `nodes` 길이 동일, `edges` 길이 동일, extra 키 없음. `graph_kind` 필드 값만 다름.

4. 코드 전체에서 `orchestration`, `merge_graph`(두 graph dict 결합) 등 외부 graph 병합 패턴 없음 (`grep` 확인: `merge` 키워드는 `merge_excluded_dir_names`, `merge_name_filter` 유틸리티 함수 이름에만 사용됨).

spec 근거: `codebase-analysis-spec-at2026-03-23-03-14.md:88` — "`merged_graph`는 codebase graph 내부 layer 통합 표현이며 analysis/orchestration graph와 병합하지 않는다."

---

### P0-2. sidecar evidence artifact와 graph core artifact의 역할 경계가 유지되는지

**판정: PASS**

**Evidence:**

1. `analyze_codebase.py:171-248` — `extract_imports()`는 두 개의 독립 리스트를 반환: `edges` (graph core용), `sidecar` (sidecar evidence용). 두 리스트에 담기는 dict 구조가 완전히 다름.
   - edges: `{"src", "dst", "rel", "source_tool", "confidence"}`
   - sidecar: `{"evidence_kind", "subject_anchor", "summary", "source_path", "evidence_path", "reason", "confidence"}`

2. `analyze_codebase.py:369-393` — `build_canonical_graph()`는 nodes와 edges를 `graph_dict`에, sidecar_evidence를 별도 리스트로 반환. 두 가지가 같은 컨테이너에 담기지 않음.

3. `analyze_codebase.py:397-457` — `write_canonical_artifacts()`는 `graph_dict`와 `sidecar_evidence`를 별개 파라미터로 받아, `normalized_graph.json`, `nodes.jsonl`, `edges.jsonl` (graph core), `sidecar_evidence.jsonl` (sidecar)를 각각 별도 파일로 씀.

4. Runtime 검증: `build_canonical_graph()`에 unresolved import가 있는 fixture를 주면 — `graph['nodes']` 필드에 `evidence_kind` 없음, `graph['edges']`에 `evidence_kind` 없음, sidecar에 `evidence_kind='unresolved'` 3건 존재.

spec 근거: `codebase-analysis-spec-at2026-03-23-03-14.md:47-49` — "graph core에는 weak signal을 넣지 않고, `unresolved`, `risk`, `warning`, `ownership_exception`, `weak_signal` evidence kind는 sidecar evidence로 분기한다."

---

### P0-3. export/view output이 canonical source-of-truth를 대체하지 않는지

**판정: PASS**

**Evidence:**

1. `analyze_codebase.py` 전체에 export/view 도구 연동 코드 없음 (`grep` 확인: `normalized_graph`, `export`, `view`, `render` 관련 코드는 파일 쓰기 경로만 존재).

2. `write_canonical_artifacts()`는 canonical artifact를 `output_dir`에 쓰는 것이 전부. 이를 읽어 다른 형식으로 변환하거나 대체하는 코드 경로 없음.

3. CLI에 `--canonical-output` 옵션만 있고, export/view 형식 변환 옵션 없음. `normalized_graph.json`이 항상 primary artifact로 생성됨.

spec 근거: `codebase-analysis-spec-at2026-03-23-03-14.md:86` — "source of truth는 visualization format이 아니라 canonical graph artifact다."
canonical-graph-artifact-contract-at2026-03-20-21-04.md:106 — "Renderers and databases consume exports derived from canonical artifacts. They do not replace canonical artifacts."

---

### P0-4. 기존 테스트가 깨지지 않았는지

**판정: PASS**

**Evidence:**

실행 결과:
```
python3.13 .../scripts/test_analyze_codebase.py
........................
----------------------------------------------------------------------
Ran 24 tests in 0.217s

OK
```

기존 4개 테스트 (`AnalyzeCodebaseTests`) — `test_build_summary_supports_custom_exclude_dir_names`, `test_cli_output_creates_parent_directory`, `test_build_summary_reports_python_parse_failures`, `test_cli_include_and_exclude_top_level_controls_scope` — 모두 포함됨. 전체 24개 테스트 OK.

---

## P1 Strong-Fail Review Items

### P1-5. optional slice-stage 관련 구현 분기가 추가되지 않았는지

**판정: PASS**

**Evidence:**

`analyze_codebase.py` 전체에 `slice`, `slice_seed`, `parallel_slices`, `runtime_overlay`, `fan_in`, `handoff` 관련 코드 없음 (`grep` 확인: `slice_seed`, `parallel_slices`, `runtime_overlay` 키워드 — 0건).

`test_analyze_codebase.py` 전체에도 slice-stage 관련 테스트 없음.

spec 근거: `codebase-analysis-spec-at2026-03-23-03-14.md:91` — "optional slice stage는 이번 skill의 공식 범위와 평가 대상에 포함하지 않는다."

---

### P1-6. `DEFINES`가 v0 core 최소 relation 집합으로 승격되지 않았는지

**판정: PASS**

**Evidence:**

1. `analyze_codebase.py` 전체에 `DEFINES` 문자열 없음 (`grep` 확인: 0건).

2. `test_analyze_codebase.py:331-338` — `test_v0_core_relation_is_imports_centered` 테스트: "모든 edge의 `rel`이 `IMPORTS`여야 한다" — PASS.

3. `extract_imports()`는 `ast.Import` / `ast.ImportFrom` 노드에서 `rel="IMPORTS"` 엣지만 생성. 다른 relation 생성 코드 경로 없음.

spec 근거: `codebase-analysis-spec-at2026-03-23-03-14.md:90` — "`DEFINES`는 v0 core relation 최소 집합에 포함하지 않는다."

---

### P1-7. class hierarchy/detail symbol relation이 v0 core node/edge로 승격되지 않았는지

**판정: PASS**

**Evidence:**

1. `analyze_codebase.py` 전체에 `INHERITS`, `IMPLEMENTS`, `class_hierarchy`, `parent_class`, `ClassDef`, symbol locator 패턴 없음 (`grep` 확인: 0건).

2. `collect_nodes()`는 File과 Folder 두 가지 `kind`만 생성. 클래스/함수/심볼 수준 노드 없음.

3. `extract_imports()`는 `ast.Import` / `ast.ImportFrom` 계열만 처리. `ast.ClassDef`, `ast.FunctionDef` 등 symbol 계층 처리 없음.

4. Runtime 검증: fixture 실행 결과 `node kinds = {'File', 'Folder'}`, `edge rels = set()` (내부 import 없는 경우) 또는 `{'IMPORTS'}` — class/symbol 관련 kind 없음.

spec 근거: `codebase-analysis-spec-at2026-03-23-03-14.md:44` — "class structure evidence는 v0 core의 1급 node/edge로 채택하지 않고, 세부 symbol 구조는 future symbol graph core의 우선 수용 대상으로 남긴다."

---

### P1-8. 기존 coarse summary 기능이 제거되지 않았는지

**판정: PASS**

**Evidence:**

1. `analyze_codebase.py:87-129` — `build_summary()` 함수 존재. 구조 변경 없음.

2. CLI `main()` (`analyze_codebase.py:460-514`) — 기존 `build_summary()` 호출 경로 보존. `--canonical-output`이 없어도 coarse summary는 항상 실행됨.

3. `test_analyze_codebase.py:307-319` — `test_existing_coarse_summary_preserved`: `build_summary()`의 11개 expected_key 구조 확인 — PASS.

4. Runtime 검증: `build_summary()` 직접 호출 시 expected 11개 키 모두 존재 확인.

5. `test_cli_both_outputs` — `--output`과 `--canonical-output` 동시 지정 시 coarse summary 파일도 생성됨 — PASS.

spec 근거: implementation-request-at2026-03-23-10-49.md:137 — "기존 coarse summary만이 아니라 canonical artifact triple과 graph_meta.json 생성을 지원한다." (coarse summary를 보존하면서 추가하는 것이 목표)

---

## Warning Review Items

### W-9. run artifact가 `scripts/`가 아니라 `runs/` 아래에 기록되는지

**판정: PASS**

**Evidence:**

`scripts/` 디렉토리 내용:
```
scripts/
  analyze_codebase.py
  test_analyze_codebase.py
  __pycache__/
```

run artifact (`plan.md`, `doc.md`, `log.json`)는 `runs/codebase-analysis-spec-v0-core-implementation/` 아래에 존재. `scripts/`에 run artifact 없음.

---

### W-10. `log`가 markdown이 아니라 `json`으로 남는지

**판정: PASS**

**Evidence:**

`runs/codebase-analysis-spec-v0-core-implementation/log.json` — JSON array 형식, 3개 entries, `json.load()` 파싱 성공.

`runs/codebase-analysis-spec-v0-core-implementation/` 내 `.md` 파일: `plan.md`, `doc.md` (log 파일 아님). `log.md` 또는 `log.txt` 없음.

---

## Observations (수정 불필요, 참고용)

1. **`merged_graph` 구현 범위**: 현재 `merged_graph`는 `graph_kind` 필드 값만 변경하고 내부 layer 통합 로직은 없음. 이는 v0 core 최소 구현으로 spec-compliant이나, 향후 codebase graph 내부 layer 실제 통합이 필요할 때 확장이 필요함. 이번 review 범위 밖.

2. **`report.md` 미생성**: `runs/codebase-analysis-spec-v0-core-implementation/`에 `report.md`가 없음 (`plan.md`, `doc.md`, `log.json`만 있음). implementation request Done Definition에는 `report.md`가 deliverable로 명시됨. 이 review의 판정 대상이 아닌 관찰 사항이나, 후속 확인 여지 있음.

3. **relative import resolution**: `_resolve_module_to_file()`의 relative import 처리 (`level > 0`) 로직이 존재하며 테스트(`test_extract_imports_resolves_internal`, `test_sidecar_routing_when_empty`)에서 검증됨.

---

## Conclusion

P0/P1 항목 전체 PASS, Warning 항목 전체 PASS. semantic contract 위반 없음.
