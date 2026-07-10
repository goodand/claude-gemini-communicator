# Phase Guide — Skill 제작 상세 절차

> **이 절차는 전진(Phase -2→7)과 역진입(issue→layer→phase) 양방향으로 사용한다.**
> 새 skill 제작은 Phase -2부터 순서대로 진행한다.
> 평가/리팩토링 중 issue가 발생하면 `(→ references/reverse-entry-workflow-at2026-03-27.md)`를 따라 해당 phase로 직접 재진입한다.

## Skill Type Branch (이 섹션이 canonical owner)

phase를 밟기 전에 skill의 **primary type 1개 + secondary tags 0~N개**를 결정한다.

### Primary Type (택 1)

| primary type | 설명 |
|-------------|------|
| document-only | KB/reference 중심, 실행 코드 없음 |
| contract-heavy | enum/field/transition을 정의하고 외부에 노출 |
| runtime-heavy | 스크립트/CLI 중심, 내부 contract만 |

### Secondary Tags (해당하는 것 모두)

| tag | 의미 | gate 영향 |
|-----|------|----------|
| `cross-skill(contract)` | 다른 skill의 contract(registry, enum, field set)을 consume하거나 노출 | 4.2A 필수, cross-skill audit 필요 (`references/cross_skill_dependencies.yaml` 유지) |
| `cross-skill(adjacent)` | 다른 skill의 reference/KB를 참조하지만 contract binding은 없음 | freshness scan에서 역참조 확인, 4.2A 불필요 |
| `has-registry` | machine-readable contract registry 보유 | sync audit 필수 |

### Gate 결정 규칙

| 조건 | 4.2A | 5-1G sync audit | 5-1G freshness |
|------|------|-----------------|----------------|
| primary = document-only, tag 없음 | 아니오 | 아니오 | 예 |
| primary = contract-heavy | **예** | **예** | 예 |
| primary = runtime-heavy, tag 없음 | 아니오 | 아니오 | 예 |
| tag `cross-skill(contract)` 있음 | **예** | **예** | 예 |
| tag `cross-skill(adjacent)` 있음 | 아니오 | 아니오 | 예 (역참조 포함) |
| tag `has-registry` 있음 | **예** | **예** | 예 |

### 예시

- agent-task-packet: `contract-heavy` + `cross-skill(contract)`
- claim-verifier: `runtime-heavy` + `cross-skill(contract)` (doc-code-sync의 비교 로직 consume)
- codebase-analysis: `document-only` + `cross-skill(adjacent)` (다른 skill의 reference를 참조)
- tmux-controller: `runtime-heavy` (tag 없음)

### 판정 기준

- `contract-heavy` 판정: Phase 4.2A 적용 조건(3개 이상 층 복제, 외부 contract 노출, builder와 reference가 동일 enum 정의)에 하나 이상 해당
- `cross-skill(contract)` 판정: 이 skill이 다른 skill의 registry/enum/field set을 import하거나, 이 skill의 contract을 다른 skill이 consume
- `cross-skill(adjacent)` 판정: 다른 skill의 reference/KB/troubleshooting을 참조하지만 기계적 contract binding은 없음
- `has-registry` 판정: `references/contracts/` 디렉토리에 machine-readable JSON registry가 존재

---

## Phase -2: 사용자 의도 파악

스킬 제작 전에 **사용자가 실제로 무엇을 원하는지** 먼저 고정한다.

### 절차:
1. 사용자 요청을 1-3문장으로 정규화
2. 무엇을 가장 중요하게 보는지 우선순위 고정
3. source of truth와 평가 기준을 확인

### 산출물:
- 의도 요약
- 우선순위/제약
- human-in-the-loop 확인 포인트

---

## Phase -1: Human In The Loop + 동기 정의 (최선행)

스킬 제작의 **출발점은 반복되는 문제**다. 다만 그 전에 사람이 확인해야 할 지점을 먼저 잠근다.

