# research URL Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-17`
- updated_at: `2026-03-17` (v0.1.0: initial official-doc research KB)
- canonical_role: `execution-contract-mapper를 위한 research_index_kb`
- canonical_slice: `아직 없음. 이 KB를 기반으로 consistency checklist를 먼저 만든다.`
- source_research_files: `web official-doc research on 2026-03-17`
- format: `- [한 줄 설명](URL)`
- generation_method: `공식 specification / 공식 documentation / 공식 repository 위주로 execution contract 축을 선별`
- total_urls: `11`
- paper_like_urls: `2`
- other_urls: `9`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · 현재 scaffold 상태 |
| `execution-contract-mapper-knowledge_base-at2026-03-17-00-44.md` (이 파일) | execution contract 조사 자산을 모아둔 research_index_kb |
| [execution-contract-mapper-issues-at2026-03-16.md](./execution-contract-mapper-issues-at2026-03-16.md) | 현재 필요성과 빈 공간 정리 |

## Table of Contents
- [Profile](#profile)
- [Research Focus](#research-focus)
- [Candidate Execution Contract Families](#candidate-execution-contract-families)
- [Recommended First Vertical Slices](#recommended-first-vertical-slices)
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Profile

- 이 문서는 `execution-contract-mapper`의 첫 `research_index_kb`다.
- 아직 `Canonical Design Takeaways`는 없다. 먼저 research space를 정리하고, 그 다음 consistency checklist를 통해 canonical slice를 고정한다.
- 핵심 질문은 `개념 공간을 어떤 execution contract artifact로 내릴 것인가`다.
- 여기서 말하는 execution contract는 `JSON schema`, `OpenAPI`, `CLI contract`, `rule schema`, `breaking-change diff basis`, `traceability link`를 포함한다.

## Research Focus

- `schema contract`: 구조화 입력과 출력 필드를 어떤 schema 언어로 고정할지
- `CLI contract`: subcommand, option, argument, help text를 어떤 형식으로 고정할지
- `mapping contract`: TypeSpec 같은 DSL에서 OpenAPI/JSON Schema로 어떻게 내릴지
- `diff contract`: 바뀐 계약을 어떤 bucket으로 비교할지
- `traceability contract`: requirement/checklist/schema/code 간 연결을 어떻게 남길지

## Candidate Execution Contract Families

- `JSON Schema family`
  - execution artifact를 language-neutral schema로 고정하는 층이다.
  - JSON Schema Draft 2020-12와 OpenAPI 3.1의 schema alignment가 핵심이다.
- `OpenAPI family`
  - HTTP/API contract를 구조적으로 표현하는 층이다.
  - operation, parameter, request/response, component schema를 1급 artifact로 다룰 수 있다.
- `TypeSpec family`
  - 더 상위 개념 표현에서 OpenAPI/JSON Schema를 emit하는 contract authoring 층이다.
  - execution-contract-mapper가 장기적으로 `concept -> contract artifact`를 내리는 방향과 잘 맞는다.
- `Pydantic model family`
  - Python codebase 안에서 schema contract를 실제 타입/validation 모델로 구현하는 층이다.
  - JSON Schema export가 가능해 code-first와 schema-first를 연결하기 좋다.
- `CLI contract family`
  - `argparse`, `click`는 subcommand/option/help/output expectation을 코드에서 명시하게 해준다.
  - execution-contract-mapper의 v0.1에서는 CLI contract 추출 slice 후보가 된다.
- `traceability family`
  - StrictDoc, Sphinx-Needs는 requirement/spec/test를 링크 가능한 engineering object로 다루게 해준다.
  - execution contract를 checklist, schema, evidence와 연결할 때 참고할 근거가 된다.
- `contract diff family`
  - openapi-diff, oasdiff는 계약 변경을 raw textual diff가 아니라 typed diff / breaking-change basis로 본다.
  - execution-contract-mapper가 후속 skill과 연결될 때 `before/after contract delta` 표현에 직접 도움이 된다.

## Recommended First Vertical Slices

- `schema_contract`
  - KB/checklist에서 나온 필드 정의를 JSON Schema 또는 Pydantic model skeleton으로 내리는 slice
- `cli_contract`
  - subcommand/argument/option/help/exit behavior를 contract map으로 내리는 slice
- `rule_schema`
  - checklist item을 machine-readable rule schema로 내리는 slice
- `contract_diff_basis`
  - later compare skill이 읽을 typed diff basis를 미리 정의하는 slice

## Paper-like URLs

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
  - sources: `official web documentation`
  - agent: `A00`
  - taxonomy: `[[schema_contract]] · standard schema language`
  - key_idea: execution contract를 language-neutral schema로 고정할 때 가장 직접적인 기준점이다.
  - execution_conditions: field/type/required/constraint를 구조화해서 표현할 필요가 있다.
  - pseudocode_3lines:
    - 1) checklist나 concept unit에서 필드와 제약을 추출한다.
    - 2) 이를 JSON Schema object로 정규화한다.
    - 3) downstream validator나 diff tool이 읽을 artifact로 저장한다.

- [OpenAPI Specification v3.1.0](https://spec.openapis.org/oas/v3.1.0)
  - sources: `official specification`
  - agent: `A00`
  - taxonomy: `[[api_contract]] · interface description`
  - key_idea: HTTP/API execution contract는 path, operation, parameter, request/response schema를 가진 표준 인터페이스 서술로 고정할 수 있다.
  - execution_conditions: API-like contract를 operation/parameter/schema 단위로 분해할 필요가 있다.
  - pseudocode_3lines:
    - 1) 개념 공간에서 API surface를 operation 단위로 분리한다.
    - 2) parameter/request/response contract를 구조화한다.
    - 3) OpenAPI artifact로 내린 뒤 diff/validation에 사용한다.

