# CSO 아키텍처 리뷰: claude-gemini-communicator (상세 근거 포함)

> 작성: Gemini (CSO Role)
> 날짜: 2026-02-17
> 분석 기반: `src/`, `config.json`, `architecture/*.md`
> 업데이트: 각 비판 항목에 코드 레벨 근거 추가

---

## 1. 의도 부합성 — [4/5]
**근거**: `architecture/001_decision_framework.md`에 명시된 "멀티 에이전트 메시지 버스 확립"이라는 핵심 의도에 매우 충실하게 구현되었습니다. `src/hooks/hook_auto_task.py`는 Claude의 파일 수정(Write/Edit) 이벤트를 받아 `src/core/gemini_service.py`를 통해 평가를 요청하고 `src/shared/feedback.py`로 결과를 기록하는, "Claude 작성 → Gemini 평가" 워크플로우를 명확히 보여줍니다. `src/core/a2a_protocol.py`의 8필드 공통 엔벨로프와 `request_id`를 이용한 E2E 추적 기능은 메시지 버스의 핵심 요구사항을 직접적으로 구현한 결과입니다.

**과설계**: `src/core/`의 `memory.py`, `router.py`, `scheduler.py`는 현재 `cli.py`의 테스트용 서브커맨드에서만 제한적으로 사용되고 있어 YAGNI 원칙 위반으로 보일 수 있습니다. 그러나 `001_decision_framework.md`에서 제시된 2단계 확장(JSONL 버스, 멀티홉 체인)과 장기 아키텍처(Agent Teams, 장기 Memory)를 고려하면, 이는 과설계라기보다는 **합리적인 선행 투자(Reasonable a priori investment)**에 가깝습니다. 특히 `router.py`는 향후 `codex` 등 다른 에이전트로의 확장을 위한 필수적인 추상화입니다.

**누락**: 현재 피드백 메커니즘은 `plans/gemini/gemini_feedback.md`에 비동기적으로 추가하는 단방향 통신입니다. Claude 에이전트가 이 피드백을 '읽고' 자신의 다음 행동에 직접 반영하는 **능동적인 순환(active feedback loop) 구조는 아직 구현되지 않았습니다.** 현재는 사용자가 `gemini_feedback.md`를 읽고 Claude에게 지시하는 수동적 순환에 의존합니다.

**개선**: `gemini_feedback.md`나 `plans/gemini/a2a_events.jsonl`에 기록된 Gemini의 평가 결과를 Claude가 다음 프롬프트 컨텍스트에 포함하도록 하는 `hook_pre_prompt` 같은 새로운 훅을 구현하여 **피드백 루프를 자동화**할 것을 제안합니다.

#### 코드 레벨 근거:
- **문제 지점**: 현재 구조는 피드백을 생성하고 저장하는 '쓰기' 경로만 존재합니다. 예를 들어 `src/hooks/hook_auto_task.py`는 `save_feedback()`을 호출하여 `gemini_feedback.md`에 결과를 기록할 뿐입니다.
- **부재하는 기능**: Claude 에이전트의 프롬프트를 구성할 때 `gemini_feedback.md` 파일의 내용을 읽어 컨텍스트에 추가하는 '읽기' 경로, 예를 들어 `hook_pre_prompt.py`와 같은 기능이 부재합니다. 이로 인해 피드백이 실제 코드/문서 개선에 자동으로 활용되지 못하고 단방향으로만 흐릅니다.

## 2. 이식성 — [2/5]
**근거**: `src/`와 `skills/`의 분리, `requirements.txt` 사용 등 이식성을 고려한 설계가 보이나, 여러 심각한 저해 요인이 존재하여 다른 환경으로의 이식이 매우 어렵습니다.

**저해 요인**:
1.  **플랫폼 의존성**: `fcntl` 모듈은 Unix 계열 OS에서만 사용 가능하여 Windows에서의 실행을 직접적으로 막습니다 (`src/shared/feedback.py`, `src/core/error_analyzer.py`).
2.  **하드코딩된 절대 경로**: 여러 파일(`cli.py`, `gemini_service.py` 등)에서 `Path(__file__).resolve()`를 사용하여 `PROJECT_ROOT`를 각자 계산합니다. 이는 파일 위치나 심볼릭 링크 환경에 따라 다른 결과를 낳아 심각한 오류를 유발할 수 있습니다.
3.  **외부 설정 의존**: `gemini_service.py`가 `~/.gemini/oauth_creds.json` 같은 사용자 홈 디렉토리의 특정 경로를 암묵적으로 의존하는 것은 이식성을 크게 저해합니다.

#### 코드 레벨 근거:
1.  **플랫폼 의존성 (`fcntl`)**:
    - **파일**: `src/shared/feedback.py` 및 `src/core/error_analyzer.py`
    - **코드**: `import fcntl` 구문과 `fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)` 같은 함수 호출이 명백한 증거입니다. 이 코드는 Windows 환경에서 `ModuleNotFoundError`를 발생시킵니다.
