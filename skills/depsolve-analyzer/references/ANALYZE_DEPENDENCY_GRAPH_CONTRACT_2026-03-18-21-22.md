# analyze_dependency_graph Contract

## 목적
`depsolve-analyzer`의 하위 계약으로 mixed codebase의 dependency graph를 MECE하게 추출한다.

## 입력
- `project_root`
- `include_paths`
- `exclude_paths`
- `ecosystem`: `python | javascript | mixed`
- `render_format`: `json | markdown | mermaid`
- `region_strategy`: `source | package | hybrid`

## 출력
- `graph_summary.json`
- `edge_list.json`
- `risk_report.md`
- `mermaid.mmd` 또는 동등 시각화
- `parallel_slices.json`

## 필수 분석 축
1. package/manifest dependency
2. source import dependency
3. wrapper indirection (`runpy`, generated wrapper, monkeypatch wrapper)
4. path mutation (`sys.path.insert`, `sys.path.append`, file-loader import)
5. region crossings
6. hub concentration
7. SCC/cycle status

## 경계 규칙
- static dependency graph와 runtime flow graph는 분리한다
- 단순 import graph와 실제 wrapper-aware graph를 구분한다
- 결과는 hotspot map과 verified graph를 혼동하지 않는다

## 최소 합격선
- phantom/cycle/diamond 중 최소 3종 리스크를 리포트한다
- mixed repo에서 manifest root가 여러 개면 boundary drift를 분리해서 다룬다
- 병렬 분석용 `parallel_slices.json`을 생성한다