## Other research References URLs

- [OpenAPI v3 emitter | TypeSpec](https://typespec.io/docs/emitters/openapi3/openapi/)
  - sources: `official TypeSpec docs`
  - agent: `A00`
  - taxonomy: `[[concept_to_contract]] · emitter mapping`
  - key_idea: 상위 TypeSpec language element를 OpenAPI 표현으로 매핑하는 규칙을 공개적으로 보여준다.
  - execution_conditions: concept unit을 operation, route, server, encoding 같은 명시적 contract unit으로 바꿀 수 있어야 한다.
  - pseudocode_3lines:
    - 1) 상위 concept를 TypeSpec-like contract unit으로 표현한다.
    - 2) 각 unit을 OpenAPI component/operation으로 매핑한다.
    - 3) emit 결과를 execution contract artifact로 저장한다.

- [Emitter usage | TypeSpec](https://typespec.io/docs/emitters/openapi3/reference/emitter/)
  - sources: `official TypeSpec docs`
  - agent: `A00`
  - taxonomy: `[[contract_emission]] · output control`
  - key_idea: emitter output directory, output file, OpenAPI version 같은 emission contract도 명시적으로 고정할 수 있다.
  - execution_conditions: contract artifact를 한 번 생성하는 것이 아니라 재생산 가능한 output convention이 필요하다.
  - pseudocode_3lines:
    - 1) contract generation target을 고른다.
    - 2) emitter option과 output location을 고정한다.
    - 3) repeatable build artifact로 관리한다.

- [Pydantic JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
  - sources: `official Pydantic docs`
  - agent: `A00`
  - taxonomy: `[[python_schema_contract]] · model-to-schema`
  - key_idea: Python model에서 JSON Schema Draft 2020-12 / OpenAPI 3.1 compatible schema를 자동 생성할 수 있다.
  - execution_conditions: Python codebase 안에서 execution contract를 타입과 validation 모델로 구현할 필요가 있다.
  - pseudocode_3lines:
    - 1) contract field를 Pydantic model로 정의한다.
    - 2) model에서 JSON Schema를 생성한다.
    - 3) generated schema를 contract artifact와 비교한다.

- [argparse — Parser for command-line options, arguments and subcommands](https://docs.python.org/3/library/argparse.html)
  - sources: `official Python docs`
  - agent: `A00`
  - taxonomy: `[[cli_contract]] · stdlib parser`
  - key_idea: CLI contract는 option, argument, subcommand, choices, required 여부를 명시적으로 고정한 parser object로 표현할 수 있다.
  - execution_conditions: CLI가 stable entrypoint여야 하고, usage/help contract도 중요한 경우
  - pseudocode_3lines:
    - 1) command surface를 subcommand와 parameter로 분해한다.
    - 2) required/choices/default/help를 contract로 고정한다.
    - 3) parser definition과 KB/checklist를 대조한다.

