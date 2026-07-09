# hybrid research Knowledge Base
- ver: `v0.1.0`
- generated_at: `2026-03-17`
- canonical_role: `evidence-trace-auditor를 위한 hybrid_kb`
- canonical_slice: `Canonical Design Takeaways 섹션은 v0.1 checklist와 직접 연결되는 source of truth`
- source_research_files: `local skill artifacts on 2026-03-17`
- generation_method: `execution-contract-mapper와 doc-code-sync-checker 결과를 evidence audit 관점으로 정리`

## Document Map

| 문서 | 역할 |
|------|------|
| [SKILL.md](../SKILL.md) | skill 목적 · workflow |
| `evidence-trace-auditor-knowledge_base-at2026-03-17-01-52.md` (이 파일) | 조사 자산과 canonical slice를 함께 담는 hybrid_kb |
| [evidence-trace-auditor-issues-at2026-03-16.md](./evidence-trace-auditor-issues-at2026-03-16.md) | 현재 필요성과 빈 공간 정리 |

## Table of Contents
- [Profile](#profile)
- [Canonical Design Takeaways](#canonical-design-takeaways)
- [Current Implementation Target](#current-implementation-target)
- [Research Focus](#research-focus)
- [Candidate Evidence Inputs](#candidate-evidence-inputs)
- [Candidate Audit Outputs](#candidate-audit-outputs)
- [Paper-like URLs](#paper-like-urls)
- [Other research References URLs](#other-research-references-urls)

## Profile

- 이 문서는 `evidence-trace-auditor`의 첫 `hybrid_kb`다.
- 조사 자산을 유지하면서 checklist source of truth가 될 `Canonical Design Takeaways`를 같은 문서에 둔다.
- 핵심 질문은 `stored claim과 verified evidence를 어떤 ledger로 분리할 것인가`다.

## Canonical Design Takeaways

- 이 skill의 핵심 목적은 runtime/test/json/file evidence를 구조화해 contract와 대조 가능한 evidence object로 정리하는 것이다.
- source of truth 순서는 `Canonical Design Takeaways 또는 더 좁은 canonical KB -> consistency checklist -> implementation checklist -> scripts`다.
- `execution-contract-mapper`가 만든 contract artifact와 `contract_diff_basis`는 evidence audit의 선행 입력이다.
- v0.1의 첫 입력은 `raw smoke report JSON`이다.
- v0.1의 첫 출력은 `evidence_ledger`다.
- `evidence_ledger`는 최소 `finding_family`, `kind`, `name`, `observed_bucket`, `evidence`, `trace_status`, `action`을 가진다.
- `trace_status`는 최소 `verified_evidence`, `missing_evidence`, `residual_uncertainty`를 구분한다.
- `artifact_path_evidence`에서는 path가 실제로 존재하면 `verified_evidence`, required path가 비어 있거나 존재하지 않으면 `missing_evidence`로 본다.
- evidence는 있지만 현재 `recommended_diff_buckets`에 직접 매핑되지 않는 경우 `residual_uncertainty`로 남긴다.
- `support audit`는 `contract_diff_basis`의 `recommended_diff_buckets`와 실제 evidence entry를 대조해 `supported`, `missing_evidence`, `residual_uncertainty`를 계산한다.
- machine-readable artifact와 human-readable summary를 분리해 남기는 편이 맞다.
- 이 skill은 contract 설계나 code 수정 자동화를 하지 않는다.
- codebase와 문서의 정합성 비교 자체는 `doc-code-sync-checker`의 책임이고, 이 skill은 그 결과에서 evidence trace를 정리한다.

## Current Implementation Target

- 현재 선택한 KB profile은 `hybrid_kb`다.
- v0.1 첫 vertical slice는 `raw_smoke_report -> evidence_ledger -> support_audit`다.
- 첫 실제 연결 대상은 [typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/doc-code-sync-checker/references/typed-mismatch-enum-value-smoke-report-at2026-03-16-22-43.json) 과 [contract-diff-basis-smoke-at2026-03-17-01-40.json](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/execution-contract-mapper/references/contract-diff-basis-smoke-at2026-03-17-01-40.json) 이다.
- 두 번째 slice는 `test_result_evidence`로 구현됐다.
- 세 번째 slice는 `log_evidence`로 구현됐다.
- 네 번째 slice는 `artifact_path_evidence`로 구현됐다.
- 다섯 번째 slice는 `attestation_evidence`로 구현됐다.
- 여섯 번째 slice는 `tool_call_evidence`로 구현됐다.
- 현재 후속 slice 후보는 `repetition_count_collector`가 아니라 `evidence-trace-auditor` 밖의 bridge 강화 작업이다.

## Research Focus

- `provenance model`: evidence object를 entity/activity/agent 관점으로 식별 가능한가
- `log/event data model`: log 기반 evidence를 공통 필드로 정규화할 수 있는가
- `analysis result interchange`: finding/result artifact를 machine-readable object로 유지할 수 있는가
- `attestation/provenance`: verifiable evidence와 self-report를 어떻게 구분할 것인가
- `test result artifact`: 후속 slice에서 JUnit XML 같은 test result evidence를 수용할 수 있는가

## Candidate Evidence Inputs

- raw smoke report JSON
- metricized smoke report JSON
- test result JSON/text
- execution log text
- generated artifact path list

## Candidate Audit Outputs

- evidence ledger
- support summary
- missing evidence summary
- residual uncertainty queue

## Paper-like URLs

- [PROV-Overview](https://www.w3.org/TR/prov-overview/)
  - sources: `official W3C note`
  - taxonomy: `[[provenance_model]] · evidence provenance`
  - key_idea: provenance는 data를 만든 entity, activity, agent 정보를 통해 quality와 trustworthiness를 평가하게 해준다.
  - execution_conditions: evidence entry가 어디서 왔고 무엇을 가리키는지 추적 가능한 최소 provenance field가 필요하다.

- [Logs Data Model | OpenTelemetry](https://opentelemetry.io/docs/specs/otel/logs/data-model/)
  - sources: `official OpenTelemetry spec`
  - taxonomy: `[[log_evidence]] · common event model`
  - key_idea: 다양한 log/event format을 공통 log record field로 정규화할 수 있다.
  - execution_conditions: timestamp, source, body, attributes 같은 공통 필드를 유지하는 log evidence layer가 필요하다.

- [Static Analysis Results Interchange Format (SARIF) Version 2.1.0](https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html)
  - sources: `official OASIS specification`
  - taxonomy: `[[analysis_result_evidence]] · machine-readable findings`
  - key_idea: 분석 결과는 version, runs, result object를 가진 machine-readable interchange format으로 유지할 수 있다.
  - execution_conditions: finding/result/evidence를 free-text가 아니라 structured object로 남겨야 한다.

## Other research References URLs

- [What is in-toto?](https://in-toto.io/docs/what-is-in-toto/)
  - sources: `official in-toto docs`
  - taxonomy: `[[attestation_evidence]] · step provenance`
  - key_idea: software supply chain의 step이 무엇을 어떤 순서로 수행했는지 투명하게 남기면 intended step 여부와 actor 적합성을 검증할 수 있다.
  - execution_conditions: evidence audit가 step/source/action 관점을 보존해야 한다.

- [SLSA Provenance](https://slsa.dev/provenance/)
  - sources: `official SLSA docs`
  - taxonomy: `[[verifiable_provenance]] · artifact provenance`
  - key_idea: provenance는 artifact가 어디서, 언제, 어떻게 만들어졌는지를 추적 가능한 verifiable information으로 본다.
  - execution_conditions: self-report와 검증 가능한 evidence를 분리하는 판단 기준이 필요하다.

- [JUnit legacy XML reporting package](https://docs.junit.org/5.9.1/api/org.junit.platform.reporting/org/junit/platform/reporting/legacy/xml/package-summary.html)
  - sources: `official JUnit docs`
  - taxonomy: `[[test_result_evidence]] · xml report`
  - key_idea: test execution result도 stable XML artifact로 남길 수 있어 후속 evidence slice의 입력이 된다.
  - execution_conditions: 후속 `test_result_evidence` slice에서 XML report 수집/정규화가 필요하다.