### 절차:
1. **human-in-the-loop 포인트 고정** — 나중에 사용자 확인이 필요한 결정 지점 표시
2. **반복 패턴 식별** — Agent/Codex가 반복적으로 실수하거나 비효율이 발생하는 지점
3. **목표 설정** — 이 스킬이 해결할 구체적 문제 1문장
4. **우선순위 분석** — 다른 스킬 대비 긴급도·영향도 판단
5. **의존성 분석** — 선행 스킬이 필요한지, 기존 스킬과 책임 겹침이 있는지
6. **기능 범위 경계 (비목표)** — 이 스킬이 **하지 않을 것**을 명시. agent-task-packet의 non_goals 개념과 동일:
   - `Case: State` — 보장하지 않는 상태
   - `Case: Type` — 제외할 에러/예외
   - `Case: Performance` — null/over/under
7. **구현 순서 계획** — 단계별 구현 순서 (의존성 그래프 기반)

반복된 작업/이슈 패턴 정리가 필요하면 `(→ references/repeated-task-and-issue-patterns-at2026-03-19-13-34.md)`를 먼저 확인한다.

### 산출물:
- 1문장 목표 + 비목표 목록 + 의존성 그래프
- 이것 없이 Phase 0으로 넘어가지 않는다
- 상세 기준은 `(→ references/intent-and-reference-analysis-details.md)` 참고

---

## Phase 0: 자료 조사 + Reference 저장

근거 자료를 먼저 확보하고, **reference 원자료를 먼저 저장**한다. 자료 없이 초안을 작성하지 않는다.

### Mode Branch

- 기본값: `external_research`
- opt-in: `internal_codebase_only`
- 상세 규칙: `(→ ../references/reference-acquisition-modes-at2026-03-17-09-35.md)`

`internal_codebase_only`는 사용자가 명시적으로 요청했을 때만 켠다.

### 조사 방법:
- `external_research`
  - **GitHub 딥리서치**: `github-deep-research` 스킬로 유사 오픈소스 탐색
  - **논문/사례 검색**: 관련 논문, 블로그, 기술 문서 탐색
  - **Codex CLI 활용**: 로컬 코드 분석이 필요하면 Codex에게 요청
    - Codex는 샌드박스(네트워크 차단)이므로 **로컬 코드 분석·리팩토링** 전용
    - API 호출·외부 검색이 필요한 조사는 Claude 또는 사용자가 직접 수행
  - **기존 코드베이스 스킬 확인**: 기존 스킬과의 관계를 먼저 파악
- `internal_codebase_only`
  - 현재 workspace의 codebase만 읽는다
  - 현재 workspace의 기존 `references/`, `knowledge_bases/`, `checklist-*`, `scripts/`만 쓴다
  - 외부 웹 검색과 새로운 외부 reference 유입은 금지한다
  - 현재 local source of truth와 정합적인 MD 작성/코딩이 목표일 때 쓴다

### 산출물:
- `references/` 디렉토리에 조사 결과 저장 (분 단위 타임스탬프 파일명: `*-atYYYY-MM-DD-HH-MM.md`)
- 아직 정제되지 않은 원자료/검색 메모/후보 문서도 우선 `references/`에 둔다
- `internal_codebase_only`를 썼다면 `reference_acquisition_mode: internal_codebase_only`를 남긴다
- 조사 없이 Phase 1로 넘어가지 않는다

---

## Phase 1: Knowledge Base 저장

`references/`에 모은 넓은 자료를 구조화·정리해 `knowledge_bases/`로 올린다.

### 절차:
1. `references/` 전체 파일 읽기
2. 반복 패턴/핵심 설계/채택할 방향만 추출
3. 원자료와 구분되는 KB 파일 작성
4. KB profile을 고른다:
   - `research_index_kb`: 조사 자산/후보/원자료 중심
   - `hybrid_kb`: 조사 자산을 유지하면서 `Canonical Design Takeaways`를 같은 문서에 함께 둠
   - `canonical_design_kb`: 채택된 설계만 남긴 좁은 source of truth 문서
5. 분기 규칙은 `research_index_kb -> (hybrid_kb | canonical_design_kb)`로 둔다
   - 공용 템플릿 규칙은 `(→ ../templates/progressive-context-skill-strategy-template.md "KB Profile Branch")`
   - 실전 예시는 `(→ ../../contract-to-concept-mapper/references/kb-profile-generalization-note-at2026-03-16-17-34.md)` 참고
6. checklist와 codebase의 source of truth가 될 KB에는 `Canonical Design Takeaways`를 포함한다

