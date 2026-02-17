# Gemini CSO 아키텍처 심층 리뷰 요청

> 이 프롬프트를 Gemini CLI에서 직접 실행하세요.
> `gemini` 실행 후 아래 내용을 붙여넣기하면 됩니다.

---

## 프롬프트

너는 이 프로젝트의 CSO(Chief Strategy Officer)이자 소프트웨어 아키텍트다.
아래 5가지 관점에서 현재 코드베이스를 심층 분석하고, 각 항목별로 , **근거**, **개선 제안**을 한국어로 작성하라.

### 분석 대상
- `src/` 디렉토리 전체 (3-레이어 DAG: hooks/ → core/ → shared/)
- `config.json` (설정 구조)
- `plans/codex/codebase_analysis.md` (Codex가 작성한 기존 분석 — 참조용)

### 평가 축 5가지

#### 1. 의도 부합성 (Effectiveness)
- 이 시스템의 **본래 의도**: "Claude가 코드/문서를 작성하면 Gemini가 자동으로 평가하는 크로스-에이전트 협업"
- 현재 구현이 이 의도를 얼마나 충실히 달성하고 있는가?
- 과설계(Over-engineering)된 부분은 없는가? 의도에 비해 불필요하게 복잡한 레이어가 있는가?
- 반대로, 의도 달성에 필요하지만 아직 빠진 것은 무엇인가?
- [decision_framework.md](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/architecture/001_decision_framework.md)
- 기존 아키텍처와 어떠한 차이가 발생했는가? 
- (/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/architecture/04_new_architecture_analysis.md)


#### 2. 이식성 (Portability)
- 이 시스템을 다른 프로젝트에 가져다 쓸 수 있는가?
- `python3.13` 하드코딩, `fcntl` (Unix-only), 절대경로 `PROJECT_ROOT` 패턴 등이 이식성을 저해하는가?
- skills/ 디렉토리의 자립성(cp -r 설치)은 실제로 작동하는가?
- `.claude/settings.local.json`에 대한 의존이 타 플랫폼 이식을 막는가?

#### 3. 재사용성 (Reusability)
- 각 모듈이 독립적으로 재사용 가능한가?
- `memory.py`, `router.py`, `scheduler.py`가 현재 테스트 전용인데, 이것이 YAGNI 위반인가 아니면 합리적 선투자인가?
- `gemini_service.py`를 Gemini 외 다른 LLM 호출에 재사용할 수 있는 구조인가?
- `a2a_protocol.py`의 엔벨로프 구조가 범용적인가, 아니면 이 프로젝트에만 특화된 스키마인가?

#### 4. 다이아몬드 의존성 (Diamond Dependency)
- `shared/config.py`가 in-degree 6인 허브 노드다. 이것이 다이아몬드 의존성 문제를 만드는가?
- `hooks/hook_auto_task.py`가 `core/gemini_service.py`와 `core/a2a_protocol.py`를 동시에 import하고, 둘 다 `shared/config.py`를 import한다. 이 다이아몬드 패턴에서 상태 불일치 위험이 있는가?
- `PROJECT_ROOT`가 `config.py`, `feedback.py`, `error_analyzer.py`, `cooldown.py`에 각각 독립 선언되어 있다. 이것이 다이아몬드의 "서로 다른 버전" 문제와 유사한 리스크를 만드는가?

#### 5. 순환 의존성 (Cyclic Dependency)
- 현재 DAG 규칙(hooks/ → core/ → shared/, 역방향 금지)이 코드에서 실제로 지켜지고 있는가?
- `error_analyzer.py`가 지연 import로 `gemini_service.py`를 호출한다. 이것이 사실상 `core/ → core/` 순환인가?
- `error_analyzer.py`가 지연 import로 `shared/feedback.py`도 호출한다. 이것이 레이어 규칙 위반인가?
- `cli.py`가 `hooks/hook_pre_tool.py`를 테스트용으로 import한다. 이것이 역방향 의존인가?

### 출력 형식

```
## 1. 의도 부합성 — [점수/5]
**근거**: ...
**과설계**: ...
**누락**: ...
**개선**: ...

## 2. 이식성 — [점수/5]
**근거**: ...
**저해 요인**: ...
**개선**: ...

## 3. 재사용성 — [점수/5]
**근거**: ...
**YAGNI 판정**: ...
**개선**: ...

## 4. 다이아몬드 의존성 — [점수/5] (5=문제없음, 1=심각)
**근거**: ...
**위험 패턴**: ...
**개선**: ...

## 5. 순환 의존성 — [점수/5] (5=완전 DAG, 1=순환 심각)
**근거**: ...
**위반 사례**: ...
**개선**: ...

## 종합 평가
**총점**: /25
**가장 시급한 개선 1가지**: ...
**이 아키텍처의 강점**: ...
**이 아키텍처의 약점**: ...
```
