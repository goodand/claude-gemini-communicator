# Phase Guide — Skill 제작 상세 절차

## Phase -1: 동기 정의 (최선행)

스킬 제작의 **출발점은 반복되는 문제**다. 왜 이 스킬이 필요한지를 먼저 확정한다.

### 절차:
1. **반복 패턴 식별** — Agent/Codex가 반복적으로 실수하거나 비효율이 발생하는 지점
2. **목표 설정** — 이 스킬이 해결할 구체적 문제 1문장
3. **우선순위 분석** — 다른 스킬 대비 긴급도·영향도 판단
4. **의존성 분석** — 선행 스킬이 필요한지, 기존 스킬과 책임 겹침이 있는지
5. **기능 범위 경계 (비목표)** — 이 스킬이 **하지 않을 것**을 명시. agent-task-packet의 non_goals 개념과 동일:
   - `Case: State` — 보장하지 않는 상태
   - `Case: Type` — 제외할 에러/예외
   - `Case: Performance` — null/over/under
6. **구현 순서 계획** — 단계별 구현 순서 (의존성 그래프 기반)

### 산출물:
- 1문장 목표 + 비목표 목록 + 의존성 그래프
- 이것 없이 Phase 0으로 넘어가지 않는다

---

## Phase 0: 자료 조사

근거 자료를 먼저 확보한다. 자료 없이 초안을 작성하지 않는다.

### 조사 방법:
- **GitHub 딥리서치**: `github-deep-research` 스킬로 유사 오픈소스 탐색
- **논문/사례 검색**: 관련 논문, 블로그, 기술 문서 탐색
- **Codex CLI 활용**: 로컬 코드 분석이 필요하면 Codex에게 요청
  - Codex는 샌드박스(네트워크 차단)이므로 **로컬 코드 분석·리팩토링** 전용
  - API 호출·외부 검색이 필요한 조사는 Claude 또는 사용자가 직접 수행
- **기존 코드베이스 스킬 확인**: 기존 스킬과의 관계를 먼저 파악

### 산출물:
- `knowledge_bases/` 디렉토리에 조사 결과 저장 (타임스탬프 파일명)
- 조사 없이 Phase 1로 넘어가지 않는다

---

## Phase 1: Reference 분석 (입력)

1. `knowledge_bases/` 전체 파일 읽기
2. 각 reference에서 **핵심 패턴** 추출:
   - 워크플로우 단계
   - 도구/명령어 목록
   - 주의사항/함정
   - 사례/패턴
3. 패턴 간 **교차 검증** — 여러 reference에서 공통으로 나오는 패턴 식별
4. **Reference 기반 Checklist 생성**:
   - reference에서 발견한 핵심 패턴을 체크리스트로 정리
   - 이 체크리스트가 Phase 2 SKILL.md 작성의 **입력**이 됨
5. **Task용 references 정제** — 조사 자산에서 실제 skill 사용 시 필요한 문서만 `references/`로 승격:
   - 필드 정의서, 예시 모음, 체크리스트, 책임 경계표
   - troubleshooting 케이스 — 실험 후 추가
   - 각 문서는 **독립적으로 읽을 수 있어야** 함
6. **SKILL.md에 녹일 것 vs references에 남길 것** 분리 기준:
   - SKILL.md: 워크플로우 골격, 언제 쓸지, 핵심 주의사항
   - references: 실제 task 수행용 상세 커맨드, 스키마, 운영 규칙
   - knowledge_bases: 사례 조사, 외부 URL KB, 설계 근거, 긴 탐색 로그

---

## Phase 2: SKILL.md 작성 (~45줄)

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
- 워크플로우: Phase 1 체크리스트의 핵심 패턴이 단계에 반영됨
- reference에 있는 내용을 SKILL.md에 중복하지 않음
- Notes: reference에서 발견한 실제 함정/주의사항
- **Progressive Context Injection**: 모든 하위 레이어 참조에 "(→ `파일경로` 섹션명)" 형식 사용
- **Notes에 해결된 버그 규칙 포함**: troubleshooting 케이스의 핵심만 1줄로

---

## Phase 3: Scripts 작성 (적극 권장)

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

### 좋은 예시:
| 스킬 | 스크립트 | 역할 |
|------|---------|------|
| github-deep-research | `deep_search.py` | 4개 scope 검색 자동화 |
| tmux-controller | `tmux_helper.py` | create→run→capture→stop 래핑 |
| worktree-parallel | `worktree_manager.py` | spawn→status→cleanup + .gitignore 관리 |
| agent-task-packet | `packet_builder.py` | new→validate→render-prompt 통합 |
| codex-worktree-dispatch | `dispatch_manager.py` | new→transition→merge-check 통합 |

---

## Phase 4: Evals 작성

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

---

## Phase 5: 검증 (3단계)

### 5-1. 정적 검증 (자동)
```bash
python3 super-skill-creator/scripts/quick_validate.py <skill-dir>
python3 super-skill-creator/scripts/skill_smoke_test.py <skill-dir>
python3 <script> --help
```

### 5-2. 실전 테스트 (tmux + Codex)
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

### 5-3. Troubleshooting 패턴 저장
1. **`references/troubleshooting.md`** 에 상세 케이스 추가 (증상 → 원인 → 해결 → 교훈)
2. **SKILL.md Notes** 에 해결된 규칙 1줄 추가 + `(→ references/troubleshooting.md CASE-XXX)` 포인터
3. **같은 패턴이 반복되면 validate 함수에 추가** — 문서 규칙에서 코드 검증으로 승격 (→ `practical-lessons.md` §11)

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
- **명명 규칙**: 스크립트 파일명에 타임스탬프 (`-at2026-03-14`)
- **의존성 방향**: SKILL.md → scripts/ → references/ (역방향 참조 금지)
- **exit code 계약**: 모든 스크립트는 0(성공) / 1(실패)
- **필수 파일 존재**: `references/troubleshooting.md` 없으면 린트 경고

### 린트 오류 메시지로 수정 지침 주입:
- 예: `"SKILL.md가 50줄을 초과합니다. 상세 내용을 references/로 이동하세요."`
- 예: `"스크립트에 --help가 없습니다. argparse를 추가하세요."`
- 예: `"references/troubleshooting.md 없음. 필수 파일입니다."`