### 산출물:
- `knowledge_bases/` 디렉토리의 KB 파일 (`*-atYYYY-MM-DD-HH-MM.md`)
- 설계 요약, URL KB, canonical design takeaways
- 넓은 reference는 `references/indexes` 또는 `references/families`에 두고, 채택된 설계는 canonical KB에 고정
- `research_index_kb`는 탐색용이고, checklist 입력은 `hybrid_kb` 또는 `canonical_design_kb`로 닫는다
- KB profile 선택 기준은 `(→ ../templates/progressive-context-skill-strategy-template.md "KB Profile Branch")`로 되돌아가 확인한다
- 다른 workspace 재사용이 목표면 `(→ ../references/portable-skill-hierarchy-rules-at2026-03-17-09-22.md)` 기준으로 core context가 skill 내부에서 닫히는지도 같이 점검한다

---

## Phase 2: Knowledge Base 분석 + 정합성 평가용 Checklist

`knowledge_bases/`를 읽고 먼저 **정합성 평가용 checklist**를 만든다.

### 절차:
1. `knowledge_bases/` 전체 파일 읽기
2. 각 KB에서 **핵심 패턴** 추출:
   - 워크플로우 단계
   - 도구/명령어 목록
   - 주의사항/함정
   - 사례/패턴
3. 패턴 간 **교차 검증** — 여러 KB에서 공통으로 나오는 패턴 식별
4. **정합성 평가용 checklist 생성**:
   - 무엇이 맞아야 하는지를 먼저 고정
   - source of truth는 `Canonical Design Takeaways`가 있는 KB로 고정
   - 이 체크리스트가 구현용 checklist의 **입력**이 됨

### 산출물:
- `checklist-forconsistency-evaluation/`의 정합성 체크리스트 (`*-atYYYY-MM-DD-HH-MM.md` 권장)
- source of truth와 불일치 판정 기준
- 세부 추출/교차검증 기준은 `(→ references/intent-and-reference-analysis-details.md)` 참고

---

## Phase 3: 구현용 Checklist + TDD

정합성 평가용 checklist를 구현 항목으로 낮추고, 테스트를 먼저 설계한다.

### 절차:
1. consistency checklist에서 구현 대상 항목 추출
2. 구현용 checklist 작성
3. TDD 기준으로 테스트/입출력 계약을 먼저 설계
4. 이후 `scripts/` 또는 비문서 구현 파일을 만들 예정이면, 대응하는 TDD 파일 이름과 위치를 먼저 고정

### 산출물:
- `checklist-forimplementation/`의 구현용 체크리스트 (`*-atYYYY-MM-DD-HH-MM.md` 권장)
- 테스트 계획, 입력/출력 계약, 최소 smoke scenario
- TDD 파일 계획 (`scripts/test_*.py` 또는 `tests/test_*.py`)

---

## Phase 4: Codebase 작성

### 4-1. SKILL.md 작성 (~45줄)

### 필수 구조:
```
---
name: <skill-name>
description: >-
  Use this skill when [영어 트리거]. [한국어 설명].
---

# <Title>
## Purpose — 1-2줄
## When to use — 3-4개 트리거 사례
## Workflow — 4-6단계 명령형, reference 포인터 포함
## Scripts — scripts/ 파일 포인터 + 간략 용법
## References — 전체 reference 파일 포인터 (troubleshooting.md 포함 필수)
## Notes — 핵심 주의사항 + troubleshooting 규칙
```

### 품질 기준:
- description: "Use this skill when..." 패턴
- 45줄 이하
- `quick_validate`에서 SKILL.md line-count warning이 나오면 압축보다 먼저 자연스러운 split point를 찾아 별도 파일로 분리하고, `SKILL.md`에는 그 파일 링크를 추가한다
- 워크플로우: Phase 1 체크리스트의 핵심 패턴이 단계에 반영됨
- reference에 있는 내용을 SKILL.md에 중복하지 않음
- Notes: reference에서 발견한 실제 함정/주의사항
- **Progressive Context Injection**: 모든 하위 레이어 참조에 "(→ `파일경로` 섹션명)" 형식 사용
- **Notes에 해결된 버그 규칙 포함**: troubleshooting 케이스의 핵심만 1줄로

---

### 4-2. Scripts 작성 (적극 권장)

Scripts는 단순 자동화 도구가 아니라 **스킬 작동 결과를 추적·검증하는 핵심 인프라**다.

