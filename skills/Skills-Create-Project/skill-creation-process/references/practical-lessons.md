# Practical Lessons — 실전에서 배운 스킬 제작 노하우

> 11개 스킬 구현 과정에서 반복적으로 발견된 패턴. anti-patterns.md가 "하지 말 것"이라면 이 문서는 "이렇게 하면 좋다 + 왜 그런지 실제 사례".

---

## 1. 헬퍼 함수의 반환 타입을 일관되게

**사례**: `workflow_bridge.py`의 `_load()`가 `.json`이면 dict, 아니면 string 반환. `classify_output()`이 dict에 `.strip()` 호출하여 AttributeError.

**교훈**: 하나의 함수가 여러 타입을 반환하면 **모든 호출부가 분기 비용을 지불**한다.
- 방법 A: `_load()`를 항상 string 반환으로 통일, JSON 파싱은 호출부에서
- 방법 B: `_load_text()` / `_load_json()` 분리
- 방법 C: 함수 상단에 `isinstance` guard 추가 (최소 수정)

**적용한 해결**: 방법 C (classify_output 상단에 isinstance 체크). 신규 스크립트에서는 방법 B 권장.

---

## 2. 래퍼 함수의 check=False 반환값 의미를 정확히

**사례**: `orchestrator.py`의 `_tmux(check=False)`가 returncode≠0일 때도 `(stdout, None)` 반환. `_session_exists`가 `err is None`으로 판정하여 서버 없을 때도 True.

**교훈**: 범용 래퍼에 `check=False`를 넣으면 "에러를 무시"와 "에러가 없다"의 구분이 사라진다.
- **존재 확인 함수는 래퍼를 쓰지 말고 returncode를 직접 검사**
- 래퍼의 반환 시맨틱: `(data, None)` = 성공, `(None, err)` = 실패 — 이 계약을 check 옵션이 깨뜨리지 않게 설계

---

## 3. 문서에 쓴 규칙은 반드시 validate에 구현

**사례 1**: `dispatch-fields.md`에 "symlink 방지"라고 적었지만 `validate_dispatch()`에서 symlink 검사 없음.
**사례 2**: `dispatch-fields.md`에 "queued→blocked 전이"가 전이 테이블에서 누락. 코드는 허용했지만 문서와 불일치.

**교훈**: 문서와 코드의 정합성은 **어느 한쪽이 진실**이어야 한다.
- **코드가 canonical source** — 문서는 코드의 반영이어야 한다
- 규칙을 문서에 쓸 때 동시에 validate 함수에도 구현할 것
- Consistency Checklist(정합성 체크리스트)로 교차 검증하면 이런 gap을 사전에 잡을 수 있다

---

## 4. 검증은 변경 전에 (validate-before-mutate)

**사례**: `dispatch_manager.py`의 `_do_transition()`에서 retry_count 검사보다 status/history 변경이 먼저 실행. ValueError 발생 시 객체가 이미 오염.

**교훈**:
```
Bad:  status = new_status → retry 검사 → ValueError → 객체 오염
Good: retry 검사 → ValueError → 객체 무변경 → 안전
```
- 모든 변이(mutation) 함수는 **guard clause → validation → mutation** 순서
- 이 원칙은 상태 머신, DB 트랜잭션, 파일 쓰기 모두에 적용

---

## 5. Preflight은 1급 기능

**사례**: `orchestrator.py`의 12항목 preflight가 branch 불일치, 중복 runtime, session 충돌을 launch 전에 모두 차단.

**교훈**:
- Preflight를 "있으면 좋은 것"이 아니라 **launch의 필수 전제**로 설계
- 각 항목이 실패하면 **명확한 에러 메시지** + **해결 지침** 출력
- preflight 통과 없이 다음 단계로 넘어가는 경로를 코드에서 차단

---

## 6. 실제 실행 테스트가 설계 결함을 노출한다

**사례**: codex-worktree-dispatch를 Codex로 실전 테스트했을 때 path traversal과 retry 오염 버그 2건 발견. 정적 검증(--help, validate)으로는 발견 불가.

**교훈**:
- Phase 5-1(정적)만으로 "완료"하지 않는다
- Phase 5-2(실전)에서 **edge case 입력**(빈 값, `..`, symlink, 한국어 경로)을 의도적으로 넣어야 함
- 파일시스템 의존 검증은 문자열 placeholder만 넣지 말고 **실제 fixture**(symlink, 존재 파일, repo-root 상대경로)를 준비해야 함
- 발견된 버그는 즉시 troubleshooting.md에 기록 → SKILL.md Notes에 1줄 규칙

---

