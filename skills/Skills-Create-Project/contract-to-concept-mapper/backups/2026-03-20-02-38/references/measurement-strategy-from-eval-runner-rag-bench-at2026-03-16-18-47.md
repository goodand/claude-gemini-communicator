# Measurement Strategy From Eval Runner + Rag Bench

## Purpose

`contract-to-concept-mapper`의 성과 측정 방식을 외부 skill 기준과 연결하기 위한 메모다.
실행, 해석, naming/formula governance를 분리해 metric drift를 줄이는 데 목적이 있다.

## Shared Inputs

- `eval-runner`
  - 실행 오케스트레이션
  - preflight, run, metrics, report, chain 담당
- `rag-bench`
  - metric 해석, 비교, taxonomy, report-facing 진단 담당
- `metric_formula_contract.md`
  - naming, formula, strict-vs-proxy, suffix governance의 fixed point

## Recommended Split

1. 실행이 필요하면 `eval-runner`를 먼저 쓴다.
2. 해석과 metric naming은 `rag-bench`를 기준으로 본다.
3. 두 skill이 충돌하면 `metric_formula_contract.md`를 정본으로 삼는다.

## Why This Helps Here

`contract-to-concept-mapper`도 현재 아래 metric을 다룬다.

- `coverage_ratio`
- `unsupported_item_ratio`
- `traceability_ratio`
- `boundary_preservation_ratio`

문제는 계산 스크립트, 해석 문서, naming이 서로 엇갈리기 쉬운 구조라는 점이다.
따라서 이 skill에서도 아래 3층 분리를 유지하는 편이 좋다.

1. fixed point
   - metric 이름, formula, variant/profile 규약
2. interpretation layer
   - 지표가 무엇을 의미하는지 설명
3. execution layer
   - 실제 계산 스크립트와 report output

## Applied Rule For This Skill

- `kb_to_consistency_check.py`는 execution layer에 가깝다.
- coverage/tracability 계열 metric 설명은 KB/checklist에서 interpretation layer로 다룬다.
- metric 이름과 formula를 추가·변경할 때는 fixed-point 문서처럼 contract를 먼저 적고, 그 뒤 KB/checklist/scripts로 내린다.
- local fixed point는 `knowledge_bases/kb-to-consistency-metric-formula-contract-at2026-03-16-19-02.md`다.

## Short Reusable Phrase

검색 능력 측정은 아래 2개 skill을 같이 쓴다.

1. `eval-runner`
   - preflight, run, chain, bundled metrics, report 자동화
2. `rag-bench`
   - retrieval/coverage/ranking/context-integrity metric 해석과 비교

공통 기준:
- metric naming / formula / strict-vs-proxy 판단은 `metric_formula_contract.md`를 따른다
- `eval-runner`는 실행 오케스트레이션만 담당하고, metric 정의를 새로 만들지 않는다

## Next Use

일반 KB인 `contract-to-concept-mapper-knowledge_base-at2026-03-16-13-58.md`를 `research_index_kb -> hybrid_kb`로 승격할 때,
metric 관련 `Canonical Design Takeaways`는 이 문서의 3층 분리 원칙을 따라 보강한다.
