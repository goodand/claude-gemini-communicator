# slice-experiment-lab 정합성 평가용 체크리스트

## A. Identity

- [ ] 이 skill은 smoke runner가 아니라 experiment evaluator인가
- [ ] 이 skill은 contract-oriented implementation slice의 반복 실험 루프를 다루는가

## B. Boundary

- [ ] smoke command 실행 자체는 비목표인가
- [ ] evidence ledger 계산 자체는 `evidence-trace-auditor` 책임으로 남는가
- [ ] before/after diff 계산 자체는 `baseline-diff-lab` 책임으로 남는가

## C. Input Bundle

- [ ] `contract_artifact`, `valid_artifact`, `invalid_artifact`, `quick_validate_status`가 canonical input인가
- [ ] triad artifact는 실제 파일 path여야 하는가

## D. Decision Semantics

- [ ] contract artifact 존재 + valid smoke status + invalid smoke status + quick_validate pass가 함께 맞을 때만 `ready_for_next_slice`인가
- [ ] 위 조건 중 하나라도 깨지면 `hold_current_slice`인가

## E. Output Contract

- [ ] 결과에 `bundle_status`, `workflow_status`, `gaps`가 들어가는가
- [ ] JSON artifact와 Markdown summary를 함께 남길 수 있는가

## F. Source Of Truth Order

- [ ] source of truth는 hybrid KB의 `Canonical Design Takeaways`인가
- [ ] workflow status는 triad와 `quick_validate_status`만으로 derived 되는가
