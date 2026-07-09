# kb_to_consistency_check.py 정합성 평가 체크리스트

> 목적: `knowledge_bases/kb-to-consistency-check-knowledge_base-at2026-03-16-15-44.md`가 정의한 평가 기준이 `kb_to_consistency_check.py` 설계에 제대로 내려오는지 구현 전에 점검한다.
> 우선순위: `knowledge_base <-> 정합성 평가용 checklist`
> 주의: 이 문서는 `구현용 checklist`보다 먼저 고정되는 상위 checklist다.

## A. Role / Scope 정합

- [ ] **A-01**: 이 대상은 완전 자동 semantic judge가 아니라 `candidate traceability gap detector`로 정의돼 있다
- [ ] **A-02**: 비교 대상이 `knowledge_base 전체 vs checklist 전체`가 아니라 `KB canonical unit vs consistency checklist item`으로 분리돼 있다
- [ ] **A-03**: 구현용 checklist 동기화 문제와 혼동되지 않는다
- [ ] **A-04**: codebase 구현 검증기와 직접 동일시되지 않는다

## B. Comparison Direction 정합

- [ ] **B-01**: `forward` 비교가 정의돼 있다
  - KB unit이 checklist에 반영되었는가
- [ ] **B-02**: `backward` 비교가 정의돼 있다
  - checklist item이 KB 근거를 갖는가
- [ ] **B-03**: forward만 있고 backward가 빠지지 않는다
- [ ] **B-04**: backward만 있고 coverage 관점이 빠지지 않는다

## C. Canonical Unit 정합

- [ ] **C-01**: KB를 canonical unit으로 나눌 필요가 반영돼 있다
- [ ] **C-02**: checklist item도 별도 비교 단위로 다뤄진다
- [ ] **C-03**: artifact-level과 object-level을 구분한다
- [ ] **C-04**: section-level comparison으로 시작하되 항목-level 확장 가능성이 남아 있다

## D. Verdict Taxonomy 정합

- [ ] **D-01**: 최소 판정 유형에 `covered`가 있다
- [ ] **D-02**: 최소 판정 유형에 `missing_from_checklist`가 있다
- [ ] **D-03**: 최소 판정 유형에 `unsupported_in_checklist`가 있다
- [ ] **D-04**: 최소 판정 유형에 `scope_inflation`이 있다
- [ ] **D-05**: 최소 판정 유형에 `boundary_loss`가 있다

## E. Metrics 정합

- [ ] **E-01**: `coverage_ratio`를 계산하거나 동등 지표가 있다
- [ ] **E-02**: `unsupported_item_ratio`를 계산하거나 동등 지표가 있다
- [ ] **E-03**: `traceability_ratio`를 계산하거나 동등 지표가 있다
- [ ] **E-04**: `boundary_preservation_ratio`를 계산하거나 동등 지표가 있다
- [ ] **E-05**: 단일 종합 점수만으로 끝내지 않는다

## F. Explainability / Traceability 정합

- [ ] **F-01**: checklist 판정에 KB 근거를 연결할 수 있어야 한다
- [ ] **F-02**: per-unit table 또는 동등한 traceability matrix 개념이 있다
- [ ] **F-03**: ambiguity가 높은 항목은 human review queue로 보낸다
- [ ] **F-04**: traceability 없는 결과를 canonical output으로 채택하지 않는다

## G. Output Contract 정합

- [ ] **G-01**: machine-readable JSON 출력이 있다
- [ ] **G-02**: human-readable markdown report 출력이 있다
- [ ] **G-03**: missing / unsupported / inflation / boundary loss를 분리해 보여준다
- [ ] **G-04**: human review needed 항목을 별도 출력할 수 있다

## H. v0.1 Guardrail 정합

- [ ] **H-01**: v0.1은 `anchor/keyword + section-level comparison`으로 시작한다
- [ ] **H-02**: 현재 checklist 포맷에 `derived_from` / `evidence`가 없다는 한계를 숨기지 않는다
- [ ] **H-03**: 완전한 traceability matrix가 아직 어렵다는 점이 드러난다
- [ ] **H-04**: heuristic mapping 결과를 최종 truth로 단정하지 않는다

## I. 최종 판정

- [ ] **I-01**: 이 checklist는 KB의 canonical slice를 충분히 operationalize한다
- [ ] **I-02**: 구현 전 단계에서 봐야 할 주요 risk가 coverage / unsupported / boundary / inflation으로 정리된다
- [ ] **I-03**: 다음 단계 구현용 checklist는 이 문서를 source of truth로 삼아야 한다
