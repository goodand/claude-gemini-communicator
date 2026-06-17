# slice-experiment-lab knowledge base

- kb_profile: `hybrid_kb`
- reference_acquisition_mode: `internal_codebase_only`
- source_family:
  - `skill-creation-process/references/phase-guide.md`
  - `skill-creation-process/references/execution-evidence-pattern-at2026-03-17-04-03.md`
  - `dependency-slice-planner/checklist-forimplementation/implementation-checklist-at2026-03-19-00-01.md`
  - `dependency-slice-planner/references/vertical-slice-slice-manifest-contract-at2026-03-19-00-03.md`
  - `dependency-slice-planner/references/vertical-slice-handoff-packet-contract-at2026-03-19-00-08.md`
  - `dependency-slice-planner/references/vertical-slice-inventory-snapshot-contract-at2026-03-19-00-18.md`
  - `dependency-slice-planner/references/vertical-slice-slice-seed-candidates-contract-at2026-03-19-00-22.md`
  - `evidence-trace-auditor/SKILL.md`
  - `baseline-diff-lab/SKILL.md`

## Problem Framing

여러 skill을 만들면서 반복된 실험 루프는 거의 같았다.

- contract emit/validate를 먼저 구현한다
- positive/invalid sample로 smoke를 돌린다
- JSON/MD artifact를 `references/`에 남긴다
- `quick_validate`로 구조 정합성을 다시 본다
- 현재 slice가 `ready`인지 `hold`인지 판단한다

이 패턴은 공용 skill 제작 절차보다 좁고, `baseline-diff-lab`보다도 더 앞단의 contract-slice 실험 루프다.

## Scope

이 skill은 다음을 담당한다.

- contract-oriented implementation slice의 실험 bundle 형식 고정
- `contract / valid / invalid` artifact와 `quick_validate_status`를 함께 읽는 평가
- `ready_for_next_slice` 또는 `hold_current_slice` 판단

이 skill은 다음을 담당하지 않는다.

- smoke command 실행 자체
- raw evidence 수집 자체
- before/after diff 계산 자체
- 실제 다음 slice 구현 자체

## Canonical Input Bundle

실험 bundle은 최소 다음을 포함한다.

- `skill_name`
- `current_slice`
- `contract_artifact`
- `valid_artifact`
- `invalid_artifact`
- `quick_validate_status`

## Decision Logic

`ready_for_next_slice`는 아래가 모두 맞을 때만 낸다.

- contract artifact가 존재한다
- valid artifact가 존재하고 `status == valid`
- invalid artifact가 존재하고 `status == invalid`
- `quick_validate_status == passed`

그 외는 `hold_current_slice`다.

## Canonical Outputs

- `experiment_bundle_contract`
- `experiment_bundle_evaluation`
- `artifact_triad_naming_suggestion`
- `quick_validate_capture`
- `smoke_command_capture`

평가 결과에는 최소 아래가 있어야 한다.

- `bundle_status`
- `workflow_status`
- `current_slice`
- `gaps`

## Canonical Design Takeaways

- 공용 process는 `KB -> checklist -> TDD -> smoke -> evidence`까지만 강하게 다룬다.
- `현재 contract slice가 준비됐는지` 판단은 skill 내부 실험 루프로 분리하는 편이 낫다.
- `contract / valid / invalid` triad와 `quick_validate_status`는 함께 읽어야 readiness 판단을 안정적으로 할 수 있다.
- 이 skill은 smoke runner가 아니라 experiment evaluator여야 한다.

## Current Implementation Target

v0.2는 `experiment_bundle_contract`, `evaluate-experiment-bundle`, `artifact_triad_naming_helper`, `quick_validate_capture_adapter`, `smoke_command_capture_adapter`, `strict_warning_policy_gate`까지 구현한다.