### 스크립트 3가지 역할:

**1. 작업 자동화** — reference의 반복 패턴을 CLI로 묶기
**2. 검증 로직** — 결과물의 구조/필수 필드 존재 여부 검증, exit code로 성공/실패 반환
**3. 결과 추적** — `--output` 옵션으로 결과를 파일 저장, 타임스탬프 포함 헤더

### 설계 원칙:
- `from __future__ import annotations` (Python 3.9 호환)
- CLI: `--help` 필수, subcommand 구조 권장
- 외부 의존성 없음 (subprocess로 CLI 도구 호출)
- exit code 계약: 정상=0, 경고=0+stderr, 실패=1
- stderr로 진행 상황/경고 출력, stdout은 결과 데이터만
- `_load_text()` / `_load_json()` 분리 — 반환 타입 혼재 방지 (→ `practical-lessons.md` §1)
- 존재 확인 함수는 래퍼 쓰지 말고 returncode 직접 검사 (→ `practical-lessons.md` §2)
- validate-before-mutate — 검증 실패 시 객체 무변경 보장 (→ `practical-lessons.md` §4)
- 경로 검증 3종: `..`, 절대경로, symlink 동시 검사 (→ `practical-lessons.md` §3)
- `scripts/`에 실행 파일을 추가하면 대응하는 TDD 파일도 함께 둔다
  - 권장: `scripts/test_<target>.py`
  - 대안: `tests/test_<target>.py`

### 구현 파일 규칙:
- `md/txt/image`가 아닌 구현 파일을 새로 만들면 TDD 파일을 함께 만든다
- 스크립트만 만들고 테스트 파일이 없으면 절차 위반으로 본다
- lint는 기본 경고, `quick_validate.py --strict`에서는 실패로 승격할 수 있다

### 좋은 예시:
| 스킬 | 스크립트 | 역할 |
|------|---------|------|
| github-deep-research | `deep_search.py` | 4개 scope 검색 자동화 |
| tmux-controller | `tmux_helper.py` | create→run→capture→stop 래핑 |
| worktree-parallel | `worktree_manager.py` | spawn→status→cleanup + .gitignore 관리 |
| agent-task-packet | `packet_builder.py` | new→validate→render-prompt 통합 |
| codex-worktree-dispatch | `dispatch_manager.py` | new→transition→merge-check 통합 |

---

### 4-2A. Contract Owner Map + Sync Audit

같은 사실이 여러 층에 복제될 때, **소유권을 먼저 고정**하고 projection이 동기화됐는지 검증하는 단계.

### 적용 조건 (아래 중 하나 이상 해당할 때 mandatory):
- 같은 fact(enum, field set, transition)가 **3개 이상 층**(reference + template + builder 등)에 복제되는 경우
- stable JSON/CLI **contract를 외부에 노출**하는 경우 (다른 skill이 이 contract을 consume)
- builder와 reference가 **동일한 enum/transition/field set을 각각 정의**하는 경우

적용 조건에 해당하지 않으면(단일 스크립트 skill, 문서형 skill 등) 이 단계를 건너뛴다.

### 절차:
1. **Fact owner map 작성** — 이 스킬에서 정의하는 핵심 사실마다 canonical owner를 **1곳만** 지정
   - 기계적 사실(enum, field set, transition, profile policy) → registry(.json) owner, reference(.md)는 mirror
   - 자연어 규칙(boundary, non-goals, why, 설계 원칙) → reference(.md) owner
   - template / builder constant / test = consumer (재정의 금지)
2. **Machine-readable registry 추가** — `references/contracts/<name>_contract_v<version>.json`에 enum, field set, transition 등 반복 사실을 기계가 읽을 수 있는 형태로 저장
3. **Sync audit 실행** — registry ↔ template ↔ builder ↔ test 간 parity를 기계적으로 비교
4. **Paired-change review** — SPEC과 code가 동시에 바뀌면 양방향 재확인 필수:
   - SPEC → code: SPEC 변경이 code에 반영됐는가
   - code → SPEC: code 변경이 SPEC/reference에 반영됐는가
   - 이 검토 없이 Phase 5로 넘어가지 않는다

