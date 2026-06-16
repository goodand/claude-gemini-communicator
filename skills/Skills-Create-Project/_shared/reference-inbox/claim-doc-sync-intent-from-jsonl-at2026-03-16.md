# Claude Intent Recovery — claim-verifier / doc-code-sync-checker

Source:
- `~/.claude/projects/.../26a19d71-1520-42ba-9ba3-d98b431f9d07.jsonl`
- `~/.claude/history.jsonl`

## Recovered Intent

### claim-verifier

- 출발점은 자연어 출력, 외부 피드백, 문서 서술 같은 **claim 집합**
- 반복 수작업:
  1. claim 분해
  2. 근거 파일/라인 찾기
  3. 참/거짓/부분참 판정
  4. 표로 정리
- 확장 방향:
  - `workflow-bridge-eval`의 NL claim 평가 패턴을 코드/문서 영역으로 확장
  - artifact 존재 여부와 claim을 직접 대조

### doc-code-sync-checker

- 출발점은 자연어 주장보다 **규칙 집합(rule set)** 과 계약 문서
- 반복 수작업:
  1. reference 규칙 추출
  2. validate 구현 여부 확인
  3. 다이어그램/표/상수 dict 3자 대조
  4. drift 발견 시 코드 수정 + troubleshooting 기록
- 대표 사례:
  - `dispatch-fields.md`의 symlink 규칙 미구현
  - `queued -> blocked` 전이표 누락
  - `packet-fields.md`의 why/task_id 규칙과 validate 불일치

## Boundary

- `claim-verifier`:
  - 입력 단위 = claim
  - 출력 단위 = claim별 verdict + evidence
- `doc-code-sync-checker`:
  - 입력 단위 = rule set / contract
  - 출력 단위 = missing_in_code / missing_in_doc / mismatch

## Priority Signal from Memory

- Claude는 세 후보를 `claim-verifier` / `doc-code-sync-checker` / `edge-case-generator`로 압축
- 당시 우선순위 제안은 `claim-verifier` 1순위, `doc-code-sync-checker` 2순위, `edge-case-generator` 3순위였음
- 다만 사용자가 즉시 구현 대상으로 선택한 것은 `edge-case-generator`
- 사용자는 `claim-verifier`, `doc-code-sync-checker`에 대해 "둘 다 정합성 문제인 것 같은데 내가 자료 조사 해둘께"라고 말함
