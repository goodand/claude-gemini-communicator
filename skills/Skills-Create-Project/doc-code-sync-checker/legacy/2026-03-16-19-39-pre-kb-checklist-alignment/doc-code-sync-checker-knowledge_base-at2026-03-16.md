# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-16`
- updated_at: `2026-03-16` (v0.1.0: initial doc-code-sync-checker KB)
- canonical_role: `외부 사례·설계 선택지·현재 구현 상태를 함께 담는 research/hybrid knowledge base`
- canonical_slice: `직접 대조 기준은 doc-code-sync-canonical-design-at2026-03-16-18-18.md`
- format: `- [한 줄 설명](URL)`
- generation_method: `JSONL intent 복원 + GitHub repository search + 비교 가능한 diff/doc tooling 선별`
- total_urls: `6`
- paper_like_urls: `0`
- other_urls: `6`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 워크플로우 |
| `doc-code-sync-checker-knowledge_base-at2026-03-16.md` (이 파일) | GitHub URL 인덱스 |
| [doc-code-sync-family-index-at2026-03-16-18-18.md](../references/indexes/doc-code-sync-family-index-at2026-03-16-18-18.md) | family 선택용 index |
| [doc-code-sync-canonical-design-at2026-03-16-18-18.md](../knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md) | checklist/codebase의 직접 source of truth |
| [implementation-checklist.md](../checklist-forimplementation/implementation-checklist.md) | KB를 코드 작업 항목으로 낮춘 구현 체크리스트 |
| [doc-code-sync-checker-github-search-at2026-03-16.md](../../github-deep-research/references/doc-code-sync-checker-github-search-at2026-03-16.md) | 후보 수집 및 선택 근거 |
| [claim-doc-sync-intent-from-jsonl-at2026-03-16.md](../../_shared/reference-inbox/claim-doc-sync-intent-from-jsonl-at2026-03-16.md) | 메모리 기반 의도 복원 |

## Table of Contents
- [Profile](#profile)
- [Canonical Design Takeaways](#canonical-design-takeaways)
- [Current Implementation Status](#current-implementation-status)
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Profile

- 이 문서는 `research_index_kb`와 `hybrid_kb` 특성이 섞인 상위 KB다.
- checklist와 codebase의 직접 source of truth는 `doc-code-sync-canonical-design-at2026-03-16-18-18.md`다.

## Canonical Design Takeaways

- v0.1의 최소 목표는 **문서 1개와 코드 1개를 비교하는 pairwise smoke-test checker**다.
- 기본 흐름은 `extract-doc -> extract-code -> compare -> report`다.
- `normalize`는 중요하지만 v0.1에서는 별도 CLI보다 **compare 내부 단계**로 취급한다.
- 최소 결과 분류는 아래 3개다.
  - `missing_in_code`
  - `missing_in_doc`
  - `mismatch`
- 우선 비교할 규칙 유형은 아래 4개다.
  - 필드/필수값
  - enum/상수 집합
  - 상태 전이표
  - 경로 규칙 (`..`, 절대경로, symlink)
- 이 skill은 repo-wide crawler가 아니라, **명시적으로 지정한 문서/스크립트 쌍**을 검사하는 로컬 도구다.

## Current Implementation Status

- 현재 `scripts/doc_code_sync.py`는 **scaffold 상태**다.
- 구현된 것:
  - CLI subcommand 구조
  - `extract-doc`, `extract-code`, `compare`, `report` 명령
  - 비교 결과용 기본 필드 자리
- 아직 미구현:
  - 문서 규칙 추출
  - 코드 규칙 추출
  - normalization / 공통 rule schema
  - 실제 drift 판정
  - 사람이 읽을 수 있는 보고서 생성
- 따라서 현재 codebase는 **계약 모양을 먼저 고정한 단계**로 보는 것이 맞다.

## Paper-like URLs

- 없음

## Other research References URLs

- [Coral RepoDocConsistencyChecker Agent - repo 문서와 변경 파일의 정합성 점검](https://github.com/Coral-Protocol/Coral-RepoDocConsistencyChecker-Agent)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 대상 repo와 변경 파일 집합을 입력받는다.
    - 2) 문서가 현재 변경을 반영하는지 점검한다.
    - 3) 불일치와 업데이트 권고를 반환한다.

- [OpenAPI-diff - 두 계약 문서를 비교해 structured diff 생성](https://github.com/OpenAPITools/openapi-diff)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) old/new spec를 읽는다.
    - 2) structured diff를 계산한다.
    - 3) Markdown/HTML/JSON 보고서를 출력한다.

- [oasdiff - diff / breaking / changelog / checks 분리형 비교 도구](https://github.com/oasdiff/oasdiff)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 두 계약 버전을 비교한다.
    - 2) 전체 diff와 breaking subset을 분리한다.
    - 3) changelog와 checks를 별도 출력한다.

- [Doc Link Checker - 문서 reference 스캔 후 내부 링크 무결성 검증](https://github.com/djmattyg007/doc-link-checker)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 문서 파일을 스캔한다.
    - 2) 링크/참조를 추출한다.
    - 3) 유효하지 않은 reference를 리포트한다.

- [Doxygen - 문서를 소스에서 직접 추출해 일관성 유지](https://github.com/doxygen/doxygen)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 소스 구조를 읽는다.
    - 2) 문서 표현을 생성한다.
    - 3) 코드 구조와 문서 표현의 일관성을 높인다.

- [pydoclint - docstring 섹션과 시그니처/구현의 일치 검사](https://github.com/jsh9/pydoclint)
  - sources: `github search`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 함수 시그니처와 docstring section을 읽는다.
    - 2) 인자/반환/예외 항목을 대조한다.
    - 3) 누락/불일치를 lint로 출력한다.
