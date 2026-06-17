# Contract Sync Patterns

- scope: 같은 사실이 여러 층에 복제될 때 drift를 막는 패턴
- source: 2026-03-26~27 세션에서 반복 발생한 4-point drift 문제 해결 경험

## 문제 정의

같은 사실(enum, field set, transition, status, policy)이 아래 4곳에 흩어진다:

1. reference(.md) — 자연어 규칙의 owner, 기계적 사실의 mirror
2. machine registry(.json) — 기계적 사실의 owner
3. template(.json) — owner의 projection
4. builder/test(.py) — owner의 consumer

한 곳을 고치면 다른 곳이 stale해진다.

## Fact Ownership 원칙

**fact별 owner는 1곳만.** "설명용"과 "실행용" 모두 canonical이면 split source of truth가 재발한다.

### 기계적 사실 (enum, field set, transition, profile policy)
- **owner**: registry(.json) — 유일한 정의
- **mirror**: reference(.md) — registry의 설명용 거울. owner가 아니다
- **consumer**: template, builder, test — 재정의 금지

### 자연어 규칙 (boundary, non-goals, why, 설계 원칙)
- **owner**: reference(.md) — 유일한 정의
- **consumer**: template $schema_notes, builder 주석 — 복사가 아니라 포인터

| fact 유형 | owner | mirror/consumer |
|-----------|-------|-----------------|
| enum / field set / transition | registry(.json) | reference(.md)=mirror, template/builder/test=consumer |
| boundary / non-goals / why | reference(.md) | template/builder=consumer |
| 학습 예시 | local support template | canonical에 넣지 않음 |

## Registry 구조

```
<skill>/references/contracts/<domain>_contract_v<version>.json
```

포함할 것:
- `enums` — 허용 값 집합
- `fields.required` / `fields.optional` / `fields.forbidden`
- `transitions` — 상태 전이 맵 (해당 시)
- `validation_rules` — 교차 검증 규칙

## Sync Audit 패턴

```
registry ──┬── vs template $schema_notes  → enum/field parity
           ├── vs builder constants       → set parity
           ├── vs reference tables        → field/enum parity
           └── vs test assertions         → coverage parity
```

출력: fact별 `in_sync | drift | error`

## 수정 순서 (Owner-First)

fact 유형에 따라 **owner를 먼저 수정**하고, mirror/consumer를 순서대로 갱신한다.

### 기계적 사실 (enum, field set, transition, profile policy)

1. registry(.json) 수정 — **owner** 먼저
2. reference(.md) mirror 갱신 — registry 변경을 반영
3. template / builder / test 반영 — consumer 갱신
4. sync audit 실행 — drift 확인
5. smoke / validate — 기능 검증

### 자연어 규칙 (boundary, non-goals, why, 설계 원칙)

1. reference(.md) 수정 — **owner** 먼저
2. template / builder / test 반영 — consumer 갱신
3. sync audit 실행 — drift 확인
4. smoke / validate — 기능 검증

**핵심: owner를 먼저 수정한다. mirror를 먼저 수정하면 owner 개념이 약해지고 drift가 재발한다.**
**절대 consumer(template/code)를 먼저 고치고 owner를 나중에 고치지 않는다.**

## 실전 교훈

1. `dispatch_status_enum`을 template에서 5개로 고쳤는데 canonical은 8개 → 다음 라운드에서 drift 재발견
2. `packet_profile` 정책을 builder에서 "항상 명시"로 바꿨는데 reference 4곳이 "없으면 standard" → 문서가 1라운드 뒤처짐
3. `error_log` 필드를 template에 추가했는데 canonical dispatch-fields.md에 미등록 → validator가 느슨해서 통과
