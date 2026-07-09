# Reverse-Entry Workflow

- scope: 평가/리팩토링 중 발견된 issue에서 시작해, 어느 phase로 되돌아갈지 결정하는 절차
- source: 실전에서 "Phase 0부터 다시"가 아니라 issue가 가리키는 layer에서 재진입하는 패턴이 반복됨

## 문제 정의

phase-guide.md는 Phase -2 → -1 → 0 → 1 → 2 → 3 → 4 → 5 → 6 → 7로 전진하는 흐름을 명시한다.
실제 평가는 보통 아래 순서로 **역진입**한다:

```
smoke/issue 발견 → reference 재검토 → KB 수정 → checklist 재작성 → code 수정
```

"항상 Phase 0부터 다시 돌리기"는 비효율적이고, 수정 범위보다 넓은 phase를 다시 밟으면 context가 분산된다.

## 핵심 원칙

1. **issue가 가리키는 layer를 먼저 식별**한다
2. **그 layer에 해당하는 phase로 직접 재진입**한다
3. 재진입 후 수정이 끝나면 **그 phase 이후의 gate만 다시 통과**한다

## Layer → Phase 매핑

| issue가 가리키는 layer | 재진입 phase | 비고 |
|----------------------|-------------|------|
| SKILL.md (trigger/router) | Phase 4-1 | SKILL.md는 Phase 4에서 최종 작성. 수정 후 5-1+ gate 재실행 |
| references/ (index/family) | Phase 0 또는 Phase 5-3 | 조사 자료 보강 → Phase 0, 운영 중 갱신 → Phase 5-3 |
| knowledge_bases/ (canonical contract) | Phase 1 또는 Phase 2 | KB 신규/대폭 수정 → Phase 1, 채택 설계 갱신 → Phase 2 |
| checklist-forconsistency-evaluation/ | Phase 2 | consistency checklist는 canonical contract의 판정 도구 — source-of-truth layer에서 재진입해야 drift 재발을 막음 |
| checklist-forimplementation/ | Phase 3 | implementation checklist는 consistency checklist의 실행 단위 — consistency를 먼저 확인한 뒤 구현 layer에서 재진입 |
| contracts/ (registry) | Phase 4.2A | registry 수정 후 sync audit 필수 |
| scripts/ (builder/validator) | Phase 4 | code 수정 후 test + smoke 재실행 |
| tests/ | Phase 4 | test 수정 후 smoke 재실행 |
| template (.json) | Phase 4.2A | template 수정 → sync audit → paired-change review |
| evals/ | Phase 4-3 | eval 수정 후 smoke 재실행 |
| logs/, runs/ (evidence) | Phase 5-3 | evidence 재수집/갱신 |

## 재진입 절차

### 1. Issue Triage

```
issue 발생
  ├── 어떤 파일/layer에서 문제인가?
  ├── 해당 layer의 owner는 누구인가? (registry? reference? code?)
  └── 수정 범위는? (단일 파일? 다층 연쇄?)
```

### 2. 단일 layer issue

가장 흔한 경우. 한 layer만 수정하면 되는 issue.

1. issue가 가리키는 layer의 파일을 수정
2. 해당 phase의 산출물 갱신
3. 그 phase 이후의 gate 재실행 (5-1G sync audit, freshness scan 포함)

### 3. 다층 연쇄 issue (cascade)

하나의 수정이 여러 층에 파급되는 경우.

1. **owner를 먼저 수정** — owner-first 순서 적용 `(→ contract-sync-patterns-at2026-03-27.md)`
   - 기계적 사실 → registry(owner) 먼저 → reference(mirror) 갱신
   - 자연어 규칙 → reference(owner) 먼저
2. **consumer를 순서대로 갱신** — registry → template → builder → test
3. **sync audit 실행** — cascade가 있으면 반드시 Phase 4.2A gate
4. **freshness scan 실행** — 수정하지 않은 문서가 stale candidate가 됐는지 확인

### 4. Paired-change issue

SPEC과 code가 동시에 바뀐 상태에서 발견된 issue.

1. SPEC → code 방향 확인: SPEC 변경이 code에 반영됐는가
2. code → SPEC 방향 확인: code 변경이 SPEC/reference에 반영됐는가
3. 둘 다 확인 후 sync audit 실행
4. 상세 규칙: `(→ paired-spec-code-change-rule-at2026-03-27.md)`

## Gate 재실행 범위

재진입 phase에 따라 다시 통과해야 하는 gate:

| 재진입 phase | 다시 통과할 gate |
|-------------|----------------|
| Phase 0 | 해당 reference 갱신 → 5-3B |
| Phase 1 | KB 갱신 → consistency checklist 재판정 → 4.2A(해당 시) → 5-1 → 5-1G → 5-3B |
| Phase 2 | consistency checklist 재판정 → implementation checklist 확인 → 4.2A(해당 시) → 5-1 → 5-1G → 5-3B |
| Phase 3 | implementation checklist 확인 → code 재확인 → 5-1 → 5-1G → 5-3B |
| Phase 4 | 5-1 → 5-1G → 5-3B |
| Phase 4-1 | SKILL.md 수정 → 5-1 → 5-1G → 5-3B |
| Phase 4.2A | sync audit → 5-1 → 5-1G → 5-3B |
| Phase 5-3 | 5-3B (freshness scan만) |

## Skill 유형별 재진입 특성

skill type은 `primary type + secondary tags`로 결정한다. canonical 정의는 `(→ phase-guide.md)` Skill Type Branch 참고.

