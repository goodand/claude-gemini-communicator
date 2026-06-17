# Progressive Context Skill Strategy Template

## Purpose

이 템플릿은 `reference 정리법`이 아니라 `Skill 전체 설계 전략`을 잡기 위한 것이다.
핵심 목표는 문서를 많이 두는 것이 아니라, LLM이 필요한 층만 단계적으로 읽도록 설계하는 것이다.

## Core Principle

`trigger -> router -> index -> family -> canonical contract -> checklist -> scripts/tests -> evidence`

- 앞단 문서는 **무엇을 읽을지 고르는 문서**
- 중간 문서는 **무엇을 따를지 고정하는 문서**
- 뒷단 문서는 **실제로 실행하고 검증하는 문서**

## Layer Strategy

### 0. Trigger Layer

- 위치: `SKILL.md` frontmatter
- 역할: 언제 이 skill을 써야 하는지 최소 정보만 제공
- 규칙:
  - 문제 유형
  - 제외할 문제 유형
  - 언제 이 skill이 아닌 다른 skill을 써야 하는지

### 1. Router Layer

- 위치: `SKILL.md` 본문
- 역할: 링크 중심 네비게이션
- 규칙:
  - 직접 설명보다 읽을 문서 순서를 안내
  - variant/family 선택 기준을 먼저 제시
  - 상세 설명은 하위 문서로 내린다

### 2. Index Layer

- 예시: `metric_definition_examples.md`
- 역할: family index / variant index / concept map
- 규칙:
  - 넓은 공간을 빠르게 훑게 해주는 문서
  - 어떤 family 문서로 내려갈지 결정
  - source of truth가 아니라 탐색용 지도

### 3. Family Layer

- 예시: family별 reference 문서
- 역할: tags + script/output mapping + 사용 맥락 정리
- 규칙:
  - 비슷한 케이스를 묶어둔다
  - 후보 구조와 패턴을 정리한다
  - 아직 최종 계약 문서는 아니다

### 4. Canonical Contract Layer

- 예시:
  - `Canonical Design Takeaways`
  - naming/formula governance
  - output contract
- 역할: 현재 채택한 설계만 남기는 규범층
- 규칙:
  - checklist와 codebase의 직접 입력이 된다
  - research 후보, 대안, 탐색 로그와 분리한다
  - source of truth를 여기에 고정한다

### 5. Consistency Checklist Layer

- 위치: `checklist-forconsistency-evaluation/`
- 역할: canonical contract가 실제로 유지되는지 판정
- 규칙:
  - 무엇이 맞아야 하는지 먼저 고정
  - implementation checklist의 입력
  - 비교 단위와 metric 정의가 명확해야 한다

### 6. Implementation Checklist Layer

- 위치: `checklist-forimplementation/`
- 역할: consistency checklist를 구현 가능한 작업 단위로 내림
- 규칙:
  - scripts/tests/outputs를 포함
  - 임시성이 더 강함
  - source of truth는 consistency checklist

### 7. Execution Layer

- 위치: `scripts/`, `tests/`, `evals/`
- 역할: 실제 구현과 검증
- 규칙:
  - scripts를 만들면 대응하는 TDD 파일을 같이 만든다
  - stdout/stderr/exit code 계약을 분리한다
  - `--help`와 smoke test를 제공한다

### 8. Evidence Layer

- 위치 (2층 분리):
  - **Raw archive**: `logs/`, `runs/` — raw logs, raw artifact, evidence ledger, support audit (`issue-evidence-storage-rule` Layer 1)
  - **Human-readable summary**: `references/troubleshooting.md`, `references/*-smoke-*.json` (`issue-evidence-storage-rule` Layer 2~3)
- 역할: 실제 결과와 오류를 축적
- 규칙:
  - raw archive를 먼저 저장하고, 요약으로 대체하지 않는다
  - 반복 버그는 troubleshooting 케이스로 저장한다 (CASE-XXX 형식)
  - 다음 canonical contract 개선의 입력으로 사용한다
  - 상세 저장 경계: `(→ ../references/issue-evidence-storage-rule-at2026-03-21-16-33.md)`

## Template Identity Rules

모든 template / reference 파일은 아래 4가지 신분 중 하나를 가진다. 신분이 모호하면 canonical처럼 읽히는 문제가 반복된다.

### Canonical Template
- manifest에 canonical로 등록된 파일
- 예: `task_packet_standard_template.json`, `dispatch_state_extended_template.json`
- canonical template는 **owner가 아니라 projection** — fact별 owner(기계적 사실→registry, 자연어 규칙→reference)의 내용을 반영만 함
- template 자체가 enum/field를 정의하지 않는다

