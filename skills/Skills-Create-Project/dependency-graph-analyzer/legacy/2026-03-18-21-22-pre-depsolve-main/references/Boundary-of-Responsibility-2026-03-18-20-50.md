# Boundary of Responsibility

## dependency-graph-analyzer가 소유하는 것
- include/exclude 범위 정의
- dependency edge 추출 결과
- graph summary와 risk classification
- Mermaid/JSON/GraphML 같은 render target
- parallel slice 후보 산출

## 읽기만 하는 것
- 코드베이스 원본 파일
- 기존 architecture docs
- package manifest (`pyproject.toml`, `package.json`, `requirements.txt` 등)
- 논문/체크리스트/설계 문서

## 소유하면 안 되는 것
- 자동 코드 수정
- dependency install/remove
- build/runtime orchestration
- merge readiness 판정
- reviewer findings의 최종 승인

## subagent와의 관계
- dependency-graph-analyzer는 상위 orchestration 없이도 단독 분석 가능해야 한다
- subagent는 analyzer 결과를 소비할 수 있어야 하며, analyzer 자체가 subagent controller 역할까지 전부 떠안으면 안 된다
- v0.1에서는 `graph extraction + risk report + parallel_slices`까지만 소유한다
