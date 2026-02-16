# [Framework] 의사결정 및 설계 정의서 — 아키텍처 재구조화

> 작성: CTO(Claude) | CEO 인터뷰 기반 | 날짜: 2026-02-16

---

## 1. 배경 (Background)

### Needs (본질적 필요)

- **Before**: Phase 1~6 동안 기능 중심으로 빠르게 성장한 결과, `scripts/a2a_bridge.py`(836줄)가 프로젝트의 모든 기능(Gemini 호출, 쿨다운, A2A 프로토콜, 에러 감지, 설정 로딩, 피드백 저장)을 독점하는 **God Object**가 되었다. Phase 6에서 `skills/` 3개를 추출했으나 `scripts/`를 정리하지 않아 **이중 구조**(scripts/ vs skills/)가 공존하며, 동일 로직이 최대 7곳에 중복된다. 3-Agent(Claude/Gemini/Codex) 협업 체계에서 각 에이전트에게 작업을 위임하려면 모듈 경계가 명확해야 하나, 현재는 하나의 파일을 건드리면 어디까지 영향이 미치는지 추적할 수 없다.

### Wants (구체적 요구)

- **After (Outcome)**:
  - 모든 `.py` 파일이 **단일 책임**을 가지며, 파일 단위로 Codex에게 위임 가능
  - `src/`를 정본으로 확정하고 `scripts/`는 **호환 레이어로 단계적 축소** (완전 소멸은 후순위)
  - 3-Agent 역할이 디렉토리 구조에 반영되어, "이 디렉토리는 Codex가 코딩, Claude가 리뷰"가 자명

- **Task (실행 절차)**:
  1. 기존 코드 베이스의 의존성 분석 → Hub 식별 → Mermaid 시각화 (완료)
  2. CSO(Gemini) 거시 전략 → CTO(Claude) 세부 보완 (완료)
  3. 이 프레임워크로 의사결정 확정 (이 문서)
  4. 새로운 아키텍처의 의존성 분석 → Hub 식별 → Mermaid 시각화 
  5. 5단계 마이그레이션 실행

---

## 2. 문제 (Problem)

### Painpoint (고통의 지점)

| 고통 | 정량적 비용 | 인지적 부하 |
|---|---|---|
| **코드 수정 시 파급 범위 불명확** | a2a_bridge.py 1줄 수정 → 5개 파일(3 hooks + cli + async_runner) 영향 확인 필요 | "이거 고치면 뭐가 깨지지?" 매번 전체 grep |
| **새 기능 추가 시 위치 혼란** | scripts/ vs skills/ vs a2a_bridge.py 중 어디가 정본? → 매번 3곳 확인 | 결정 피로 → 결국 a2a_bridge.py에 또 추가 |
| **3-Agent 협업 시 역할 경계 불명확** | Codex에게 "이 파일만 수정해"가 불가 — a2a_bridge.py는 836줄에 33개 함수 | 위임 비용 > 직접 작업 비용 → 협업 포기 |

### Problem Causes (원인 분석)

#### Causal Relationship (단선적 인과)

```
Phase 1에서 a2a_bridge.py에 모든 기능 구현
    ↓
Phase 2~4에서 기능 추가할 때마다 같은 파일에 함수 추가 (편의)
    ↓
Phase 6에서 skills/ 추출했으나, hooks/cli는 여전히 a2a_bridge.py 의존
    ↓
scripts/와 skills/ 이중 구조 — 동일 로직 7곳 중복
```

**SW 관점 — 의존성과 의도의 충돌**:
- **의존성**: hooks → a2a_bridge.py (33개 함수 중 9~11개씩 import)
- **의도**: skills/는 자립형(cp -r 독립) ↔ a2a_bridge.py는 모놀리식
- **충돌**: skills/는 독립을 지향하지만, hooks/cli는 여전히 모놀리식 hub에 의존 → 두 설계 철학이 한 프로젝트에 공존

#### Vicious Circle (악순환 루프)

```
a2a_bridge.py가 크다
    → 수정 영향 범위가 불명확
    → 새 기능을 별도 모듈로 분리하기 귀찮음
    → "일단 a2a_bridge.py에 추가"
    → a2a_bridge.py가 더 커짐
    → (반복)
```

---

## 3. 해결책 (Solution)

### 문제 해결 상태 (State)

- **가능성**: 모듈 경계가 명확해지면:
  - Codex에게 "src/core/cooldown.py만 수정해" 위임 가능 → 3-Agent 병렬 작업 현실화
  - 새 기능 추가 시 "src/core/에 새 모듈 생성" → 즉각 결정 가능
  - 코드 수정 시 "이 모듈의 의존자는 2개" → 영향 범위 즉시 파악

- **변화된 환경**:
  - `src/` 정본화 + `scripts/` 단계 축소 → 정본 위치 논쟁 종결
  - God Object 소멸 → 핵심 모듈 300줄 내외, 진입점은 실용 범위(최대 500줄)
  - 의존성 방향 확정: hooks → core → shared (역방향 금지)

### Type (데이터 구조/아키텍처)

```
src/
├── core/           ← 비즈니스 로직 (4 모듈, 각 100~200줄)
│   ├── cooldown.py
│   ├── gemini_service.py
│   ├── a2a_protocol.py
│   └── error_analyzer.py
├── shared/         ← 공용 유틸 (3 모듈, 각 50~80줄)
│   ├── config.py
│   ├── feedback.py
│   └── hook_io.py
├── hooks/          ← 진입점 (각 50~100줄, 로직 최소)
│   ├── hook_auto_task.py
│   ├── hook_stop.py
│   └── hook_pre_tool.py
├── cli.py          ← CLI 진입점 (500줄 이하)
└── async_runner.py

skills/             ← 자립형 (변경 없음, cp -r 독립)
├── gemini-reviewer/
├── agent-parser/
└── cross-agent-bridge/
```

