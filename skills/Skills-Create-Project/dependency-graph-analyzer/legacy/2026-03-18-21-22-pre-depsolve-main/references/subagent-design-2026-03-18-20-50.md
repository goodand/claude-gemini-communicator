# Subagent Design

## 목적
`dependency-graph-analyzer`를 실제 병렬 분석에 연결하기 위한 subagent 역할 정의.

## 권장 서브에이전트

### 1. dependency-graph-analyst
- 역할: repo의 import/module/package dependency graph 추출
- 입력: repo root, include/exclude, target language
- 출력: `edge_list.json`, `graph_summary.json`, `mermaid.mmd`
- 기본 성격: read-only

### 2. dependency-risk-auditor
- 역할: cycle, phantom dependency, layer violation, hub risk 해석
- 입력: edge list + depsolve output
- 출력: `risk_report.md`
- 기본 성격: read-only

### 3. dependency-slice-planner
- 역할: 병렬 분석 가능한 코드 슬라이스 설계
- 입력: graph summary + hub/cycle 정보
- 출력: `parallel_slices.json`, `fanout_plan.md`
- 기본 성격: read-only, planning only

## 공통 출력 계약
- `summary`
- `artifacts`
- `risks`
- `next_action`
- `confidence`

## 운영 규칙
- repo root 밖 쓰기 금지
- 산출물은 `plans/claude/graphs/` 또는 지정된 분석 디렉토리에만 저장
- raw graph와 human summary를 함께 남긴다