2.  **하드코딩된 절대 경로 (`PROJECT_ROOT`)**:
    - **파일**: `src/cli.py`, `src/core/gemini_service.py`, `src/hooks/hook_auto_task.py` 등 다수
    - **코드 패턴**: `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent` 와 같이 각 파일이 자신의 위치를 기준으로 프로젝트 루트를 추정하고 있습니다. 이는 파일 구조가 변경되거나 심볼릭 링크가 사용될 경우, 각기 다른 `PROJECT_ROOT` 값을 갖게 만들어 문제를 일으킵니다.
3.  **외부 설정 의존**:
    - **파일**: `src/core/gemini_service.py`
    - **코드**: `_call_gemini_with_oauth` 함수 내의 `creds_path = Path(sdk_config.get("oauth_creds_path", "~/.gemini/oauth_creds.json")).expanduser()` 라인은 사용자 홈 디렉토리의 특정 파일을 하드코딩된 기본값으로 사용하고 있어, 해당 파일이 없는 환경에서는 예외를 발생시킵니다.

**개선**:
1.  `fcntl` 대신 `filelock`과 같은 크로스플랫폼 라이브러리를 `requirements.txt`에 추가하여 사용해야 합니다.
2.  모든 경로는 코드에서 동적으로 계산하지 말고, 애플리케이션 진입점에서 결정되어 설정 객체를 통해 **명시적으로 주입(dependency injection)**되어야 합니다.
3.  `.claude/`나 `~/.gemini/` 같은 외부 설정 파일 경로 또한 환경변수나 설정 파일을 통해 명시적으로 지정하도록 변경해야 합니다.

## 3. 재사용성 — [3/5]
**근거**: 3-레이어 DAG로 잘 분리된 모듈 구조는 재사용을 위한 좋은 기반을 제공합니다. `a2a_protocol.py`의 메시지 엔벨로프는 범용성이 높아 다른 프로젝트에서도 충분히 재사용 가능합니다.

**YAGNI 판정**: `memory.py`, `router.py`, `scheduler.py`는 현재 시점에서는 YAGNI 위반처럼 보이지만, 프로젝트의 명시된 목표("메시지 버스 확립" 및 향후 에이전트 확장)에 비추어 볼 때, 이는 아키텍처의 확장성을 위한 합리적인 선행 투자로 판단하는 것이 타당합니다.

**개선**:
1.  **LLM 서비스 추상화**: `gemini_service.py`는 Gemini에 강하게 종속되어 있습니다. 재사용성을 높이려면 `LLMService` 같은 추상 기본 클래스를 정의하고, `GeminiService`, `ClaudeService` 등이 이를 상속받아 구현하는 **전략 패턴(Strategy Pattern)**을 도입해야 합니다. `config.json`에서 사용할 서비스를 지정하면 해당 구현체를 동적으로 로드하도록 개선할 수 있습니다.

#### 코드 레벨 근거:
- **문제 지점**: `src/core/gemini_service.py` 전체가 Gemini API에 특화되어 있습니다.
- **증거**:
    - 함수명 자체가 `_call_gemini_with_api_key`, `_call_gemini_cli` 등으로 특정 서비스(Gemini)를 명시합니다.
    - SDK `import` 문(`from google import genai`)이 모듈 내에 존재합니다.
    - 모델명 (`gemini-2.5-flash` 등)이 내부 `_get_fallback_models` 함수를 통해 하드코딩에 가깝게 관리됩니다.
    - 이 구조에서는 다른 LLM(예: Anthropic Claude API)을 호출하는 기능을 추가하려면 이 파일 자체를 대대적으로 수정하거나, 완전히 새로운 서비스 파일을 만들어야만 합니다.

## 4. 다이아몬드 의존성 — [3/5] (5=문제없음, 1=심각)
**근거**: `shared/config.py`가 in-degree 6인 핵심 허브 노드이며, 여러 모듈이 이를 참조하는 다이아몬드 패턴이 다수 존재합니다.

**위험 패턴**:
- **상태 불일치**: Python 모듈이 싱글톤으로 관리되고 `config.json`이 사실상 읽기 전용이라 설정값 자체의 상태 불일치 위험은 낮습니다.
- **`PROJECT_ROOT` 중복 선언**: `cli.py`, `gemini_service.py`, `hook_auto_task.py` 등 여러 파일에서 `PROJECT_ROOT`를 각자 독립적으로 계산하는 것이 가장 큰 문제입니다. 이는 다이아몬드 의존성의 "서로 다른 버전" 문제와 유사하며, 환경에 따라 각 모듈이 서로 다른 루트 경로를 참조하여 예측 불가능한 파일 I/O 오류를 발생시킬 수 있는 심각한 리스크입니다.

