---
name: verification-router
description: Use when a verification/validation/audit need must be routed to the right skill family — checking a claim, auditing a branch or PR for merge safety, verifying code↔doc consistency, confirming runtime/simulator truth, resolving semantic ambiguity, or gating findings into one verdict. Routes an intent to a composed verification skill family (claim / evidence / consistency / merge-audit / decision-gate / semantic / runtime-truth / validation-run). Triggers on 검증, verify, validate, audit, merge/PR safety, 정합성, proof, verdict, gate.
---

# Verification Router

이 skill 코퍼스의 **1등 주제는 "검증"** (verify/validate가 skill 절반에 등장,
Claim Verifier가 최다 사용). 검증 계열 skill이 여러 위치에 흩어져 있어, **검증 의도
→ 알맞은 skill 패밀리**로 라우팅하는 진입점입니다.

## 메커니즘 (Hermes toolsets 패턴 차용)

- `FAMILIES` 레지스트리: `{name: {description, skills, includes}}`
- `resolve(family)`: `includes`를 **재귀 합성 + 사이클 감지 + dedup** → 평탄한 skill 목록
- `route(intent)`: 자연어 의도 → 키워드 규칙 → 패밀리
- 실제 skill 경로 존재 확인은 형제 모듈 `../resolve_skill.py`에 위임 (없으면 `(MISSING)` 표시)

## 패밀리 계층

| family | 설명 | 합성(includes) |
|--------|------|----------------|
| `claim` | 주장/사실 검증 허브 (claim-verifier) | — |
| `evidence` | 증거 수집·추적·감사 (OCR/이미지/실행 증거) | claim |
| `consistency` | 코드↔문서↔의존성 구조 정합성 | claim |
| `decision-gate` | findings → 단일 통과/차단 판정 | claim |
| `merge-audit` | 브랜치/PR 머지 안전성 감사 | evidence, decision-gate |
| `semantic` | 의미 모호성 제거·개념 명료성 | claim |
| `runtime-truth` | 실행/런타임 상태 실측 진위 | evidence |
| `validation-run` | 산출물 검증 실행 파이프라인 | evidence |
| `skill-eval` | **agent skill 자체의 실행을 평가·측정** (behavior eval·benchmark·baseline diff) | evidence |
| `all` | 전체 검증 패밀리 | (전부) |

`skill-eval`은 "검증 도구를 검증"하는 메타 계층입니다 — skill 실행을 측정(measurement-evaluation-orchestrator 허브, agent-tool-benchmark, baseline-diff-lab, skill-workflow-bridge-eval, slice-experiment-lab).

허브는 **`claim-verifier`** — 모든 패밀리가 claim으로 수렴합니다.

## 사용법

```bash
# 패밀리 목록
python3 skills/verification-router/router.py families

# 패밀리를 실제 skill로 평탄화 (존재 확인 포함)
python3 skills/verification-router/router.py resolve merge-audit

# 자연어 의도 → 패밀리 + skill (JSON)
python3 skills/verification-router/router.py route "이 PR 머지해도 되는지 검증"

# PreToolUse hook: stdin JSON → 검증 라우팅 힌트 additionalContext (stdout)
echo '{"tool_input":{"description":"이 브랜치 머지 검증"}}' | \
  python3 skills/verification-router/router.py hook
```

## hook 연동 (선택)

이 repo는 이미 `.claude/settings.local.json`에 PreToolUse/PostToolUse/Stop hook과
`src/hooks/`를 갖고 있습니다. 검증 의도가 감지될 때 라우팅 힌트를 주입하려면
PreToolUse 커맨드 hook으로 `router.py hook`을 물릴 수 있습니다:

```json
{
  "hooks": {
    "PreToolUse": [
      { "hooks": [ { "type": "command",
        "command": "python3 skills/verification-router/router.py hook" } ] }
    ]
  }
}
```

`router.py hook`은 입력 JSON에 검증 신호(검증/verify/validate/audit/merge/정합/claim…)가
없으면 **빈 `{}`로 통과**하고, 있으면 추천 패밀리+skill을 `additionalContext`로 돌려줍니다.
기존 `src/hooks/hook_pre_tool.py`와 병행하거나 그 안에서 호출해도 됩니다.

## 분류 체계 연계

각 검증 skill의 트리거 경계는 `skills/--help-routing.md` 컨벤션(trigger / do-not-trigger
/ nearby / examples)을 따릅니다. 라우터는 그 위에서 **패밀리 단위 상위 분류**를 제공하고,
개별 skill 내부의 세부 트리거는 각 skill의 routing hint가 담당합니다.

## 확장

- 새 검증 skill: 해당 `FAMILIES[...]["skills"]`에 이름 추가.
- 새 패밀리: `FAMILIES`에 항목 추가 + 필요한 `includes` 지정 (사이클은 resolve가 자동 감지).
- 새 라우팅 규칙: `ROUTE_RULES`에 `(정규식, family)` 추가 (위에서부터 첫 매치).