## 7. 스킬 간 책임 경계를 명확히

**사례**: codex-tmux-orchestrator가 worktree를 직접 생성하면 codex-worktree-dispatch와 소유권 충돌. "이미 정해진 worktree를 소비만 한다"로 해결.

**교훈**:
- 각 스킬은 **소유/읽기전용/금지** 필드를 명시
- 상위 스킬의 출력을 하위 스킬이 읽기전용으로 소비하는 **단방향 의존**
- "이 스킬이 아닌 것" 목록을 reference에 명시하면 scope creep 방지

| 계층 | 소유 | 읽기전용 |
|------|------|----------|
| task-packet | goal, done_definition | - |
| dispatch | status, locked_paths | goal, done_definition |
| orchestrator | session, heartbeat | status, locked_paths, goal |

---

## 8. 위임 메시지는 구조화하라

**사례**: codex-delegation-protocol에서 5-section 구조(Mission/Scope/Context/Constraints/Done Definition)를 정형화.

**교훈**:
- 자유 형식 프롬프트보다 **고정 섹션**이 누락 방지 + 검증 가능
- **코드/파일 내용을 프롬프트에 직접 붙이지 않는다** — 경로만 전달, Agent가 직접 읽음
- done_definition은 **기계 검증 가능**해야 한다: "잘 작성" ✗, "pytest 통과" ✓

---

## 9. 상태 머신 다이어그램과 전이 테이블은 둘 다 필요

**사례**: dispatch-fields.md의 ASCII 다이어그램에는 queued→blocked 화살표가 있었지만, 전이 테이블에는 빠져있었다. 외부 평가에서 "런타임 버그"로 오인.

**교훈**:
- 다이어그램은 **직관적 이해**, 테이블은 **정밀한 구현 근거**
- 둘을 동기화하지 않으면 혼란 유발
- **머신-리더블 레지스트리가 존재하는 경우(예: `dispatch_contract_v0_1.json`)**, 레지스트리가 canonical source이다 — 코드의 `VALID_TRANSITIONS`와 문서는 모두 레지스트리를 반영하는 컨슈머(projection)이며, `_shared/scripts/audit_contract_sync.py`가 동기화 여부를 감사한다.
- **레지스트리가 없는 경우(코드 vs 산문 문서 불일치 상황)에만** 코드의 `VALID_TRANSITIONS`를 canonical source로 간주한다. 두 규칙은 상호 배타적이다.

---

## 10. Consistency Checklist는 구현 전에 작성

**사례**: skill-workflow-bridge-eval에서 109항목 정합성 체크리스트를 reference 분석 직후(구현 전)에 작성. 5개 문서 간 모순 15건을 사전 발견.

**교훈**:
- reference가 3개 이상이면 **구현 전 교차 검증** 필수
- 체크리스트 항목 구조: `[섹션] 검증 대상 — 기대 상태 — 근거 문서`
- 구현 후에도 체크리스트로 최종 점검 가능

---

## 11. troubleshooting.md는 진화하는 문서

**사례**: 모든 스킬에 troubleshooting.md 템플릿을 먼저 만들고, Codex 실전 테스트/외부 평가 후 케이스 추가.

**교훈**:
- 빈 템플릿이라도 먼저 만들어야 기록 습관이 생긴다
- 케이스 형식 통일: `CASE-XXX: 제목` → 증상 → 원인 → 해결 → 교훈
- SKILL.md Notes에 규칙 1줄 + `(→ troubleshooting.md CASE-XXX)` 포인터
- **같은 패턴이 반복되면 validate 함수에 추가** — 문서 규칙에서 코드 검증으로 승격

---

## 스크립트 작성 시 실전 패턴 요약

```python
# 1. 존재 확인은 returncode 직접 검사 (래퍼 X)
def _exists(name):
    r = subprocess.run([...], capture_output=True)
    return r.returncode == 0

# 2. validate-before-mutate
def transition(data, new_status):
    # ① validation (side-effect 없음)
    if new_status not in VALID_TRANSITIONS[data["status"]]:
        raise ValueError(...)
    if data["retry_count"] > data["max_retries"]:
        raise ValueError(...)
    # ② mutation (validation 통과 후에만)
    data["status"] = new_status
    data["history"].append(...)

# 3. _load 타입 분리
def _load_text(path):
    with open(path) as f: return f.read()

def _load_json(path):
    with open(path) as f: return json.load(f)

# 4. symlink 포함 경로 정규화 3종 세트
def _validate_path(p):
    if ".." in p: error("path traversal")
    if p.startswith("/"): error("절대경로")
    if os.path.exists(p) and os.path.islink(p): error("symlink")
```
