---
name: troubleshooting-cot-2
description: Git 히스토리 기반 Chain-of-Thought 트러블슈팅. 커밋 메시지 분석, Good/Bad Case 식별, 실행 기반 가설 검증을 통해 버그의 근본 원인을 체계적으로 찾습니다. 에러 발생, 회귀 버그, 예상치 못한 동작, 간헐적 버그 발견 시 사용하세요. 트리거: 트러블슈팅, 디버깅, 회귀 버그, 근본 원인, root cause, bisect, good/bad case, 왜 안 되지, 에러 원인.
license: Apache-2.0
metadata:
  version: "3.4"
  context_window: 2000000
---

# Troubleshooting-CoT

Git 히스토리와 Chain-of-Thought를 결합한 체계적 트러블슈팅.
**Git 이력(과거 실행 결과의 아카이브)**을 근거로 현재 코드를 분석하라.

## 이 스킬은 merge 판단용이 아닙니다

이 스킬은 **회귀 원인 추적과 git history 분석 전용**입니다. merge readiness 판단, PR scope 결정, split/archive 판단은 이 스킬의 범위가 아닙니다.

- merge 판단이 필요하면 → merge-audit family (`runtime-core-merge-audit`, `artifact-noise-merge-audit`, `red-team-merge-verdict` 등)로 전환하세요.
- 이 스킬의 출력(root cause, delta, fix)은 merge-audit의 **입력 근거**로 쓸 수 있지만, 이 스킬이 직접 merge verdict를 내리지 않습니다.

## 5 원칙

1. **실행 > 추측**: Linter/테스트 먼저, LLM 분석은 최후
2. **메시지 → diff 순**: 커밋 메시지로 1차 필터 → 상위만 diff 분석
3. **Good/Bad 델타**: 구체적 델타(Δ)를 파일:라인 + 변경 전/후로 명시한다
4. **반사실적 검증**: "IF X THEN Y" 형태로 실제 테스트
5. **패턴 저장**: 해결 후 반드시 PATTERN_LIBRARY.md에 기록

## 프로세스

```
Phase 0  → 목표 설정 (문제 정의)
Phase 1  → 변경 범위 탐색 (Working Tree → HEAD → 40개 확대)
Phase 2  → diff 기반 Good/Bad Case 분석
Phase 3  → 실행 기반 가설 검증
  3-0: 문법 검증 (자동)
  3-1: Git Bisect (자동)
  3-2: Mutation Testing (수동)
  3-3: 임시 계측 (수동)
  3-4: 하드코딩 재구현 (수동)
  3-5: LLM 분석 (최후)
Phase 4  → 해결 + 패턴 문서화
Phase 5  → 악순환 탐지 + 루프 탈출
  5-1: 사후 패턴 분석
  5-2: 코드베이스 검색
  5-3: 외부 검색 (Google)
  5-4: 연계 스킬 전환

※ 근거가 명확하면 Phase 건너뛰기 허용.
  예: 원인 후보를 이미 알면 Phase 1-2 생략 → Phase 3부터.
  예: 커밋 1개뿐이면 Phase 1 생략.
```

## 자가 점검 (매 Phase 전환 시)

- [ ] 델타에 `파일:라인` + `변경 전/후`를 명시했다
- [ ] 모든 서술이 검증 가능한 사실이다 (✅ "커밋 abc의 파일:42에서 X→Y")
- [ ] 이전과 다른 파일 또는 다른 방식으로 시도한다 (같다면 → Phase 5)

---

## Phase 0: 목표 설정

**입력:** 증상, 재현 조건, 예상 vs 실제 동작
**출력:** 명확한 문제 정의 + 범위

```
문제: [구체적 증상]
범위: [모듈/기간]
```

컨텍스트 70% 이상 확보 시 Phase 1 진행.

---

## Phase 1: 변경 범위 탐색 (가벼운 것부터)

**단계적 확대 (대부분의 버그는 최근 변경에 있다):**

1. **Working Tree / HEAD 먼저** (LLM이 직접 `git diff` 결과를 읽고 판단):
```bash
git diff                    # 아직 커밋 안 한 변경
git diff HEAD~1             # 직전 커밋
git log -5 --stat           # 최근 5개 커밋 요약
```

2. **안 보이면 확대:** 최근 40개 커밋 스코어링
```bash
git log -40 --pretty=format:"%h|%ad|%an|%s" --date=short
```

LLM에게 0-10점 스코어링 요청. 프롬프트: [references/GEMINI_PROMPTS.md](references/GEMINI_PROMPTS.md) 템플릿 1

**인라인 스코어링 기준:**
- 문제 키워드 직접 언급: +3점
- 관련 모듈/파일 수정: +2점
- 테스트/검증 포함: +2점
- 리팩토링·문서만: -3점

