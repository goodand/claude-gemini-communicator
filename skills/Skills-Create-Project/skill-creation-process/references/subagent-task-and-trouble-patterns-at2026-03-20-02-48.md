# Subagent Task And Trouble Patterns

- generated_at: `2026-03-20-02-48`
- scope: `bounded subagent delegation / preservation-first handoff / main-agent verification`

## Purpose

최근 실제 subagent 운영에서 반복된 task 패턴과 trouble 패턴을 따로 정리한다.  
공용 skill 제작 패턴과 달리, 이 문서는 `무엇을 subagent에 넘기면 잘 닫히고`, `무엇 때문에 자주 틀어지는지`에 집중한다.

## Repeated Subagent Task Patterns

### SUBTASK-01. Bounded extension implementation

- 작은 기능 조각 1개를 명확한 write scope와 함께 넘긴다
- 예: metadata join, register 추가, narrow validator 추가
- 잘 맞는 skill:
  - `dependency-slice-planner`
  - `slice-experiment-lab`

### SUBTASK-02. SKILL.md split + reference link 정리

- line-count warning이나 entrypoint 과밀을 split point 기준으로 정리한다
- `SKILL.md`는 짧게 유지하고 상세는 별도 page로 분리한다
- 잘 맞는 skill:
  - `agent-task-packet`
  - `dependency-slice-planner`

### SUBTASK-03. Preservation-first rewrite

- overwrite, cleanup, rename 가능성이 있으면 먼저 backup을 만든 뒤 수정한다
- done-definition에 exact backup path 보고를 넣는다
- 잘 맞는 skill:
  - `agent-task-packet`
  - `artifact-lifecycle-manager`

### SUBTASK-04. Contract-first vertical slice 구현

- 전체 기능이 아니라 `emit/validate/build` 중 작은 조각 1개만 맡긴다
- triad artifact, TDD, quick_validate까지 완료 조건을 고정한다
- 잘 맞는 skill:
  - `dependency-slice-planner`
  - `slice-experiment-lab`

### SUBTASK-05. Bounded doc/code alignment

- script 변경과 같은 write set의 checklist/reference만 같이 수정하게 한다
- script, test, vertical-slice note, implementation checklist 정도로 범위를 고정한다
- 잘 맞는 skill:
  - `dependency-slice-planner`
  - `skill-creation-process`

### SUBTASK-06. Main-agent recheck handoff

- subagent는 구현과 1차 검증까지 맡고
- 메인은 `py_compile`, `quick_validate`, test rerun, stale-link grep를 다시 돈다
- 이 패턴은 거의 항상 붙는다

## Repeated Subagent Trouble Patterns

### SUBISSUE-01. Preservation rule이 packet에 약하게 들어감

- `allowed_paths`만 있고 backup 의무가 빠지면 destructive edit 위험이 남는다
- 해결:
  - `legacy-safe handoff clause`
  - `subagent preservation rule`

### SUBISSUE-02. Legacy rule을 알고만 있고 기계적 계약으로 못 박지 않음

- `legacy 건드리지 말 것`만으로는 overwrite 이전 backup 의무가 생기지 않는다
- 해결:
  - packet에 preservation-first 문구를 고정
  - backup path report를 done-definition에 넣음

### SUBISSUE-03. Special-case troubleshooting을 subagent에 넘기려 함

- 희소하고 해석 비용이 큰 troubleshooting은 bounded implementation task와 다르다
- 예: `claude-session-poison-recovery`
- 해결:
  - rare troubleshooting은 메인 agent가 직접 처리
  - subagent는 반복 구현 조각만 맡김

### SUBISSUE-04. Scope가 넓어서 process-heavy cleanup까지 같이 끌고 감

- packet이 넓으면 구현 외의 cleanup, refactor, delete까지 같이 건드리기 쉽다
- 해결:
  - write scope를 파일 단위로 줄임
  - non-goal에 delete/rename/cleanup 금지 명시

### SUBISSUE-05. 삭제 후 stale reference가 남음

- 코드/문서 조각을 지운 뒤 `SKILL.md`, KB, checklist, smoke artifact가 예전 shape를 계속 가리킨다
- 해결:
  - main agent가 마지막에 stale grep를 돈다
  - 삭제 작업은 references triage까지 포함해 packet을 짠다

### SUBISSUE-06. “subagent로 했다”와 “실제로 위임했다”가 어긋남

- orchestration 설명과 실제 delegation 상태가 다르면 운영 기록이 흐려진다
- 해결:
  - spawn 여부를 명확히 기록
  - 메인이 직접 한 작업은 직접 했다고 적는다

### SUBISSUE-07. Done-definition에 재검증이 부족함

- worker가 구현만 끝내고 끝내면 main이 다시 context를 모아야 한다
- 해결:
  - 최소 `tests + py_compile + quick_validate`
  - 필요시 smoke artifact 갱신까지 packet에 포함

## Routing Rule

- subagent에 넘길 것:
  - bounded extension
  - split/TDD/doc cleanup
  - contract-first vertical slice 1개
  - 작은 validator/register/ledger 추가

- 메인이 직접 할 것:
  - rare troubleshooting
  - legacy/cleanup/delete 기준 정하기
  - 삭제 후 전체 문서 체인 정리
  - 최종 rerun/verification과 active-core 판단

## Related Skills

- [agent-task-packet](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/agent-task-packet/SKILL.md)
- [artifact-lifecycle-manager](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/artifact-lifecycle-manager/SKILL.md)
- [skill-creation-process](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/claude-gemini-communicator/skills/Skills-Create-Project/skill-creation-process/SKILL.md)

## Minimal Operational Rule

- subagent는 `bounded task + preservation-first + explicit done-definition` 3개가 같이 있을 때만 적극 위임한다
- 그 외는 메인이 직접 처리한다
