# kb_to_consistency_check.py 구현용 체크리스트

> 위치: `knowledge_base` 아래, `codebase` 위
> 역할: `kb-to-consistency-consistency-checklist-at2026-03-16-15-55.md`를 실제 구현 항목과 테스트 계획으로 내린다.
> 선행조건: `checklist-forconsistency-evaluation/kb-to-consistency-consistency-checklist-at2026-03-16-15-55.md` 작성 및 1차 검토 완료

## A. Scope 고정

- [ ] v0.1은 완전 자동 semantic judge가 아니라 `candidate traceability gap detector`로 고정한다
- [ ] 비교 단위는 `KB canonical unit`과 `consistency checklist item`으로 고정한다
- [ ] 결과는 최종 truth가 아니라 human review queue를 포함한 후보 진단으로 제한한다

## B. Input / Parsing

- [ ] `--kb`와 `--checklist` 입력 계약을 정한다
- [ ] KB에서 canonical unit을 추출하는 규칙을 정한다
- [ ] checklist item을 섹션/항목 단위로 분해하는 규칙을 정한다
- [ ] v0.1은 `anchor/keyword + section-level comparison`으로 시작한다

## C. Comparison Direction

- [ ] `forward` 비교를 구현한다
  - KB unit이 checklist에 반영되었는가
- [ ] `backward` 비교를 구현한다
  - checklist item이 KB 근거를 갖는가
- [ ] artifact-level과 object-level을 구분하는 내부 구조를 둔다

## D. Verdict Taxonomy

- [ ] 최소 verdict를 구현한다
  - `covered`
  - `missing_from_checklist`
  - `unsupported_in_checklist`
  - `scope_inflation`
  - `boundary_loss`
- [ ] 각 verdict에 KB/checklist 근거를 함께 남긴다

## E. Metrics

- [ ] `coverage_ratio` 계산
- [ ] `unsupported_item_ratio` 계산
- [ ] `traceability_ratio` 계산
- [ ] `boundary_preservation_ratio` 계산
- [ ] 단일 종합 점수만 출력하지 않는다

## F. Output

- [ ] machine-readable JSON 출력 설계
  - 예: `coverage.json`
- [ ] human-readable markdown report 출력 설계
  - 예: `coverage_report.md`
- [ ] `human_review_queue` 또는 동등 필드를 둔다
- [ ] missing / unsupported / inflation / boundary loss를 분리해 출력한다

## G. Guardrail / Explainability

- [ ] heuristic mapping 결과를 최종 truth처럼 단정하지 않는다
- [ ] traceability matrix 또는 동등한 per-unit mapping 테이블을 남긴다
- [ ] ambiguity 높은 항목은 human review 대상임을 표시한다
- [ ] checklist 포맷에 `derived_from` / `evidence`가 아직 없다는 한계를 출력/문서에 드러낸다

## H. TDD 계획

- [ ] KB unit 누락 시 `missing_from_checklist`가 나오는 fixture 준비
- [ ] KB 근거 없는 checklist 항목 시 `unsupported_in_checklist`가 나오는 fixture 준비
- [ ] guardrail 누락 시 `boundary_loss`가 나오는 fixture 준비
- [ ] checklist가 더 강한 요구를 추가한 경우 `scope_inflation`이 나오는 fixture 준비
- [ ] JSON/markdown output schema를 검증하는 테스트 작성
