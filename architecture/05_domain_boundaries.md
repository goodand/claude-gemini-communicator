# 05. 3-도메인 경계 지도 + 운영 전략 (2026-07-11)

> 이 문서는 생태계 전체 작업을 3개 도메인으로 구분하는 정본 경계 지도다.
> **skills/ 독립 repo 분리 작업은 이 문서를 청사진으로 참조한다.**
> 분석 방법 = 의미 추측이 아니라 "누가 누구를 참조하는가"(기계적 기준) 실측:
> check.sh probe, `src/cli.py` 설치 목록, import 스캔, guard 스캔 루트.

## 1. 경계 지도 — 3개는 병렬이 아니라 "2·3 위에 1이 걸친" 구조

```
도메인 3: multi-agent (repo의 존재 이유)     도메인 2: skill catalog (이식 가능 자산)
  src/ hooks tests config codex.toml           skills/ 범용 스킬 + Skills-Create-Project
  schemas plans .codex/agents                   + 발견층(DISCOVERY/TAXONOMY/resolve_skill)
  + 전용 스킬 6종(_INSTALL_SKILLS)              + external/ 미러 + integration-gate
        │ 소비(3→2): notify 경로, 스킬 사용            │
        ▼                                             ▼
도메인 1: path/백링크 복구 (위상 인프라 — 콘텐츠가 아니라 '연결'을 다룸)
  migration/ 전체 · 심링크 95개(git 밖) · path_integrity_guard(전 생태계 스캔)
  · Obsidian vault 링크(미해결 unknown)
```

**판별 테스트** (항목의 도메인 소속을 정하는 질문):

| 도메인 | 질문 |
|---|---|
| 3 multi-agent | "Claude·Gemini·Codex 협업 파이프라인이 없으면 존재 이유가 없는가?" |
| 2 skill catalog | "다른 프로젝트에 복사해도 그대로 가치가 있는가?" |
| 1 위상 인프라 | "콘텐츠가 아니라 콘텐츠 사이의 연결(위상)을 다루는가?" |

**분리 가능성의 구조적 근거**: 의존이 전부 단방향(3→2 소비, 1→2·3 감시)이고 순환 없음.
cross-agent-bridge조차 `src/`를 import하지 않는 자체 완결 스크립트(subprocess 호출) —
코드 결합이 아니라 용도 결합뿐이라 물리 분리에 장애물이 없다.

## 2. 겹침 지점 9개 (실측) + 해소 방침

| # | 겹침 | 방향 | 해소 |
|---|---|---|---|
| 1 | **전용 스킬 6종이 skills/에 거주** (agent-parser, codex-user-context, cross-agent-bridge, gemini-cli-context, gemini-reviewer, install) | 3의 자산이 2의 집에 | skills/ 분리 시 6종은 repo **잔류**. `src/cli.py`의 `_INSTALL_SKILLS`가 이미 정확한 잔류 목록 |
| 2 | `codex.toml` notify → `skills/gemini-reviewer/scripts/codex_notify.py` | 3→2 경로 | #1 잔류 시 자동 해소 (수정 0줄) |
| 3 | `check.sh` probe → `skills/{catalog_resolver_audit,integration-gate,resolve_skill}` | 1→2 호출 | 분리 시 경로 갱신 or catalog repo 자체 CI로 이관 |
| 4 | **resolve_skill.py / skill-path-resolver** — 2에 있으나 성격은 1(경로 해석) | 개념 겹침 최대 | "무엇을 찾나"=2 / "연결이 살아있나"=1(guard). 파일은 2를 따라감 |
| 5 | 심링크 95개: 타겟이 2(skills)와 3(.codex/agents) | 1이 2·3을 감시 | 정상적 계층 의존. 분리 시 gen_restore 재생성 1회 |
| 6 | install 스킬: hook 3개(도메인3)+스킬 심링크(도메인2)를 함께 설치 | 하이브리드 | **3 소속** — 배포기이고, 배포 대상에 2가 포함될 뿐 |
| 7 | integration-gate: 2의 병합 게이트를 1(probe)이 소비 | 2 소속, 1이 사용 | 2를 따라감 |
| 8 | verification-router: 2에 거주, hook(PreToolUse) 연결 예정 | 미래 결합 예약 | 라우터 본체=2, hook 연결부만 3 |
| 9 | CONTINUATION.md: 세 도메인 역사가 한 문서 | 문서 결합 | 분리 시 catalog 부분만 발췌 이관, 원본은 포인터 유지 |