### 산출물:
- `references/contracts/` 디렉토리의 registry JSON
- fact owner map (코드베이스 공용이면 `_shared/fact-owner-map.md`)
- sync audit 결과 (all in_sync이면 pass, drift가 있으면 수정 후 재실행)

### 기준:
- 수정 순서: owner-first (기계적 사실: registry → reference mirror → consumer, 자연어 규칙: reference → consumer) → audit
- 공용 패턴은 `(→ references/contract-sync-patterns-at2026-03-27.md)` 참고
- paired-change 규칙은 `(→ references/paired-spec-code-change-rule-at2026-03-27.md)` 참고

---

### 4-3. Evals 작성

super-skill-creator 스키마:
```json
{
  "skill_name": "<name>",
  "evals": [
    {
      "id": 0,
      "prompt": "실제 사용자가 할 법한 요청",
      "expected_output": "기대 결과 서술",
      "files": [],
      "assertions": ["Output includes X", "Output includes Y"]
    }
  ]
}
```
- 4개 이상, mainline + edge case
- assertions는 객관적으로 검증 가능

### 4-4. Execution Contract To Evidence

실행 계약을 만들었다면, 그 다음 구현/실행/증거 흐름도 고정한다.

### 절차:
1. implementation checklist와 TDD를 먼저 고정
2. 실행 계약 artifact를 입력으로 구현 진행
3. raw smoke artifact 저장
4. evidence ledger / support audit 계산
5. 필요하면 before/after diff까지 계산

### 산출물:
- smoke artifact
- evidence ledger
- support audit
- optional before/after diff

### 기준:
- 공용 규칙은 `(→ ../references/execution-evidence-pattern-at2026-03-17-04-03.md)` 참고
- single-run support 확인이 목적이면 `evidence-trace-auditor`
- fix effect까지 주장하면 `baseline-diff-lab`

---

## Phase 5: Smoke Test + 실험 결과 기반 References 갱신

### 5-1. 정적 검증 (자동)
```bash
python3 super-skill-creator/scripts/quick_validate.py <skill-dir>
python3 super-skill-creator/scripts/skill_smoke_test.py <skill-dir>
python3 <script> --help
python3 skill-creation-process/scripts/verify_artifact_order.py --skill-dir <skill-dir>
```

### 5-1G. Post-Validate Gates (quick_validate 후속)

quick_validate 통과 후, 아래 gate를 순서대로 실행한다. **validate 통과 ≠ 정렬 완료**임을 명심한다.

1. **Contract Sync Audit** (contract-heavy, 또는 `cross-skill(contract)`/`has-registry` tag 해당 — Skill Type Branch Gate 결정 규칙 참고)
   ```bash
   python3 _shared/scripts/audit_contract_sync.py
   ```
   - all `in_sync`이면 pass. `drift`가 하나라도 있으면 Phase 4.2A로 되돌아가 수정 후 재실행
   - 이 gate는 runtime validate와 **별개** — validate는 실행 호환성, sync audit는 canonical parity

2. **Reference Freshness Scan** (source-of-truth 변경이 있는 모든 round 종료 시 — code, KB, reference, registry, cross-skill contract 변경 포함)
   - Phase 5.3B 절차를 실행하여 `references/*-at...md`, `knowledge_bases/*`, `checklist-*`의 stale candidate를 선별
   - executable artifact가 바뀐 round면 smoke 직후, 문서/registry-only round면 round 종료 직후 실행
   - stale candidate가 있으면 Phase 5.3B의 갱신/archive 절차를 먼저 완료한 뒤 다음 단계로 진행
   - candidate가 없으면 pass

3. **Cross-Skill Dependency Audit** (선택적 v1 — `cross-skill(contract)` consumer만)
   ```bash
   python3 _shared/scripts/audit_cross_skill_dependencies.py --skills-root .
   ```
   - v1 자동화는 declaration 존재, provider/contract 경로, `last_synced_at` stale 여부만 검사
   - semantic drift는 `(→ references/reverse-entry-workflow-at2026-03-27.md)`의 수동 절차를 유지
   - `--strict`는 declaration 규칙이 안정된 뒤에만 사용

**이 두 gate를 건너뛰면 "테스트 통과했는데 문서가 낡은" 문제가 반복된다.**

