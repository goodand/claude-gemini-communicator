# Codebase-Analysis Semantic Review Request

- recorded_at: `2026-03-23-11-27`
- packet_version: `0.1`
- task_id: `codebase-analysis-spec-v0-core-semantic-review`
- priority: `high`
- created_by: `Codex`

## Goal

`codebase-analysis`의 v0 core 구현 결과가 core spec의 고위험 semantic contract를 위반하지 않았는지 검토한다.

이 review는 lint 대체가 아니라 semantic review다.
다음 위반 여부를 증거 기반으로 판정한다.
- `merged_graph`가 analysis/orchestration graph 또는 외부 graph와 병합되었는가
- sidecar evidence가 graph core에 섞였는가
- export/view output이 source-of-truth처럼 취급되는가
- `DEFINES` 또는 class hierarchy/detail symbol relation이 v0 core로 승격되었는가
- optional slice-stage 구현이 현재 scope에 끼어들었는가
- 기존 coarse summary 기능이 제거되었는가
- 기존 테스트가 회귀했는가

## Why

이 항목들은 문자열 규칙만으로 탐지하기 어렵다.
의미 판단과 evidence trace가 필요한 review를 별도 bounded task로 분리한다.

## Allowed Paths

- `runs/codebase-analysis-spec-v0-core-semantic-review/plan.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/doc.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/report.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/log.json`

## Run Artifact Paths

- `runs/codebase-analysis-spec-v0-core-semantic-review/plan.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/doc.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/report.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/log.json`

## Context Files

- `references/codebase-analysis-spec-at2026-03-23-03-14.md`
- `references/codebase-analysis-development-playbook-at2026-03-23-03-36.md`
- `references/codebase-analysis-implementation-request-at2026-03-23-10-49.md`
- `checklist-forconsistency-evaluation/kb-grounding-checklist-at2026-03-23-02-17.md`
- `checklist-forconsistency-evaluation/doc-code-consistency-checklist-at2026-03-23-02-44.md`
- `scripts/analyze_codebase.py`
- `scripts/test_analyze_codebase.py`
- `runs/codebase-analysis-spec-v0-core-implementation/`

## Constraints

- review-only task로 수행한다.
- 코드, 문서, checklist, spec을 수정하지 않는다.
- 증거가 부족하면 추측하지 말고 `inconclusive`로 둔다.
- 판정은 `pass / fail / inconclusive`로 기록한다.
- 모든 판정은 파일 근거 또는 실행 근거를 남긴다.
- ambiguity가 생기면 넓게 해석하지 말고 spec의 보수적 해석을 따른다.

## Non-Goals

- 구현 보완 또는 리팩토링
- spec 재작성
- playbook 재정리
- optional slice-stage 설계 검토
- future symbol graph core 설계 검토
- export/view tool integration 품질 평가

## Review Scope

### P0 Hard-Fail Review Items

- `merged_graph`가 codebase graph 내부 layer 통합 표현을 넘어서 외부 graph 또는 analysis/orchestration graph와 병합되지 않았는지 확인
- sidecar evidence artifact와 graph core artifact의 역할 경계가 유지되는지 확인
- export/view output이 canonical source-of-truth를 대체하지 않는지 확인
- 기존 테스트가 깨지지 않았는지 확인

### P1 Strong-Fail Review Items

- optional slice-stage 관련 구현 분기가 추가되지 않았는지 확인
- `DEFINES`가 v0 core 최소 relation 집합으로 승격되지 않았는지 확인
- class hierarchy/detail symbol relation이 v0 core node/edge로 승격되지 않았는지 확인
- 기존 coarse summary 기능이 제거되지 않았는지 확인

### Warning Review Items

- run artifact가 `scripts/`가 아니라 `runs/` 아래에 기록되는지 확인
- `log`가 markdown이 아니라 `json`으로 남는지 확인

## Done Definition

- 각 P0/P1 항목에 대해 `pass / fail / inconclusive` 판정이 있다.
- 각 판정마다 file evidence 또는 실행 evidence가 기록된다.
- `report.md`에는 최종 findings가 심각도 순서로 정리된다.
- `log.json`에는 review에서 실제로 확인한 명령 또는 evidence trace가 남는다.
- evidence 부족으로 판정 불가인 항목은 `inconclusive`와 부족한 근거를 같이 남긴다.

## Required Checks

- `python3 scripts/test_analyze_codebase.py` 실행 가능 여부와 결과를 확인
- 구현 결과 artifact가 존재하면 `normalized_graph.json`, `nodes.jsonl`, `edges.jsonl`, `graph_meta.json`의 역할 경계를 확인
- `graph_meta.json.graph_kind`와 `artifact_paths`가 spec 의미와 맞는지 확인
- `scripts/analyze_codebase.py`에서 v0 core 최소 relation이 `IMPORTS` 중심으로 유지되는지 확인
- code path와 test path에서 `DEFINES`, class hierarchy/detail symbol relation, optional slice-stage branch가 현재 scope에 끼어들지 않았는지 확인
- coarse summary 관련 기존 동작이 유지되는지 확인
- run artifact 저장 위치가 `runs/codebase-analysis-spec-v0-core-semantic-review/`인지 확인

## Deliverables

- `runs/codebase-analysis-spec-v0-core-semantic-review/plan.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/doc.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/report.md`
- `runs/codebase-analysis-spec-v0-core-semantic-review/log.json`

## Handoff Notes

- 이 문서는 구현 요청이 아니라 semantic review 요청이다.
- 수정 제안은 `report.md`에 남기되, 직접 패치는 하지 않는다.
- `report.md`는 findings-first로 작성한다.
- `log`는 `json`, `plan/doc/report`는 markdown으로 남긴다.
- source handoff 문서는 `references/`에 유지하고, 실행 산출물만 `runs/` 아래에 남긴다.