### Local Support Template
- canonical template보다 풍부한 예시, 설명, 주석을 포함하는 파일
- 예: `task_packet_template.json` (canonical extended를 감싸는 예시 문서)
- canonical에 없는 규범을 local support에만 두면 안 됨 → 규범은 canonical로 승격
- 예시와 학습 보조 정보만 여기에 둔다

### Legacy Alias
- 이전 이름/구조에서 새 canonical 파일을 가리키는 stub
- 예: `task_state_extended_template.json` → `dispatch_state_extended_template.json`
- 본문에 `_comment: "LEGACY ALIAS"` + `canonical_files` 포인터만 가진다
- 새 코드에서 import/참조 금지

### Runtime Evidence
실행 결과를 두 층으로 나눈다:

**Raw archive** — `logs/`, `runs/` 디렉토리에 격리
- raw logs, raw artifact, evidence ledger, support audit
- 가공하지 않은 원본. 요약으로 대체하지 않는다
- `issue-evidence-storage-rule`의 Layer 1에 해당

**Human-readable summary** — `references/` 디렉토리에 포인터로 저장 허용
- `references/*-smoke-*.json` — smoke 결과 요약
- `references/troubleshooting.md` — 서술 증거 (CASE-XXX 형식)
- raw archive의 `archive_dir`를 포인터로 가리킴
- `issue-evidence-storage-rule`의 Layer 2~3에 해당

template로 착각하지 않도록 raw archive는 반드시 `logs/`/`runs/`로 분리

### 판별 규칙 (1순위: 외부 manifest → 2순위: 파일 내부 메타):
1. `template_manifest.json`의 `canonical` 배열에 있음 → canonical template
2. `template_manifest.json`의 `legacy_alias` 배열에 있음 → legacy alias
3. `template_manifest.json`의 `local_support` 배열에 있음 → local support
4. `runs/`, `logs/`, `reports/` 디렉토리에 있음 → runtime evidence
5. 위 모두 아님 → 분류 오류. manifest에 먼저 등록할 것

**핵심**: `template_manifest.json`이 유일한 판별 소스. `$schema_notes`는 보조 정보일 뿐 판별 기준이 아니다.

manifest 자체의 owner, 위치, 필수 필드, 갱신 규칙은 `(→ ../references/template-identity-rule-at2026-03-27.md)` Manifest Contract + Manifest 관리 규칙 참고

---

## Recommended Folder View

```text
<skill-name>/
├── SKILL.md
├── references/
│   ├── <index-doc>.md
│   ├── <family-doc>.md
│   └── troubleshooting.md
├── knowledge_bases/
│   └── <canonical-kb>.md
├── checklist-forconsistency-evaluation/
│   └── <consistency-checklist>.md
├── checklist-forimplementation/
│   └── <implementation-checklist>.md
├── scripts/
│   ├── <script>.py
│   └── test_<script>.py
└── evals/
    └── evals.json
```

## Decision Rules

### Reference Acquisition Branch

- 절차 본문과 연결된 규칙은 `(→ ../references/phase-guide.md "Phase 0: 자료 조사 + Reference 저장")`
- 기본값은 `external_research`
- 사용자가 명시적으로 요청할 때만 `internal_codebase_only`
- `internal_codebase_only`에서는
  - 외부 웹 검색을 하지 않는다
  - 현재 workspace의 codebase와 local artifact만 사용한다
  - local checklist/contract/source-of-truth와의 정합성을 우선한다
- MD 작성이나 script 작성이 현재 local contract에 맞아야 하는 작업이면 이 분기가 특히 유용하다
- 상세 규칙은 `(→ ../references/reference-acquisition-modes-at2026-03-17-09-35.md)`

### KB Profile Branch

- 절차 본문과 연결된 규칙은 `(→ ../references/phase-guide.md "Phase 1: Knowledge Base 저장")`
- `research_index_kb`
  - Reference 조사 자산, 후보, 원자료를 넓게 모아두는 KB
  - 아직 checklist source of truth는 아니다
- `hybrid_kb`
  - 조사 자산을 유지하면서 같은 문서 안에 `Canonical Design Takeaways`를 함께 둔다
  - 탐색용 정보와 source of truth slice를 같이 가져가고 싶을 때 쓴다
- `canonical_design_kb`
  - 채택한 설계만 남긴 좁은 source of truth 문서
  - checklist/codebase/eval이 직접 읽는 기준 문서로 가장 적합하다
- 분기 규칙:
  - `research_index_kb -> hybrid_kb`
  - 또는 `research_index_kb -> canonical_design_kb`
  - `hybrid_kb -> canonical_design_kb`는 선택적 세분화다