| primary type | 흔한 재진입 패턴 | 기본 필수 gate |
|-------------|----------------|--------------|
| document-only | reference 수정 → freshness scan | 5-3B |
| contract-heavy | registry 수정 → sync audit → consumer 갱신 | 4.2A + 5-1G |
| runtime-heavy | code 수정 → test → smoke → freshness scan | 5-1 + 5-1G |

| secondary tag | 추가 gate |
|--------------|----------|
| `cross-skill(contract)` | owner skill 수정 → consumer skill 역참조 확인 (cross-skill audit) |
| `cross-skill(adjacent)` | 참조 대상 skill의 reference 변경 시 freshness scan에서 역참조 확인 |
| `has-registry` | sync audit 필수 |

## Cross-Skill Audit 최소 정의

`cross-skill(contract)` tag가 있는 skill에서 재진입할 때 적용한다.
`cross-skill(adjacent)`는 freshness scan의 역참조 확인으로 충분하며, 이 절차는 불필요.

### Owner

cross-skill audit의 owner는 **contract을 정의하는 skill** (provider)이다.
contract을 consume하는 skill (consumer)은 audit 대상이지 owner가 아니다.

### Audit Trigger (양방향)

audit는 **provider 변경**과 **consumer 변경** 양쪽에서 모두 trigger된다.

| trigger 방향 | 상황 | 확인 내용 |
|-------------|------|----------|
| provider → consumer | provider의 contract이 변경됨 | consumer가 변경된 contract을 반영하고 있는지 |
| consumer → provider | consumer가 독자적으로 값을 추가/변경함 | provider의 contract에 없는 값을 consumer가 정의하고 있지 않은지 |

**consumer-side trigger가 필요한 이유**: provider는 안 바뀌었는데 consumer가 local override나 mirror 문서에서 독자적으로 drift하는 경우가 실전에서 자주 발생한다. provider-only trigger로는 이 패턴을 놓친다.

### Consumer Dependency Declaration

`cross-skill(contract)` tag가 있는 consumer skill은 아래 선언을 유지해야 한다.

**저장 위치**: consumer skill의 `references/cross_skill_dependencies.yaml`

> 보수적 v1 자동화는 이 파일만 읽는다. `SKILL.md Notes` fallback은 수동 기록용으로만 남기고, 자동 audit 대상에서는 제외한다.

```yaml
cross_skill_dependencies:
  - provider: "agent-task-packet"
    contract: "references/contracts/packet_contract_v0_1.json"
    consumed_facts: ["packet_profile enum", "priority enum", "required fields"]
    last_synced_at: "2026-03-27T14:30:00+09:00"
```

**필드 규칙**:
- `provider`: contract을 정의하는 skill 이름
- `contract`: provider의 registry 파일 경로 (상대경로)
- `consumed_facts`: consumer가 실제 사용하는 fact 목록
- `last_synced_at`: 마지막으로 provider contract과 정합성을 확인한 시점 (ISO 8601)

**이 선언이 필요한 이유**: provider는 안 바뀌었는데 consumer의 local mirror, copied checklist, support template에서 독자적으로 drift하는 경우, provider-side trigger만으로는 탐지 불가. consumer가 "어떤 provider의 무엇을 소비하는지"를 선언해야 양방향 audit trigger가 작동한다.

### 최소 Audit 기준

1. **역참조 확인** — provider 또는 consumer의 contract 관련 파일이 바뀌었을 때, 상대편 skill 목록을 확인
   - provider 방향: `_shared/fact-owner-map.md`의 consumer 열에서 식별
   - consumer 방향: consumer의 `cross_skill_dependencies` 선언에서 provider를 식별
   - 상대편이 없으면 cross-skill audit 불필요
2. **v1 자동 검사 범위** — 선언 파일 기준으로 아래만 자동 검사
   - provider skill이 실제 존재하는지
   - `contract` 경로가 실제 provider 아래에 존재하는지
   - `last_synced_at`이 ISO 8601인지
   - `last_synced_at`이 provider contract의 mtime보다 오래됐으면 `stale_dependency`
3. **심화 정합성 확인** — consumer가 provider의 현행 contract을 실제로 반영하고 있는지는 현재 수동 확인
   - consumer가 사용하는 enum/field/transition이 provider의 현행 contract과 일치하는지
   - consumer가 provider의 contract에 없는 enum 값, 필드, transition을 독자적으로 정의하고 있지 않은지
   - local override가 발견되면: provider로 승격할지, consumer에서 제거할지 결정

### 산출물

- cross-skill drift 목록 (provider, consumer, drift 방향, drift 내용)
- all clear이면 "cross-skill audit pass" 1줄 기록
- consumer의 `last_synced_at` 갱신

### 한계

- 보수적 v1 자동화는 declaration 존재/경로/stale 여부까지만 본다. consumer 내부의 semantic drift는 아직 수동 절차
- skill 수가 늘어나면 `_shared/fact-owner-map.md` + consumer dependency declaration 기반의 자동 역참조 스캔이 필요할 수 있음

---

## 실전 교훈

1. **"Phase 0부터 다시"는 거의 항상 과잉** — issue가 Phase 4 layer에 있으면 Phase 4에서 재진입하면 된다
2. **cascade issue에서 가장 위험한 것은 owner를 건너뛰는 것** — consumer만 고치면 다음 sync audit에서 다시 drift가 난다
3. **재진입 후 gate를 건너뛰면 이전 세션의 반복 이슈가 다시 돌아온다** — 특히 freshness scan 누락이 잦았다
4. **reverse-entry가 3회 이상 같은 layer를 치면** 그 layer의 설계를 의심해야 한다 — owner 분리나 contract 구조 변경이 필요한 신호
