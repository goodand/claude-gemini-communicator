# Contract-To-Concept Canonical Design

- ver: `v0.1.0`
- generated_at: `2026-03-16-18-06`
- canonical_role: `contract-to-concept-mapper의 현재 채택 설계를 고정하는 canonical KB`
- source_of_truth_for: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-14-03.md`

## Canonical Design Takeaways

- 이 skill의 핵심 목적은 `실행 계약 공간 -> 개념 공간` 복원이다.
- `개념 -> 실행 계약` 문제와 혼동하지 않는다.
- codebase 정합성 평가 도구와 직접 동일시하지 않는다.
- 단순 summarizer가 아니라 `설명 가능한 lifting system`으로 본다.
- 기본 입력은 `checklist`, `task`, `schema`, `CLI contract`, `함수 시그니처`다.
- checklist를 1급 입력으로 다룬다.
- `정합성 평가용 checklist`와 `구현용 checklist`를 구분한다.
- 최소 출력은 `concept summary`, `boundary description`, `semantic relation map`이다.
- Mermaid / pseudocode는 주요 render target이다.
- 벡터 인덱스/벡터 값은 보조 출력이다.
- 핵심 단계는 `collect contracts -> segment units -> lift concepts -> render concepts`다.
- `contract unit`과 `concept unit`의 중간 계층이 필요하다.
- render 이전에 relation / boundary 정리가 선행된다.
- traceability 없는 자연어 요약만 남기는 출력은 실패 사례로 본다.
- uncertainty 또는 weak support를 표시할 수 있어야 한다.
- project context가 부족할 때 과도한 개념 복원을 경계한다.
- 이 skill은 코드 수정 도구가 아니다.
- 이 skill은 실행 로그 수집기가 아니다.
- 외부 검색 자동화 자체가 목적이 아니다.
- `semantic-slice-mapper`, `execution-contract-mapper`, `evidence-trace-auditor`와 책임이 다르다.

## Current Implementation Target

- 현재는 scaffold 단계다.
- future output과 current capability를 혼동하지 않는다.
- 현재는 traceable lifting 구조를 먼저 고정하는 단계다.
- 현재 consistency checklist는 이 canonical KB를 source of truth로 사용한다.
