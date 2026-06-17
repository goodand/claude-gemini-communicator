# Evidence Promotion Pattern

## Purpose

실험/증거 결과를 바로 KB에 복붙하지 않고, 구조화된 승격 파이프라인을 거쳐 `hybrid_kb` 또는 `canonical_design_kb`로 올리는 공용 패턴이다.

## Core Pipeline

`evidence -> summary -> trigger evaluation -> KB patch plan -> KB apply`

## Step 1. Summary

증거를 먼저 아래 단위로 정규화한다.

- `finding`
- `delta`
- `lesson_candidate`
- `residual_uncertainty`

원칙:
- 단일 관측 사실은 기본값으로 `finding`
- before/after가 수치로 닫히면 `delta`
- verified evidence와 positive delta가 함께 있으면 `lesson_candidate`
- 근거 부족이나 미해결 해석은 `residual_uncertainty`

## Step 2. Trigger Evaluation

summary를 읽고 KB profile 승격 가능 여부를 판정한다.

### hybrid_kb

- `lesson_candidate >= 1`
- `residual_uncertainty = 0`

위 조건이 맞으면 `promote`, 아니면 `hold`

### canonical_design_kb

- `hybrid_kb = promote`
- `lesson_candidate` 존재
- `residual_uncertainty = 0`
- `repetition_count >= 2` 같은 반복 검증 신호 존재

위 조건이 맞으면 `candidate`, 아니면 `hold`

## Step 3. KB Patch Plan

승격이 가능하면 실제 KB patch를 먼저 계획으로 만든다.

기본 규칙:
- `lesson_candidate` -> `Canonical Design Takeaways`
- candidate `delta` -> `Current Implementation Target`
- `finding` -> `Research Focus`
- `hold`면 문서 변경 대신 보류 사유만 남긴다

## Step 4. KB Apply

- source KB 원본은 바로 덮어쓰지 않는다
- 먼저 `copy` 또는 patch artifact에 적용한다
- review 후 필요하면 lifecycle 규칙에 따라 active artifact를 갱신한다

## Promotion Guardrails

- residual uncertainty가 있으면 lesson/adoption rule로 올리지 않는다
- 단일 run에서 한 번만 관찰된 변화는 바로 `canonical_design_kb`로 올리지 않는다
- provenance가 불분명하면 `research_index_kb` 또는 `hybrid_kb` supporting note에 머문다
- `canonical_design_kb`는 반복 검증된 rule만 남긴다

## Example Implementation

- skill: [evidence-to-knowledge-promoter](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/SKILL.md)
- summary slice:
  - [vertical-slice-promotion-summary-at2026-03-17-03-08.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-promotion-summary-at2026-03-17-03-08.md)
- trigger slice:
  - [vertical-slice-promotion-trigger-evaluator-at2026-03-17-03-14.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-promotion-trigger-evaluator-at2026-03-17-03-14.md)
- patch plan slice:
  - [vertical-slice-hybrid-kb-patch-plan-at2026-03-17-03-20.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-hybrid-kb-patch-plan-at2026-03-17-03-20.md)
- apply slice:
  - [vertical-slice-apply-hybrid-kb-patch-at2026-03-17-03-27.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-apply-hybrid-kb-patch-at2026-03-17-03-27.md)
- canonical candidate slice:
  - [vertical-slice-canonical-candidate-evaluator-at2026-03-17-03-36.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/evidence-to-knowledge-promoter/references/vertical-slice-canonical-candidate-evaluator-at2026-03-17-03-36.md)
