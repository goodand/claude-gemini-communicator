# Git Worktree 기반 Main Coder / Sub Coder 병렬 에이전트 시스템 구현 체크리스트

## 문서 목적

이 문서는 다음 구조를 실제로 구현하기 위한 매우 상세한 체크리스트다.

- `git worktree`를 활용한 병렬 작업 공간 분리
- Main Coder / Sub Coder 역할 분리
- 역할별 Skill 분리
- Skill ↔ Agent 브리지 설계
- 오케스트레이터 기반 라우팅
- 실행 / 검증 / 재시도 루프
- merge 전 검증 및 문서화 체계

---

# 0. 최종 목표 정의

## 0.1 구현 목표

구현 목표는 다음과 같다.

1. 메인 브랜치를 직접 오염시키지 않는다.
2. 작업마다 독립 worktree를 만든다.
3. Main Coder는 설계, 분해, 라우팅, 통합, 검증 기준 수립을 담당한다.
4. Sub Coder는 각 worktree에서 구현, 테스트, 리팩터링을 담당한다.
5. Skill은 역할별로 분리한다.
6. Agent 간 handoff는 브리지 규약으로 표준화한다.
7. 실패 시 같은 repo / 같은 module 내 fallback 순서를 먼저 탄다.
8. 최종적으로는 main에 merge 가능한 산출물만 통과시킨다.

## 0.2 성공 조건

아래 조건이 충족되어야 구현 성공으로 본다.

- Main Coder와 Sub Coder의 책임 경계가 문서로 명시되어 있음
- worktree 생성 규칙이 자동화되어 있음
- 각 에이전트가 어떤 Skill을 언제 호출할지 명확함
- handoff payload 형식이 정해져 있음
- 테스트 실패 시 retry 루프가 정의되어 있음
- merge 전 검증 항목이 체크리스트화되어 있음
- 메인 브랜치와 서브 브랜치 간 상호작용 규칙이 존재함

---

# 1. 요구사항 정리 단계

## 1.1 기능 요구사항 체크

- [ ] worktree를 자동 생성할 수 있어야 한다
- [ ] 작업별 branch naming 규칙이 있어야 한다
- [ ] Main Coder가 task decomposition을 수행해야 한다
- [ ] Sub Coder가 독립 작업을 수행해야 한다
- [ ] 역할별 Skill이 분리되어 있어야 한다
- [ ] 브리지 Skill 또는 handoff schema가 있어야 한다
- [ ] 결과 통합 담당 주체가 명확해야 한다
- [ ] 실패 시 fallback 대상이 정의되어 있어야 한다
- [ ] 테스트 기준이 main과 sub에 대해 분리되어 있어야 한다

## 1.2 비기능 요구사항 체크

- [ ] worktree 디렉터리 오염 방지
- [ ] `.gitignore` 안전성 보장
- [ ] context leakage 최소화
- [ ] merge conflict 최소화
- [ ] 작업 로그 추적 가능
- [ ] 에이전트 간 상태 공유 가능
- [ ] handoff payload 재현 가능
- [ ] role drift 방지 가능
- [ ] 실패 원인 추적 가능

## 1.3 제외 조건 정의

- [ ] worktree 없이 단일 디렉터리에서 병렬 개발하는 방식 제외
- [ ] 역할 구분 없이 모든 에이전트가 동일 권한으로 일하는 구조 제외
- [ ] 문서 없는 ad-hoc handoff 제외
- [ ] 테스트 없는 merge 허용 제외
- [ ] main에서 직접 구현하는 방식 제외
- [ ] branch naming 규칙 없는 방식 제외
- [ ] 실패 시 무조건 새 repo로 넘어가는 탐색 방식 제외

---

# 2. 역할 모델 설계

## 2.1 Main Coder 역할 정의

Main Coder는 아래만 담당한다.

- [ ] 사용자 요구사항 분석
- [ ] 작업 분해
- [ ] 우선순위 결정
- [ ] worktree 생성 지시
- [ ] Sub Coder에게 task 할당
- [ ] 공통 인터페이스 / API 계약 작성
- [ ] merge 기준 정의
- [ ] 최종 통합
- [ ] 최종 승인 / reject 결정

### Main Coder 금지 사항

- [ ] 대규모 구현 직접 수행 금지
- [ ] 여러 feature를 main 작업공간에서 직접 수정 금지
- [ ] validation 없는 merge 금지
- [ ] undocumented handoff 금지

## 2.2 Sub Coder 역할 정의

Sub Coder는 아래만 담당한다.

- [ ] 개별 기능 구현
- [ ] 테스트 작성
- [ ] 로컬 리팩터링
- [ ] 작업 결과 보고
- [ ] handoff payload 작성
- [ ] 문제 발생 시 escalation

