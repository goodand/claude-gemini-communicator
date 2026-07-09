# slice-experiment-lab 구현용 체크리스트

> 목적: contract slice 실험 bundle을 읽고 next-slice gate를 내리는 재사용 실험 skill을 만든다.
> 선행조건: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-19-00-45.md`

## A. Source Lock

- [ ] `knowledge_bases/slice-experiment-lab-knowledge_base-at2026-03-19-00-45.md`를 단일 source of truth로 읽는다
- [ ] first implementation target은 experiment bundle contract와 evaluator로 고정한다

## B. First Vertical Slice

- [ ] 첫 slice를 `experiment_bundle_contract`로 고정한다
- [ ] `skill_name`, `current_slice`, `contract_artifact`, `valid_artifact`, `invalid_artifact`, `quick_validate_status`, `next_slice_candidate`를 required field로 고정한다
- [ ] `quick_validate_status`는 최소 `passed|failed`를 허용한다

## C. Evaluation Slice

- [ ] `evaluate-experiment-bundle`는 triad artifact와 quick_validate 상태를 함께 읽는다
- [ ] 결과는 `bundle_status`와 `workflow_status`를 분리한다
- [ ] next-slice 판단은 `ready_for_next_slice` 또는 `hold_current_slice`로 고정한다

## D. Script + TDD

- [ ] `scripts/slice_experiment_lab.py`를 만든다
- [ ] 대응 TDD 파일을 먼저 만든다
- [ ] `--help`, exit code, stdout/stderr 계약을 고정한다

## E. Smoke + Evidence

- [ ] positive bundle sample 1개를 만든다
- [ ] hold 또는 invalid bundle sample 1개 이상을 만든다
- [ ] contract JSON/MD를 남긴다
- [ ] evaluation JSON/MD를 `references/`에 남긴다

## F. Follow-up

- [x] `quick_validate_capture_adapter`를 구현했다
- [x] `smoke_command_capture_adapter`를 구현했다
- [x] `artifact_triad_naming_helper`를 구현했다
- [x] `quick_validate_artifact_bundle_bridge`를 구현했다
- [x] `captured_smoke_to_bundle_adapter`를 구현했다
- [x] `strict_warning_policy_gate`를 구현했다

## G. Current Progress

- [x] KB를 만들었다
- [x] consistency checklist를 만들었다
- [x] implementation checklist를 만들었다
- [x] `emit-experiment-bundle-contract`를 구현했다
- [x] `evaluate-experiment-bundle`를 구현했다
- [x] `artifact_triad_naming_helper`를 구현했다
- [x] `quick_validate_capture_adapter`를 구현했다
- [x] `smoke_command_capture_adapter`를 구현했다
- [x] `quick_validate_artifact_bundle_bridge`를 구현했다
- [x] `captured_smoke_to_bundle_adapter`를 구현했다
- [x] `strict_warning_policy_gate`를 구현했다
