# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-16-22-22`
- updated_at: `2026-03-16-22-22` (v0.1.0: mismatch semantics KB 생성)
- format: `- [한 줄 설명](URL)`
- generation_method: `GitHub/공식 문서 기반 mismatch semantics 조사 후 typed mismatch 설계 관점으로 정리`
- total_urls: `4`
- paper_like_urls: `0`
- other_urls: `4`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 라우터 |
| [doc-code-sync-canonical-design-at2026-03-16-18-18.md](../knowledge_bases/doc-code-sync-canonical-design-at2026-03-16-18-18.md) | 현재 채택 설계 source of truth |
| `mismatch-semantics-knowledge_base-at2026-03-16-22-22.md` (이 파일) | mismatch semantics 연구 KB |
| [consistency-checklist.md](../checklist-forconsistency-evaluation/consistency-checklist.md) | 현재 skill 전체 정합성 기준 |
| [mismatch-semantics-consistency-checklist-at2026-03-16-22-32.md](../checklist-forconsistency-evaluation/mismatch-semantics-consistency-checklist-at2026-03-16-22-32.md) | mismatch typed expansion 전용 정합성 기준 |
| [implementation-checklist.md](../checklist-forimplementation/implementation-checklist.md) | 현재 skill 전체 구현 기준 |
| [mismatch-semantics-implementation-checklist-at2026-03-16-22-36.md](../checklist-forimplementation/mismatch-semantics-implementation-checklist-at2026-03-16-22-36.md) | mismatch typed expansion 전용 구현 기준 |
| [doc_code_sync.py](../scripts/doc_code_sync.py) | 현재 pairwise codebase |

## Table of Contents
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Paper-like URLs

- 없음

## Other research References URLs

- [OpenAPI-diff - 계약 간 변경을 missing과 changed 계열로 구조화하는 diff 도구](https://github.com/OpenAPITools/openapi-diff)
  - sources: `legacy/2026-03-16-22-22-pre-kb-relocation/mismatch-semantics-web-research-at2026-03-16-22-18.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) old/new contract를 읽는다.
    - 2) missing/breaking/changed를 분리해 diff를 계산한다.
    - 3) 사람이 읽는 보고와 기계가 읽는 artifact를 함께 출력한다.

- [oasdiff - checks/breaking/changelog를 분리해 계약 drift를 분류하는 도구](https://github.com/oasdiff/oasdiff)
  - sources: `legacy/2026-03-16-22-22-pre-kb-relocation/mismatch-semantics-web-research-at2026-03-16-22-18.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) 두 계약 버전을 비교한다.
    - 2) 단순 존재 차이와 의미 있는 변경을 다른 category로 나눈다.
    - 3) 이후 액션이 가능하도록 typed result를 남긴다.

- [pydoclint - 문서와 시그니처의 불일치를 typed lint로 보고하는 도구](https://github.com/jsh9/pydoclint)
  - sources: `legacy/2026-03-16-22-22-pre-kb-relocation/mismatch-semantics-web-research-at2026-03-16-22-18.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) docstring과 코드 시그니처를 함께 읽는다.
    - 2) 동일 이름 항목끼리 비교 가능한 속성을 추출한다.
    - 3) 누락과 불일치를 다른 lint category로 출력한다.

- [StrictDoc - requirements와 구현 traceability를 명시적으로 연결하는 도구](https://github.com/strictdoc-project/strictdoc)
  - sources: `legacy/2026-03-16-22-22-pre-kb-relocation/mismatch-semantics-web-research-at2026-03-16-22-18.md`
  - agent: `A00`
  - pseudocode_3lines:
    - 1) requirement와 implementation artifact를 연결한다.
    - 2) 연결 가능한 단위끼리 traceability를 계산한다.
    - 3) 연결된 규칙쌍에서 mismatch를 증거 기반으로 판단한다.