9-10점 커밋 → Phase 2로.

---

## Phase 2: Good/Bad Case 정밀 분석

HIGH 커밋들의 diff 수집:
```bash
git show <commit_hash> -p
# 구조적 변경 확인 (Python only):
python scripts/semantic_diff.py --good <good_hash> --bad <bad_hash> --file path/to/file.py
# 출력 예: [-] REMOVED: validate_response  ← 코드 누락 의심!
#         [*] MODIFIED: generate_story    ← 로직 변경
#         [->] RENAMED: process_data -> handle_data  ← 이름만 변경, 무시 가능
```

LLM에게 분석 요청. 프롬프트: [references/GEMINI_PROMPTS.md](references/GEMINI_PROMPTS.md) 템플릿 2

**필수 출력 형식:**
```
Good Case: <커밋 해시>
메커니즘: [수도코드 3줄 이내]

Bad Case: <커밋 해시>
위반: [구체적 변경 사항]

델타(Δ):
  파일: path/to/file.js:42
  변경 전: setState({key: value})
  변경 후: setState(key, value)
  영향: API 시그니처 불일치 → TypeError
```

**Phase 3 진행 기준 — 다음 수준이어야 한다:**

| ✅ 이 수준으로 작성한다 | → 이 수준은 재분석 |
|------------------------|-------------------|
| "커밋 abc의 file.js:42에서 X→Y 변경이 원인이다" | "이 커밋이 의심스럽다" |
| "이 변경이 원인이면 bisect가 이 커밋을 가리킨다" | "여기가 문제일 수도 있다" |
| 파일:라인 + 변경 전/후 + 영향이 있는 델타 | 파일:라인 또는 변경 전/후가 빠진 델타 |

---

## Phase 3: 실행 기반 가설 검증

빠르고 확실한 것부터 순서대로 실행한다.

**가설 선언 (매 검증 전 필수):**
```
가설: [X를 Y로 바꾸면 문제가 해결된다]
근거: Phase 2 델타에서 [파일:라인]의 변경이 원인
검증 방법: [3-0 ~ 3-5 중 선택]
예상 결과: 성공 시 [이것], 실패 시 [다음 가설로 전환]
```

### 3-0. 문법 검증 (최우선, Working Tree 변경 없음)

**프로젝트 린터가 있으면 그것을 우선 사용** (`package.json`의 `scripts` 또는 `Makefile`에서 lint 명령 확인):
```bash
npm run lint          # JS/TS 프로젝트
ruff check .          # Python 프로젝트
tsc --noEmit          # TypeScript 타입 검증
```

**린터가 없거나 과거 커밋 검증 시 폴백:**
```bash
python scripts/syntax_checker.py --commits abc123,def456
```

- `git show`로 파일 추출 → 임시 파일 검증 → Working Tree 안전

### 3-1. Git Bisect

```bash
python scripts/bisect_runner.py --good abc123 --bad HEAD --test "npm test"
```

### 3-2. Mutation Testing

의심 함수 무력화 → 인과관계 검증. 상세: [references/HYPOTHESIS_GUIDE.md](references/HYPOTHESIS_GUIDE.md)

### 3-3. 임시 계측 (Instrumentation)

간헐적 버그, 비동기 타이밍, 런타임 상태 불명확 시 사용.

1. 의심 지점에 로깅 코드 삽입 (마커 필수)
2. 재현 시도 → 로그 수집
3. 원인 파악 후 `grep -rn "임시 트래커"` 로 완전 제거

```javascript
// ── 임시 트래커 START (troubleshooting-cot) ──
console.log('[TRACKER]', { key, value, caller: new Error().stack?.split('\n')[2] });
// ── 임시 트래커 END ──
```

규칙: `START/END` 마커 필수, 커밋 전 트래커 코드를 완전히 제거한다.

### 3-4. 하드코딩 재구현

핵심 메커니즘만 추출, 의존성 없이 최소 재구현으로 검증.

### 3-5. LLM 로직 분석 (최후)

비동기 타이밍, 레이스 컨디션 등. 프롬프트: [references/GEMINI_PROMPTS.md](references/GEMINI_PROMPTS.md) 템플릿 4

---

## Phase 4: 해결 및 문서화

**수정 원칙:**
- 수정 대상: Phase 2 델타의 파일:라인만 수정한다.
- 수정 단위: 한 커밋에 한 원인만 해결한다.
- 완료 기준: 델타의 변경 전 상태로 복원되었는지 확인한다.

1. 수정 적용 + 커밋
2. **PATTERN_LIBRARY.md에 패턴 저장**

```bash
python scripts/pattern_archiver.py --good abc123 --bad def456 --category authentication
```