### 5-2. 실전 테스트 / Smoke Test (tmux + Codex)
Claude가 tmux-controller로 Codex를 격리 세션에서 실행하여 스킬을 실전 테스트:
```bash
# tmux 세션 생성 → Codex 실행 → 출력 캡처 → 정리
python3 tmux-controller/scripts/tmux_helper.py create codex-test
python3 tmux-controller/scripts/tmux_helper.py run codex-test "codex exec --full-auto '<prompt>'"
python3 tmux-controller/scripts/tmux_helper.py wait codex-test --pattern "tokens used" --timeout 180
python3 tmux-controller/scripts/tmux_helper.py capture codex-test --lines 300
python3 tmux-controller/scripts/tmux_helper.py kill codex-test
```

**실전 테스트에서 의도적으로 넣어야 할 edge case 입력:**
- 빈 값 / 최소 길이 미달 (빈 `why`, 1글자 `goal`)
- 경로 조작: `..`, 절대경로, symlink
  symlink는 placeholder 문자열이 아니라 **실제 fixture 경로**로 넣는다
- 한국어 경로 / 특수문자 경로
- 이미 존재하는 ID / 이미 점유된 경로
- 최대 재시도 초과 상태에서 전이 시도

> 정적 검증(--help, validate)으로는 발견 불가능한 버그가 실전 테스트에서 노출된다. (→ `practical-lessons.md` §6)
> multi-file smoke raw archive는 `logs/smoke/<command>/<timestamp>/...`에 보관하고, detailed layout은 `(→ smoke-archive-layout-rule-at2026-03-21-19-06.md)`를 따른다.

### 5-3. 실험 결과 기반 Reference 갱신
이 단계의 저장 경계는 `(→ issue-evidence-storage-rule-at2026-03-21-16-33.md)`를 따른다.
`references/fixtures/`는 sample bundle 계층이며 smoke issue 저장소가 아니다.
raw multi-file archive가 필요하면 `logs/smoke/<command>/<timestamp>/...`로 분리하고 smoke report에 `archive_dir`를 기록한다.

1. **`references/troubleshooting.md`** 에 상세 케이스 추가 (증상 → 원인 → 해결 → 교훈)
2. 새로 얻은 운영 규칙/예시/경계 설명을 `references/`에 반영
3. **SKILL.md Notes** 에 해결된 규칙 1줄 추가 + `(→ references/troubleshooting.md CASE-XXX)` 포인터
4. **같은 패턴이 반복되면 validate 함수에 추가** — 문서 규칙에서 코드 검증으로 승격 (→ `practical-lessons.md` §11)
5. active artifact rename/delete/cleanup이 필요하면 `(→ references/artifact-lifecycle-bridge-at2026-03-16-23-58.md)`를 따라 `artifact-lifecycle-manager`로 handoff
6. 실험 결과를 KB insight로 올릴 때는 바로 KB를 고치지 말고 `(→ ../references/evidence-promotion-pattern-at2026-03-17-03-45.md)`의 승격 파이프라인을 따른다

### 5-3A. Portable Install Readiness Audit

다른 workspace의 Codex CLI가 이 skill을 바로 쓸 예정이면, link/bridge 계층을 먼저 감사한다.

### 절차:
1. `(→ ../portable-skill-hierarchy-rules-at2026-03-17-09-22.md)` 기준으로 분류 규칙 확인
2. `scripts/skill_portability_audit.py`로 `internal / bridge / external_dependency / missing` 분포를 계산
3. `external_dependency`가 있으면
   - install set에 포함할지
   - internal sample로 복제할지
   - optional fixture로 남길지
   결정한다
4. `absolute_path`와 `missing`은 다른 workspace 배포 전 우선 제거한다

### 산출물:
- portability audit JSON
- portability audit MD
- install set에 포함해야 할 sibling skill/폴더 목록

### 5-3B. Reference Freshness Audit

코드가 바뀐 뒤 `references/*-at...md`, `knowledge_bases/*`, `checklist-*`가 stale candidate가 되는 문제를 공용 절차로 잡는다.

