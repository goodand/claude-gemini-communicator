---
name: kb-checklist-pipeline
description: >-
  workspace-artifact-production-process family의 knowledge-to-checklist
  specialist. Use this skill when researched knowledge must be turned into a
  canonical knowledge base, a consistency checklist, and an implementation
  checklist. broader artifact production order는
  workspace-artifact-production-process를 사용하라.
---

# KB Checklist Pipeline

`references -> knowledge_base -> consistency checklist -> implementation checklist`를 고정하고, 산출물 종류에 따라 분기한다.

## Read Order

1. `references/indexes/kb-checklist-pipeline-branch-index-at2026-03-16-23-11.md`
2. branch 선택: 문서만이면 `references/families/document-output-branch-at2026-03-16-23-11.md`, script/비문서면 `references/families/implementation-output-branch-at2026-03-16-23-11.md`
3. `knowledge_bases/kb-checklist-pipeline-canonical-design-at2026-03-16-23-11.md`
4. `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-11.md`
5. `checklist-forimplementation/implementation-checklist-at2026-03-16-23-11.md`
6. 필요하면 `scripts/pipeline_router.py --help`

## Use When

- 조사 자료를 KB와 checklist로 내려야 할 때
- 산출물이 문서만인지, script/비문서 구현물인지 먼저 갈라야 할 때
- script branch에서 TDD를 선행하도록 강제하고 싶을 때
- progressive context injection 순서를 skill 자체에 넣고 싶을 때

## Branch Rules

- `document_output`: `md`, `txt`, `image`
- `script_output`: 실행 코드 생성
- `implementation_output`: `md/txt/image`가 아닌 비문서 구현물

## Router Output

- `scripts/pipeline_router.py`는 `target`, `artifact_kind`, `branch`, `tdd_required`, `read_order`, `next_actions`를 기본으로 낸다
- implementation branch면 `execution_evidence_handoff`와 `baseline_diff_handoff`를 같이 낸다
- payload 상세 shape는 `references/families/router-output-contract-at2026-03-18-23-32.md`

## Notes

- source of truth는 항상 canonical KB다
- script/비문서 branch는 `implementation checklist -> TDD -> implementation -> raw smoke -> evidence audit -> debug -> before/after diff` 순서를 따른다
- debug와 before/after diff를 별도 skill로 분리하고 싶으면 `references/families/baseline-diff-bridge-at2026-03-16-23-17.md`를 따라 `baseline-diff-lab`으로 handoff한다
- handoff 대상이 raw smoke report만 만들면 `baseline-diff-lab/scripts/metricize_smoke_report.py`로 먼저 `metrics` dict artifact를 만든다
- 문서 branch는 TDD가 필수는 아니다
- evidence는 `references/troubleshooting.md`와 smoke 보고로 남긴다
