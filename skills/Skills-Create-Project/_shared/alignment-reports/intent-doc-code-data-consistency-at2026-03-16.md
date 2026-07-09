# Intent-Reference-KB-Checklist-Code-Data Consistency Evaluation

- date: `2026-03-16`
- scope:
  - `claim-verifier`
  - `doc-code-sync-checker`
- layers:
  - `intent(사람)`
  - `references(runtime task 문서)`
  - `knowledge_bases(skill 구체화용 연구 자산)`
  - `checklists(정합성 평가용 + 실행계획용)`
  - `code(scripts/)`
  - `data(JSONL intent memo + GitHub research reports + 생성된 보조 메모)`

## Source of Truth

1. 현재 사람 의도는 최근 사용자 지시를 우선한다.
2. JSONL 기반 메모는 과거 의도 복원용이며, 현재 의도를 덮어쓰지 못한다.
3. 문서는 현재 구현 수준을 과장 없이 반영해야 한다.
4. checklist는 한 종류가 아니라 `정합성 평가용`과 `실행계획용`을 구분해서 본다.

## Findings

### F1. `doc-code-sync-checker`는 사람 의도보다 reference/KB가 더 크다

- severity: `high`
- intent:
  - 사용자 의도는 "Skills가 정상 작동하는지 smoke test하면서 디버깅하는 정도"로 축소됨
- references:
  - `extract-doc -> extract-code -> compare -> report`의 일반화된 rule engine처럼 서술됨
  - 비교 대상도 `field / enum / transition / path / length / ownership`까지 넓음
- knowledge_bases:
  - KB와 GitHub 조사도 `openapi-diff`, `oasdiff`, `doxygen`, `pydoclint` 같은 일반화된 diff/정규화 도구 위주
- judgement:
  - 현재 reference와 KB는 "가벼운 smoke-test skill"보다 "범용 contract diff 엔진" 방향으로 치우쳐 있다.

### F2. checklist 층이 약해서 KB에서 바로 code scaffold로 점프했다

- severity: `high`
- consistency-eval checklist:
  - 예시로 존재하는 `skill-workflow-bridge-eval/checklist-forconsistency-evaluation/consistency-checklist.md`는
    "무엇이 canonical source인지", "문서 간 계약이 일치하는지"를 구현 전에 검증한다.
- execution-plan checklist:
  - `template/decision_framework.md`는 "무엇을 먼저 고칠지", "코드만 고칠지, 문서/회귀까지 같이 할지"를 결정한다.
- current state:
  - `claim-verifier/references/verification-checklist.md`와 `doc-code-sync-checker/references/sync-checklist.md`는
    runtime 판정용 체크리스트에 가깝다.
  - 하지만 두 신규 skill에는 전용 `정합성 평가용 checklist`와 `실행계획용 checklist`가 아직 없다.
- judgement:
  - 현재는 checklist 층이 설계 검증용이 아니라 사용 중 판정용에 치우쳐 있어,
    scope inflation을 막아야 할 지점에서 제동 역할을 못 했다.

### F3. 두 skill 모두 reference가 코드보다 앞서 있다

- severity: `high`
- references:
  - `claim-verifier`는 claim 분해, 증거 수집, verdict 보고를 수행한다고 서술
  - `doc-code-sync-checker`는 문서 규칙 추출, 코드 규칙 추출, 비교, drift 보고를 수행한다고 서술
- code:
  - 두 스크립트 모두 현재는 `status: scaffold` JSON만 출력하는 TODO 상태
  - 실제 claim extraction, evidence collection, rule normalization, drift detection 로직 없음
- judgement:
  - "스캐폴드"라는 표시는 있으나, top-level reference 설명과 workflow는 현재 구현 수준보다 강하다.

### F4. data는 충분하지만 아직 실행 데이터가 아니라 설계 데이터다

- severity: `medium`
- data:
  - JSONL intent memo
  - GitHub research report
  - 생성된 intent recovery 메모
- code:
  - 위 데이터를 읽어 실제 판정에 쓰는 구현 경로가 없음
- judgement:
  - 현재 데이터는 구현을 돕는 설계 자산이며, skill 실행 시 직접 활용되는 runtime reference는 아니다.

### F5. JSONL 메모는 현재 의도와 부분 불일치할 수 있다

- severity: `medium`
- data:
  - 메모에는 `claim-verifier > doc-code-sync-checker > edge-case-generator` 우선순위 제안이 남아 있음
- intent:
  - 실제 사람 선택은 먼저 `edge-case-generator`
  - 이후 `doc-code-sync-checker`도 더 작고 실용적으로 보정됨
- judgement:
  - 메모는 historical signal로는 유효하지만, 현재 사람 의도의 canonical source는 아니다.

## Layer-by-Layer Summary

### `claim-verifier`

- intent -> references: `대체로 일치`
- references -> knowledge_bases: `대체로 일치`
- knowledge_bases -> checklists: `약한 연결`
- checklists -> code: `부분 불일치`
- code -> data: `약한 연결`
- note:
  - 개념 축은 안정적이지만 구현 깊이가 아직 없다.

### `doc-code-sync-checker`

- intent -> references: `불일치`
- references -> knowledge_bases: `대체로 일치`
- knowledge_bases -> checklists: `약한 연결`
- checklists -> code: `부분 불일치`
- code -> data: `약한 연결`
- note:
  - 가장 큰 문제는 기능 부재보다도 scope inflation이다.

## Checklist Comparison

### 정합성 평가용 checklist가 보는 것

- canonical source가 무엇인지
- 문서 간 계약이 같은지
- 용어, 필드, 전이표, 경계 정의가 충돌하지 않는지

### 실행계획용 checklist가 보는 것

- 무엇을 먼저 고칠지
- 코드만 고칠지 문서/회귀까지 함께 할지
- 어떤 증거와 회귀 검증을 남길지

### 이번 평가에서의 판단

- `claim-verifier`와 `doc-code-sync-checker`는 정합성 문제에서 출발했는데,
  실제로는 전용 정합성 평가 checklist 없이 scaffold가 먼저 생겼다.
- 그 결과 `doc-code-sync-checker`는 사람 의도보다 큰 구조로 커졌다.
- 즉, 이 두 skill에는 `정합성 평가 checklist -> 실행계획 checklist -> code` 순서가 아직 완전히 적용되지 않았다.

## Recommended Next Actions

1. `doc-code-sync-checker`에 전용 `정합성 평가 checklist`와 `실행계획 checklist`를 먼저 만든다.
   - 정합성 평가 checklist: scope, canonical source, 출력 단위, 금지 범위
   - 실행계획 checklist: smoke test 입력, 비교 쌍, 산출물, 회귀 범위
2. `doc-code-sync-checker`의 reference 범위를 1차 버전 기준으로 축소한다.
   - 입력: `reference 문서 1개 + validate 스크립트 1개`
   - 출력: `missing_in_code / missing_in_doc / mismatch` 짧은 보고
3. `claim-verifier`와 `doc-code-sync-checker`의 `SKILL.md` 첫 문단에 `현재는 scaffold`를 더 직접적으로 명시한다.
4. KB는 유지하되, 실제 사용 단계용 `references/`는 runtime task 수행 기준으로 다시 추린다.