### 절차:
1. **stale candidate 탐지** — `artifact-lifecycle-manager scan-stale-candidates`로 문서 내 참조 대상의 mtime을 비교
2. **semantic owner 분류** — 각 stale candidate를 rule_bearing(→ doc-code-sync-checker) 또는 claim_heavy(→ claim-verifier)로 분류
3. **갱신 또는 archive 결정**:
   - 여전히 유효 → 최소 review 기록(`reviewed_at`, `review_basis`)을 남긴 뒤 candidate 해제. **touch만으로 해제 금지**
   - rule_bearing 문서 → semantic recheck(doc-code-sync-checker) 없이 해제 금지
   - 내용이 outdated → reference 갱신 후 sync audit 재실행
   - 더 이상 필요 없음 → artifact-lifecycle-manager로 archive/delete handoff
4. **contract registry 정합성 재확인** — freshness audit 중 registry와 reference 간 drift가 발견되면 Phase 4.2A sync audit로 되돌아간다

### 산출물:
- stale candidate 목록 (file, status, semantic_owner)
- 갱신된 reference 파일 또는 archive handoff 기록

### 기준:
- 공용 패턴은 `(→ references/reference-freshness-audit-pattern-at2026-03-27.md)` 참고
- review record 저장 위치: `references/` → 대상 문서의 YAML frontmatter, `knowledge_bases/`·`checklist-*` → sidecar `.freshness_audit.yaml`. shape와 분기 규칙은 `(→ references/reference-freshness-audit-pattern-at2026-03-27.md)` Review Record Shape 참고
- stale candidate ≠ semantic stale — 1차 탐지만 하고 최종 판단은 semantic owner에게 위임

---

### 5-4. Evidence To KB Promotion

실험 결과를 reusable rule이나 insight로 올릴 때는 아래 순서를 고정한다.

1. `evidence -> summary`
2. `summary -> promotion trigger evaluation`
3. `promotion trigger -> KB patch plan`
4. `KB patch plan -> KB copy apply`
5. 필요한 경우에만 `canonical_design_kb` candidate를 따로 평가

### 산출물:
- promotion summary
- promotion trigger evaluation
- KB patch plan
- patched KB copy 또는 hold report

### 기준:
- `hybrid_kb`는 `lesson_candidate >= 1` 과 `residual_uncertainty = 0`일 때만 `promote`
- `canonical_design_kb`는 여기에 더해 반복 검증 신호가 있을 때만 `candidate`
- 상세 규칙과 예시는 `(→ ../references/evidence-promotion-pattern-at2026-03-17-03-45.md)` 참고

---

## Phase 6: 계획 관리 (계획 = 일급 아티팩트)

- 간단한 변경은 일시적 계획으로 처리
- 복잡한 작업은 **실행 계획**으로 리포지토리에 저장 (`plans/` 디렉토리)
- 진행 중인 계획, 완료된 계획, 기술 부채 모두 **버전화**
- `quick_validate.py` / `skill_smoke_test.py`가 구조 검증을 자동 수행

---

## Phase 7: 구조적 제약 (아키텍처 린터)

### 적용 범위:
- **파일 크기 제한**: SKILL.md ≤ 50줄
- **명명 규칙**: reference/knowledge_base/checklist 문서 파일명에 분 단위 타임스탬프 (`-at2026-03-14-13-58`)
- **생성 순서**: `knowledge_base -> consistency checklist -> implementation checklist` 메타데이터 순서 보장
- **의존성 방향**: SKILL.md → scripts/ → references/ (역방향 참조 금지)
- **exit code 계약**: 모든 스크립트는 0(성공) / 1(실패)
- **필수 파일 존재**: `references/troubleshooting.md` 없으면 린트 경고

### 린트 오류 메시지로 수정 지침 주입:
- 예: `"SKILL.md가 50줄을 초과합니다. 상세 내용을 references/로 이동하세요."`
- line-count warning이 나오면 기본 반응은 문장 압축이 아니라 split point 탐색 + 별도 파일 링크 추가다
- 예: `"스크립트에 --help가 없습니다. argparse를 추가하세요."`
- 예: `"references/troubleshooting.md 없음. 필수 파일입니다."`
- 예: `"consistency checklist 파일명에 분 단위 타임스탬프가 없습니다."`

### lifecycle handoff:
- rename, replace, delete, duplicate cleanup이 나오면 skill-creation-process 안에서 즉흥적으로 정리하지 않는다
- `(→ references/artifact-lifecycle-bridge-at2026-03-16-23-58.md)`를 따라 `artifact-lifecycle-manager`에서 order/duplicate audit를 먼저 돌린다