커밋 메시지에 Good/Bad Case 해시, 델타, 검증 결과 포함.
패턴 형식: [references/PATTERN_LIBRARY.md](references/PATTERN_LIBRARY.md)

---

## Phase 5: 악순환 탐지 + 루프 탈출

**트리거:** 같은 가설 2회 이상 반복, 같은 파일을 같은 방식으로 재시도, 추측 표현 반복 시.

### 5-1. 사후 패턴 분석

```bash
python scripts/pattern_detector.py --mode all --days 90
```

Fix→Revert 간격, 파일 Hot Spot, 개발자별 Fix 비율 분석.

### 5-2. 코드베이스 검색

```bash
grep -rn "에러키워드" --include="*.py" --include="*.js" .
rg "함수명|변수명" -t py -t js
```

증상과 관련된 함수 호출처, 설정값, 유사 패턴을 찾아 분석 범위를 확장.

### 5-3. 외부 검색 (Google via Gemini)

- 검색 쿼리: `"에러메시지" site:stackoverflow.com`, `"라이브러리명" "버전" breaking change`
- 검색 결과에서 핵심만 추출 → 새 가설 수립

### 5-4. 연계 스킬 강제 전환

```bash
python scripts/bridge.py full-scan /path/to/project --exclude .venv,node_modules
```

| 막힌 상황 | bridge 커맨드 | 기대 효과 |
|----------|--------------|----------|
| 어디서 호출되는지 모름 | `identify-modules` | 전역 import 그래프, hub 노드 |
| 의존성 순환 의심 | `check-deps` | phantom/circular 의존성 |
| 구조 문제 의심 | `classify-structure` | DAG/순환 판별 |
| 런타임 경로 불명확 | `trace-runtime` | 실제 콜그래프 |

> **원칙:** 3회 시도 후 5-2 또는 5-3의 검색 전략으로 전환한다.

---

## 연계 스킬

`bridge.py`로 다른 스킬의 스크립트를 직접 호출:

```bash
# Phase 0: 장애 관련 허브 모듈 식별
python scripts/bridge.py identify-modules /path/to/project --exclude .venv,node_modules

# Phase 0: 의존성 문제 탐지
python scripts/bridge.py check-deps /path/to/project --verify

# Phase 2: 모듈 그래프 구조 분류 (DAG/순환 판별)
python scripts/bridge.py classify-structure --project /path/to/project

# Phase 3: 런타임 함수 호출 추적
python scripts/bridge.py trace-runtime python /path/to/script.py

# 종합 스캔 (Phase 0 + 2 통합)
python scripts/bridge.py full-scan /path/to/project --exclude .venv,node_modules
```

| Phase | 커맨드 | 연계 스킬 | 용도 |
|-------|--------|----------|------|
| 0 | `identify-modules` | `codebase-architecture-mapper` | Hub 노드, import 그래프로 영향 범위 파악 |
| 0 | `check-deps` | `depsolve-analyzer` | phantom/circular 의존성 탐지 |
| 2 | `classify-structure` | mapper → `graph-structure-classifier` | DAG/순환 구조 판별 (파이프) |
| 3 | `trace-runtime` | `runtime-flow-tracer` | 실제 함수 호출 순서, 동적 call graph |

모든 커맨드에 `--json` 플래그로 LLM용 원본 JSON 출력 가능.

---

## 핵심 스크립트

> **원칙:** 스크립트는 반복적이고 실수가 잦은 검증 작업에만 쓴다. 판단과 추론은 LLM이 한다.

| 스크립트 | Phase | 용도 |
|----------|-------|------|
| `semantic_diff.py` | 2 | AST 비교로 삭제/수정/리네이밍 분류 (Python only) |
| `bisect_runner.py` | 3-1 | Git bisect 자동화 |

<details>
<summary>보조 스크립트 (필요 시에만)</summary>

| 스크립트 | Phase | 용도 |
|----------|-------|------|
| `commit_analyzer.py` | 1 | 커밋 스코어링 폴백 (LLM 없을 때) |
| `syntax_checker.py` | 3-0 | 문법 검증 폴백 (프로젝트 린터 없을 때) |
| `pattern_archiver.py` | 4 | PATTERN_LIBRARY.md에 패턴 저장 |
| `pattern_detector.py` | 5-1 | 사후 악순환 패턴 분석 |
| `bridge.py` | 5-4 | 연계 스킬 오케스트레이터 |

</details>

## 참고 문서

- [LLM 프롬프트 템플릿](references/GEMINI_PROMPTS.md) — Phase 1, 2, 5 스코어링/분석 프롬프트
- [가설 검증 방법론](references/HYPOTHESIS_GUIDE.md) — Phase 3 Mutation/하드코딩/반사실 검증
- [패턴 라이브러리](references/PATTERN_LIBRARY.md) — Good/Bad Case 아카이브
