# Artifact Lifecycle Manager Canonical Design

- ver: `v0.1.0`
- generated_at: `2026-03-16-23-53`
- canonical_role: `artifact lifecycle governance source of truth`
- source_of_truth_for: `checklist-forconsistency-evaluation/consistency-checklist-at2026-03-16-23-53.md`

## Canonical Design Takeaways

- lifecycle 기본 순서는 `legacy backup -> timestamp naming -> metadata order -> duplicate cleanup`이다.
- active artifact naming은 minute-level timestamp를 따른다.
- 생성 순서는 파일명보다 metadata가 우선이다.
- destructive 변경 전에만 legacy backup을 만든다.
- same-content duplicate는 active tree에서 정리하고 legacy에 중복 보관하지 않는다.
- 기본 audit 대상 chain은 `knowledge_base -> consistency checklist -> implementation checklist`다.
- order와 duplicate는 script로 반복 검증할 수 있어야 한다.

## Current Implementation Target

- 현재는 lifecycle guard script와 TDD를 먼저 둔다.
- script는 order audit, duplicate scan, combined audit를 지원한다.
- destructive file operation 자체는 자동화하지 않고, 먼저 audit와 decision support를 제공한다.
