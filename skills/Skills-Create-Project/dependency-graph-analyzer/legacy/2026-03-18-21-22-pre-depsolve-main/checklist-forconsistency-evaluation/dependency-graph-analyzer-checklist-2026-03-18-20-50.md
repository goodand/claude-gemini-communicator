# dependency-graph-analyzer Consistency Checklist

## A. 정체성
- [ ] 이 skill은 dependency graph 추출/분석/정규화가 주목적이다
- [ ] runtime orchestration과 코드 수정은 범위 밖이다
- [ ] static dependency graph와 runtime call graph를 구분한다

## B. 입력
- [ ] repo root를 명시적으로 받는다
- [ ] include/exclude 규칙이 있다
- [ ] Python/JS/혼합 repo 여부를 구분한다
- [ ] manifest level dependency와 source import dependency를 분리한다

## C. 출력
- [ ] `edge_list.json`이 있다
- [ ] `graph_summary.json`이 있다
- [ ] `risk_report.md`가 있다
- [ ] `mermaid.mmd` 또는 동등한 시각화 출력이 있다
- [ ] `parallel_slices.json`이 있다

## D. 분석 품질
- [ ] cycle을 감지한다
- [ ] hub module을 식별한다
- [ ] phantom/undeclared dependency를 감지한다
- [ ] connected component 또는 SCC를 구분한다
- [ ] graph health를 Tree/DAG/cyclic 류로 분류한다

## E. 병렬 분석 준비도
- [ ] 그래프를 subagent 단위 슬라이스로 자를 수 있다
- [ ] 서로 강하게 결합된 SCC는 한 슬라이스로 유지한다
- [ ] 독립 component는 병렬 분할 가능하게 표시한다
- [ ] hub module은 별도 검토 대상으로 표시한다

## F. 문서-코드 정합성
- [ ] 로컬 reference skill들과 역할이 충돌하지 않는다
- [ ] `depsolve-analyzer`와 `codebase-architecture-mapper`를 어떻게 재사용할지 문서에 적혀 있다
- [ ] render MCP는 선택 기능으로 분리되어 있다

## G. v0.1 최소 합격선
- [ ] 읽기 전용 분석만으로 동작한다
- [ ] JSON + Mermaid 두 출력이 있다
- [ ] cycle/hub/phantom 최소 3종 리스크를 다룬다
- [ ] 병렬 분석용 `parallel_slices.json`을 만든다
