---

# 🚀 AI 오케스트레이션 개발 프로세스 가이드 

## 💡 개발 원칙

> **실행 및 검증 우선순위:**
> 1. **의존성 분석** (선행)
> 2. **테스트하기 쉬운 것** 우선
> 3. **테스트 시 영향이 적은 것** 우선 (코드 영향 시 `git worktree` 활용)
> 4. **분류하기 쉬운 것** 우선
> 5. **구현하기 쉬운 것** 순으로 진행
> 
> 

---

## 👥 조직 구성 및 RnR (Roles and Responsibilities)

₩₩₩

| 역할 | 담당 AI | 주요 책임 및 핵심 참조 경로 |
| --- | --- | --- |
| **👑 CEO** | **사용자 (나)** | 최종 의사결정 및 승인 |
| **👨‍💻 CTO** | **Claude** | **역할:** 의존성 분석, 실행 계획 수립, 코드 리뷰, `git push`<br>

<br>**경로:** `plans/claude/`, `plans/project_handoff.md`, `architecture/` |
| **🏛️ CSO** | **Gemini** | **역할:** 거시적 아키텍처 비판, `codebase_investigator agent` 활용 코드베이스 거시 분석<br>

<br>**경로:** 프로젝트 `skills` 활용 중심 |
| **👷 Dev** | **Codex** | **역할:** TDD 기반 코딩 (테스트 및 메인 코드 병렬 구현), `git commit` 수행<br>

<br>**경로:** `plans/codex/` |

---
₩₩₩

## 🛠️ 기획 및 설계 4단계 (Planning Phase)
1. 상위 기획 (High-level Design)

대상: 신규 프로젝트이거나 decision_framework.md가 없는 경우 진행.
도구: template/decision_framework.md 템플릿 사용.
목적: 프로젝트의 의도 파악, 핵심 허브 및 의존성 정의.

2. 현황 파악 및 심층 분석 (Gemini 중심)
대상: 기존 프로젝트 수정/확장 시 진행 (신규 프로젝트는 생략).
도구: codebase_investigator 에이전트.
목적: 기존 로직 존재 여부 확인 및 거시적 방향 제시.

3. 아키텍처 검증 및 표현 (Claude 중심)
활동: Mermaid.js를 사용하여 아키텍처 시각화.
목적: 모듈 간 의존성과 허브를 예측하고 구조적 타당성 검토.
비판: Gemini가 Claude의 아키텍처 설계를 검토하고 세부 사항 누락을 비판.

4. 실행 계획 수립 (Action Items) (Claude 중심)
활동: 체크박스(- [ ]) 형태의 Action Item 레벨로 작성.
비판: Gemini가 실행 계획의 현실성과 누락된 의존성을 최종 비판 및 수정 제안.

## 🛠️ 구현 및 검증 단계 워크플로우 (Execution Phase)
5. 5단계: 구현 및 단위 테스트 (Codex 중심)
대상: plans/codex/에 정의된 단위 기능
도구: Codex CLI, TDD 환경
목적: 테스트 코드와 메인 코드를 병렬 구현하고, .gitmessage 템플릿에 맞춰 로컬 커밋(commit)만 수행 (Push는 claude가)

6. 6단계: 코드 검증 및 직접 수정 (Claude 중심)
대상: Codex가 작성한 최신 커밋 및 소스 코드
도구: git status, git commit, git push, 프로젝트 스킬
목적: - Codex가 작성한 코드의 완성도 및 로직 오류 확인
통과 시: git push를 수행하여 해당 작업 완료 처리
결함 발견 시: Claude가 직접 코드를 수정하여 문제를 해결하고, 수정 사항을 사용자(CEO)에게 보고

7. 7단계: 최종 아키텍처 비판 및 정합성 검토 (Gemini 중심)
대상: Claude가 수정한 최종 코드 및 결과물
도구: codebase_investigator, CSO 비판(Criticism), gemini-reviewer (평가 도구)
목적: 최종 구현물이 기획 단계에서 수립한 decision_framework.md 및 아키텍처 허브 구조와 일치하는지 이식성이나 코드의 유지보수 등 최종 확인

8. 8단계: 세션 종료 및 기록
대상: 작업 완료된 전체 소스, plans/claude 폴더에 phase 번호를 추가한 파일명으로 작성, 다음 Action Item 업데이트 
도구: Git (Push 완료 상태)
시기 : 사용자 요청시
목적: 수정 사항 요약 보고 및 새로운 세션이나 다른 에이전트, 다른 LLM이 문서를 보고 프로젝트를 이어서 할 수 있도록 작성


## 🛠️ AI 전용 도구 (Skills) 현황

### 🌍 범용 스킬 (Common Skills)

* **경로:** `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/narrative-ai/.claude/skills`
* **주요 도구:**
* `class-hierarchy-classifier`: 클래스 상속 및 구조 분석 (Tree/DAG)
* `codebase-architecture-mapper`: 소스 전체 스캔 및 아키텍처 청사진 생성
* `depsolve-analyzer`: 패키지 의존성 해결 (package.json 등)
* `graph-structure-classifier`: 의존성 그래프의 순환 참조/레이어 패턴 식별
* `runtime-flow-tracer-web-preview`: 실행 흐름 시각화 다이어그램 생성
* `skill-path-resolver`: 등록된 스킬들의 정확한 경로 관리 (Meta Skill)
* `troubleshooting-cot-2`: 단계별 추론(CoT)을 통한 체계적 문제 진단



### 🏗️ 프로젝트 전용 스킬 (Internal Skills)

* **경로:** `/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills`
* **주요 도구:**
* `agent-parser`: 각 모델(Codex/Gemini/Claude)의 출력을 구조화하여 파싱
* `codex-user-context`: Codex CLI 실행 안정화 및 폴백 처리
* `cross-agent-bridge`: 통합 오케스트레이션 CLI (리뷰/파싱/진단 통합)
* `gemini-reviewer`: Gemini SDK 기반 코드/문서 평가 및 결과 저장



---

## 📂 주요 Plan 및 Architecture 경로

| 모델 | 참조 경로 |
| --- | --- |
| **Common** | `.../claude-gemini-communicator/plans/` |
| **Claude** | `.../plans/claude/` <br>

<br> `.../plans/project_handoff.md` <br>

<br> `.../architecture/` |
| **Codex** | `.../plans/codex/` |

---

## 📄 Git Commit 설정

* **템플릿 경로:** `template/.gitmessage`
* **로컬 파일 링크:** [.gitmessage 열기](https://www.google.com/search?q=file:///Users/jaehyuntak/Desktop/Project_____%ED%98%84%EC%9E%AC_%EC%A7%84%ED%96%89%EC%A4%91%EC%9D%B8/claude-gemini-communicator/template/.gitmessage)
* **규칙:** 이슈/문제 정의 위주로 **Multi-line**으로 매우 구체적으로 작성.

---

## 📜 System Prompt 핵심 요약

1. **기존 로직 확인 필수:** 수정 전 "기존에 만들어둔 로직" 확인 필수.
2. **오류 우선순위:** 실행 및 문법 오류 최우선 해결.
3. **언어:** 모든 분석과 설명은 **한국어**로 수행.
4. **Skills 활용:** 문제 해결 시 상황에 맞는 범용/프로젝트 스킬을 적극 호출.

---