핵심 원칙: **단방향 의존은 겹침이 아니라 정상적 소비/감시 관계**다. 해소가 필요한 것은
물리 배치와 논리 소속의 불일치(#1)와 문서 결합(#9)뿐이며, 나머지는 경로 갱신 수준.

## 3. Workflows 전략 — 도메인별 고유 루프 + 교차 글루

각 도메인은 이미 자기 워크플로우를 갖고 있다(신설이 아니라 **명명**과 결선이 과제):

| 도메인 | 워크플로우 | 상태 |
|---|---|---|
| 3 multi-agent | **실행 루프**: Write/Edit → PostToolUse hook → Gemini 평가 → `plans/` 피드백 / Stop → plan·error 감지 / PreToolUse → 명령 가드. 수동 진입점 = `bridge.py review·codex-review·parse·doctor` | 가동 중 (auto_hooks=true) |
| 2 skill catalog | **생산 파이프라인**: skill-creation-process Phase 1~5 (5-1G Post-Validate Gates → 5-2 smoke) → integration-gate 4-subflow(병합) → `resolve_skill.py list`(충돌 확인) → catalog 편입 | 가동 중 |
| 1 위상 인프라 | **감시 루프**: ASSUMPTIONS 원장 ↔ `check.sh` probe + baseline 관찰("증가하면 조사") + 개명 전 `inbound` 가드(사전) | 가동 중 (트리거는 머신별 등록) |

**교차 글루 3개**:
1. **커밋 전 통합점** = `check.sh` 한 방 — (1)이 (2)·(3)을 소비하는 probe들이 곧 도메인 교차 검증점.
2. **상시 트리거** — 머신마다 launchd/cron 1줄 등록 (ASSUMPTIONS.md 하단).
3. **대형 변경 후 적대 감사** — 통합·분리·마이그레이션급 변경 뒤 독립 세션(별도 모델)이
   주장을 공격하는 감사 1회 (2026-07-11 Sonnet 감사가 전례·양식).

## 4. Unknown-Unknown 탐지 전략 — 4층 + 메타 규칙

unknown unknown은 직접 탐지가 불가능하므로, 전략은 "**known unknown으로 전환하는 층**"과
"**모르는 채로도 신호를 받는 층**"의 조합이다:

| 층 | 메커니즘 | 원리 | 실증 (2026-07-11 세션) |
|---|---|---|---|
| L1 가정 열거 | `ASSUMPTIONS.md` 원장 — "probe 없는 줄 = 알려진 unknown" | unknown의 최대 발생지 = 적을 생각조차 못 한 가정. 열거가 unknown→known 전환 | rescue-7이 원장에 있었기에 재적용의 done-definition이 됨 |
| L2 불변량 트립와이어 | `check.sh` ALL GREEN + baseline 개수 + gate 충돌 **클래스** 판정 | 무엇이 깨질지 몰라도 불변량 이탈 신호는 받음 | rehearse FAIL이 예상 못 한 검증기 회귀를 즉시 잡음 |
| L3 적대적 반증 | 주기 감사: 주장을 가설로 놓고 공격 | 커버리지 맵이 못 보는 "검증 **논거** 자체의 빈틈"을 찾음 | "회귀 0" 논거 붕괴 발견(테스트가 신규 분기를 아예 안 건드림) |
| L4 경계 감시 | 겹침 9지점(§2)마다 소유자+probe 명시 | unknown unknown은 도메인 **경계에서 번식** | rescue-7(소유권 모호)·디스크 덮어쓰기(git↔디스크 갭)·TCC(환경 경계) 전부 경계에서 발생 |

**메타 규칙**: *검증자와 생성자가 같은 가정을 공유하면 probe는 통과하면서 틀린다.*
`gen_restore_symlinks.py`(SCAN)와 `rehearse.sh`(roots)가 같은 누락을 공유해 50/50 "PASS"가
가능했던 사례. 검증자는 피검증자와 **다른 출처**에서 기댓값을 유도해야 한다 —
rehearse.sh는 이 규칙에 따라 하드코딩 루트 대신 생성된 스크립트의 linkpath에서
검증 대상을 역파싱한다.