### Type + Performance (성능 지표)

| KPI | 현재 | 목표 | 해결 기준 |
|---|---|---|---|
| 최대 파일 줄 수 | 953줄 (cli.py) | **핵심 모듈 300줄 내외 / 진입점 500줄 이하** | core/shared는 300줄 내외, cli/hook은 최대 500줄 |
| save_feedback() 중복 | 7곳 | **1곳** (src/shared/feedback.py) | skills/는 자체 복사본 허용 (자립성) |
| Codex 위임 가능 여부 | 불가 (God Object) | **모듈 단위 위임** | "이 파일만 수정해" 지시로 작업 완료 가능 |
| 코드 수정 영향 범위 | 최대 5개 파일 확인 | **최대 2개 파일** | 의존성 그래프에서 직접 의존자 ≤ 2 |
| scripts/ 디렉토리 | 존재 (9개 파일) | **우선순위 낮은 단계 축소** | 신규 로직은 src에만 추가, scripts는 호환 경로만 유지 |
| 기존 기능 동작 | 100% | **100%** | hooks/cli/skills 모든 기능 정상 |

---

## 4. 비목표 (Non-goals)

### 비목표 설정 근거

이번 재구조화는 **"코드의 물리적 위치와 의존성 방향 정리"**에 집중한다. 기능 개선, 성능 최적화, 인프라 구축은 별도 태스크로 분리한다.

### 비목표 분류

#### Case: State — 보장하지 않는 상태

| 비목표 | 이유 |
|---|---|
| **skills/ 내부 코드 변경** | Phase 6에서 완성된 3개 skill의 내부 로직은 건드리지 않음. 디렉토리 위치만 조정 가능. 자립성 원칙상 skills/는 독립 단위이므로 이번 리팩토링의 책임 범위 밖 |
| **Hook 트리거 조건 변경** | PostToolUse/Stop/PreToolUse의 발동 조건과 stdout 출력 형식은 현행 유지. 내부 import 경로만 변경 |

#### Case: Type — 제외할 설계 범위

| 비목표 | 이유 |
|---|---|
| **Gemini SDK/CLI 호출 전략 최적화** | retry, fallback, 모델 순회 등 호출 로직은 이번에 개선하지 않음. 코드를 gemini_service.py로 이동만 하고 로직은 as-is 유지 |
| **Reference Architecture 구현** | plans/claude/reference_communicator.md의 Scheduler/Router/Memory/Vector DB는 장기 비전. 이번에는 구조 정리만 |

#### Case: Performance

| 비목표 | 유형 | 설명 |
|---|---|---|
| **테스트 인프라 전면 고도화** | Over | 대규모 CI/CD 파이프라인, 커버리지 게이트, 통합 테스트 자동화까지는 이번 범위 밖. 단, 최소 pytest 스모크 테스트는 포함 가능 |
| **실행 성능 최적화** | Null | Hook 실행 속도, Gemini 호출 지연 등 성능 지표 개선 목표 없음 |
| **config.json 스키마 정제** | Under | config 필드 이름 변경이나 구조 개선은 하지 않음. 위치만 루트로 이동 |

---

## 5. 제약 (Constraints)

### 기술적 제약

| 제약 | 설명 |
|---|---|
| **자립성 원칙** | skills/의 `_common.py`는 ~55줄 복사본 유지 필수. src/core/ import 불가 |
| **Hook 경로 등록** | `.claude/settings.local.json`에 hook 실행 경로가 하드코딩. 이동 시 동시 업데이트 필수 |
| **fcntl 파일 락** | `save_feedback()`의 fcntl 락 패턴은 정확히 보존. concurrent write 보호 필수 |
| **exit(0) 보장** | 모든 hook script는 예외 시에도 exit(0) 반환. 외부 연산 대기는 허용하되 타임아웃 기반으로 Claude 주 흐름을 블로킹하지 않도록 유지 |
| **Python 3.10+ 호환** | `str \| None` 타입 힌트 등 3.10+ 문법 사용 중. 하위 호환 불필요 |

### 비용적 제약

| 제약 | 설명 |
|---|---|
| **Codex sandbox 네트워크 제한** | Codex CLI는 sandbox에서 외부 API 호출 불가 → Gemini 호출 테스트는 Claude가 담당 |
| **Gemini 무료 티어 rate limit** | CSO(Gemini) 리뷰 요청 시 429 에러 빈번 → 요청 최소화, 핵심 설계만 리뷰 |

### 시간적 제약

| 제약 | 설명 |
|---|---|
| **점진적 마이그레이션** | 빅뱅 리팩토링 금지. 5단계 순차 실행, 각 단계별 커밋 + 동작 검증 |
| **a2a_bridge.py 프록시 유지** | 단계 2~4 동안 새 모듈의 프록시로 유지하고, 단계 5에서도 필요 시 호환 레이어로 잔존 가능 |

---

## 요약: 의사결정 한 줄

> **"a2a_bridge.py(836줄) God Object를 src/core/(4) + src/shared/(3)으로 분해해 Codex가 모듈 단위로 작업할 수 있는 구조를 만든다. scripts/는 정본에서 제외하고 호환 레이어로 단계 축소하며, skills/ 내부와 hook 동작 방식은 건드리지 않는다."**