- [Click Documentation](https://click.palletsprojects.com/en/stable/)
  - sources: `official Click docs`
  - agent: `A00`
  - taxonomy: `[[cli_contract]] · composable CLI`
  - key_idea: composable command tree, 자동 help page, lazy loading을 갖는 CLI contract를 decorator 기반으로 고정할 수 있다.
  - execution_conditions: subcommand tree와 help text가 execution contract의 일부일 때
  - pseudocode_3lines:
    - 1) command group과 subcommand를 구조화한다.
    - 2) option/argument/help를 decorator layer에서 고정한다.
    - 3) runtime CLI surface를 contract artifact로 추출한다.

- [StrictDoc Documentation](https://strictdoc.readthedocs.io/en/stable/)
  - sources: `official documentation`
  - agent: `A00`
  - taxonomy: `[[traceability_contract]] · requirement object`
  - key_idea: requirement/specification을 문서 객체와 traceable link로 관리하는 방식이 execution contract traceability에 직접 참고된다.
  - execution_conditions: checklist, schema, implementation rule, evidence를 연결 가능한 object로 다루고 싶을 때
  - pseudocode_3lines:
    - 1) 계약 항목을 requirement-like object로 식별한다.
    - 2) 상하위 계약과 구현 근거를 링크한다.
    - 3) 누락된 trace나 stale contract를 감시한다.

- [Sphinx-Needs documentation](https://sphinx-needs.readthedocs.io/en/latest/)
  - sources: `official documentation`
  - agent: `A00`
  - taxonomy: `[[traceability_contract]] · engineering object graph`
  - key_idea: requirements, specifications, test cases 같은 engineering object를 link/filter/analyze 가능한 graph로 다룬다.
  - execution_conditions: execution contract를 later evidence/test space와 연결하는 경우
  - pseudocode_3lines:
    - 1) contract unit을 need object로 본다.
    - 2) spec/test/evidence와 relation을 건다.
    - 3) relation graph로 coverage와 stale link를 분석한다.

- [OpenAPITools/openapi-diff](https://github.com/OpenAPITools/openapi-diff)
  - sources: `official repository`
  - agent: `A00`
  - taxonomy: `[[contract_diff]] · typed API diff`
  - key_idea: OpenAPI contract 변경을 HTML/Markdown/JSON renderable diff로 분해할 수 있다.
  - execution_conditions: contract artifact 전후 버전과 render target이 필요하다.
  - pseudocode_3lines:
    - 1) old/new contract artifact를 준비한다.
    - 2) 변경을 typed diff bucket으로 분해한다.
    - 3) machine-readable diff와 human-readable report를 같이 남긴다.

- [oasdiff](https://github.com/oasdiff/oasdiff)
  - sources: `official repository`
  - agent: `A00`
  - taxonomy: `[[contract_diff]] · breaking change detection`
  - key_idea: contract diff를 단순 변경이 아니라 breaking/non-breaking/changelog 관점으로 나눌 수 있다.
  - execution_conditions: backward compatibility를 execution contract 수준에서 보고 싶은 경우
  - pseudocode_3lines:
    - 1) old/new contract를 입력으로 넣는다.
    - 2) breaking과 non-breaking change를 분리한다.
    - 3) downstream debug/evidence step에 delta basis를 제공한다.

- [TypeSpec](https://typespec.io/)
  - sources: `official project homepage`
  - agent: `A00`
  - taxonomy: `[[single_source_contract]] · API-first contract authoring`
  - key_idea: 단일 source of truth에서 OpenAPI, JSON Schema, client/server scaffolding으로 내려가는 접근이 execution-contract-mapper의 장기 방향과 맞는다.
  - execution_conditions: 하나의 상위 contract language에서 여러 execution artifact를 emit하고 싶을 때
  - pseudocode_3lines:
    - 1) 상위 contract를 단일 표현으로 정의한다.
    - 2) 필요한 artifact 형식으로 emit한다.
    - 3) emitted artifact를 downstream checker와 sync한다.
