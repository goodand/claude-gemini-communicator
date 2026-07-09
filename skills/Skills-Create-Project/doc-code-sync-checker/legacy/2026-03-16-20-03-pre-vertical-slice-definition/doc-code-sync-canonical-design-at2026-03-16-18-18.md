# canonical design Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-16-18-18`
- canonical_role: `doc-code-sync-checker의 현재 채택 설계 source of truth`
- canonical_slice: `이 문서 전체`
- source_research_kb: `doc-code-sync-checker-knowledge_base-at2026-03-16.md`

## Document Map

| 문서 | 역할 |
|---|---|
| [SKILL.md](../SKILL.md) | 라우터 · 읽기 순서 |
| [doc-code-sync-family-index-at2026-03-16-18-18.md](../references/indexes/doc-code-sync-family-index-at2026-03-16-18-18.md) | family 선택 index |
| [consistency-checklist.md](../checklist-forconsistency-evaluation/consistency-checklist.md) | canonical 설계 판정 |
| [implementation-checklist.md](../checklist-forimplementation/implementation-checklist.md) | 구현 작업 항목 |
| [doc_code_sync.py](../scripts/doc_code_sync.py) | 현재 scaffold codebase |

## Canonical Design Takeaways

- v0.1의 최소 목표는 `문서 1개 + 코드 1개`를 비교하는 pairwise smoke-test checker다.
- 기본 흐름은 `extract-doc -> extract-code -> compare -> report`다.
- `normalize`는 별도 CLI가 아니라 compare 내부 단계다.
- 최소 결과 분류는 `missing_in_code`, `missing_in_doc`, `mismatch`다.
- rule 단위는 문서와 코드 양쪽에서 공통으로 비교 가능한 object여야 한다.
- 우선 지원할 규칙 유형은 필수 필드, enum/상수, 상태 전이표, 경로 규칙이다.
- 이 skill은 repo-wide crawler가 아니라 명시적으로 지정한 문서/스크립트 쌍을 검사하는 로컬 도구다.
- 입력 범위는 기본적으로 `reference 문서 1개 + script 1개` 쌍이다.

## Output Contract

- `extract-doc`는 compare가 소비 가능한 rules artifact를 출력한다.
- `extract-code`도 같은 shape의 rules artifact를 출력한다.
- `compare`는 `missing_in_code`, `missing_in_doc`, `mismatch`를 유지한다.
- `report`는 drift 요약과 후속 액션을 사람이 읽을 수 있는 형태로 변환한다.

## Guardrails

- `intent`는 참고용이고 구현 기준이 아니다.
- 네트워크 비의존 로컬 분석 도구로 유지한다.
- runtime smoke test용 pairwise 도구이며, 대규모 semantic diff 엔진과 경계를 구분한다.
- claim-verifier와 달리 자연어 주장보다 rule set 비교가 시작점이다.
- code 변경 없이 smoke test/검증 보고만 만드는 사용 시나리오를 지원한다.
- checklist source of truth는 이 canonical KB로 고정한다.
- scaffold 단계와 실제 구현 단계를 혼동하지 않는다.
- 현재 불일치는 구현 깊이 부족인지, scope inflation인지 분류 가능해야 한다.

## Current Implementation Target

- 현재 `scripts/doc_code_sync.py`는 scaffold 상태다.
- 이미 고정된 것:
  - CLI subcommand 구조
  - `extract-doc`, `extract-code`, `compare`, `report`
  - 기본 JSON output shell
- 아직 구현할 것:
  - 문서 규칙 추출
  - 코드 규칙 추출
  - normalization / 공통 rule schema
  - 실제 drift 판정
  - 사람이 읽는 보고서 생성