- consistency checklist의 source of truth는 `hybrid_kb` 또는 `canonical_design_kb`로 고정한다
- 실제 적용 메모는 `(→ ../../contract-to-concept-mapper/references/kb-profile-generalization-note-at2026-03-16-17-34.md)` 참고

### 문서가 너무 넓다면

- `references/index` 성격으로 내린다
- family 선택과 탐색을 돕는 문서로 사용한다

### 문서가 실제 구현 기준이라면

- `knowledge_bases/` 또는 canonical contract 섹션으로 승격
- checklist의 source of truth로 사용
- consistency checklist가 있으면 `Canonical Design Takeaways`가 있는 KB를 source of truth로 둔다

### 문서가 후보/대안/사례 모음이라면

- family 또는 index 층에 둔다
- 탐색/선별 입력으로 사용하고, 채택된 설계는 canonical contract 층으로 올린다

### 문서가 metric/formula/naming 규칙이라면

- canonical contract 층으로 승격
- implementation 전 반드시 consistency checklist에 반영

### 실험 결과를 KB로 올릴 때

- 바로 KB를 수정하지 말고 `evidence -> summary -> trigger evaluation -> KB patch plan -> KB apply` 순서를 따른다
- `hybrid_kb`는 `lesson_candidate`와 `residual_uncertainty` 기준으로 먼저 판정한다
- `canonical_design_kb`는 반복 검증 신호가 더 있을 때만 후보로 본다
- 공용 규칙은 `(→ ../references/evidence-promotion-pattern-at2026-03-17-03-45.md)` 참고

### 실행 계약을 증거로 내릴 때

- `execution contract -> TDD -> implementation -> smoke -> evidence audit -> optional diff` 순서를 따른다
- single-run support 확인이 목적이면 `evidence-trace-auditor`를 먼저 붙인다
- before/after improvement 주장까지 필요하면 `baseline-diff-lab`을 추가한다
- 공용 규칙은 `(→ ../references/execution-evidence-pattern-at2026-03-17-04-03.md)` 참고

## Skill Type Branch

> **이 섹션은 `phase-guide.md` Skill Type Branch 섹션의 mirror다.**
> canonical 정의(primary type, secondary tags, gate 결정 규칙)는 `(→ ../references/phase-guide.md)` 참고.

Fill-In Template의 Skill Identity에서 primary type 1개 + secondary tags를 먼저 결정한다.

## Reverse-Entry Workflow

이 전략의 Layer 0~8은 문서 계층 구조이고, phase-guide.md의 Phase -2~7은 작업 절차다.
평가/리팩토링 중 issue가 발생하면 issue가 가리키는 layer를 식별하고, 대응하는 phase로 직접 재진입한다.

상세 규칙: `(→ ../references/reverse-entry-workflow-at2026-03-27.md)`

---

## Fill-In Template

### Skill Identity

- skill name:
- primary type: (document-only / contract-heavy / runtime-heavy)
- secondary tags: (cross-skill(contract), cross-skill(adjacent), has-registry — 해당 없으면 비움)
- consumer dependency declaration: (`cross-skill(contract)` consumer면 `references/cross_skill_dependencies.yaml`, 아니면 비움)
- 핵심 문제:
- 비목표:
- 다른 skill과의 경계:

### Router Plan

- SKILL.md에서 바로 안내할 문서:
- SKILL.md에서 숨길 상세 정보:

### Index Plan

- 어떤 family/index 문서가 필요한가:
- variant 선택 기준은 무엇인가:

### Canonical Contract Plan

- 현재 채택한 naming rule:
- 현재 채택한 formula / metric:
- 현재 채택한 output contract:
- 현재 채택한 guardrail:

### Checklist Plan

- consistency checklist source:
- implementation checklist source:
- scripts/test mapping:

### Evidence Plan

- smoke test 방식:
- troubleshooting 저장 규칙:
- report/coverage 파일명 규칙:

## Short Heuristic

- `references`는 넓게 모은다
- `knowledge_bases`는 `research_index_kb`에서 시작하고, 필요 시 `hybrid_kb` 또는 `canonical_design_kb`로 올린다
- checklist source of truth는 `Canonical Design Takeaways`가 있는 KB로 고정한다
- 실행 계약을 구현/관측으로 내릴 때는 `TDD -> implementation -> smoke -> evidence audit -> diff`를 고정한다
- 실험 결과는 `summary -> trigger -> patch plan -> apply`를 거쳐 KB로 올린다
- `consistency checklist`는 canonical contract를 판정한다
- `implementation checklist`는 consistency checklist를 실행 단위로 내린다
- `scripts/tests`는 마지막에 구현하지만 TDD 계획은 먼저 고정한다
