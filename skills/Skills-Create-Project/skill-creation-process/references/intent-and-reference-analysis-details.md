# Intent And Reference Analysis Details

`phase-guide.md`의 상위 절차에서 생략된 세부 기준을 보존하는 문서.

## 동기 정의 세부 기준

- **반복 패턴 식별** — Agent/Codex가 반복적으로 실수하거나 비효율이 발생하는 지점
- **목표 설정** — 이 스킬이 해결할 구체적 문제 1문장
- **우선순위 분석** — 다른 스킬 대비 긴급도·영향도 판단
- **의존성 분석** — 선행 스킬이 필요한지, 기존 스킬과 책임 겹침이 있는지
- **기능 범위 경계 (비목표)** — 이 스킬이 **하지 않을 것**을 명시. agent-task-packet의 non_goals 개념과 동일:
  - `Case: State` — 보장하지 않는 상태
  - `Case: Type` — 제외할 에러/예외
  - `Case: Performance` — null/over/under

## Reference 분석 세부 기준

- 먼저 reference acquisition mode를 고정한다
  - 기본: `external_research`
  - 사용자 명시 요청 시: `internal_codebase_only`
- `internal_codebase_only`에서는 현재 workspace 밖의 신규 reference를 들여오지 않는다
- `knowledge_bases/`를 읽고 **워크플로우 단계** 추출
- `knowledge_bases/`를 읽고 **도구/명령어 목록** 추출
- `knowledge_bases/`를 읽고 **주의사항/함정** 추출
- `knowledge_bases/`를 읽고 **사례/패턴** 추출
- 패턴 간 **교차 검증** — 여러 reference에서 공통으로 나오는 패턴 식별

## Reference 기반 Checklist 생성 세부 기준

- reference에서 발견한 핵심 패턴을 체크리스트로 정리
- 먼저 **정합성 평가용 checklist**를 만들고
- 그 결과를 바탕으로 **구현용 checklist**를 만든다

## `references/` / `knowledge_bases/` / SKILL.md 분리 기준

- `references/`
  - 조사 원자료
  - task 수행용 상세 커맨드
  - 필드 정의서, 예시 모음, 운영 규칙
  - 실험 후 추가된 troubleshooting / 운영 규칙
- `knowledge_bases/`
  - `references/`를 구조화·정리한 중간 지식층
  - URL KB, 설계 근거, canonical design takeaways
- `SKILL.md`
  - 워크플로우 골격
  - 언제 쓸지
  - 핵심 주의사항
