---
name: skill-workflow-bridge-eval
description: >-
  verification-decision-gate family의 workflow output evaluation specialist.
  Use this skill when upstream skill output must be classified and converted
  into bridge_eval, retry_spec, handoff_packet, or pass/retry/reroute/stop
  decisions. broader consistency judgment는 verification-decision-gate를
  사용하라.
---

# Skill Workflow Bridge Eval

upstream skill 출력을 평가하여 다음 흐름을 결정하는 bridge + eval + decision controller.

## When to use

- upstream skill 결과를 다음 skill에 넘기기 전에 계약 충족 여부를 판정할 때
- 자연어 출력을 구조화된 handoff_packet으로 정규화할 때
- retry/reroute/stop 결정과 repair spec을 생성할 때
- 워크플로우 단계 간 decision trace를 기록할 때

## Workflow

1. **출력 분류** — `scripts/workflow_bridge.py classify` → output_type 판정 (→ `references/Concept` Output Type)
2. **추출·평가** — `scripts/workflow_bridge.py evaluate --raw <output>` → NL이면 extract→grade, JSON이면 schema 검증 (→ `references/Concept` NL 처리)
3. **결정** — `scripts/workflow_bridge.py decide --eval <bridge_eval.json>` → pass/retry/reroute/stop 중 선택 (→ `references/Reference` §12 Decision Algebra)
4. **retry spec 또는 handoff 생성** — 결정에 따라 `retry-spec` 또는 `handoff` 하위 커맨드 실행
5. **전체 파이프라인** — `scripts/workflow_bridge.py run --raw <output> --contract <contract.json>` → 1~4 일괄 실행 + 이벤트 로그

## Scripts

- `scripts/workflow_bridge.py` — classify/evaluate/decide/retry-spec/handoff/run/validate 통합 래퍼. `python3 scripts/workflow_bridge.py --help`

## References

- `references/Concept-2026-03-15-04-08.md` — NL=claim 원칙, extract→grade→decide 체인, retry/reroute/stop 규칙
- `references/skill-workflow-bridge-eval-reference-2026-03-16-01.md` — 상세 설계: workflow mode, decision algebra, artifact 스키마, state model
- `references/Boundary-of-Responsibility-2026-03-15-03-56.md` — 책임 경계: 소유/읽기전용/금지 목록
- `references/skill-workflow-bridge-eval-knowledge_base2026-03-16-00.md` — 21개 외부 참조 URL KB
- `references/skill-workflow-bridge-eval-checklist-2026-03-16-02.md` — 24섹션 구현 체크리스트
- `checklist-forconsistency-evaluation/consistency-checklist.md` — 109항목 정합성 평가
- `references/troubleshooting.md` — 실전 테스트 버그 케이스

## Notes

- **NL output은 CLAIM이지 RESULT가 아니다** — "완료했습니다"만으로 pass 불가, artifact 존재 > 자기 보고 (→ `references/Concept`)
- **blind retry 금지** — 모든 retry에 repair_instructions 포함된 retry_spec 동반 필수 (→ `references/Concept`)
- downstream은 `handoff_packet.json`을 읽는다, `raw_output`을 직접 읽지 않는다 (→ `references/Boundary`)
- 이 skill은 실행하지 않는다 — tmux/worktree/task-packet은 다른 skill 소유 (→ `references/Boundary`)