### Sub Coder 금지 사항

- [ ] 전체 아키텍처 변경 독단 수행 금지
- [ ] 공용 인터페이스 임의 변경 금지
- [ ] main branch 직접 수정 금지
- [ ] 다른 worktree 결과를 임의 merge 금지

## 2.3 Validator 역할 정의

- [ ] 요구사항 대비 구현 정합성 점검
- [ ] 테스트 결과 검토
- [ ] 보안 / 성능 / 회귀 위험 검토
- [ ] merge 허용 여부 판정

## 2.4 Bridge / Orchestrator 역할 정의

- [ ] 어떤 Skill을 누구에게 연결할지 결정
- [ ] handoff schema 검증
- [ ] 메시지 흐름 유지
- [ ] retry / fallback 실행
- [ ] 상태 추적

---

# 3. Skill 구조 설계

## 3.1 Skill 분류

아래처럼 최소 5종으로 분리한다.

- [ ] `using-git-worktrees`
- [ ] `architect-role-skill`
- [ ] `builder-role-skill`
- [ ] `agent-skill-bridge`
- [ ] `skill-orchestrator`

선택적으로 추가한다.

- [ ] `validator-role-skill`
- [ ] `scribe-role-skill`
- [ ] `subagent-driven-development`
- [ ] `workflow-orchestrator`
- [ ] `agent-capability-matrix`

## 3.2 Skill 디렉터리 규칙

- [ ] 각 Skill마다 별도 폴더 사용
- [ ] 각 Skill마다 `SKILL.md` 존재
- [ ] 목적, 입력, 출력, 호출 조건, 금지 조건 명시
- [ ] 관련 예시 포함
- [ ] 실패 처리 방식 포함
- [ ] dependent skill 명시

예시 구조:

```text
skills/
  using-git-worktrees/
    SKILL.md
  architect-role-skill/
    SKILL.md
  builder-role-skill/
    SKILL.md
  agent-skill-bridge/
    SKILL.md
  skill-orchestrator/
    SKILL.md
  validator-role-skill/
    SKILL.md
```

---

# 누락 범위 감사 + Remote Baseline 체크리스트

(참조: `references/subagent-audit-and-remote-baseline-at2026-06-15-20-22.md`)

## Fan-out Audit 준비

- [ ] 감사할 concern/gate 목록을 작성했다 (각 행 = 하나의 concern)
- [ ] concern 하나당 subagent 하나를 배정했다 (하나의 subagent가 여러 concern을 담당하지 않음)
- [ ] 각 subagent 패킷에 "PASS/FAIL/PASS_WITH_RISK 중 하나로 판정, evidence path 필수" 조건을 명시했다
- [ ] coverage matrix (concern | validator coverage | test coverage | audit status)를 준비했다

## FAIL 판정 처리

- [ ] 모든 FAIL 판정에 remediation owner가 지정되어 있다 (역할명 또는 파일 경로)
- [ ] 모든 FAIL 판정에 evidence path가 있다 (파일:줄번호, 실행 명령, 또는 diff 출력 중 하나)
- [ ] evidence path 없이 FAIL이 보고된 경우 미검증(unverified)으로 표기하고 수락하지 않았다

## 파괴적 작업 전 Plan-Only Audit

- [ ] git worktree remove --force, 광범위 staging, 브랜치 일괄 삭제 등 파괴적 작업 전 plan-only audit을 실행했다
- [ ] plan-only 출력을 검토한 뒤 실제 명령을 실행했다

## Branch/PR Sequencing

- [ ] 현재 PR을 세 종류 중 하나로 분류했다: product code / docs-artifact / release-gate
- [ ] 의존성이 있는 경우 product code → docs-artifact → release-gate 순서로 merge한다
- [ ] 세 종류가 하나의 PR에 혼합되어 있지 않다

## Remote Baseline Loop

- [ ] clean audit worktree를 origin/main 기준으로 생성했다 (`git worktree add /tmp/<repo>-origin-main-audit origin/main`)
- [ ] audit worktree에서 validator와 테스트를 실행하고 결과를 기록했다
- [ ] PR merge 후 `git fetch origin`을 실행했다
- [ ] audit worktree를 재생성 또는 갱신하고 validator + 테스트를 재실행했다
- [ ] merge 전후 결과를 비교했다
- [ ] dirty main이 아닌 clean audit worktree를 truth source로 사용했다

## Subagent Self-Report 검증

- [ ] PASS 판정을 수락하기 전 evidence path (파일:줄번호, 명령, diff 출력 중 하나)를 확인했다
- [ ] "완료했습니다", "PASS 확인" 등 evidence 없는 자가 보고를 그대로 수락하지 않았다
- [ ] evidence가 없는 경우 미검증으로 표기하고 evidence를 요청했다