#### 코드 레벨 근거:
- **문제 지점**: `PROJECT_ROOT` 또는 그와 유사한 변수(`_PROJECT_ROOT`)가 여러 파일에서 각자의 방식으로 정의됩니다.
- **증거**:
    - `src/shared/config.py`: `PROJECT_ROOT = Path(__file__).resolve().parent.parent`
    - `src/core/gemini_service.py`: `PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent`
    - `src/hooks/hook_auto_task.py`: `_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`
    - 이처럼 계산 방식과 `parent`의 개수가 파일마다 달라, 잠재적으로 서로 다른 디렉토리를 가리킬 위험이 매우 큽니다. 이는 다이아몬드 의존성 문제의 전형적인 증상으로, 동일한 설정(루트 경로)에 대해 여러 버전이 존재하는 것과 같습니다.

**개선**: `PROJECT_ROOT`를 한 곳(예: `shared/config.py`)에서만 계산하고 다른 모듈은 이를 import하여 사용하도록 즉시 통일해야 합니다. 더 나아가, 이 값을 코드에서 계산하지 않고 **애플리케이션 진입점에서 주입**하는 방식을 채택하는 것이 가장 이상적입니다.

## 5. 순환 의존성 — [4/5] (5=완전 DAG, 1=순환 심각)
**근거**: `graph-structure-classifier` 분석 결과 `src/` 내부에는 순환 의존성이 없음이 확인되었습니다. `hooks/ → core/ → shared/` DAG 규칙은 대체로 잘 지켜지고 있습니다.

**위반 사례**:
- **지연 Import**: `core/error_analyzer.py`가 `core/gemini_service.py`를 지연 import하는 것은 순환을 회피하기 위한 기술이지만, 두 모듈 간 강한 결합이 존재함을 시사합니다.
- **역방향 의존성**: `cli.py`(상위 레이어)가 테스트 목적으로 `hooks/hook_pre_tool.py`(하위 플러그인 레이어)의 함수를 직접 import하는 것은 아키텍처 원칙의 명백한 위반입니다. 이는 계층 간의 경계를 허물고 결합도를 높입니다.

#### 코드 레벨 근거:
- **문제 지점**: 상위 애플리케이션 레이어(`src/cli.py`)가 하위 플러그인 레이어(`src/hooks/`)의 모듈을 직접 import 합니다.
- **증거**:
    - **파일**: `src/cli.py`
    - **코드**: `from src.hooks.hook_pre_tool import check_command`
    - **설명**: `hooks` 디렉토리는 `src/core`나 `src/shared`의 기능을 사용하는 플러그인 모음이어야 합니다. 하지만 이 import 구문은 그 관계를 역전시켜, `cli.py`가 `hook_pre_tool.py`의 존재와 그 안의 `check_command` 함수를 알아야만 동작하게 만듭니다. 이는 `hooks`의 독립성을 훼손하고 시스템 전체의 결합도를 높입니다.

**개선**: `cli.py`가 사용하는 `check_command`와 같은 공통 유틸리티 함수는 `hooks`가 아닌 `shared` 또는 별도의 `utils` 모듈로 옮겨, `cli.py`와 `hook_pre_tool.py` 양쪽에서 안전하게 import하도록 구조를 즉시 변경해야 합니다.

---

## 종합 평가
**총점**: 16/25

**가장 시급한 개선 1가지**:
**`PROJECT_ROOT`의 중구난방 선언을 단일 출처로 통일하는 것**입니다. 이 문제는 이식성(2)과 다이아몬드 의존성(4) 축에서 모두 심각한 위험으로 지적되었으며, 예기치 않은 파일 시스템 오류를 유발할 가능성이 가장 큰 시한폭탄과 같습니다.

**이 아키텍처의 강점**:
- **명확한 목표**: "메시지 버스"라는 명확한 목표 아래 모든 설계 결정이 이루어져 있습니다.
- **견고한 구현**: Gemini API 호출 시 SDK, OAuth, CLI로 이어지는 다중 폴백(fallback) 전략은 매우 인상적이며 시스템의 안정성을 크게 높입니다.
- **확장 가능한 구조**: 3-레이어 DAG와 A2A 프로토콜은 향후 다른 에이전트나 기능을 추가하기에 용이한 구조입니다.

**이 아키텍처의 약점**:
- **심각한 이식성 부족**: 플랫폼 종속적인 코드(`fcntl`)와 하드코딩된 절대 경로 패턴으로 인해 다른 환경에서 이 시스템을 구동하는 것이 거의 불가능합니다.
- **암묵적 의존성**: 코드베이스 외부의 파일(`~/.gemini/`)이나 환경에 대한 암묵적인 가정들이 많아 시스템의 행동을 예측하고 디버깅하기 어렵게 만듭니다.
- **느슨한 계층 경계**: `cli.py`가 `hooks`의 내부 구현을 직접 참조하는 등, 아키텍처 원칙이 일부 영역에서 지켜지지 않아 장기적으로 유지보수 비용을 증가시킬 수 있습니다.
