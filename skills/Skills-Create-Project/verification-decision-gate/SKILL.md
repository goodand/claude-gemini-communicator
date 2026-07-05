---
name: verification-decision-gate
description: >-
  Use this skill when multi-concern verification, consistency judgment, and
  next-step gating must be decided together across claims, documented rules,
  code-doc alignment, and upstream workflow outputs. claim-only direct call은
  claim-verifier, rule/code drift는 doc-code-sync-checker, code↔doc structural
  alignment는 codebase-doc-alignment, workflow output eval은
  skill-workflow-bridge-eval, execution evidence audit는
  evidence-trace-auditor, cross-repo product quality review와 Codex handoff
  convergence는 cross-repo-product-review, sync→async migration structural
  closure는 async-migration-verify를 사용하라.
---

# Verification Decision Gate

검증/정합성 판단 band의 workflow owner.

## When to use

- claim, rule, alignment, workflow decision, execution evidence audit이 함께 얽힌 multi-concern verification이 필요할 때
- 단일 specialist 결과를 종합해 pass/retry/reroute/hold 같은 다음 판단을 내려야 할 때
- 어떤 verification specialist를 먼저 써야 할지 불확실할 때

## Do not use

- 자연어 claim 하나만 확인하면 될 때
- 문서 규칙과 코드 구현 drift만 확인하면 될 때
- 코드와 문서 alignment만 보면 될 때
- upstream skill output 하나를 retry/reroute용으로 평가하면 될 때
- runtime evidence만 수집하고 contract 대조하면 될 때

## Family Roles

- owner:
  - `verification-decision-gate`
- direct-call specialists:
  - `claim-verifier`
  - `doc-code-sync-checker`
  - `codebase-doc-alignment`
  - `skill-workflow-bridge-eval`
  - `evidence-trace-auditor`
  - `cross-repo-product-review`
  - `async-migration-verify`

## Workflow

1. verification concern이 claim, rule, alignment, workflow, execution evidence 중 어디에 걸치는지 분류한다.
2. 필요한 specialist evidence를 먼저 모은다.
3. evidence 충돌 여부와 missing verification을 확인한다.
4. next-step gate를 `pass / retry / reroute / hold` 수준으로 정리한다.

## References

- owner band taxonomy는 [../skill-creation-process/references/owner-task-bands-at2026-04-02.md](../skill-creation-process/references/owner-task-bands-at2026-04-02.md)
- troubleshooting note는 [references/troubleshooting.md](references/troubleshooting.md)
